import sys,numpy as np,trimesh
from collections import defaultdict
p=sys.argv[1]; m=trimesh.load(p); print(p.split('/')[-1],"bounds",m.bounds.round(1).tolist())
axis=int(sys.argv[2]) if len(sys.argv)>2 else None
res=defaultdict(list)
for ax in (range(3) if axis is None else [axis]):
    o=[i for i in range(3) if i!=ax]
    for t in np.linspace(m.bounds[0][ax]+.25,m.bounds[1][ax]-.25,int(m.extents[ax]*2)):
        nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
        s=m.section(plane_origin=org,plane_normal=nrm)
        if s is None: continue
        for e in s.discrete:
            q=e[:,o]
            if len(q)<8: continue
            lo,hi=q.min(0),q.max(0); d=hi-lo
            # polygon area (shoelace)
            a=0.5*abs(np.dot(q[:,0],np.roll(q[:,1],1))-np.dot(q[:,1],np.roll(q[:,0],1)))
            fill=a/(d[0]*d[1]+1e-9)
            if 2.8<=d.min()<=4.8 and d.max()<=22 and fill>0.7:
                res[(ax,round((lo[0]+hi[0])/4)*2,round((lo[1]+hi[1])/4)*2,round(d[0],0),round(d[1],0))].append(t)
for k in sorted(res):
    ts=res[k]
    if max(ts)-min(ts)>=2: print("axis %s: centre %s=%.0f,%s=%.0f size %.0fx%.0f, through %.1f..%.1f"%('XYZ'[k[0]],'XYZ'[[i for i in range(3) if i!=k[0]][0]],k[1],'XYZ'[[i for i in range(3) if i!=k[0]][1]],k[2],k[3],k[4],min(ts),max(ts)))
