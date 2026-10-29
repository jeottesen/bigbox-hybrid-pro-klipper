"""Fit the owner's real blower STEP (housing solid #0, impeller #1) into the BB Dual shroud ring.
Pose family: z_b = -a (a = tilted screw-hole axis), x_b = +Y; origin shifted by (u along x_b, v along y_b, t along z_b) from the top-right hole."""
import numpy as np, trimesh, sys
from scipy import ndimage
from cadquery import importers
DX=0.25; X0,X1,Y0,Y1,Z0,Z1=-45.0,5.0,310.0,360.0,655.0,700.0
nx,ny,nz=int((X1-X0)/DX),int((Y1-Y0)/DX),int((Z1-Z0)/DX); org=np.array([X0,Y0,Z0])
def vox(pts):
    i=np.floor((pts-org)/DX).astype(int); ok=(i>=0).all(1)&(i[:,0]<nx)&(i[:,1]<ny)&(i[:,2]<nz); g=np.zeros((nx,ny,nz),bool); g[tuple(i[ok].T)]=True; return g
m=trimesh.load("shroud2/bb_dual_shroud.stl"); S=np.zeros((nx,ny,nz),bool)
n=int(m.area/((DX*0.4)**2))
for c0 in range(0,n,500_000):
    p,_=trimesh.sample.sample_surface(m,min(500_000,n-c0),seed=c0); S|=vox(p)
F="/home/claude/workspace/worktrees/bigbox-herome-gen7/printer_data/config/docs/assemblies/blower_4020_PM_from_owner.step"
H=importers.importStep(F).solids().vals()[0]
v,t=H.tessellate(0.02,0.1); bm=trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t))
bp,_=trimesh.sample.sample_surface(bm,400_000,seed=1)
# interior points of blower: fill via voxel in local frame
L=0.25; lo=np.array([-21,-21,-1.]); sh=(np.array([42,42,22])/L).astype(int)
li=np.floor((bp-lo)/L).astype(int); ok=(li>=0).all(1)&(li[:,0]<sh[0])&(li[:,1]<sh[1])&(li[:,2]<sh[2]); G=np.zeros(tuple(sh),bool); G[tuple(li[ok].T)]=True
G=ndimage.binary_fill_holes(G); loc=(np.argwhere(G)+0.5)*L+lo
print("blower cells",len(loc),"volume mm3",len(loc)*L**3)
a=np.array([-0.894,0,0.447]); a/=np.linalg.norm(a); zb=-a; xb=np.array([0,1.0,0]); yb=np.cross(zb,xb); yb/=np.linalg.norm(yb)
R=np.c_[xb,yb,zb]; P=np.array([-6.75,350.0,680.0])
def ov(u,w,tt):
    O=P-17.5*xb-17.5*yb-tt*zb+u*xb+w*yb; wp=O+loc@R.T; i=np.floor((wp-org)/DX).astype(int)
    ok=(i>=0).all(1)&(i[:,0]<nx)&(i[:,1]<ny)&(i[:,2]<nz); return int(S[tuple(i[ok].T)].sum()),O
res=[]
for tt in np.arange(-8,8.1,1.0):
    for u in np.arange(-2,2.1,0.5):
        for w in np.arange(-2,2.1,0.5):
            o,O=ov(u,w,tt); res.append((o,tt,u,w))
res.sort(); print("lowest overlaps (cells of 0.25^3 mm3):")
for r in res[:10]: print("  ov %5d  t=%.1f u=%.1f w=%.1f -> %.4f mm3"%(r[0],r[1],r[2],r[3],r[0]*DX**3))
o,O=ov(*res[0][2:4][::1],res[0][1]) if False else ov(res[0][2],res[0][3],res[0][1]); print("best origin",O.round(2))
print("\nDepth scan: for each (u,w) the largest t (deepest along -z_b ... t grows toward +z_b origin shift) with zero overlap, and overlap at t+1")
out=[]
for u in np.arange(-3,3.1,0.5):
    for w in np.arange(-3,3.1,0.5):
        ts=np.arange(-12,12.1,0.5); ovs=[ov(u,w,tt)[0] for tt in ts]
        zero=[tt for tt,o in zip(ts,ovs) if o==0]
        # first contact when moving t upward from -12: smallest t where overlap>0
        first=next((tt for tt,o in zip(ts,ovs) if o>0),None)
        out.append((first if first is not None else 99,u,w))
out.sort(reverse=True)
print("largest 'first overlap' t (blower seats deepest before colliding):")
for f,u,w in out[:10]: print("  first overlap at t=%s  u=%.1f w=%.1f"%(f,u,w))
print("u=0,w=0 profile:",[(float(tt),ov(0,0,tt)[0]) for tt in np.arange(-12,12.1,2)])
