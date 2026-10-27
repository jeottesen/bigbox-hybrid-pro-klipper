import sys
from cadquery import importers
from OCP.BRepAdaptor import BRepAdaptor_Surface
w=importers.importStep(sys.argv[1]); sols=w.solids().vals()
i=int(sys.argv[2]); ax=sys.argv[3]; cx,cy=float(sys.argv[4]),float(sys.argv[5])  # center of other two axes
rows=set()
for f in sols[i].Faces():
    if f.geomType()=='CYLINDER':
        c=BRepAdaptor_Surface(f.wrapped).Cylinder(); a=c.Axis(); d=a.Direction(); l=a.Location()
        dv={'X':d.X(),'Y':d.Y(),'Z':d.Z()}
        if abs(dv[ax])<.99: continue
        o=[k for k in 'XYZ' if k!=ax]; lv={'X':l.X(),'Y':l.Y(),'Z':l.Z()}
        if abs(lv[o[0]]-cx)>1 or abs(lv[o[1]]-cy)>1: continue
        b=f.BoundingBox(); lo,hi=getattr(b,ax.lower()+'min'),getattr(b,ax.lower()+'max')
        rows.add((round(lo,1),round(hi,1),round(c.Radius(),2)))
for r in sorted(rows): print("%s %.1f..%.1f  r=%.2f dia=%.2f"%(ax,r[0],r[1],r[2],r[2]*2))
