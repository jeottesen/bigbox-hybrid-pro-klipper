import sys,glob,numpy as np,trimesh,itertools
for p in sorted(glob.glob(sys.argv[1]+'/*.stl')):
    m=trimesh.load(p); circles=[]
    for ax in range(3):
        o=[i for i in range(3) if i!=ax]
        for t in np.linspace(m.bounds[0][ax]+.3,m.bounds[1][ax]-.3,24):
            nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
            s=m.section(plane_origin=org,plane_normal=nrm)
            if s is None: continue
            for e in s.discrete:
                q=e[:,o]
                if len(q)<8: continue
                c=q.mean(0);r=np.linalg.norm(q-c,axis=1)
                if r.std()<.12 and 1.4<r.mean()<1.9: circles.append((ax,round(c[0],1),round(c[1],1)))
    circles=sorted(set(circles))
    # pair distances of same-axis small circles
    d=set()
    for a,b in itertools.combinations(circles,2):
        if a[0]==b[0]:
            dist=np.hypot(a[1]-b[1],a[2]-b[2])
            if 5<dist<40: d.add((a[0],round(dist,1)))
    print(p.split('/')[-1],"extents",m.extents.round(1),"M3-ish hole spacings (axis,mm):",sorted(d)[:8])
