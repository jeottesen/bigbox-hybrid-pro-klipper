"""Seat the owner's real blower STEP on the shroud's two prong lugs (hole axis a, lug faces d=306.19/313.94 along a). Try 4 rotations x 2 axis signs x mirror."""
import numpy as np, trimesh, itertools
from scipy import ndimage
exec(open("asm/fit_blower_real.py").read().split("a=np.array([-0.894")[0])   # reuse S, loc (blower cells), DX, org
a=np.array([-0.894,0,0.447]); a/=np.linalg.norm(a); b=np.array([0,1.0,0]); c=np.cross(a,b); c/=np.linalg.norm(c)
Sd=ndimage.binary_dilation(S,iterations=1)
# ear z-extent in blower frame
ear=(np.abs(np.abs(loc[:,0])-17.5)<3)&(np.abs(np.abs(loc[:,1])-17.5)<3); print("ear cells z range",loc[ear,2].min().round(2),loc[ear,2].max().round(2))
P0=np.array([-6.75,350.0,680.0]); Pc=P0.copy(); Pc[1]=332.5      # centre of the two prong holes (Y 315/350)
def cnt(arr):
    i=np.floor((arr-org)/DX).astype(int); ok=(i>=0).all(1)&(i[:,0]<nx)&(i[:,1]<ny)&(i[:,2]<nz); j=tuple(i[ok].T); return int(S[j].sum()),int(Sd[j].sum())
res=[]
for sgn,flip,k in itertools.product((1,-1),(1,-1),range(4)):
    th=k*np.pi/2; Rz=np.array([[np.cos(th),-np.sin(th),0],[np.sin(th),np.cos(th),0],[0,0,1]]); F=np.diag([flip,1,1])
    pl=loc@F.T@Rz.T
    # blower frame -> world: local z -> sgn*(-a)... local x -> b, local y -> c-ish
    zw=sgn*a; xw=b; yw=np.cross(zw,xw); R=np.c_[xw,yw,zw]
    for v in np.arange(-6,6.1,1.0):           # shift along yw (ring tilt direction) to put top ears on the prongs
        for t in np.arange(-14,14.1,0.5):
            O=Pc+v*yw+t*zw; o,cl=cnt(O+pl@R.T); res.append((o,-cl,sgn,flip,k,v,t))
good=[r for r in res if r[0]==0]; good.sort(key=lambda r:r[1])
print("zero-overlap poses:",len(good)); 
for r in good[:15]: print("  ov0 contact %d  sgn %d flip %d rot %d  v=%.1f t=%.1f"%(-r[1],*r[2:]))
