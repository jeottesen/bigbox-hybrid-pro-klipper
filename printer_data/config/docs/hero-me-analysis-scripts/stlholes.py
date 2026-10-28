import sys,numpy as np,trimesh
from collections import defaultdict
p=sys.argv[1]; m=trimesh.load(p); print(p.split('/')[-1],"bounds",m.bounds.round(1).tolist())
res=defaultdict(list)
for ax in range(3):
    o=[i for i in range(3) if i!=ax]
    for t in np.linspace(m.bounds[0][ax]+.25,m.bounds[1][ax]-.25,int(m.extents[ax]*2)):
        nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
        s=m.section(plane_origin=org,plane_normal=nrm)
        if s is None: continue
        for e in s.discrete:
            q=e[:,o]
            if len(q)<8: continue
            c=q.mean(0); r=np.linalg.norm(q-c,axis=1)
            if r.std()<.12 and 1.2<r.mean()<4.0:
                res[(ax,round(c[0]*2)/2,round(c[1]*2)/2,round(2*r.mean(),1))].append(t)
for k in sorted(res):
    ts=res[k]
    if max(ts)-min(ts)>=1.5: print("axis %s hole centre (%s=%.1f,%s=%.1f) dia %.1f  depth range %.1f..%.1f"%('XYZ'[k[0]],'XYZ'[[i for i in range(3) if i!=k[0]][0]],k[1],'XYZ'[[i for i in range(3) if i!=k[0]][1]],k[2],k[3],min(ts),max(ts)))
