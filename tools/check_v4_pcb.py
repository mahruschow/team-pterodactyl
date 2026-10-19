"""Check the draft v4 PCB: native DRC with schematic parity, Step 4 separations, 3D render.

Run with KiCad Python; optional first argument selects kicad-cli.exe.
Uses Native_KiCad_v4/placement.json written by tools/build_v4_pcb.py. Once tracks exist
it also reports routing metrics: I2C length (PC11), power track widths, vias, and
tracks inside the U2/U5 envelopes (which must stay empty).
"""
from pathlib import Path
import collections,hashlib,json,math,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'
OUT=ROOT/'docs/validation/2026-10-19/step7-pcb'
POWER={'J1','F1','Q1','D1','R1','J2','C1','R2','R3','C2','U2','C3','C4'}
EXPECTED_MISSING={'U2','U5'}
# Step 4 PC1-PC7 (PLACEMENT_AND_INTERFERENCE.md): (rule, group a, group b, minimum mm)
RULES=[('PC1',{'U3'},POWER,40.0),('PC2',{'U3'},{'U1'},25.0),('PC3',{'U3'},{'U5'},20.0),
       ('PC4-teensy',{'U5'},{'U1'},20.0),('PC4-power',{'U5'},POWER,20.0),
       ('PC5-teensy',{'U4'},{'U1'},25.0),('PC5-power',{'U4'},POWER,25.0)]


def gap(a,b):
    dx=max(b[0]-a[2],a[0]-b[2],0);dy=max(b[1]-a[3],a[1]-b[3],0)
    return math.hypot(dx,dy)


PC11_MAX_MM=150.0
POWER_MIN_MM=0.5


def routing_metrics(placement):
    import pcbnew
    board=pcbnew.LoadBoard(str(PCB))
    e=board.GetBoardEdgesBoundingBox();ox,oy=pcbnew.ToMM(e.GetLeft()),pcbnew.ToMM(e.GetTop())
    tracks=[t for t in board.GetTracks() if t.GetClass()=='PCB_TRACK']
    vias=[t for t in board.GetTracks() if t.GetClass()=='PCB_VIA']
    length=collections.defaultdict(float)
    for t in tracks:length[t.GetNetname()]+=pcbnew.ToMM(t.GetLength())
    thin=sorted({t.GetNetname() for t in tracks if t.GetNetClassName()=='Power' and pcbnew.ToMM(t.GetWidth())<POWER_MIN_MM-1e-6})
    inside=[]
    for ref in ('U2','U5'):
        x0,y0,x1,y1=placement[ref]
        for t in tracks+vias:
            for p in (t.GetStart(),t.GetEnd()):
                x,y=pcbnew.ToMM(p.x)-ox,pcbnew.ToMM(p.y)-oy
                if x0<x<x1 and y0<y<y1:inside.append((ref,t.GetNetname()));break
    i2c=round(max(length.get('/I2C_SDA',0),length.get('/I2C_SCL',0)),1)
    return {'track_segments':len(tracks),'track_length_mm':round(sum(length.values()),1),'vias':len(vias),
            'i2c_longest_mm':i2c,'i2c_pass':i2c<=PC11_MAX_MM,'thin_power_nets':thin,'tracks_in_envelopes':sorted(set(inside))}


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
    OUT.mkdir(parents=True,exist_ok=True)
    drc=OUT/'drc.json'
    subprocess.run([cli,'pcb','drc','--format','json','--severity-all','--schematic-parity','--output',str(drc),str(PCB)],check=True,capture_output=True)
    subprocess.run([cli,'pcb','render','--side','top','--width','1600','--height','1600','--quality','basic',
                    '--output',str(OUT/'v4-top.png'),str(PCB)],check=True,capture_output=True)
    subprocess.run([cli,'pcb','export','pdf','--layers','Edge.Cuts,F.Fab,F.Courtyard,F.Silkscreen','--mode-single',
                    '--output',str(OUT/'v4-assembly.pdf'),str(PCB)],check=True,capture_output=True)
    report=json.loads(drc.read_text())
    violations=collections.Counter(v['type'] for v in report['violations'])
    parity=report.get('schematic_parity',[])
    missing={v['description'].split()[2] for v in parity if v['type']=='missing_footprint'}
    other_parity=[v['description'] for v in parity if v['type']!='missing_footprint']
    placement=json.loads((ROOT/'Native_KiCad_v4/placement.json').read_text())['courtyards_local_mm']
    separations=[]
    for rule,a,b,minimum in RULES:
        d=min(gap(placement[x],placement[y]) for x in a for y in b)
        separations.append({'rule':rule,'gap_mm':round(d,2),'minimum':minimum,'pass':d>=minimum})
    routing=routing_metrics(placement)
    problems=[]
    if routing['track_segments']:
        if not routing['i2c_pass']:problems.append(('PC11 I2C length',routing['i2c_longest_mm']))
        if routing['thin_power_nets']:problems.append(('power width',routing['thin_power_nets']))
        if routing['tracks_in_envelopes']:problems.append(('envelope',routing['tracks_in_envelopes']))
    if violations:problems.append(('drc',dict(violations)))
    if missing!=EXPECTED_MISSING or other_parity:problems.append(('parity',sorted(missing),other_parity))
    problems+=[('separation',s) for s in separations if not s['pass']]
    result={'pcb_sha256':hashlib.sha256(PCB.read_bytes()).hexdigest(),'drc_violations':dict(violations),
            'unconnected_items':len(report.get('unconnected_items',[])),'parity_missing_footprints':sorted(missing),
            'separations':separations,'routing':routing,'problems':problems,'result':'pass' if not problems else 'fail',
            'scope':'Draft placement with inner GND planes; tracks not yet routed, so unconnected items are expected. '
                    'Not a fabrication check: U2/U5 footprints, routing, manufacturer rules and review remain.'}
    (OUT/'pcb-check.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    assert not problems,problems
    print('PASS: DRC 0 violations; parity only missing %s; %d Step 4 separations met; %d unconnected.'%(
        sorted(missing),len(separations),result['unconnected_items']))
    print('  routing',routing)
    for s in separations:print(' ',s)


if __name__=='__main__':main()
