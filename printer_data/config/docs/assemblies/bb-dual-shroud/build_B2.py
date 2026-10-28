import numpy as np, cadquery as cq
from cadquery import importers
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape
sh=TopoDS_Shape(); assert StlAPI_Reader().Read(sh,"shroud2/bb_dual_shroud.stl")
shroud=cq.Shape.cast(sh)
try:
    shroud=cq.Solid.makeSolid(cq.Shell(shroud.wrapped)) if shroud.ShapeType()!="Solid" else shroud
except Exception as e: print("solid conversion failed, keeping shell:",e)
H=importers.importStep("step/STEP/Hybrid_v1.1.0..stp").solids().vals()
carriage=H[1]
V=importers.importStep("step2/v6/e3d v6.STEP").solids().vals()[:4]
v6=[s.rotate(cq.Vector(0,0,0),cq.Vector(1,1,1),120).rotate(cq.Vector(0,0,0),cq.Vector(0,0,1),270).translate(cq.Vector(-62.4,308.0,696.8-55.0)) for s in V]
# approximate sock (block long side now toward -X): block X -62.4-15.5..-62.4+4.5 (centre -67.9), Y 308+-8, Z 640.6..652.1
sock_outer=cq.Workplane("XY").box(23.5,19.5,14.0,centered=(True,True,False)).translate((-67.9,308.0,639.1))
sock_inner=cq.Workplane("XY").box(20.5,16.5,13.0,centered=(True,True,False)).translate((-67.9,308.0,640.6))
nozzle_hole=cq.Workplane("XY").circle(4.5).extrude(6).translate((-62.4,308.0,638.0))
sock=sock_outer.cut(sock_inner).cut(nozzle_hole).val()
asm=cq.Assembly(name="bb_dual_shroud_single_nozzle")
cols={"carriage":(0.55,0.55,0.55),"shroud":(0.2,0.45,0.85),"v6_nozzle":(0.8,0.65,0.1),"v6_block":(0.7,0.55,0.1),"v6_heatbreak":(0.8,0.8,0.8),"v6_heatsink":(0.75,0.75,0.78),"sock_approx":(0.85,0.2,0.2)}
parts=[("carriage",carriage),("shroud",shroud),("v6_nozzle",v6[0]),("v6_block",v6[1]),("v6_heatbreak",v6[2]),("v6_heatsink",v6[3]),("sock_approx",sock)]
for n,s in parts: asm.add(s,name=n,color=cq.Color(*cols[n]))
asm.save("asm/assembly_bb_dual_shroud.step")
print("saved; shroud shape type",shroud.ShapeType())
