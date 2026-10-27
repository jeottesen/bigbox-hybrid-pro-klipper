import sys,glob,itertools,numpy as np,trimesh
from collections import defaultdict
for p in sorted(glob.glob(sys.argv[1]+'/*.stl')):
    m=trimesh.load(p); holes={}
    for ax in range(3):
        o=[i for i in range(3) if i!=ax]
        for t in np.linspace(m.bounds[0][ax]+.2,m.bounds[1][ax]-.2,80):
            nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
            s=m.section(plane_origin=org,plane_normal=nrm)
            if s is None: continue
            for e in s.discrete:
                q=e[:,o]
                if len(q)<8: continue
                c=q.mean(0);r=np.linalg.norm(q-c,axis=1)
                if r.std()<.12 and 1.0<r.mean()<2.8:
                    k=(ax,round(c[0]*2)/2,round(c[1]*2)/2)
                    h=holes.setdefault(k,[t,t,2*r.mean()]); h[0]=min(h[0],t);h[1]=max(h[1],t)
    print("==",p.split('/')[-1],"holes",len(holes))
    pairs=defaultdict(list)
    for (a,ka),(b,kb) in itertools.combinations(holes.items(),2):
        if a[0]!=b[0]: continue
        d=np.hypot(a[1]-b[1],a[2]-b[2])
        va,vb=holes[a],holes[b]
        if min(va[1],vb[1])<max(va[0],vb[0]) : continue  # no overlap along axis
        if 13.0<=d<=16.5: pairs[(a[0],round(d,1))].append((a[1:],b[1:],round(va[2],1),round(va[0],1),round(va[1],1)))
    for k,v in sorted(pairs.items()): print("  axis %s spacing %.1f  e.g. %s"%('XYZ'[k[0]],k[1],v[0]), "n=%d"%len(v))
