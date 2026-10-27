import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle
R="extracted/Hero Me Gen7 Release 4/Hero Me Gen7 Release V4"
base=trimesh.load(R+"/Base/HMG7.2 Universal Base V2.stl").triangles
ROD_X=(-91.2,-33.2); MID=-62.2; YC=329.0
B_AX_Y=39.3; B_REAR=81.5; B_CX=-19.2
def draw_base(ax,mx,my):
    P=base; X=mx(P[:,:,0],P[:,:,1]); Y=my(P[:,:,0],P[:,:,1])
    ax.add_collection(PolyCollection(np.stack([X,Y],axis=2),facecolors='#3b7dd8',edgecolors='#1d3f73',alpha=.8,linewidths=.1,zorder=5))
def common(ax,title):
    for x in ROD_X: ax.add_patch(Rectangle((x-4,215),8,230,fc='#8a8f98',ec='k',lw=.5,zorder=1))
    ax.axvline(MID,ls=':',c='gray',lw=.8); ax.set_xlim(-185,15); ax.set_ylim(215,445); ax.set_aspect('equal')
    ax.set_title(title,fontsize=9,loc='left'); ax.grid(True,alpha=.25); ax.tick_params(labelsize=7)
    ax.set_xlabel('across the rods  (CAD X, mm)',fontsize=7); ax.set_ylabel('along the rods  (CAD Y, mm)',fontsize=7)
fig,axs=plt.subplots(1,2,figsize=(14,7.2))
# B: plate on the side face of the stock-size carriage
ax=axs[0]; common(ax,'B. Plate on the side of the carriage (top view)')
ax.add_patch(Rectangle((-102.1,YC-35),79.8,70.1,fc='#444',alpha=.9,zorder=3))
t=5; xp=-102.1-t
ax.add_patch(Rectangle((xp,YC-14),t,28,fc='#e0a030',ec='k',lw=.5,zorder=4))
draw_base(ax,lambda xb,yb: xp-(B_REAR-yb), lambda xb,yb: YC+(xb-B_CX))
hx=xp-(B_REAR-B_AX_Y)
ax.add_patch(Circle((hx,YC),11.15,fc='#c9a227',ec='#7a6310',zorder=6)); ax.plot(hx,YC,'v',c='#d33',ms=6,zorder=7)
ax.annotate('',xy=(hx,238),xytext=(MID,238),arrowprops=dict(arrowstyle='<->',lw=.9)); ax.text((hx+MID)/2,242,'%.0f mm sideways'%abs(hx-MID),ha='center',fontsize=8,weight='bold')
ax.text(-180,425,'nozzle sits outside the rods;\nload tips the carriage across the rod pair',fontsize=7.5)
# D: new short carriage, plate on the end face along the rods
ax=axs[1]; common(ax,'D. New short carriage, plate on its end face (top view)')
L=52
ax.add_patch(Rectangle((-102.1,YC-L/2),79.8,L,fc='#444',alpha=.9,zorder=3))
for x in ROD_X:
    for dy in (-12.5,12.5): ax.add_patch(Circle((x,YC+dy),7.7,fc='none',ec='w',lw=.8,zorder=4))
yf=YC+L/2; ax.add_patch(Rectangle((MID-14,yf),28,t,fc='#e0a030',ec='k',lw=.5,zorder=4))
draw_base(ax,lambda xb,yb: MID+(xb-B_CX), lambda xb,yb: yf+t+(B_REAR-yb))
hy=yf+t+(B_REAR-B_AX_Y)
ax.add_patch(Circle((MID,hy),11.15,fc='#c9a227',ec='#7a6310',zorder=6)); ax.plot(MID,hy,'v',c='#d33',ms=6,zorder=7)
ax.annotate('',xy=(-125,hy),xytext=(-125,YC),arrowprops=dict(arrowstyle='<->',lw=.9)); ax.text(-123,(hy+YC)/2,'%.0f mm along\nthe rods'%(hy-YC),fontsize=8,weight='bold')
ax.text(-180,425,'nozzle stays on the rod mid-plane;\nshifts along the rods instead',fontsize=7.5)
ax.text(-100,YC-L/2-8,'4 x LM8UU (white rings)',fontsize=7)
plt.tight_layout(); plt.savefig('out/herome_topview.png',dpi=90); print('ok',hy-YC,hx-MID)
