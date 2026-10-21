"""Compare the component-finalization PCB with the preserved input checkpoint.

Read-only, no pcbnew loads. Usage: python tools/verify_component_preservation.py
BASELINE_PCB OUTPUT_JSON. This is a bounded geometry/net audit, not a fit test.
"""
import hashlib, json, sys
from pathlib import Path
from sexpr import parse, find, first

ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'

def canonical(value):
    if isinstance(value,list):return [canonical(x) for x in value]
    try:return float(value)
    except (ValueError,TypeError):return str(value)

def keyed(board,kind):return {first(n,'uuid')[1]:n for n in find(board,kind)}
def properties(n):return {p[1]:p[2] for p in find(n,'property')}
def geometry(n,keys):return {k:canonical(first(n,k)) for k in keys}

def main():
    baseline=Path(sys.argv[1]);output=Path(sys.argv[2])
    a,b=[parse(p.read_text(encoding='utf-8')) for p in (baseline,PCB)]
    changed=[]
    for kind in ('segment','via'):
        old,new=keyed(a,kind),keyed(b,kind)
        assert old.keys()==new.keys(),kind+' UUID set changed'
        for uid,n in old.items():
            m=new[uid]
            fixed=['width','layer','net'] if kind=='segment' else ['at','size','drill','layers','net']
            assert geometry(n,fixed)==geometry(m,fixed),(kind,uid,'fixed routing field changed')
            if kind=='segment' and geometry(n,['start','end'])!=geometry(m,['start','end']):
                changed.append({'uuid':uid,'before':geometry(n,['start','end']),'after':geometry(m,['start','end'])})
    old,new=keyed(a,'footprint'),keyed(b,'footprint')
    assert old.keys()==new.keys(),'Footprint UUID set changed'
    moves=[];pad_changes=[]
    permitted={'C2':(0,-.30),'C6':(0,.20),'C8':(0,.15),'TP4':(0,1)}
    for uid,n in old.items():
        m=new[uid];ref=properties(n)['Reference']
        assert properties(m)['Reference']==ref
        oa,na=canonical(first(n,'at')[1:]),canonical(first(m,'at')[1:])
        if oa!=na:
            delta=[round(na[i]-oa[i],6) for i in range(2)]
            assert tuple(delta)==permitted[ref] and oa[2:]==na[2:],(ref,delta)
            moves.append({'reference':ref,'before':oa,'after':na,'delta_mm':delta})
        op,np=keyed(n,'pad'),keyed(m,'pad');assert op.keys()==np.keys(),ref
        for puid,p in op.items():
            q=np[puid];assert p[1]==q[1] and canonical(first(p,'net'))==canonical(first(q,'net')),(ref,p[1],'net changed')
            attrs=['at','size','drill','layers']
            if geometry(p,attrs)!=geometry(q,attrs):
                assert ref in ('J1','J2'),(ref,p[1],'unexpected pad geometry')
                pad_changes.append({'reference':ref,'pad':p[1],'before':geometry(p,attrs),'after':geometry(q,attrs)})
    def edges(board):return [canonical(x) for x in board if isinstance(x,list) and first(x,'layer')==['layer','Edge.Cuts']]
    assert edges(a)==edges(b),'Board outline changed'
    assert canonical(first(a,'layers'))==canonical(first(b,'layers'))
    za,zb=keyed(a,'zone'),keyed(b,'zone');assert za.keys()==zb.keys()
    for uid,z in za.items():
        assert geometry(z,['net','net_name','layer','layers','polygon','keepout'])==geometry(zb[uid],['net','net_name','layer','layers','polygon','keepout']),'Zone boundaries/nets changed'
    report={'result':'pass','baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'pcb_sha256':hashlib.sha256(PCB.read_bytes()).hexdigest(),
            'footprints':len(new),'segments':len(keyed(b,'segment')),'vias':len(keyed(b,'via')),
            'all_original_footprint_pad_track_via_uuids_retained':True,'all_pad_nets_retained':True,
            'board_outline_module_positions_zone_boundaries_retained':True,'footprint_moves':moves,
            'connector_pad_changes':pad_changes,'changed_segment_count':len(changed),'changed_segment_endpoints':changed,
            'scope':'Original checkpoint geometry/net preservation; excludes changed silkscreen, component graphics, fields and zone-fill polygons. Hardware fit and operation are untested.'}
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('changed_segment_endpoints','connector_pad_changes')},indent=2))

if __name__=='__main__':main()
