import cadquery as cq
from cadquery import importers
A=importers.importStep("step/STEP/bigbox_v1.1.0.stp").solids().vals()
carriage,front,back=A[65],A[66],A[64]
# blower: its frame has Z=thickness (ear face at Z=0), outlet at -Y edge; map x->X, y->-Z, z->+Y, centre (X=-62.4, Z=667.6), ear face on the back plate at Y=344.2
B=importers.importStep("fan/blower.step").solids().vals()
import sys
FLIP=(len(sys.argv)>1 and sys.argv[1]=="flip")
def place_blower(s):
    # base: rotate -90deg about X => x->X, y->-Z, z->+Y (ear face z=0 toward the plates)
    r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),-90)
    if not FLIP: return r.translate(cq.Vector(-62.4,344.2,667.6))
    # flipped: inlet face (z=20) toward the plates: rotate 180deg about Z (x->-X, z-axis stays vertical in this frame? use rotate about Z of the mounted frame)
    r=r.rotate(cq.Vector(0,0,0),cq.Vector(0,0,1),180)      # x->-X, Y->-Y  (outlet stays at the bottom)
    b=r.BoundingBox()
    return r.translate(cq.Vector(-62.4,0,667.6)).translate(cq.Vector(0,344.2-b.ymin,0))
blower=[place_blower(s) for s in B]
# V6 hotend (solids 0..3 of the E3D V6 STEP, axis along y_v, tip at y_v=-6.2, top at 55): x_v->+Y, y_v->+Z, z_v->+X ; axis at (X=-62.4,Y=308), top at Z=696.8
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
def place_v6(s):
    # cyclic permutation rotation: rotate 120deg about (1,1,1) maps x->y, y->z, z->x
    r=s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120)
    return r.translate(cq.Vector(-62.4,308.0,696.8-55.0))
v6=[place_v6(s) for s in V]
def vol(x): return x.Volume()/1000
def common(a,b):
    try: return vol(a.intersect(b))
    except Exception as e: return float('nan')
print("blower box check:",[round(x,1) for x in (blower[0].BoundingBox().xmin,blower[0].BoundingBox().xmax,blower[0].BoundingBox().ymin,blower[0].BoundingBox().ymax,blower[0].BoundingBox().zmin,blower[0].BoundingBox().zmax)])
print("v6 box check:",[round(x,1) for x in (lambda b:(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))(v6[3].BoundingBox())])
parts={"carriage":carriage,"front_plate":front,"back_plate":back,"blower_housing":blower[0],"blower_impeller":blower[1],"v6_nozzle":v6[0],"v6_block":v6[1],"v6_heatbreak":v6[2],"v6_heatsink":v6[3]}
names=list(parts)
import itertools
for a,b in itertools.combinations(names,2):
    ga=a.split('_')[0]; gb=b.split('_')[0]
    if ga==gb and ga in('v6','blower'): continue
    c=common(parts[a],parts[b])
    if c==c and c>0.01: print("overlap %-16s x %-16s %.3f cm3"%(a,b,c))
import pickle
asm=cq.Assembly(name="stock_single_head_cooling")
cols={"carriage":(0.55,0.55,0.55),"front_plate":(0.2,0.45,0.85),"back_plate":(0.9,0.55,0.15),"blower_housing":(0.15,0.15,0.15),"blower_impeller":(0.3,0.3,0.3),"v6_nozzle":(0.8,0.65,0.1),"v6_block":(0.7,0.55,0.1),"v6_heatbreak":(0.8,0.8,0.8),"v6_heatsink":(0.75,0.75,0.78)}
for n,s in parts.items(): asm.add(s,name=n,color=cq.Color(*cols[n]))
asm.save("asm/assembly_A%s.step"%("_alt_flipped" if FLIP else ""))
print("saved")

# ---- preview ----
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
fig,axs=plt.subplots(1,3,figsize=(21,8))
order=["carriage","v6_heatsink","v6_heatbreak","v6_block","v6_nozzle","blower_housing","blower_impeller","front_plate","back_plate"]
tess={}
for n in order:
    v,t=parts[n].tessellate(0.15,0.3); V=np.array([[q.x,q.y,q.z] for q in v]); tess[n]=V[np.array(t)]
for ax,(a,b,d,title,lim) in zip(axs,[(0,1,2,"top (X across rods, Y along rods)",((-110,-20),(270,375))),(0,2,1,"front (looking along the rods)",((-110,-20),(625,715))),(1,2,0,"side (Y along rods, Z up): nozzle at Y=308, fan at Y 344-364",((270,375),(625,715)))]):
    for n in order:
        T=tess[n]; o=np.argsort(T.mean(1)[:,d])
        ax.add_collection(PolyCollection(T[o][:,:,[a,b]],facecolors=[cols[n]]*len(T),edgecolors='none',alpha=0.5 if n=="carriage" else 0.95))
    ax.set_xlim(*lim[0]);ax.set_ylim(*lim[1]);ax.set_aspect('equal');ax.grid(True,alpha=.3);ax.set_title(title,fontsize=10)
plt.tight_layout();plt.savefig("asm/assembly_A%s_preview.png"%("_alt_flipped" if FLIP else ""),dpi=60)
