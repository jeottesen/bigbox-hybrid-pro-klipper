import sys
from cadquery import importers
from OCP.BRepAdaptor import BRepAdaptor_Surface
w=importers.importStep(sys.argv[1]); sols=w.solids().vals()
for i,s in enumerate(sols):
    for f in s.Faces():
        if f.geomType()=='CONE':
            c=BRepAdaptor_Surface(f.wrapped).Cone(); l=c.Location(); b=f.BoundingBox()
            print("solid",i,"cone ref r=%.2f"%c.RefRadius(),"loc",[round(x,1) for x in (l.X(),l.Y(),l.Z())],"zrange %.1f-%.1f"%(b.zmin,b.zmax),"xy",round((b.xmin+b.xmax)/2,1),round((b.ymin+b.ymax)/2,1))
