import sys,numpy as np,trimesh
m=trimesh.load(sys.argv[1]); print(sys.argv[1].split('/')[-1],"extents",m.extents.round(1),"bounds min",m.bounds[0].round(1))
ax=int(sys.argv[2]); n=int(sys.argv[3])
lo,hi=m.bounds[0][ax],m.bounds[1][ax]
o=[0,1,2]; o.remove(ax)
seen=set()
for t in np.linspace(lo+0.3,hi-0.3,n):
    nrm=[0,0,0];nrm[ax]=1;org=[0,0,0];org[ax]=t
    s=m.section(plane_origin=org,plane_normal=nrm)
    if s is None: continue
    p,_=s.to_planar(to_2D=None) if False else (None,None)
    for e in s.discrete:
        pts=e[:,o]
        if len(pts)<8: continue
        c=pts.mean(0); r=np.linalg.norm(pts-c,axis=1)
        if r.std()<0.15 and 1<r.mean()<12 :
            k=(round(c[0],1),round(c[1],1),round(r.mean()*2,1))
            if k not in seen:
                seen.add(k); print("  circle axis=%s at h=%.1f: center (%.1f,%.1f) dia %.1f"%('XYZ'[ax],t,k[0],k[1],k[2]))
