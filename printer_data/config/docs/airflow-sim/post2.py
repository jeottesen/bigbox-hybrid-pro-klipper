import numpy as np, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=np.load(sys.argv[1]); out=sys.argv[2]; NXn,NYn,ZT=float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]); title=sys.argv[6]
ux,uy,uz,rho,solid=R["ux"],R["uy"],R["uz"],R["rho"],R["solid"]; dx=float(R["dx"]); O=R["origin"]
S=75.0                                   # m/s per lattice velocity (same dt and viscosity in every run)
sp=np.sqrt(ux**2+uy**2+uz**2)*S; sp[solid]=np.nan
nx,ny,nz=solid.shape
X=O[0]+(np.arange(nx)+0.5)*dx; Y=O[1]+(np.arange(ny)+0.5)*dx; Z=O[2]+(np.arange(nz)+0.5)*dx
XX,YY=np.meshgrid(X,Y,indexing='ij'); rr=np.sqrt((XX-NXn)**2+(YY-NYn)**2)
res={}
for lab,(z0,z1) in (("tip zone (tip-2.6..tip+4.4)",(ZT-2.6,ZT+4.4)),("just above (tip+4.4..tip+14.4)",(ZT+4.4,ZT+14.4)),("below the tip (tip-8..tip-2.6)",(ZT-8.0,ZT-2.6))):
    for rad in (6,10,15):
        zs=(Z>=z0)&(Z<z1); m=np.zeros(solid.shape,bool); m[:,:,zs]=(rr<rad)[:,:,None]&~solid[:,:,zs]
        v=sp[m]; res[(lab,rad)]=(np.nanmean(v) if v.size else float('nan'),np.nanmax(v) if v.size else float('nan'))
print(title)
for (lab,rad),(mn,mx) in res.items(): print("  %-34s r<%2d mm: mean %.2f m/s, max %.2f"%(lab,rad,mn,mx))
# which side the air reaches the nozzle from (tip zone, r<15): angle sectors of mean speed
zs=(Z>=ZT-2.6)&(Z<ZT+4.4); ang=np.degrees(np.arctan2(YY-NYn,XX-NXn))
for nm,(a0,a1) in (("+X (right)",(-45,45)),("+Y",(45,135)),("-X (left)",(135,180)),("-Y",(-135,-45))):
    if nm=="-X (left)": msk=(ang>=135)|(ang<-135)
    else: msk=(ang>=a0)&(ang<a1)
    m=np.zeros(solid.shape,bool); m[:,:,zs]=(msk&(rr<15)&(rr>4))[:,:,None]&~solid[:,:,zs]; print("  sector %-10s mean %.2f m/s"%(nm,np.nanmean(sp[m])))
fig,axs=plt.subplots(1,3,figsize=(20,6.5))
def show(ax,img,ext,t,vmax):
    im=ax.imshow(img.T,origin='lower',extent=ext,cmap='viridis',vmin=0,vmax=vmax); ax.set_title(t,fontsize=9); ax.set_aspect('equal'); plt.colorbar(im,ax=ax,fraction=0.04,label='m/s')
k=int(np.floor((ZT+1.5-O[2])/dx)); show(axs[0],sp[:,:,k],(O[0],O[0]+nx*dx,O[1],O[1]+ny*dx),"top view, 1.5 mm above the tip (+ = nozzle)",3.0); axs[0].plot(NXn,NYn,'r+',ms=14)
j=int(np.floor((NYn-O[1])/dx)); show(axs[1],sp[:,j,:],(O[0],O[0]+nx*dx,O[2],O[2]+nz*dx),"section through the nozzle axis, X-Z",3.0)
i=int(np.floor((NXn-O[0])/dx)); show(axs[2],sp[i,:,:],(O[1],O[1]+ny*dx,O[2],O[2]+nz*dx),"section through the nozzle axis, Y-Z",3.0)
fig.suptitle(title,fontsize=10); plt.tight_layout(); plt.savefig(out,dpi=55)
