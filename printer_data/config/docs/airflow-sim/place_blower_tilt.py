import numpy as np, trimesh, itertools
from scipy import ndimage
DX=0.5; X0,X1,Y0,Y1,Z0,Z1=-44.0,14.0,298.0,368.0,636.0,708.0
nx,ny,nz=int((X1-X0)/DX),int((Y1-Y0)/DX),int((Z1-Z0)/DX); org=np.array([X0,Y0,Z0])
m=trimesh.load("shroud2/bb_dual_shroud.stl")
S=np.zeros((nx,ny,nz),bool); n=int(m.area/((DX*0.4)**2))
for c0 in range(0,n,300_000):
    p,_=trimesh.sample.sample_surface(m,min(300_000,n-c0),seed=c0); i=np.floor((p-org)/DX).astype(int)
    ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]; S[i[:,0],i[:,1],i[:,2]]=True
# blower occupancy in its own frame (x_b,y_b across, z_b thickness 0..20): disc r=20 + outlet channel + corner ears
g=np.mgrid[-21:21:DX,-21:21:DX,0:20.01:DX]; xb,yb,zb=g[0].ravel(),g[1].ravel(),g[2].ravel()
disc=(xb**2+yb**2<=20.0**2)
chan=(xb>=-19)&(xb<=9)&(yb<=0)&(yb>=-20.2)
ears=((np.abs(xb-17.5)<=3)&(np.abs(yb-17.5)<=3))|((np.abs(xb+17.5)<=3)&(np.abs(yb-17.5)<=3))|((np.abs(xb-17.5)<=3)&(np.abs(yb+17.5)<=3))
occ=disc|chan|ears; pts=np.c_[xb[occ],yb[occ],zb[occ]]
# pose: z_b->+X (inlet side toward +X), x_b->+Y, y_b->+Z  (viewed from +X as in the owner's Orca pictures)
def overlap(x0,yc,zc):
    w=np.c_[pts[:,2]+x0,pts[:,0]+yc,pts[:,1]+zc]; i=np.floor((w-org)/DX).astype(int)
    ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]
    return int(S[i[:,0],i[:,1],i[:,2]].sum())


a=np.array([-0.894,0,0.447]); a/=np.linalg.norm(a)
zb=-a; xb_v=np.array([0,1.0,0]); yb_v=np.cross(zb,xb_v); yb_v/=np.linalg.norm(yb_v)
Rm=np.c_[xb_v,yb_v,zb]; print("z_b",zb.round(3),"y_b",yb_v.round(3),"det",round(np.linalg.det(Rm),3))
P_TR=np.array([-6.75,350.0,680.0])
def ov_t(t,use_ears=True):
    O=P_TR-17.5*xb_v-17.5*yb_v-t*zb
    sel=occ if use_ears else (disc|chan)
    w=O+np.c_[xb[sel],yb[sel],zb_[sel]]@Rm.T; i=np.floor((w-org)/DX).astype(int)
    ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]; return int(S[i[:,0],i[:,1],i[:,2]].sum()),O
zb_=zb_arr=g[2].ravel()
print("overlap vs t (blower body+ears slid along its axis; t shifts z_b origin):")
for t in np.arange(-30,30.1,2.0):
    o,O=ov_t(t); ob,_=ov_t(t,False); print("  t=%5.1f ears+body %5d cells | body only %5d | origin (%.1f,%.1f,%.1f)"%(t,o,ob,*O))
