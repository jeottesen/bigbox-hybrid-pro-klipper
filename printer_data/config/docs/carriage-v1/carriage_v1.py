"""BigBox carriage v1 (Route A, reuse-first): bearings on 2 rods, one-piece top saddle that carries the STOCK extruder top plate,
Hero Me Universal Base hung under via the rear tower.  Frame: X' along rods (nozzle at 0, + toward the plate's long side),
Y' across rods (+ rear), Z' up from the rod axis.  All mm.  Belt features are parametric placeholders (see BELT_*)."""
import cadquery as cq
ROD_SP=57.8; BORE_D=15.3; BEAR_LEN=45.0
HY=-5.0                       # hotend axis across offset (window must clear the rear bearing)
X0,X1=-12.0,50.0              # carriage extent along rods (holds both plate holes at -7 and +44.9)
Cx=(X0+X1)/2; L=X1-X0
BOT=-10.0; DECK_TOP=12.7      # deck top = stock carriage top height above the rod axis
# stock plate interface (from the Hybrid STEP): two M4 holes
PLATE_HOLES=[(-7.0, HY-20.5), (44.9, HY+20.3)]    # (X', Y')
# Hero Me interface
BASE_REAR=42.2; PAT_X=16.0; PAT_Z=(-47.0,-34.5)
COLLAR_X=40.5; COLLAR_Y0=-11.4; COLLAR_Y1=23.4
TOWER_T=5.0
# belt placeholders (stock: slot ~3mm wide at ~6.8mm in front of the V6 axis, belt 6mm wide on edge) -- CONFIRM on the printer
BELT_Y=HY-6.8; BELT_Z0=3.4; BELT_H=6.4; BELT_SLOT_W=3.6
y_f,y_r=-ROD_SP/2,ROD_SP/2
y_tower=HY+BASE_REAR
CL_DY=BORE_D/2+2.4; CL_W=2*(CL_DY+3.2)
by0,by1=y_f-CL_W/2, y_tower+TOWER_T
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def xcyl(y,z,d,x0=X0-1,x1=X1+1): return cq.Workplane("YZ").circle(d/2).extrude(x1-x0).translate((x0,y,z))
def zcyl(x,y,d,z0,z1): return cq.Workplane("XY").circle(d/2).extrude(z1-z0).translate((x,y,z0))
def ycyl(x,z,d,y0,y1): return cq.Workplane("XZ").circle(d/2).extrude(-(y1-y0)).translate((x,y0,z))
SCREW_X=(Cx-16.0,Cx+16.0)
def body():
    b=box(X0,X1,by0,by1,BOT,0)
    b=b.union(box(X0+3,X1-3,y_tower,y_tower+TOWER_T,PAT_Z[0]-6,0))
    b=b.cut(box(-COLLAR_X/2,COLLAR_X/2,HY+COLLAR_Y0,HY+COLLAR_Y1,BOT-1,1))
    for y in (y_f,y_r): b=b.cut(xcyl(y,0,BORE_D))
    for y in (y_f,y_r):
        for sx in SCREW_X:
            for s in (-CL_DY,CL_DY): b=b.cut(zcyl(sx,y+s,4.0,-9,0.5))     # M3 heat-set 4.0
    for sx in (-PAT_X,PAT_X):
        for z in PAT_Z: b=b.cut(ycyl(sx,z,3.2,y_tower-1,y_tower+TOWER_T+1))
    return b
def saddle():
    s=box(X0,X1,y_f-CL_W/2,y_r+CL_W/2,0,DECK_TOP)
    for y in (y_f,y_r): s=s.cut(xcyl(y,0,BORE_D))
    s=s.cut(box(-COLLAR_X/2,COLLAR_X/2,HY+COLLAR_Y0,HY+COLLAR_Y1,-1,3.4))        # collar-mount pocket from below
    s=s.cut(zcyl(0,HY,7.0,0,DECK_TOP+1))                                          # filament path
    s=s.cut(box(X0-1,X1+1,BELT_Y-BELT_SLOT_W/2,BELT_Y+BELT_SLOT_W/2,BELT_Z0,DECK_TOP+1))   # belt slot, open to the top
    for sx in SCREW_X:
        for y in (y_f,y_r):
            for sgn in (-1,1):
                yy=y+sgn*CL_DY
                s=s.cut(zcyl(sx,yy,3.4,-1,DECK_TOP+1)).cut(zcyl(sx,yy,6.2,DECK_TOP-3,DECK_TOP+1))
    for (px,py) in PLATE_HOLES: s=s.cut(zcyl(px,py,5.6,DECK_TOP-6,DECK_TOP+1))      # M4 heat-set inserts, 6 deep
    return s
if __name__=="__main__":
    import os; os.makedirs("out_cad",exist_ok=True)
    b,s=body(),saddle()
    for n,o in (("body",b),("saddle",s)):
        cq.exporters.export(o,"out_cad/carriage_v1_%s.step"%n); cq.exporters.export(o,"out_cad/carriage_v1_%s.stl"%n)
        bb=o.val().BoundingBox(); print(n,"%.1f x %.1f x %.1f"%(bb.xlen,bb.ylen,bb.zlen),"vol %.1f cm3"%(o.val().Volume()/1000),"valid",o.val().isValid())
    print("plate holes (X',Y'):",PLATE_HOLES,"; front-hole to front rod axis %.1f"%abs(PLATE_HOLES[0][1]-y_f))
