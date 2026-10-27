import sys,re
import cadquery as cq
from cadquery import importers
for p in sys.argv[1:]:
    print("=====",p.split('/')[-1])
    txt=open(p,errors='ignore').read()
    names=re.findall(r"PRODUCT\('([^']*)'",txt)
    print("products:",len(names)); print(sorted(set(names))[:80])
    try:
        w=importers.importStep(p)
        bb=w.val().BoundingBox()
        print("bbox X%.1f Y%.1f Z%.1f"%(bb.xlen,bb.ylen,bb.zlen),"min",round(bb.xmin,1),round(bb.ymin,1),round(bb.zmin,1),"solids",len(w.solids().vals()))
    except Exception as e: print("ERR",e)
