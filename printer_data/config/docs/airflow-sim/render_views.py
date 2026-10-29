"""Render the shroud assembly and the stock-mount assembly from all sides + isometric (VTK offscreen)."""
import numpy as np, trimesh, vtk, sys, os
import cadquery as cq
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
OUT="out/renders"; os.makedirs(OUT,exist_ok=True)
def tomesh(s,tol=0.05):
    v,t=s.tessellate(tol,0.2); return trimesh.Trimesh(np.array([[q.x,q.y,q.z] for q in v]),np.array(t),process=False)
parts={"shroud":[],"stock":[]}
# --- alternate shroud assembly (STL, shared frame) ---
for f,col in (("carriage",(0.6,0.6,0.62)),("shroud",(0.2,0.45,0.9)),("v6",(0.85,0.7,0.15)),("sock_approx",(0.9,0.25,0.25))):
    parts["shroud"].append((trimesh.load(f"asm/B/{f}.stl"),col))
# --- stock mount assembly (STEP, named parts) ---
asm=cq.Assembly.importStep("/home/claude/workspace/worktrees/bigbox-herome-gen7/printer_data/config/docs/assemblies/assembly_stock_fan_mount.step")
cols={"carriage":(0.6,0.6,0.62),"front_plate":(0.2,0.7,0.35),"back_plate":(0.15,0.55,0.3),"blower_housing":(0.35,0.35,0.7),"blower_impeller":(0.2,0.2,0.5),"v6_nozzle":(0.85,0.7,0.15),"v6_block":(0.8,0.6,0.1),"v6_heatbreak":(0.8,0.8,0.8),"v6_heatsink":(0.85,0.7,0.15),"sock_approx":(0.9,0.25,0.25)}
for name,child in asm.traverse():
    pass
for child in asm.children:
    shp=child.obj.val() if hasattr(child.obj,"val") else child.obj
    loc=child.loc; shp=shp.moved(loc) if loc is not None else shp
    print("stock part",child.name); parts["stock"].append((tomesh(shp),cols.get(child.name,(0.7,0.7,0.7))))
def poly(m,col):
    pd=vtk.vtkPolyData(); pts=vtk.vtkPoints(); pts.SetData(numpy_to_vtk(np.asarray(m.vertices,float),deep=True)); pd.SetPoints(pts)
    f=np.asarray(m.faces); cells=np.hstack([np.full((len(f),1),3),f]).astype(np.int64).ravel()
    ca=vtk.vtkCellArray(); ca.SetCells(len(f),numpy_to_vtkIdTypeArray(cells,deep=True)); pd.SetPolys(ca)
    n=vtk.vtkPolyDataNormals(); n.SetInputData(pd); n.SetFeatureAngle(40); n.Update()
    mp=vtk.vtkPolyDataMapper(); mp.SetInputData(n.GetOutput()); a=vtk.vtkActor(); a.SetMapper(mp); a.GetProperty().SetColor(*col); a.GetProperty().SetSpecular(0.2); return a
views={ # name: (direction from focal point to camera, view-up)
 "front_-Y":((0,-1,0),(0,0,1)),"back_+Y":((0,1,0),(0,0,1)),"left_-X":((-1,0,0),(0,0,1)),"right_+X":((1,0,0),(0,0,1)),
 "top_+Z":((0,0,1),(0,1,0)),"bottom_-Z":((0,0,-1),(0,1,0)),"iso_1":((1,-1,0.8),(0,0,1)),"iso_2":((-1,1,0.8),(0,0,1))}
def render(name,lst,sel_bounds,fn_prefix):
    ren=vtk.vtkRenderer(); ren.SetBackground(1,1,1)
    for m,c in lst: ren.AddActor(poly(m,c))
    ren.GetActiveCamera().SetParallelProjection(False)
    b=sel_bounds; ctr=(b[:3]+b[3:])/2; diag=np.linalg.norm(b[3:]-b[:3])
    for v,(d,up) in views.items():
        w=vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.AddRenderer(ren); w.SetSize(900,900)
        cam=ren.GetActiveCamera(); d=np.array(d,float); d/=np.linalg.norm(d); cam.SetFocalPoint(*ctr); cam.SetPosition(*(ctr+d*diag*1.5)); cam.SetViewUp(*up); ren.ResetCameraClippingRange(); cam.SetViewAngle(30)
        l=ren.MakeLight() if False else None
        w.Render(); wi=vtk.vtkWindowToImageFilter(); wi.SetInput(w); wi.Update(); pw=vtk.vtkPNGWriter(); fn=f"{OUT}/{fn_prefix}_{v}.png"; pw.SetFileName(fn); pw.SetInputConnection(wi.GetOutputPort()); pw.Write(); print("wrote",fn)
for k in parts:
    allv=np.vstack([m.vertices for m,_ in parts[k]]); 
    # focus on the head region (the carriage is large): crop view bounds around shroud/hotend
    lo=np.array([-115,270,628.]); hi=np.array([10,372,712.]); render(k,parts[k],np.array([*lo,*hi]),k)
