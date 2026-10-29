"""Owner-supplied BB Dual shroud + V6 (slot 1, block toward -X) + approximate sock + Hybrid carriage + bed + NO blower body: flow injected straight across the shroud's duct mouth (fan 'fudged')."""
import numpy as np, trimesh, sys
from scipy import ndimage
import cadquery as cq
from cadquery import importers
DX=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
X0,X1,Y0,Y1,Z0,Z1=-92.0,-16.0,276.0,352.0,628.0,672.0
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
# fudged fan housing: closed chimney (stand-in for the blower's outlet walls) around the mouth, 1 mm walls, from the lid level up to Z 662, and the +X end wall raised to meet it
def box(x0,x1,y0,y1,z0,z1): solid[ix(x0):ix(x1)+1,iy(y0):iy(y1)+1,iz(z0):iz(z1)+1]=True
box(-34.5,-33.5,310,344,645,662); box(-22.5,-21.5,310,344,640,662); box(-34.5,-21.5,309.5,310.5,645,662); box(-34.5,-21.5,343.5,344.5,645,662)
# fudged fan: velocity inlet layer across the duct mouth (X -33..-24, Y 312..340, Z 651.5), flow straight down, same volumetric flow as the stock runs (476 cells x 0.04)
inlet=np.zeros_like(solid); inlet[ix(-33):ix(-24)+1,iy(312):iy(340)+1,iz(651.5)]=True
print("inlet cells",int(inlet.sum()),"free before:",int((~solid[inlet]).sum())); solid[inlet]=False
uin=0.04*476.0/(inlet.sum()*DX*DX); print("uin (lattice)",round(uin,4),"=",round(uin*75,2),"m/s")
solid[:,:,-1]=True
np.savez_compressed("sim/grid_C4_%.2f.npz"%DX,solid=solid,inlet=inlet,origin=org,dx=DX,uin=uin)
print("grid",nx,ny,nz,"cells %.2fM"%(nx*ny*nz/1e6),"solid fraction %.3f"%solid.mean())
# connectivity: air path from the inlet to the nozzle surroundings, enclosed channel?
lab,n=ndimage.label(~solid); il=np.unique(lab[inlet]); print("inlet component(s)",il,"| cells",[int((lab==k).sum()) for k in il],"| outside label",lab[0,0,nz-3] if False else lab[1,1,iz(660)])
