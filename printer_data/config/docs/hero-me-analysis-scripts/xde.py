import sys,json
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
path,out=sys.argv[1],sys.argv[2]
app=XCAFApp_Application.GetApplication_s()
doc=TDocStd_Document(TCollection_ExtendedString("doc")); app.NewDocument(TCollection_ExtendedString("MDTV-XCAF"),doc)
rd=STEPCAFControl_Reader(); rd.SetNameMode(True)
assert rd.ReadFile(path)==IFSelect_RetDone
rd.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def name(l):
    n=TDataStd_Name()
    return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),n) else ''
res=[]
def walk(label,loc,path):
    nm=name(label)
    if st.IsAssembly_s(label):
        comps=TDF_LabelSequence(); st.GetComponents_s(label,comps)
        for i in range(1,comps.Length()+1):
            c=comps.Value(i); ref=TDF_Label()
            if st.GetReferredShape_s(c,ref):
                l2=st.GetLocation_s(c)
                walk(ref,loc.Multiplied(l2),path+[nm])
    else:
        sh=st.GetShape_s(label).Located(loc)
        b=Bnd_Box(); BRepBndLib.AddOptimal_s(sh,b,False,False)
        if b.IsVoid(): return
        x0,y0,z0,x1,y1,z1=b.Get()
        res.append({'name':nm,'path':'/'.join(path[-2:]),'bbox':[round(v,1) for v in (x0,y0,z0,x1,y1,z1)]})
fs=TDF_LabelSequence(); st.GetFreeShapes(fs)
for i in range(1,fs.Length()+1): walk(fs.Value(i),TopLoc_Location(),[])
json.dump(res,open(out,'w'))
print(len(res),'leaf parts')
