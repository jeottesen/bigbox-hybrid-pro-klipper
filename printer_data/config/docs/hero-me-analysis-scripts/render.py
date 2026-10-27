import sys, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from cadquery import importers
p,out=sys.argv[1],sys.argv[2]
sel=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 and sys.argv[3]!='all' else None
w=importers.importStep(p)
sols=w.solids().vals()
cm=plt.get_cmap('tab20')
views={'top (X-Y)':(0,1,2,1),'front (X-Z)':(0,2,1,1),'side (Y-Z)':(1,2,0,1)}
fig,axs=plt.subplots(1,3,figsize=(21,8))
for ax,(name,(a,b,d,sg)) in zip(axs,views.items()):
    polys=[];cols=[];depth=[]
    for i,s in enumerate(sols):
        if sel and i not in sel: continue
        v,t=s.tessellate(0.15,0.3)
        V=np.array([[q.x,q.y,q.z] for q in v]);T=np.array(t)
        tri=V[T]
        for tr in tri:
            polys.append(tr[:,[a,b]]);depth.append(tr[:,d].mean());cols.append(cm(i%20))
    o=np.argsort(depth)
    pc=PolyCollection([polys[k] for k in o],facecolors=[cols[k] for k in o],edgecolors='k',linewidths=0.05)
    ax.add_collection(pc);ax.autoscale();ax.set_aspect('equal');ax.set_title(name)
    ax.grid(True)
plt.tight_layout();plt.savefig(out,dpi=70)
