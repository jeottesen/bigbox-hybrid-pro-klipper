"""Cheap CPU lattice-Boltzmann (D3Q19, BGK) airflow test. Velocity inlet at the blower outlet, open sides, bounce-back solids.
Strongly under-resolved and artificially viscous: only a qualitative look at where the air goes."""
import numpy as np, sys, time
from numba import njit, prange
G=np.load(sys.argv[1]); solid=G["solid"]; inlet=G["inlet"]; DX=float(G["dx"])
PRINT=int(sys.argv[6]) if len(sys.argv)>6 else 1000
STEPS=int(sys.argv[2]); NU=float(sys.argv[3]); UIN=float(sys.argv[4]); out=sys.argv[5]
nx,ny,nz=solid.shape
c=np.array([[0,0,0],[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1],
            [1,1,0],[-1,-1,0],[1,-1,0],[-1,1,0],[1,0,1],[-1,0,-1],[1,0,-1],[-1,0,1],[0,1,1],[0,-1,-1],[0,1,-1],[0,-1,1]],dtype=np.int64)
w=np.array([1/3]+[1/18]*6+[1/36]*12,dtype=np.float32)
opp=np.array([0,2,1,4,3,6,5,8,7,10,9,12,11,14,13,16,15,18,17],dtype=np.int64)
omega=np.float32(1.0/(3.0*NU+0.5))
@njit(parallel=True,fastmath=True)
def collide(f,solid,omega,w,c):
    nx,ny,nz=solid.shape
    for x in prange(nx):
        for y in range(ny):
            for z in range(nz):
                if solid[x,y,z]: continue
                rho=0.0; ux=0.0; uy=0.0; uz=0.0
                for i in range(19):
                    v=f[i,x,y,z]; rho+=v; ux+=c[i,0]*v; uy+=c[i,1]*v; uz+=c[i,2]*v
                ux/=rho; uy/=rho; uz/=rho
                usq=1.5*(ux*ux+uy*uy+uz*uz)
                for i in range(19):
                    cu=3.0*(c[i,0]*ux+c[i,1]*uy+c[i,2]*uz)
                    feq=w[i]*rho*(1.0+cu+0.5*cu*cu-usq)
                    f[i,x,y,z]+=omega*(feq-f[i,x,y,z])
@njit(parallel=True,fastmath=True)
def stream(f,g,solid,inlet,c,opp,w,uin):
    nx,ny,nz=solid.shape
    for x in prange(nx):
        for y in range(ny):
            for z in range(nz):
                if solid[x,y,z]: continue
                for i in range(19):
                    sx=x-c[i,0]; sy=y-c[i,1]; sz=z-c[i,2]
                    if sx<0 or sx>=nx or sy<0 or sy>=ny or sz<0 or sz>=nz:
                        g[i,x,y,z]=f[i,x,y,z]            # open boundary: zero-gradient
                    elif solid[sx,sy,sz]:
                        g[i,x,y,z]=f[opp[i],x,y,z]       # bounce-back
                    else:
                        g[i,x,y,z]=f[i,sx,sy,sz]
                if inlet[x,y,z]:
                    usq=1.5*uin*uin
                    for i in range(19):
                        cu=3.0*(c[i,2]*(-uin))
                        g[i,x,y,z]=w[i]*(1.0+cu+0.5*cu*cu-usq)
@njit
def feq_set(g,x,y,z,rho,ux,uy,uz,w,c):
    usq=1.5*(ux*ux+uy*uy+uz*uz)
    for i in range(19):
        cu=3.0*(c[i,0]*ux+c[i,1]*uy+c[i,2]*uz)
        g[i,x,y,z]=w[i]*rho*(1.0+cu+0.5*cu*cu-usq)
@njit
def open_bc(g,solid,w,c):
    nx,ny,nz=solid.shape
    for face in range(5):
        # faces: 0:x=0 1:x=nx-1 2:y=0 3:y=ny-1 4:z=0
        if face<2: n1,n2=ny,nz
        elif face<4: n1,n2=nx,nz
        else: n1,n2=nx,ny
        for a in range(n1):
            for b in range(n2):
                if face==0: x,y,z,xi,yi,zi=0,a,b,1,a,b
                elif face==1: x,y,z,xi,yi,zi=nx-1,a,b,nx-2,a,b
                elif face==2: x,y,z,xi,yi,zi=a,0,b,a,1,b
                elif face==3: x,y,z,xi,yi,zi=a,ny-1,b,a,ny-2,b
                else: x,y,z,xi,yi,zi=a,b,0,a,b,1
                if solid[x,y,z]: continue
                ux=0.0; uy=0.0; uz=0.0
                if not solid[xi,yi,zi]:
                    r=0.0
                    for i in range(19):
                        v=g[i,xi,yi,zi]; r+=v; ux+=c[i,0]*v; uy+=c[i,1]*v; uz+=c[i,2]*v
                    ux/=r; uy/=r; uz/=r
                feq_set(g,x,y,z,1.0,ux,uy,uz,w,c)
f=np.empty((19,nx,ny,nz),np.float32); 
for i in range(19): f[i]=w[i]
g=f.copy(); uin=np.float32(UIN)
collide(f,solid,omega,w,c); stream(f,g,solid,inlet,c,opp,w,uin); open_bc(g,solid,w,c); f,g=g,f      # compile
t=time.time()
for s in range(STEPS):
    collide(f,solid,omega,w,c); stream(f,g,solid,inlet,c,opp,w,uin); open_bc(g,solid,w,c); f,g=g,f
    if (s+1)%PRINT==0:
        rho=f.sum(0); ux=(c[:,0,None,None,None]*f).sum(0)/rho; uy=(c[:,1,None,None,None]*f).sum(0)/rho; uz=(c[:,2,None,None,None]*f).sum(0)/rho
        sp=np.sqrt(ux**2+uy**2+uz**2); sp[solid]=0
        am=np.unravel_index(np.argmax(sp),sp.shape); print("step",s+1,"at",am,"max|u| %.3f"%sp.max(),"rho mean %.4f max %.4f min %.4f"%(rho[~solid].mean(),rho[~solid].max(),rho[~solid].min()),"%.0f MLUPS"%((s+1)*nx*ny*nz/(time.time()-t)/1e6),flush=True)
        if not np.isfinite(sp).all(): print("UNSTABLE"); break
rho=f.sum(0); ux=(c[:,0,None,None,None]*f).sum(0)/rho; uy=(c[:,1,None,None,None]*f).sum(0)/rho; uz=(c[:,2,None,None,None]*f).sum(0)/rho
np.savez_compressed(out,ux=ux.astype(np.float32),uy=uy.astype(np.float32),uz=uz.astype(np.float32),rho=rho.astype(np.float32),solid=solid,dx=DX,origin=G["origin"],uin=UIN)
print("done in %.0f s"%(time.time()-t))
