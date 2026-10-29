"""Owner-supplied BB Dual shroud + V6 (slot 1, block toward -X) + approximate sock + Hybrid carriage + bed + blower (pose from the tilted screw-hole axis)."""
import numpy as np, trimesh, sys
from scipy import ndimage
import cadquery as cq
from cadquery import importers
DX=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
X0,X1,Y0,Y1,Z0,Z1=-92.0,18.0,276.0,368.0,628.0,712.0
nx,ny,nz=int(round((X1-X0)/DX)),int(round((Y1-Y0)/DX)),int(round((Z1-Z0)/DX)); org=np.array([X0,Y0,Z0])
solid=np.zeros((nx,ny,nz),bool)
def surf(m,fill=False):
    g=np.zeros_like(solid); n=int(min(4_000_000,max(30_000,m.area/((DX*0.4)**2))))
    for c0 in range(0,n,300_000):
        p,_=trimesh.sample.sample_surface(m,min(300_000,n-c0),seed=c0); i=np.floor((p-org)/DX).astype(int)
        ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]; g[i[:,0],i[:,1],i[:,2]]=True
    return ndimage.binary_fill_holes(g) if fill else g
def tomesh(s):
    v,t=s.tessellate(0.05,0.2); return trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t),process=True)
solid|=surf(trimesh.load("shroud2/bb_dual_shroud.stl"))
H=importers.importStep("step/STEP/Hybrid_v1.1.0..stp").solids().vals(); solid|=surf(tomesh(H[1]),True)
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
for s in V:
    r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120).rotate(cq.Vector(0,0,0),cq.Vector(0,0,1),270).translate(cq.Vector(-62.4,308.0,696.8-55.0)); solid|=surf(tomesh(r),True)
def ix(x): return int(np.floor((x-X0)/DX))
def iy(y): return int(np.floor((y-Y0)/DX))
def iz(z): return int(np.floor((z-Z0)/DX))
sx0,sx1=ix(-67.9-11.75),ix(-67.9+11.75); sy0,sy1=iy(308-9.75),iy(308+9.75); sz0,sz1=iz(638.1),iz(652.6)
sock=np.zeros_like(solid); sock[sx0:sx1+1,sy0:sy1+1,sz0:sz1+1]=True
inner=np.zeros_like(solid); wl=max(1,int(round(1.5/DX))); inner[sx0+wl:sx1-wl+1,sy0+wl:sy1-wl+1,sz0+wl:]=True; sock&=~inner
xx,yy=np.meshgrid(np.arange(nx),np.arange(ny),indexing='ij'); rr=np.sqrt(((xx+0.5)*DX+X0+62.4)**2+((yy+0.5)*DX+Y0-308.0)**2); sock[rr<4.5]=False; sock[:,:,sz1+1:]=False
solid|=sock
# bed 0.3 mm below the tip
kb=int(np.floor((635.3-Z0)/DX)); solid[:,:,:kb]=True
# blower
xbv=np.array([0,1.0,0]); a=np.array([-0.894,0,0.447]); a/=np.linalg.norm(a); zbv=-a; ybv=np.cross(zbv,xbv); ybv/=np.linalg.norm(ybv)
Rm=np.c_[xbv,ybv,zbv]; T=-5.0
O=np.array([-6.75,350.0,680.0])-17.5*xbv-17.5*ybv-T*zbv
g=np.mgrid[-21:21:DX*0.5,-21:21:DX*0.5,0:20.01:DX*0.5]; xb,yb,zb=g[0].ravel(),g[1].ravel(),g[2].ravel()
disc=(xb**2+yb**2<=20.0**2); ears=((np.abs(np.abs(xb)-17.5)<=3)&(np.abs(yb-17.5)<=3))|((np.abs(xb-17.5)<=3)&(np.abs(yb+17.5)<=3))
chan=(xb>=-19)&(xb<=9)&(yb<=0)&(yb>=-20.2)
body=(disc|ears|chan)
pts=np.c_[xb[body],yb[body],zb[body]]; w=O+pts@Rm.T; i=np.floor((w-org)/DX).astype(int)
ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]
blow=np.zeros_like(solid); blow[i[:,0],i[:,1],i[:,2]]=True
# outlet slot layer just outside the outlet face (y_b -22 .. -20.4), x_b -18..8, z_b 1.5..18.5
g2=np.mgrid[-18:8.01:DX*0.5,-23.0:-20.9:DX*0.5,1.5:18.51:DX*0.5].reshape(3,-1).T; w2=O+g2@Rm.T; i2=np.floor((w2-org)/DX).astype(int)
ok=(i2[:,0]>=0)&(i2[:,0]<nx)&(i2[:,1]>=0)&(i2[:,1]<ny)&(i2[:,2]>=0)&(i2[:,2]<nz); i2=i2[ok]
inlet=np.zeros_like(solid); inlet[i2[:,0],i2[:,1],i2[:,2]]=True
solid|=blow; solid[inlet]=False
# thin the inlet to a single-cell layer: keep cells whose neighbour in direction (+y_b) is solid (blower side)
d=-ybv   # flow direction (outlet normal)
inl=np.argwhere(inlet); print("inlet cells (slab)",len(inl))
Aperp=26.0*17.0; uvec=0.0412*d; print("flow direction",d.round(3),"uvec",uvec.round(4),"outlet centre",(O+np.array([-5,-21.5,10.0])@Rm.T).round(1))
solid[:,:,-1]=True
np.savez_compressed("sim/grid_B_%.2f.npz"%DX,solid=solid,inlet=inlet,origin=org,dx=DX,uvec=uvec)
print("grid",nx,ny,nz,"cells %.2fM"%(nx*ny*nz/1e6),"solid fraction %.3f"%solid.mean())
