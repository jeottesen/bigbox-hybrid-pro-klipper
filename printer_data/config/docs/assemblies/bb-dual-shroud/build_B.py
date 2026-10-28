"""Assembly B: owner-supplied BB Dual part-fan shroud (STL, assembled frame) + V6 (slot 1) + approximate sock + carriage. Blower omitted (position unknown)."""
import numpy as np, trimesh, sys
from scipy import ndimage
import cadquery as cq
from cadquery import importers
DX=0.5; X0,X1,Y0,Y1,Z0,Z1=-112.0,6.0,268.0,372.0,628.0,716.0
nx,ny,nz=int((X1-X0)/DX),int((Y1-Y0)/DX),int((Z1-Z0)/DX); org=np.array([X0,Y0,Z0])
def surf(m,fill=False):
    g=np.zeros((nx,ny,nz),bool); n=int(min(4_000_000,max(50_000,m.area/((DX*0.4)**2))))
    for c0 in range(0,n,300_000):
        p,_=trimesh.sample.sample_surface(m,min(300_000,n-c0),seed=c0); i=np.floor((p-org)/DX).astype(int)
        ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]; g[i[:,0],i[:,1],i[:,2]]=True
    return ndimage.binary_fill_holes(g) if fill else g
def tomesh(s):
    v,t=s.tessellate(0.05,0.2); return trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t),process=True)
shroud=trimesh.load("shroud2/bb_dual_shroud.stl"); S=surf(shroud)
A=importers.importStep("step/STEP/bigbox_v1.1.0.stp").solids().vals(); H=importers.importStep("step/STEP/Hybrid_v1.1.0..stp").solids().vals()
car={"carriage_single_(bigbox_v1.1.0 #65)":A[65],"carriage_hybrid_(Hybrid #1)":H[1]}
for k,s in car.items():
    C=surf(tomesh(s),True); print("overlap shroud x %-38s %d cells = %.2f mm3"%(k,int((S&C).sum()),(S&C).sum()*DX**3))
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
best=None
for ang in (0,90,180,270):
    G=np.zeros_like(S)
    for s in V:
        r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120).rotate(cq.Vector(0,0,0),cq.Vector(0,0,1),ang).translate(cq.Vector(-62.4,308.0,696.8-55.0))
        G|=surf(tomesh(r),True)
    ov=int((S&G).sum()); print("V6 rotated %3d deg about Z: overlap with shroud %d cells = %.2f mm3"%(ang,ov,ov*DX**3))
    if best is None or ov<best[0]: best=(ov,ang)
print("best V6 orientation:",best)
