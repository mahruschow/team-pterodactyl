"""Compare P1 Excellon drill positions/tools with the saved native PCB.

Run with KiCad Python. This reads the design; it never regenerates or edits it.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,re
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'
OUT=ROOT/'docs/validation/2026-10-21/first-prototype-release'
FAB=OUT/'fabrication'

def key(x,y,d):return tuple(round(float(v),6) for v in (x,y,d))
def read_drill(path):
    text=path.read_text();assert 'METRIC' in text and text.rstrip().endswith('M30')
    sizes={int(a):float(b) for a,b in re.findall(r'^T(\d+)C([\d.]+)',text,re.M)}
    tool=None;hits=Counter()
    for line in text.splitlines():
        m=re.fullmatch(r'T(\d+)',line)
        if m:tool=int(m[1])
        m=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
        if m:hits[key(m[1],-float(m[2]),sizes[tool])]+=1
    return hits

def main():
    board=pcbnew.LoadBoard(str(PCB));expected={'PTH':Counter(),'NPTH':Counter()}
    for f in board.GetFootprints():
        for p in f.Pads():
            d=p.GetDrillSize()
            if not d.x:continue
            assert d.x==d.y,'Unexpected slot'
            k='NPTH' if p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH else 'PTH'
            pos=p.GetPosition();expected[k][key(pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y),pcbnew.ToMM(d.x))]+=1
    tracks=board.GetTracks()
    for v in tracks:
        if v.GetClass()=='PCB_VIA':
            pos=v.GetPosition();expected['PTH'][key(pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y),pcbnew.ToMM(v.GetDrillValue()))]+=1
    counts={}
    for kind in expected:
        actual=read_drill(FAB/f'PTERODACTYL_v4-{kind}.drl')
        # KiCad's metric decimal Excellon rounds coordinates to 0.001 mm.
        # Compare one-to-one within half that quantum; do not change PCB geometry.
        remaining=list(actual.elements())
        for x,y,d in expected[kind].elements():
            matches=[i for i,(a,b,c) in enumerate(remaining) if abs(x-a)<=.000501 and abs(y-b)<=.000501 and d==c]
            assert len(matches)==1,(kind,(x,y,d),matches)
            remaining.pop(matches[0])
        assert not remaining,(kind,remaining)
        counts[kind]=sum(actual.values())
    layers={'F_Cu.gtl':'Copper,L1,Top','In1_Cu.g1':'Copper,L2,Inr','In2_Cu.g2':'Copper,L3,Inr','B_Cu.gbl':'Copper,L4,Bot',
            'F_Mask.gts':'Soldermask,Top','B_Mask.gbs':'Soldermask,Bot','F_Silkscreen.gto':'Legend,Top','B_Silkscreen.gbo':'Legend,Bot','Edge_Cuts.gm1':'Profile'}
    for name,function in layers.items():
        t=(FAB/('PTERODACTYL_v4-'+name)).read_text()
        assert t.rstrip().endswith('M02*'),name
        assert function.lower() in t.lower(),(name,function)
    edge=(FAB/'PTERODACTYL_v4-Edge_Cuts.gm1').read_text()
    coords=[(int(x)/1e6,int(y)/1e6) for x,y in re.findall(r'^X(-?\d+)Y(-?\d+)',edge,re.M)]
    bounds=[round(max(p[i] for p in coords)-min(p[i] for p in coords),6) for i in (0,1)]
    assert bounds==[97.79,97.79],bounds
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [PCB,PCB.with_suffix('.kicad_sch'),PCB.with_suffix('.kicad_pro'),PCB.with_suffix('.kicad_dru')]}
    assert json.loads((OUT/'layout-check.json').read_text())['pcb_sha256']==hashes[PCB.name]
    assert json.loads((OUT/'schematic-check.json').read_text())['schematic_sha256']==hashes[PCB.with_suffix('.kicad_sch').name]
    net=(FAB/'PTERODACTYL_v4-P1.d356').read_text();assert net.rstrip().endswith('999')
    report={'result':'pass','native_hashes':hashes,'drill_counts':counts,'all_drill_positions_and_diameters_match_native':True,
            'drill_position_tolerance_mm':0.000501,'outline_centerline_mm':bounds,'gerber_layer_count':len(layers),'copper_layers':4,'ipc_d356_exported':True,
            'scope':'File integrity, layer attributes, native-vs-Excellon positions/diameters and outline bounds. Copper connectivity is covered separately by native DRC/net contract; AISLER native import was visually reviewed.'}
    (OUT/'fabrication-check.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'native-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
