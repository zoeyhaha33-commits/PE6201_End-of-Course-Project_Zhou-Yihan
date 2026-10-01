"""Extract the real modelling columns from the supplied GIPT XLSX without modifying it.

Usage:
    python -m src.extract_gipt "/path/to/Global Integrated Power September 2026.xlsx"

The output is data/processed/gipt_modeling.csv.
"""
from pathlib import Path
import argparse, csv, re, zipfile, xml.etree.ElementTree as ET
from config import ROOT

MAIN_NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL_NS='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL_NS='http://schemas.openxmlformats.org/package/2006/relationships'
NS={'a':MAIN_NS,'r':REL_NS,'pr':PKG_REL_NS}
KEEP=[
    'Type','Country/area','Subregion','Region','Capacity (MW)','Status','Technology',
    'Associated storage','Fuel (combustion only)','CHP','CCS','Captive Industry Type',
    'Location accuracy','GEM location ID','GEM unit/phase ID'
]

def col_idx(ref):
    m=re.match(r'([A-Z]+)',ref); n=0
    for ch in m.group(1): n=n*26+(ord(ch)-64)
    return n-1

def get_shared(z):
    if 'xl/sharedStrings.xml' not in z.namelist(): return []
    root=ET.fromstring(z.read('xl/sharedStrings.xml')); tag=f'{{{MAIN_NS}}}t'
    return [''.join((t.text or '') for t in si.iter(tag)) for si in root.findall('a:si',NS)]

def get_sheet(z,name):
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    relmap={r.attrib['Id']:r.attrib['Target'] for r in rels}
    for s in wb.find('a:sheets',NS):
        if s.attrib['name']==name:
            rid=s.attrib[f'{{{REL_NS}}}id']; t=relmap[rid]
            return t if t.startswith('xl/') else 'xl/'+t.lstrip('/')
    raise KeyError(name)

def read_row(elem,shared):
    out={}
    for c in elem.findall('a:c',NS):
        idx=col_idx(c.attrib['r']); typ=c.attrib.get('t'); v=c.find('a:v',NS)
        val='' if v is None else (v.text or '')
        if typ=='s' and val: val=shared[int(val)]
        out[idx]=val
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('xlsx'); args=ap.parse_args()
    src=Path(args.xlsx); dest=ROOT/'data'/'processed'/'gipt_modeling.csv'; dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(src) as z:
        shared=get_shared(z); target=get_sheet(z,'Power facilities')
        with z.open(target) as f, dest.open('w',newline='',encoding='utf-8') as out:
            writer=None; header=None; count=0
            for _,elem in ET.iterparse(f,events=('end',)):
                if elem.tag!=f'{{{MAIN_NS}}}row': continue
                rv=read_row(elem,shared)
                if header is None:
                    headers=[rv.get(i,'') for i in range(max(rv)+1)]
                    header={h:i for i,h in enumerate(headers)}
                    missing=[c for c in KEEP if c not in header]
                    if missing: raise ValueError(f'Missing expected columns: {missing}')
                    writer=csv.DictWriter(out,fieldnames=KEEP); writer.writeheader()
                else:
                    writer.writerow({c:rv.get(header[c],'') for c in KEEP}); count+=1
                elem.clear()
    print(f'Extracted {count:,} rows to {dest}')
if __name__=='__main__': main()
