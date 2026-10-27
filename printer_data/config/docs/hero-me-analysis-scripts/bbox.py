import sys,struct,re
def bbox(p):
    b=open(p,'rb').read()
    if b[:5]==b'solid' and b'facet' in b[:400]:
        v=[tuple(map(float,m)) for m in re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)',b)]
    else:
        n=struct.unpack('<I',b[80:84])[0]; v=[]
        for i in range(n):
            d=struct.unpack('<12fH',b[84+i*50:134+i*50]); v+=[d[3:6],d[6:9],d[9:12]]
    return [round(max(c[i] for c in v)-min(c[i] for c in v),1) for i in range(3)]
for p in sys.argv[1:]: print(bbox(p),p.split('Release V4/')[-1])
