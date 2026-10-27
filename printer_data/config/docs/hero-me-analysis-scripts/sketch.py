import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle
from cadquery import importers

R="extracted/Hero Me Gen7 Release 4/Hero Me Gen7 Release V4"
def tris(solid):
    v,t=solid.tessellate(0.1,0.3); V=np.array([[q.x,q.y,q.z] for q in v]); return V[np.array(t)]
hy=importers.importStep("step/STEP/Hybrid_v1.1.0..stp").solids().vals()
carriage=tris(hy[1]); extr=tris(hy[0])
v6=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()
v6t=[tris(v6[i]) for i in (0,1,2,3)]
base=trimesh.load(R+"/Base/HMG7.2 Universal Base V2.stl").triangles

ROD_X=(-91.2,-33.2); ROD_Z=696.8; MID=-62.2
TIP0=636.4; CARR_TOP=709.5; CARR_BOT=681.9; CARR_XMIN=-102.1; CARR_XMAX=-22.3
# Hero Me base frame: width X(-40..1.6), depth Y(30.3..81.5, rear at 81.5), Z(24.9..63.4)
B_AX_Y=39.3; B_REAR=81.5; B_PAT_Z=37.85; B_BOT=24.9; B_TOP=63.4; TIP_BELOW_BOTTOM=63.2

def poly(ax,T,xi,zi,fc,ec='none',alpha=1,lw=0.2,z=2):
    ax.add_collection(PolyCollection(T[:,:,[xi,zi]],facecolors=fc,edgecolors=ec,alpha=alpha,linewidths=lw,zorder=z))
def draw_v6(ax,x0,ztip,col='#c9a227'):
    for T in v6t:
        P=T.copy(); P[:,:,0]=x0+T[:,:,0]; P[:,:,2]=ztip+6.2+T[:,:,1]
        poly(ax,P,0,2,col,'#7a6310',0.9,0.1,4)
def draw_rods(ax):
    for x in ROD_X:
        ax.add_patch(Circle((x,ROD_Z),4,fc='#8a8f98',ec='k',lw=.8,zorder=6))
    ax.plot([MID,MID],[560,775],ls=':',c='gray',lw=.8,zorder=1)
    ax.text(MID+1.5,764,'rod mid-plane',fontsize=7,color='gray')
def draw_carriage(ax,col='#444'):
    poly(ax,carriage,0,2,col,'none',1,0,3)
def draw_base(ax,mapx,mapz,col='#3b7dd8'):
    P=base.copy(); X=mapx(P[:,:,1]); Z=mapz(P[:,:,2]); T=np.stack([X,np.zeros_like(X),Z],axis=2)
    poly(ax,T,0,2,col,'#1d3f73',0.85,0.1,5)
def setup(ax,title):
    ax.set_xlim(-185,5); ax.set_ylim(560,775); ax.set_aspect('equal'); ax.set_title(title,fontsize=9,loc='left')
    ax.grid(True,alpha=.25); ax.tick_params(labelsize=7)
    ax.axhline(TIP0,ls='--',c='#d33',lw=.8,zorder=1); ax.text(3,TIP0+2,'stock nozzle-tip height',fontsize=6.5,color='#d33',ha='right')
def mark_nozzle(ax,x,ztip):
    ax.plot([x],[ztip],marker='v',c='#d33',ms=6,zorder=9)
    ax.annotate('',xy=(x,566),xytext=(MID,566),arrowprops=dict(arrowstyle='<->',lw=.9,color='k'))
    ax.text((x+MID)/2,568,'%.0f mm'%abs(x-MID),ha='center',fontsize=8,weight='bold')
    ax.plot([x,x],[566,ztip],ls=':',c='k',lw=.6)

fig,axs=plt.subplots(1,3,figsize=(19,6.2))
# A stock
ax=axs[0]; setup(ax,'A. Stock BigBox Hybrid (view along the rods)')
poly(ax,extr,0,2,'#9aa0a6','none',1,0,2)
draw_carriage(ax); draw_rods(ax); draw_v6(ax,-62.4,TIP0); mark_nozzle(ax,-62.4,TIP0)
ax.text(-100,735,'extruder',fontsize=7,color='#555'); ax.text(-100,676,'carriage',fontsize=7,color='w',zorder=9)
ax.text(-95,606,'hotend sits BETWEEN\nthe rods, ~45 mm below\nthe carriage',fontsize=7)
# B plate on carriage face
ax=axs[1]; zp=700.0; t=5.0; xp=CARR_XMIN-t
setup(ax,'B. Hero Me base bolted to a carriage face (plate behind it)')
poly(ax,extr,0,2,'#9aa0a6','none',.35,0,2)
draw_carriage(ax); draw_rods(ax)
ax.add_patch(Rectangle((xp,zp-14),t,28,fc='#e0a030',ec='k',lw=.5,zorder=5))
mx=lambda y: xp-(B_REAR-y); mz=lambda z: zp+(z-B_PAT_Z)
draw_base(ax,mx,mz)
hx=xp-(B_REAR-B_AX_Y); ztip=zp-(B_PAT_Z-(B_BOT-TIP_BELOW_BOTTOM))
draw_v6(ax,hx,ztip); mark_nozzle(ax,hx,ztip)
ax.text(xp-52,744,'Hero Me\nUniversal Base',fontsize=7,color='#1d3f73')
ax.text(-100,613,'nozzle %.0f mm lower than stock\n(bolt pattern at Z=700)'%(TIP0-ztip),fontsize=7)
ax.text(CARR_XMIN+1,690,'adapter\nplate',fontsize=6,color='#a06800',ha='right')
# C beneath
ax=axs[2]; setup(ax,'C. Hero Me base directly under the carriage')
draw_carriage(ax); draw_rods(ax)
mx=lambda y: -62.4+(y-B_AX_Y); mz=lambda z: CARR_BOT-(B_TOP-z)
draw_base(ax,mx,mz)
ztip=CARR_BOT-(B_TOP-(B_BOT-TIP_BELOW_BOTTOM))
draw_v6(ax,-62.4,ztip); mark_nozzle(ax,-62.4,ztip)
ax.text(-175,740,'nozzle %.0f mm lower than stock;\nextruder has nowhere to sit\n(carriage occupies the space\nabove the base)'%(TIP0-ztip),fontsize=7)
plt.tight_layout(); plt.savefig('out/herome_positioning.png',dpi=95)
print('ok')
