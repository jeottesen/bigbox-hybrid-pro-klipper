import sys
from cadquery import importers
from collections import defaultdict
w=importers.importStep(sys.argv[1]); sols=w.solids().vals()
for i in map(int,sys.argv[2].split(',')):
    s=sols[i]; seen=defaultdict(int); print("-- solid",i)
    for f in s.Faces():
        if f.geomType()=='CYLINDER':
            from OCP.BRepAdaptor import BRepAdaptor_Surface
            sf=BRepAdaptor_Surface(f.wrapped).Cylinder()
            ax=sf.Axis(); d=ax.Direction(); l=ax.Location()
            key=(round(sf.Radius(),2),tuple(round(abs(x)) for x in (d.X(),d.Y(),d.Z())),round(l.X()),round(l.Y()),round(l.Z()))
            # collapse by axis line: drop along-axis coordinate
            dd=[k for k,x in enumerate((d.X(),d.Y(),d.Z())) if abs(x)>.9][0] if any(abs(x)>.9 for x in (d.X(),d.Y(),d.Z())) else None
            loc=[round(l.X(),1),round(l.Y(),1),round(l.Z(),1)]
            if dd is not None: loc[dd]='*'
            seen[(round(sf.Radius(),2),'XYZ'[dd] if dd is not None else '?',tuple(loc))]+=1
    for k in sorted(seen,key=lambda k:(k[1],-k[0])): print(" r=%s axis=%s at %s  x%d"%(k[0],k[1],k[2],seen[k]))
