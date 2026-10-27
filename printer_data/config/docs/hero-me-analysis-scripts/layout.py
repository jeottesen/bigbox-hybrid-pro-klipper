import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle
from cadquery import importers
T=np.load('out/asm_tris.npy'); c=T.mean(1)
m=(c[:,0]>200)&(c[:,0]<360)&(c[:,1]>-320)&(c[:,1]<-190)&(c[:,2]>455)&(c[:,2]<630)
S=T[m].copy(); S[:,:,0]-=296.9; S[:,:,1]+=258.2; S[:,:,2]-=524.5   # local: X' along rods, Y' across (+ = rear), Z' up from rod axis
v6=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()
def tris(s):
    v,t=s.tessellate(0.1,0.3); V=np.array([[q.x,q.y,q.z] for q in v]); return V[np.array(t)]
v6t=[tris(v6[i]) for i in (0,1,2,3)]
def draw_v6(ax,col='#c9a227'):
    for Tt in v6t:
        P=Tt[:,:,[0,1]].copy(); P[:,:,1]=Tt[:,:,1]-55
        ax.add_collection(PolyCollection(P,facecolors=col,edgecolors='#7a6310',linewidths=.1,alpha=.95,zorder=4))
RY=28.9
def rods(ax):
    for y in (-RY,RY):
        ax.add_patch(Circle((y,0),4,fc='#8a8f98',ec='k',zorder=6)); ax.add_patch(Circle((y,0),7.5,fc='none',ec='#555',lw=1,ls='--',zorder=6))
fig,axs=plt.subplots(1,2,figsize=(15,7.5))
# left: stock head, view along rods (Y' horizontal, Z' vertical)
ax=axs[0]
order=np.argsort(S.mean(1)[:,0])
ax.add_collection(PolyCollection(S[order][:,:,[1,2]],facecolors='#b9c2cc',edgecolors='none',alpha=.9,zorder=2))
rods(ax); draw_v6(ax)
ax.set_xlim(-60,70); ax.set_ylim(-70,100); ax.set_aspect('equal'); ax.grid(True,alpha=.3)
ax.set_title('Stock Hybrid head from the assembly model\nview along the rods; origin = V6 axis / rod-axis height',fontsize=9)
ax.set_xlabel("across the rods Y' (mm, + = rear rod side)"); ax.set_ylabel("height Z' above rod axis (mm)")
ax.annotate('nozzle tip -61',xy=(0,-61),xytext=(25,-60),fontsize=8,arrowprops=dict(arrowstyle='->'))
ax.annotate('motor ~45 x 45 here,\nbottom at Z\'=+13..+21',xy=(35,40),xytext=(38,78),fontsize=8,arrowprops=dict(arrowstyle='->'))
# right: constraint sketch for the compact head
ax=axs[1]
rods(ax); draw_v6(ax)
ax.add_patch(Rectangle((-21,10.5),42,42,fc='#7aa6d6',ec='#1d3f73',alpha=.55,zorder=3))
ax.text(-19,30,'motor 42x42 (axis along rods)\nlowest position: bottom at Z\'=+10.5\n(clears bearing tops +7.5 by 3)',fontsize=7.5,zorder=9)
ax.add_patch(Rectangle((8,10.5),34,42,fc='none',ec='#d9534f',ls='--',lw=1.5,zorder=5))
ax.text(10,56,'alt: motor axis across rods\n(34 long, behind the V6)',fontsize=7.5,color='#d9534f')
ax.add_patch(Rectangle((-45,-20),24,-0.0001,fc='none'))
ax.add_patch(Rectangle((-RY-11,-10),2*RY+22,20.5,fc='#444',alpha=.25,ec='k',ls=':',zorder=1))
ax.text(-RY-9,-9.5,'carriage body (bearing seats + hotend clamp)',fontsize=7)
ax.add_patch(Rectangle((-11,-41),-10,30,fc='#d0d6dd',ec='#555',alpha=.7,zorder=3)); ax.text(-48,-45,'30x30x10 heatsink fan\nin front of the fins',fontsize=7.5)
ax.add_patch(Rectangle((11.5,-40),20,40,fc='#e8c9a0',ec='#7a5a1f',alpha=.6,zorder=2)); ax.text(14,-55,'4020 blower (40x40x20)\nbeside / behind, duct to nozzle',fontsize=7.5)
ax.set_xlim(-60,70); ax.set_ylim(-70,100); ax.set_aspect('equal'); ax.grid(True,alpha=.3)
ax.set_title('What has to fit (same view): rods, 45mm bearings, V6, motor, fans',fontsize=9)
ax.set_xlabel("across the rods Y' (mm)"); 
plt.tight_layout(); plt.savefig('out/stock_head_and_constraints.png',dpi=85); print('ok')
