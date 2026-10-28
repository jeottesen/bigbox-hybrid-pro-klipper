"""Rough Hero Me comparison case (NOT a validated baseline): W-left 4020 duct + V6 + approximate sock, in the duct file frame.
Nozzle axis (X=-142.4, Y=22.0) from the gauge/mirror symmetry; nozzle tip at Z=4.27 so the duct tips sit 1.6 mm above it.
The blower interface could not be located, so the flow is injected inside the duct's slanted tube at Z=30 along the tube axis."""
import numpy as np, trimesh, sys
from scipy import ndimage
import cadquery as cq
from cadquery import importers
DX=1.0
NX_,NY_,TIPZ=-142.4,22.0,4.27
X0,X1=-215.0,-100.0; Y0,Y1=-30.0,70.0; Z0,Z1=-4.0,58.0
nx,ny,nz=int(round((X1-X0)/DX)),int(round((Y1-Y0)/DX)),int(round((Z1-Z0)/DX))
R="extracted/Hero Me Gen7 Release 4/Hero Me Gen7 Release V4/Part Cooling Ducts/Standard Ducts/4020 fans/HMG7.4 Standard Single 4020W Left Duct V3.stl"
duct=trimesh.load(R)
solid=np.zeros((nx,ny,nz),bool)
def vox(m,fill):
    vg=m.voxelized(DX); pts=vg.points
    idx=np.floor((pts-np.array([X0,Y0,Z0]))/DX).astype(int)
    ok=(idx[:,0]>=0)&(idx[:,0]<nx)&(idx[:,1]>=0)&(idx[:,1]<ny)&(idx[:,2]>=0)&(idx[:,2]<nz)
    idx=idx[ok]; part=np.zeros_like(solid); part[idx[:,0],idx[:,1],idx[:,2]]=True
    return ndimage.binary_fill_holes(part) if fill else part
d=vox(duct,False); solid|=d; print("duct cells",int(d.sum()))
# V6 hotend (solids 0..3): x_v->+Y, y_v->+Z, z_v->+X; axis at (NX_,NY_); tip at TIPZ (tip is y_v=-6.2)
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
for s in V:
    r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120).translate(cq.Vector(NX_,NY_,TIPZ+6.2))
    v,t=r.tessellate(0.05,0.2); m=trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t),process=True)
    solid|=vox(m,True)
def ix(x): return int(np.floor((x-X0)/DX))
def iy(y): return int(np.floor((y-Y0)/DX))
def iz(z): return int(np.floor((z-Z0)/DX))
# approximate sock around the block (block: Y NY_-15.5..NY_+4.5, Z TIPZ+5.0..TIPZ+16.5)
cy=NY_-5.5; sx0,sx1=ix(NX_-9.75),ix(NX_+9.75); sy0,sy1=iy(cy-11.75),iy(cy+11.75); sz0,sz1=iz(TIPZ+3.5),iz(TIPZ+18.0)
sock=np.zeros_like(solid); sock[sx0:sx1+1,sy0:sy1+1,sz0:sz1+1]=True
inner=np.zeros_like(solid); wl=1; inner[sx0+wl:sx1-wl+1,sy0+wl:sy1-wl+1,sz0+wl:]=True; sock&=~inner
xx,yy=np.meshgrid(np.arange(nx),np.arange(ny),indexing='ij'); rr=np.sqrt(((xx+0.5)*DX+X0-NX_)**2+((yy+0.5)*DX+Y0-NY_)**2); sock[rr<4.5]=False
solid|=sock
# internal inlet: enclosed fluid cross-section of the duct tube at Z=30
ZI=30.0; k=iz(ZI); sl=~solid[:,:,k]; lab,nl=ndimage.label(sl)
edge=set(np.unique(np.r_[lab[0,:],lab[-1,:],lab[:,0],lab[:,-1]]))
enc=[l for l in range(1,nl+1) if l not in edge]
areas=[(int((lab==l).sum()),l) for l in enc]; print("enclosed fluid regions at Z=%.0f (cells, label):"%ZI,sorted(areas,reverse=True)[:5])
big=max(areas)[1]; inlet=np.zeros_like(solid); inlet[:,:,k]=(lab==big)
# cap everything upstream: enclosed fluid in slices above, within this tube's footprint
for kk in range(k+1,nz):
    s2=~solid[:,:,kk]; l2,n2=ndimage.label(s2)
    e2=set(np.unique(np.r_[l2[0,:],l2[-1,:],l2[:,0],l2[:,-1]]))
    for l in range(1,n2+1):
        if l in e2: continue
        reg=(l2==l)
        if (reg&ndimage.binary_dilation(inlet[:,:,k],iterations=12)).any(): solid[:,:,kk]|=reg
solid[inlet]=False; solid[:,:,-1]=True
np.savez_compressed("sim/grid_hero.npz",solid=solid,inlet=inlet,origin=np.array([X0,Y0,Z0]),dx=DX,nozzle=np.array([NX_,NY_,TIPZ]))
print("grid",nx,ny,nz,"cells %.2fM"%(nx*ny*nz/1e6),"inlet cells",int(inlet.sum()))
