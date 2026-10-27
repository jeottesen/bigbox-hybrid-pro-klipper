import sys,glob,itertools,numpy as np,trimesh
def loops(m):
    out=[]
    for ax in range(3):
        o=[i for i in range(3) if i!=ax]
        for t in np.linspace(m.bounds[0][ax]+.3,m.bounds[1][ax]-.3,30):
            nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
            s=m.section(plane_origin=org,plane_normal=nrm)
            if s is None: continue
            for e in s.discrete:
                q=e[:,o]
                if len(q)<6: continue
                lo,hi=q.min(0),q.max(0); d=hi-lo
                if d.min()>=2.8 and d.min()<=4.8 and d.max()<=20: out.append((ax,lo,hi,t))
    return out
tgt=15.5
for p in sorted(sum([glob.glob(a) for a in sys.argv[1:]],[])):
    m=trimesh.load(p); L=loops(m); hits=set()
    for a,b in itertools.combinations(L,2):
        if a[0]!=b[0]: continue
        # hole-to-hole distance range (min..max over positions within loops)
        ca,cb=(a[1]+a[2])/2,(b[1]+b[2])/2
        ra,rb=(a[2]-a[1])/2,(b[2]-b[1])/2
        d=np.linalg.norm(ca-cb)
        dx=np.abs(ca-cb); 
        # allow slot travel: range per-axis extents beyond a 3.4 circle
        ex=np.maximum(ra-1.7,0)+np.maximum(rb-1.7,0)
        lo=np.linalg.norm(np.maximum(dx-ex,0)); hi=np.linalg.norm(dx+ex)
        if lo-0.1<=tgt<=hi+0.1 and abs(a[3]-b[3])>=0: hits.add((a[0],round(lo,1),round(hi,1),tuple(np.round(ca,1)),tuple(np.round(cb,1))))
    print(p.split('/')[-1],"loops",len(L),"hits",len(hits))
    for h in sorted(hits)[:4]: print("   ",h)
