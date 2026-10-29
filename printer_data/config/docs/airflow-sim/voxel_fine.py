"""Voxelise the stock single-head cooling assembly (carriage, two-piece fan mount, V6) on a 1 mm grid for the LBM test."""
import numpy as np, trimesh, sys
import os
sys_path_dir=os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0,sys_path_dir)   # python -I drops the script dir
import memcap; memcap.apply()
CH=memcap.chunk(200,hi=300_000)   # surface-sample points per chunk (about 200 bytes each with temporaries)

from scipy import ndimage
from cadquery import importers
import cadquery as cq
DX=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
X0,X1=-92.0,-30.0; Y0,Y1=284.0,368.0; Z0,Z1=626.0,690.0
nx,ny,nz=int(round((X1-X0)/DX)),int(round((Y1-Y0)/DX)),int(round((Z1-Z0)/DX))
A=importers.importStep("step/STEP/bigbox_v1.1.0.stp").solids().vals()
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
def place_v6(s):
    r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120); return r.translate(cq.Vector(-62.4,308.0,696.8-55.0))
parts={"carriage":A[65],"front":A[66],"back":A[64]}
for k,s in enumerate(V): parts["v6_%d"%k]=place_v6(s)
solid=np.zeros((nx,ny,nz),bool)
def mesh(s):
    v,t=s.tessellate(0.05,0.2); m=trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t),process=True); return m
for name,s in parts.items():
    m=mesh(s)
    # memory-light surface voxelisation: dense area-weighted surface samples in chunks (trimesh.voxelized used >1 GB at 0.5 mm)
    part=np.zeros_like(solid); n=int(min(4_000_000,max(50_000,m.area/((DX*0.4)**2)))); rng=np.random.default_rng(0); org=np.array([X0,Y0,Z0])
    for c0 in range(0,n,CH):
        pts,_=trimesh.sample.sample_surface(m,min(CH,n-c0),seed=int(c0))
        idx=np.floor((pts-org)/DX).astype(int)
        ok=(idx[:,0]>=0)&(idx[:,0]<nx)&(idx[:,1]>=0)&(idx[:,1]<ny)&(idx[:,2]>=0)&(idx[:,2]<nz)
        idx=idx[ok]; part[idx[:,0],idx[:,1],idx[:,2]]=True
    if name.startswith("v6") or name=="carriage":
        part=ndimage.binary_fill_holes(part)           # bulky bodies: fill the inside
    solid|=part
    print(name,"watertight",m.is_watertight,"cells",int(part.sum()))
# blower: solid block above the tray windows, with a one-cell inlet layer at the blower outlet footprint
def ix(x): return int(np.floor((x-X0)/DX))
def iy(y): return int(np.floor((y-Y0)/DX))
def iz(z): return int(np.floor((z-Z0)/DX))
bx0,bx1,by0,by1=ix(-82.6),ix(-42.2),iy(344.2),iy(364.2)
zin=iz(648.0)
solid[bx0:bx1+1,by0:by1+1,zin+1:]=True
inlet=np.zeros_like(solid); 
x0,x1,y0,y1=ix(-70.5),ix(-44.0),iy(346.0),iy(362.5)
inlet[x0:x1+1,y0:y1+1,zin]=True
solid[inlet]=False
solid[:,:,-1]=True   # lid
SOCK=(len(sys.argv)>2 and sys.argv[2]=="sock")
if SOCK:
    # APPROXIMATE silicone sock (the supplied sock file is Fusion-only and could not be read): open-top box shell around the heater block
    sx0,sx1=ix(-62.4-9.75),ix(-62.4+9.75); sy0,sy1=iy(302.5-11.75),iy(302.5+11.75); sz0,sz1=iz(638.9),iz(652.6)
    sock=np.zeros_like(solid); sock[sx0:sx1+1,sy0:sy1+1,sz0:sz1+1]=True
    inner=np.zeros_like(solid); wl=max(1,int(round(1.5/DX)))
    inner[sx0+wl:sx1-wl+1,sy0+wl:sy1-wl+1,sz0+wl:]=True; sock&=~inner
    xx,yy=np.meshgrid(np.arange(nx),np.arange(ny),indexing='ij'); rr=np.sqrt(((xx+0.5)*DX+X0+62.4)**2+((yy+0.5)*DX+Y0-308.0)**2)
    sock[rr<4.5]=False                                  # nozzle comes through the floor
    sock[:,:,sz1+1:]=False
    solid|=sock; print("sock cells",int(sock.sum()))
np.savez_compressed("sim/gridfine_%.2f%s.npz"%(DX,"_sock" if SOCK else ""),solid=solid,inlet=inlet,origin=np.array([X0,Y0,Z0]),dx=DX)
print("grid",nx,ny,nz,"cells %.2fM"%(nx*ny*nz/1e6),"solid fraction %.3f"%solid.mean(),"inlet cells",int(inlet.sum()))
# connectivity check: can air reach the nozzle zone from the inlet?
fluid=~solid; lab,n=ndimage.label(fluid)
il=np.unique(lab[inlet]); il=il[il>0]; print("fluid components:",n,"inlet in component(s)",il)
reach=np.isin(lab,il); 
nzx,nzy=ix(-62.4),iy(308.0); 
print("cells reachable from inlet:",int(reach.sum()),"| cell next to the nozzle tip reachable:",bool(reach[nzx+6,nzy,iz(636.5)] or reach[nzx-6,nzy,iz(636.5)] or reach[nzx,nzy-6,iz(636.5)] or reach[nzx,nzy+6,iz(636.5)]))
