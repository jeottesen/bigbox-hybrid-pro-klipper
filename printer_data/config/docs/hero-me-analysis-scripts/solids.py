import sys
from cadquery import importers
w=importers.importStep(sys.argv[1])
for i,s in enumerate(w.solids().vals()):
    b=s.BoundingBox()
    print(i,"vol%.0f"%s.Volume(),"X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]"%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax),"size %.1f x %.1f x %.1f"%(b.xlen,b.ylen,b.zlen),"faces",len(s.Faces()))
