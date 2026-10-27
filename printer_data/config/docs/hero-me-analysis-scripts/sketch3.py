import re
src=open('src/sketch.py').read()
head=src.split("fig,axs=plt.subplots")[0]
exec(head)
fig,axs=plt.subplots(1,2,figsize=(13,6.4))
# A stock
ax=axs[0]; setup(ax,'A. Stock head (view along the rods)')
poly(ax,extr,0,2,'#9aa0a6','none',1,0,2)
draw_carriage(ax); draw_rods(ax); draw_v6(ax,-62.4,TIP0); mark_nozzle(ax,-62.4,TIP0)
ax.text(-100,735,'extruder',fontsize=7,color='#555')
# C2: Hero Me base hung under a stock-like carriage, collar mount in a pocket
ax=axs[1]; setup(ax,'B. Hero Me base hung UNDER a stock-style carriage (corrected geometry)')
poly(ax,extr,0,2,'#9aa0a6','none',1,0,2)
draw_carriage(ax,'#444'); draw_rods(ax)
mx=lambda y: -62.4+(y-B_AX_Y); mz=lambda z: CARR_BOT-(B_TOP-z)
draw_base(ax,mx,mz)
ztip=CARR_BOT-(B_TOP-(B_BOT-7.5))
draw_v6(ax,-62.4,ztip); mark_nozzle(ax,-62.4,ztip)
# collar mount pocket marker
ax.add_patch(Rectangle((-62.4-17,CARR_BOT),34,18.4,fc='none',ec='#e0a030',lw=1.5,ls='--',zorder=8))
ax.text(-40,688,'collar mount\n(in carriage pocket)',fontsize=6.5,color='#a06800',zorder=9)
ax.text(-175,600,'nozzle %.1f mm from stock height,\n0 mm sideways offset,\nno loss of X travel'%(TIP0-ztip),fontsize=8)
plt.tight_layout(); plt.savefig('out/herome_under_carriage.png',dpi=95); print('tip',ztip)
