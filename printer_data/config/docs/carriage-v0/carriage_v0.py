"""BigBox short carriage v0 (Route A): Hero Me Universal Base hung under it via the rear 32x12.5 plate.
Local frame: X along the rods (carriage centred), Y across the rods (+ = rear), Z up; rod axis at Z=0.
Parametric; all lengths in mm. Run with cadquery: python carriage_v0.py"""
import cadquery as cq

# --- hardware (measured / from manual) ---
ROD_SP   = 57.8            # rod spacing across Y
BEAR_OD  = 15.0            # LM8LUU 8x15x45
BEAR_LEN = 45.0
BORE_D   = 15.3            # print clearance for the bearing
L        = 50.0            # carriage length along the rods (<=50 rule)
# --- Hero Me interface (measured from the STLs) ---
HY       = -5.0            # hotend axis Y offset from rod mid-plane (toward front rod)
BASE_REAR_FROM_AXIS = 42.2 # base rear face is 42.2 behind the hotend axis
PAT_X    = 16.0            # rear plate pattern: +-16 (32 mm)
PAT_Z    = (-47.0, -34.5)  # 12.5 mm apart, centre ~ -40.7 (nozzle at stock height)
COLLAR_X = 40.5; COLLAR_Y0 = -11.4; COLLAR_Y1 = 23.4   # collar mount footprint rel. to hotend axis (+clearance)
# --- carriage geometry ---
BOT      = -10.0           # underside
CLAMP_TOP= 10.5            # top of the bearing clamps (clears bearing tops by 3)
TOWER_T  = 5.0
y_r, y_f = ROD_SP/2, -ROD_SP/2
y_tower0 = HY + BASE_REAR_FROM_AXIS
CL_SCREW_DY = BORE_D/2 + 2.4
CL_W = 2*(CL_SCREW_DY+3.2)
body_y0, body_y1 = y_f-CL_W/2, y_tower0+TOWER_T

# lower body: Z BOT..0, full footprint
body = cq.Workplane("XY").box(L, body_y1-body_y0, -BOT, centered=(True,False,False)).translate((0, body_y0, BOT))
# rear tower down to cover the 4-hole plate
tower = cq.Workplane("XY").box(L-6, TOWER_T, -(PAT_Z[0]-6.0), centered=(True,False,False)).translate((0, y_tower0, PAT_Z[0]-6.0))
body = body.union(tower)
# hotend window (collar mount + V6 top), through the lower body
win = cq.Workplane("XY").box(COLLAR_X, COLLAR_Y1-COLLAR_Y0, -BOT+1, centered=(True,False,False)).translate((0, HY+COLLAR_Y0, BOT-0.5))
body = body.cut(win)
# bearing cradles (lower halves): cylinders along X
for y in (y_f, y_r):
    cyl = cq.Workplane("YZ").circle(BORE_D/2).extrude(L+2).translate((-L/2-1, y, 0))
    body = body.cut(cyl)
# clamp screw holes into the body (M3, heat-set 4.0 mm), 2 per clamp
CL_SCREW_X = 16.0
for y in (y_f, y_r):
    for sx in (-CL_SCREW_X, CL_SCREW_X):
        for sy in (-CL_SCREW_DY, CL_SCREW_DY):
            body = body.cut(cq.Workplane("XY").circle(2.0).extrude(9).translate((sx, y+sy, -9)))
# Hero Me base bolt pattern through the tower (M3 pilot 3.2)
for sx in (-PAT_X, PAT_X):
    for z in PAT_Z:
        body = body.cut(cq.Workplane("XZ").circle(1.6).extrude(-(TOWER_T+2)).translate((sx, y_tower0-1, z)))
# clamp (upper half), printed twice
def clamp():
    c = cq.Workplane("XY").box(L, CL_W, CLAMP_TOP, centered=(True,True,False))
    c = c.cut(cq.Workplane("YZ").circle(BORE_D/2).extrude(L+2).translate((-L/2-1, 0, 0)))
    # shave below rod axis: clamp sits from Z=0 up
    for sx in (-CL_SCREW_X, CL_SCREW_X):
        for sy in (-CL_SCREW_DY, CL_SCREW_DY):
            c = c.cut(cq.Workplane("XY").circle(1.7).extrude(CLAMP_TOP+1).translate((sx, sy, -0.5)))
            c = c.cut(cq.Workplane("XY").circle(3.2).extrude(3).translate((sx, sy, CLAMP_TOP-3)))
    return c
if __name__=="__main__":
    import os; os.makedirs("out_cad",exist_ok=True)
    cq.exporters.export(body,"out_cad/carriage_v0_body.step"); cq.exporters.export(body,"out_cad/carriage_v0_body.stl")
    c=clamp(); cq.exporters.export(c,"out_cad/carriage_v0_clamp.step"); cq.exporters.export(c,"out_cad/carriage_v0_clamp.stl")
    for n,s in (("body",body),("clamp",c)):
        bb=s.val().BoundingBox(); print(n,"size %.1f x %.1f x %.1f"%(bb.xlen,bb.ylen,bb.zlen),"vol %.1f cm3"%(s.val().Volume()/1000),"valid",s.val().isValid())
