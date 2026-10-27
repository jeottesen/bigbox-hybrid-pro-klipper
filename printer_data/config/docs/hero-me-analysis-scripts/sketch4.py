import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Rectangle, Polygon
from cadquery import importers
R="extracted/Hero Me Gen7 Release 4/Hero Me Gen7 Release V4"
base=trimesh.load(R+"/Base/HMG7.2 Universal Base V2.stl").triangles
v6=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()
def tris(s):
    v,t=s.tessellate(0.1,0.3); V=np.array([[q.x,q.y,q.z] for q in v]); return V[np.array(t)]
v6t=[tris(v6[i]) for i in (0,1,2,3)]
RY=28.9; SHIFT=0.0
fig,ax=plt.subplots(figsize=(9,9))
# base in (Y',Z'): base Y_b -> Y' = Y_b-39.3 (rear +); Z' = Z_b-78.6
P=base.copy(); X=P[:,:,1]-39.3+SHIFT; Z=P[:,:,2]-78.6
ax.add_collection(PolyCollection(np.stack([X,Z],axis=2),facecolors='#3b7dd8',edgecolors='#1d3f73',alpha=.75,linewidths=.1,zorder=5))
for Tt in v6t:
    Q=Tt[:,:,[0,1]].copy(); Q[:,:,1]=Tt[:,:,1]-55; Q[:,:,0]+=SHIFT
    ax.add_collection(PolyCollection(Q,facecolors='#c9a227',edgecolors='#7a6310',linewidths=.1,alpha=.95,zorder=6))
for y in (-RY,RY):
    ax.add_patch(Circle((y,0),4,fc='#8a8f98',ec='k',zorder=8)); ax.add_patch(Circle((y,0),7.5,fc='#ddd',ec='#555',alpha=.6,zorder=3))
# carriage body + rear tower (concept)
body=[(-40,-10),(47,-10),(47,-47),(42.2,-47),(42.2,-10),(-40,-10)]
ax.add_patch(Polygon([(-40,-10),(-40,14),(47,14),(47,-47),(42.2+0.0,-47),(42.2,-10)],closed=True,fc='#555',alpha=.55,ec='k',zorder=2))
ax.add_patch(Rectangle((-9,-15.2),33.7,18.4,fc='none',ec='#e0a030',ls='--',lw=1.4,zorder=9)); ax.text(-8,5.5,'collar-mount pocket (34 x 18)',fontsize=7,color='#a06800',zorder=9)
# 4010 fan at front of base
ax.add_patch(Rectangle((-19,-55),10,40,fc='#d0d6dd',ec='#555',alpha=.8,zorder=7)); ax.text(-48,-58,'4010 heatsink fan\n(front of base)',fontsize=8)
# motor above rear bearing (axis across rods)
ax.add_patch(Rectangle((10,10.5),40,42,fc='#7aa6d6',ec='#1d3f73',alpha=.5,zorder=4)); ax.text(12,48,'BigBox extruder motor\n(~42 x ~40, axis across rods)',fontsize=8)
ax.text(44,-30,'rear tower:\nbase bolts here\n(32 x 12.5)',fontsize=7.5,rotation=0)
ax.axhline(-61.2,ls='--',c='#d33',lw=.8); ax.text(-48,-60,'stock nozzle-tip height',fontsize=7,color='#d33',va='bottom')
ax.set_xlim(-55,60); ax.set_ylim(-70,60); ax.set_aspect('equal'); ax.grid(True,alpha=.3)
ax.set_title("Route A concept: Hero Me base hung under a short carriage (view along rods)\nY' across rods (+ = rear), Z' above rod axis; V6 axis at Y'=0",fontsize=9)
plt.tight_layout(); plt.savefig('out/routeA_concept.png',dpi=90); print('ok')
