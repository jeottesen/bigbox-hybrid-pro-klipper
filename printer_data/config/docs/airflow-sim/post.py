import numpy as np, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=np.load(sys.argv[1]); out=sys.argv[2]
ux,uy,uz,rho,solid=R["ux"],R["uy"],R["uz"],R["rho"],R["solid"]; dx=float(R["dx"]); O=R["origin"]; uin=float(R["uin"])
S=3.0/uin                       # m/s per lattice velocity if the blower window speed is 3 m/s
sp=np.sqrt(ux**2+uy**2+uz**2)*S; sp[solid]=np.nan
nx,ny,nz=solid.shape
X=O[0]+(np.arange(nx)+0.5)*dx; Y=O[1]+(np.arange(ny)+0.5)*dx; Z=O[2]+(np.arange(nz)+0.5)*dx
def idx(v,o): return int(np.floor((v-o)/dx))
nxi,nyi=idx(-62.4,O[0]),idx(308.0,O[1])
# --- metrics
inl=R["rho"]*0  # placeholder
# flux through boundaries (lattice units, only outward) and into window
def flux(face):
    if face=="bottom": return float((rho[:,:,1]*(-uz[:,:,1])).clip(0).sum())
    if face=="xmin": return float((rho[1,:,:]*(-ux[1,:,:])).clip(0).sum())
    if face=="xmax": return float((rho[-2,:,:]*(ux[-2,:,:])).clip(0).sum())
    if face=="ymin": return float((rho[:,1,:]*(-uy[:,1,:])).clip(0).sum())
    if face=="ymax": return float((rho[:,-2,:]*(uy[:,-2,:])).clip(0).sum())
fl={k:flux(k) for k in ("bottom","xmin","xmax","ymin","ymax")}
tot=sum(fl.values()); print("outflow share by domain face (diffusive/open-boundary estimate):",{k:round(v/tot*100,1) for k,v in fl.items()})
# near-nozzle zone: cells within r<10 mm of the nozzle axis, Z 633..642
XX,YY=np.meshgrid(X,Y,indexing='ij')
rr=np.sqrt((XX+62.4)**2+(YY-308.0)**2)
for z0,z1,label in ((633,640,"tip zone Z 633-640"),(640,650,"Z 640-650")):
    zs=(Z>=z0)&(Z<z1); m=np.zeros(solid.shape,bool); m[:,:,zs]=(rr<10)[:,:,None]&~solid[:,:,zs]
    print("%-20s mean air speed within 10 mm of the nozzle axis: %.2f m/s (max %.2f)"%(label,np.nanmean(sp[m]),np.nanmax(sp[m])))
# split left/right of the nozzle (X) and front/back (Y) at tip zone
zs=(Z>=633)&(Z<640)
for nm,msk in (("X<axis (left)",XX<-62.4),("X>axis (right)",XX>-62.4),("Y<axis (front of nozzle)",YY<308.0),("Y>axis (fan side)",YY>308.0)):
    m=np.zeros(solid.shape,bool); m[:,:,zs]=(msk&(rr<14))[:,:,None]&~solid[:,:,zs]
    print("  %-26s mean speed %.2f m/s"%(nm,np.nanmean(sp[m])))
# --- plots
fig,axs=plt.subplots(2,3,figsize=(21,12))
def show(ax,img,ext,title,vmax=4.0):
    im=ax.imshow(img.T,origin='lower',extent=ext,cmap='viridis',vmin=0,vmax=vmax); ax.set_title(title,fontsize=9); ax.set_aspect('equal'); plt.colorbar(im,ax=ax,fraction=0.04,label='m/s')
for ax,zv in zip(axs[0][:2],(637.0,643.0)):
    k=idx(zv,O[2]); show(ax,sp[:,:,k],(O[0],O[0]+nx*dx,O[1],O[1]+ny*dx),"air speed, top view at Z=%.0f (nozzle tip at 635.6); nozzle marked +"%zv); ax.plot(-62.4,308,'r+',ms=14); ax.set_xlabel("X across rods");ax.set_ylabel("Y along rods (fan at 344-364)")
j=nyi; show(axs[0][2],sp[:,j,:],(O[0],O[0]+nx*dx,O[2],O[2]+nz*dx),"section through the nozzle axis (X-Z) at Y=308")
i=nxi; show(axs[1][0],sp[i,:,:],(O[1],O[1]+ny*dx,O[2],O[2]+nz*dx),"section along the rods at X=-62.4 (Y-Z)")
i2=idx(-77.0,O[0]); show(axs[1][1],sp[i2,:,:],(O[1],O[1]+ny*dx,O[2],O[2]+nz*dx),"section at X=-77 (left channel) (Y-Z)")
i3=idx(-48.0,O[0]); show(axs[1][2],sp[i3,:,:],(O[1],O[1]+ny*dx,O[2],O[2]+nz*dx),"section at X=-48 (right channel) (Y-Z)")
plt.tight_layout();plt.savefig(out,dpi=55)
