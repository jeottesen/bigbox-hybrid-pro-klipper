import sys,numpy as np,trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
files=sys.argv[2:]; out=sys.argv[1]
fig,axs=plt.subplots(len(files),3,figsize=(15,4.6*len(files)),squeeze=False)
for r,f in enumerate(files):
    m=trimesh.load(f); tri=m.triangles; n=m.face_normals
    for c,(a,b,d,name) in enumerate([(0,1,2,'top XY'),(0,2,1,'front XZ'),(1,2,0,'side YZ')]):
        ax=axs[r][c]
        sgn=1
        order=np.argsort(tri[:,:,d].mean(1))
        sh=0.5+0.5*np.abs(n[:,d]) 
        pc=PolyCollection(tri[order][:,:,[a,b]],facecolors=[(sh[i]*.6,sh[i]*.7,sh[i]) for i in order],edgecolors='none')
        ax.add_collection(pc);ax.autoscale();ax.set_aspect('equal');ax.set_title(f.split('/')[-1][:40]+' '+name,fontsize=8);ax.grid(True,alpha=.3)
plt.tight_layout();plt.savefig(out,dpi=60)
