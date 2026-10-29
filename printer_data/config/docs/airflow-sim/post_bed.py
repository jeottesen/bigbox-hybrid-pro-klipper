import numpy as np, sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import memcap; memcap.apply()
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=np.load(sys.argv[1]); out=sys.argv[2]; NXn,NYn,BED=float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]); title=sys.argv[6]
ux,uy,uz,solid=R["ux"],R["uy"],R["uz"],R["solid"]; dx=float(R["dx"]); O=R["origin"]; S=75.0
sp=np.sqrt(ux**2+uy**2+uz**2)*S; sp[solid]=np.nan; nx,ny,nz=solid.shape
X=O[0]+(np.arange(nx)+0.5)*dx; Y=O[1]+(np.arange(ny)+0.5)*dx; Z=O[2]+(np.arange(nz)+0.5)*dx
XX,YY=np.meshgrid(X,Y,indexing='ij'); rr=np.sqrt((XX-NXn)**2+(YY-NYn)**2); ang=np.degrees(np.arctan2(YY-NYn,XX-NXn))
print(title)
for lab,(h0,h1) in (("0.3-2.3 mm above the bed",(0.3,2.3)),("2.3-5.3 mm above the bed",(2.3,5.3))):
    zs=(Z>=BED+h0)&(Z<BED+h1)
    for rad in (8,15,25):
        m=np.zeros(solid.shape,bool); m[:,:,zs]=((rr<rad)&(rr>3))[:,:,None]&~solid[:,:,zs]; v=sp[m]
        print("  %-26s r<%2d mm: mean %.2f m/s, max %.2f"%(lab,rad,np.nanmean(v),np.nanmax(v)))
zs=(Z>=BED+0.3)&(Z<BED+3.3)
for nm,msk in (("+X",(ang>=-45)&(ang<45)),("+Y (fan side)",(ang>=45)&(ang<135)),("-X",(ang>=135)|(ang<-135)),("-Y (front)",(ang>=-135)&(ang<-45))):
    m=np.zeros(solid.shape,bool); m[:,:,zs]=(msk&(rr<20)&(rr>3))[:,:,None]&~solid[:,:,zs]; print("  sector %-14s (0.3-3.3 mm above bed, r 3-20): mean %.2f m/s"%(nm,np.nanmean(sp[m])))
k=int(np.floor((BED+1.3-O[2])/dx))
fig,ax=plt.subplots(figsize=(8,7)); im=ax.imshow(sp[:,:,k].T,origin='lower',extent=(O[0],O[0]+nx*dx,O[1],O[1]+ny*dx),cmap='viridis',vmin=0,vmax=4); ax.plot(NXn,NYn,'r+',ms=14); ax.set_title(title+"\nair speed 1.3 mm above the bed",fontsize=9); ax.set_aspect('equal'); plt.colorbar(im,fraction=0.04,label='m/s'); plt.tight_layout(); plt.savefig(out,dpi=60)
