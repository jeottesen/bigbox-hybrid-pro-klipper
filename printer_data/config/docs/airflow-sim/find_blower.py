import numpy as np, trimesh, itertools, json
from scipy import ndimage, signal
DX=1.0; X0,X1,Y0,Y1,Z0,Z1=-80.0,32.0,280.0,372.0,628.0,706.0
nx,ny,nz=int((X1-X0)/DX),int((Y1-Y0)/DX),int((Z1-Z0)/DX); org=np.array([X0,Y0,Z0])
m=trimesh.load("shroud2/bb_dual_shroud.stl")
S=np.zeros((nx,ny,nz),bool); n=int(m.area/((DX*0.4)**2))
for c0 in range(0,n,300_000):
    p,_=trimesh.sample.sample_surface(m,min(300_000,n-c0),seed=c0); i=np.floor((p-org)/DX).astype(int)
    ok=(i[:,0]>=0)&(i[:,0]<nx)&(i[:,1]>=0)&(i[:,1]<ny)&(i[:,2]>=0)&(i[:,2]<nz); i=i[ok]; S[i[:,0],i[:,1],i[:,2]]=True
Sd=ndimage.binary_dilation(S)
# blower local frame (mm): body box x,y in +-20.2, z in 0..20 ; outlet box in front of the outlet face (y=-20.2), x -18.6..8.6, z 1.5..18.5, 6 mm deep
def box(lo,hi):
    g=np.mgrid[int(lo[0]):int(hi[0])+1,int(lo[1]):int(hi[1])+1,int(lo[2]):int(hi[2])+1].reshape(3,-1).T+0.5
    return g
body=box((-20,-20,0),(19,19,19)); outl=box((-18,-26,2),(8,-21,17))
rots=[]
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1,-1),repeat=3):
        R=np.zeros((3,3));
        for r,(c,s) in enumerate(zip(perm,sg)): R[r,c]=s
        if np.linalg.det(R)>0: rots.append(R)
print(len(rots),"rotations")
def raster(pts,R):
    q=pts@R.T; lo=np.floor(q.min(0)).astype(int); return q,lo
def kern(pts,R,shape_pad=30):
    q=np.floor(pts@R.T).astype(int); lo=q.min(0); q-=lo; g=np.zeros(q.max(0)+1,bool); g[q[:,0],q[:,1],q[:,2]]=True; return g,lo
res=[]
for ri,R in enumerate(rots):
    # shared origin: express both kernels relative to the same lowest corner
    qb=np.floor(body@R.T).astype(int); qo=np.floor(outl@R.T).astype(int); lo=np.minimum(qb.min(0),qo.min(0))
    shp=np.maximum(qb.max(0),qo.max(0))-lo+1
    H=np.zeros(shp,bool); H[tuple((qb-lo).T)]=True; O=np.zeros(shp,bool); O[tuple((qo-lo).T)]=True
    Q=ndimage.binary_dilation(O,iterations=2)&~O&~H
    def corr(A,K): return signal.fftconvolve(A.astype(np.float32),K[::-1,::-1,::-1].astype(np.float32),mode='valid')
    ov=corr(S,H); blocked=corr(S,O); ring=corr(S,Q)/max(1,Q.sum()); contact=corr(Sd,H)
    ok=(ov<2.5)&(blocked<3.5)&(contact>3.5)
    idx=np.argwhere(ok)
    for p in idx: res.append((float(ring[tuple(p)]),ri,tuple(p),float(blocked[tuple(p)]),float(ov[tuple(p)]),lo,shp))
res.sort(key=lambda r:-r[0])
print("candidates with no interference, outlet mouth not blocked, touching the shroud:",len(res))
out=[]
for sc,ri,p,bl,ov,lo,shp in res[:12]:
    R=rots[ri]; cen=(np.array(p)+lo)  # kernel origin in grid cells; blower local origin sits at p+lo cells -> world
    w=org+(np.array(p)-0)*DX  # placeholder
    out.append((sc,ri,p,bl,ov)); print("enclosure %.3f rot %2d pos %s blocked %.0f overlap %.1f"%(sc,ri,p,bl,ov))
np.save("asm/blower_candidates.npy",np.array([ (r[0],r[1],*r[2]) for r in res[:200]],dtype=float))
np.save("asm/rots.npy",np.array(rots))
