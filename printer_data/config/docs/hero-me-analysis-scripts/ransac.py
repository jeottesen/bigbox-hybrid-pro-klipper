import sys,numpy as np,trimesh,itertools
rng=np.random.default_rng(1)
def circ3(a,b,c):
    A=np.array([[b[0]-a[0],b[1]-a[1]],[c[0]-a[0],c[1]-a[1]]])*2
    B=np.array([b@b-a@a,c@c-a@a])
    try: x=np.linalg.solve(A,B)
    except: return None
    return x,np.linalg.norm(x-a)
def find(P,rmin,rmax,minin=30):
    found=[];P=P.copy()
    for _ in range(4):
        best=None
        if len(P)<minin: break
        for _ in range(1500):
            i=rng.choice(len(P),3,replace=False); r=circ3(*P[i])
            if r is None or not(rmin<=r[1]<=rmax): continue
            n=(np.abs(np.linalg.norm(P-r[0],axis=1)-r[1])<0.12).sum()
            if best is None or n>best[0]: best=(n,r[0],r[1])
        if best is None or best[0]<minin: break
        found.append((best[1],best[2],best[0]))
        P=P[np.abs(np.linalg.norm(P-best[1],axis=1)-best[2])>=0.12]
    return found
for f in sys.argv[1:]:
    m=trimesh.load(f); res=[]
    for ax in range(3):
        o=[i for i in range(3) if i!=ax]
        for t in np.linspace(m.bounds[0][ax]+m.extents[ax]*.15,m.bounds[1][ax]-m.extents[ax]*.15,5):
            nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
            s=m.section(plane_origin=org,plane_normal=nrm)
            if s is None: continue
            P=np.vstack([np.c_[e[:,o]] for e in s.discrete]);
            if len(P)<60: continue
            cs=find(P,6.8,9.2)
            if len(cs)>=2:
                for a,b in itertools.combinations(cs,2):
                    res.append((ax,round(float(np.linalg.norm(a[0]-b[0])),1),round(float(a[1]),1),round(float(b[1]),1)))
    from collections import Counter
    c=Counter(res)
    print(f.split('/')[-1],"extents",m.extents.round(1),"-> bore pairs (axis,spacing,r1,r2):",c.most_common(3))
