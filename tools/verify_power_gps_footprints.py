"""Independent native checks for the regulator and UNVERIFIED GPS carrier.

Run with KiCad Python. Checks source geometry, symbol/pad contracts, the current
schematic and routed board, an isolated fixture, and a placement-move regression.
Does not modify the main schematic, board, or libraries.
"""
from pathlib import Path
import sys, json, hashlib, subprocess, xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
import pcbnew
import check_v4_pcb as placement_check
from verify_v4_schematic import EXPECTED, EXPECTED_NC
from sexpr import parse, find, first

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'
PRJ=ROOT/'Native_KiCad_v4'
OUT=ROOT/'docs/validation/2026-10-19/regulator-gps'
REG='Pololu_S9V11F5_SSW_Carrier'
GPS='Adafruit_GPS_5440_UNVERIFIED_Legacy_Carrier'


def close(a,b): assert abs(a-b)<1e-5,(a,b)
def point(x,y): return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
def pad_xy(p): return (pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y))


def dxf_header_centres():
    lines=(ROOT/'docs/reference/regulator-gps/reg20a-drill.dxf').read_text().splitlines()
    pairs=list(zip(lines[::2],lines[1::2]));entities=[];current=None
    for code,value in pairs+[("0","EOF")]:
        code=code.strip();value=value.strip()
        if code=='0':
            if current:entities.append(current)
            current={'type':value}
        elif current is not None:current[code]=value
    # This drill guide draws hole-centre crosses as pairs of two-vertex
    # polylines, not circles. The three header crosses span .040 inches;
    # smaller .015-inch crosses elsewhere denote vias.
    horizontal=set();vertical=set();vertices=[]
    for e in entities:
        if e['type']=='POLYLINE':vertices=[]
        elif e['type']=='VERTEX':vertices.append((float(e['10']),float(e['20'])))
        elif e['type']=='SEQEND' and len(vertices)==2:
            (x0,y0),(x1,y1)=vertices
            centre=(round((x0+x1)/2,6),round((y0+y1)/2,6))
            if abs(y0-y1)<1e-6 and abs(abs(x1-x0)-.04)<1e-6:horizontal.add(centre)
            if abs(x0-x1)<1e-6 and abs(abs(y1-y0)-.04)<1e-6:vertical.add(centre)
    centres=horizontal&vertical
    assert len(centres)==3,centres
    return sorted((x*25.4,y*25.4) for x,y in centres)


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
    OUT.mkdir(parents=True,exist_ok=True)
    def run(*args):subprocess.run([cli,*map(str,args)],check=True,capture_output=True)
    reg=pcbnew.FootprintLoad(str(LIB),REG);gps=pcbnew.FootprintLoad(str(LIB),GPS)
    rp={p.GetNumber():p for p in reg.Pads()};assert set(rp)=={'VIN','GND','VOUT'}
    # DXF uses inches; official top-side pinout maps left to right VIN/GND/VOUT.
    centres=dxf_header_centres()
    for name,(x,y) in zip(('VIN','GND','VOUT'),centres):
        ax,ay=pad_xy(rp[name]);close(ax,x-centres[0][0]);close(ay,centres[0][1]-y)
    source=json.loads((ROOT/'docs/reference/step3-cad-geometry.json').read_text())
    src=next(b for b in source['boards'] if b['file']=='Adafruit-Ultimate-GPS/Adafruit Ultimate GPS.brd')
    jp=next(h for h in src['headers'] if h['element']=='JP1')['pads'];origin=jp[0]
    identifiers={'1':'PPS','2':'VIN','3':'GND','4':'RX','5':'TX','6':'FIX','7':'VBAT','8':'EN','9':'3V3_OUT'}
    gp={p.GetNumber():p for p in gps.Pads() if p.GetNumber()}
    assert set(gp)==set(identifiers.values())
    for p in jp:
        actual=pad_xy(gp[identifiers[p['pad']]])
        close(actual[0],p['x']-origin['x']);close(actual[1],origin['y']-p['y'])
    holes=[p for p in gps.Pads() if not p.GetNumber()];assert len(holes)==2
    actual=sorted(tuple(round(v,5) for v in pad_xy(p)) for p in holes)
    expected=sorted((round(h['pads'][0]['x']-origin['x'],5),round(origin['y']-h['pads'][0]['y'],5))
                    for h in src['headers'] if 'MOUNTINGHOLE' in h['package'])
    assert actual==expected
    for p in [*rp.values(),*gp.values()]:
        assert p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH
        close(pcbnew.ToMM(p.GetDrillSize().x),1.04)
        close(pcbnew.ToMM(p.GetSize().x),1.8)
    for p in holes:
        assert p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH
        close(pcbnew.ToMM(p.GetDrillSize().x),2.7)
    for fp in (reg,gps):
        fp.BuildCourtyardCaches();assert fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount()==1
        assert len(list(fp.Zones()))==1
    # Confirm named pads match the real library contracts, not just generator labels.
    def pin_numbers(symbol):
        result=set()
        def walk(n):
            for c in n:
                if isinstance(c,list) and c:
                    if c[0]=='pin':result.add(str(first(c,'number')[1]))
                    else:walk(c)
        walk(symbol);return result
    lib=parse((PRJ/'Pterodactyl_v4.kicad_sym').read_text(encoding='utf-8'))
    assert pin_numbers(next(s for s in find(lib,'symbol') if s[1]=='Pololu_S9V11F5_Header'))==set(rp)
    lib=parse((ROOT/'Native_KiCad_v11/Pterodactyl_Modules.kicad_sym').read_text(encoding='utf-8'))
    assert pin_numbers(next(s for s in find(lib,'symbol') if s[1]=='Adafruit_PA1616D_5440_Logical'))==set(gp)
    fixture=pcbnew.BOARD()
    edge=pcbnew.PCB_SHAPE(fixture);edge.SetShape(pcbnew.SHAPE_T_RECT);edge.SetStart(point(10,10));edge.SetEnd(point(110,80));edge.SetLayer(pcbnew.Edge_Cuts);edge.SetWidth(pcbnew.FromMM(.05));fixture.Add(edge)
    reg.SetReference('U_REG');reg.SetPosition(point(30,50));fixture.Add(reg)
    gps.SetReference('U_GPS_DRAFT');gps.SetPosition(point(85,55));fixture.Add(gps)
    pcbnew.SaveBoard(str(OUT/'footprint-fixture.kicad_pcb'),fixture)
    run('pcb','drc','--format','json','--severity-all','--output',OUT/'fixture-drc.json',OUT/'footprint-fixture.kicad_pcb')
    run('pcb','export','svg','--layers','F.Cu,F.Fab,F.Silkscreen,Dwgs.User,F.Courtyard,Edge.Cuts','--mode-single','--page-size-mode','2','--exclude-drawing-sheet','--output',OUT/'footprint-fixture.svg',OUT/'footprint-fixture.kicad_pcb')
    run('sch','erc','--format','json','--severity-all','--output',OUT/'erc.json',PRJ/'PTERODACTYL_v4.kicad_sch')
    run('sch','export','netlist','--format','kicadxml','--output',OUT/'netlist.xml',PRJ/'PTERODACTYL_v4.kicad_sch')
    run('pcb','drc','--format','json','--severity-all','--schematic-parity','--refill-zones','--output',OUT/'board-drc.json',PRJ/'PTERODACTYL_v4.kicad_pcb')
    nets={};nc=set();netlist=ET.parse(OUT/'netlist.xml').getroot()
    for n in netlist.iter('net'):
        nodes={p.get('ref')+'.'+p.get('pin') for p in n.iter('node')}
        name=n.get('name').lstrip('/')
        if name.startswith('unconnected-('):nc|=nodes
        else:nets[name]=nodes
    assert nets==EXPECTED and nc==set(EXPECTED_NC)
    parts={c.get('ref'):c for c in netlist.iter('comp')}
    assert parts['U2'].findtext('footprint')=='Pterodactyl_Modules:'+REG
    assert not parts['U5'].findtext('footprint')
    erc=json.loads((OUT/'erc.json').read_text());assert not [v for s in erc['sheets'] for v in s['violations']]
    drc=json.loads((OUT/'board-drc.json').read_text());assert not drc['violations'],drc['violations']
    parity=drc['schematic_parity'];assert len(parity)==1 and parity[0]['description'].startswith('Missing footprint U5 ')
    f=json.loads((OUT/'fixture-drc.json').read_text());assert not f['violations'],f['violations']
    board=pcbnew.LoadBoard(str(PRJ/'PTERODACTYL_v4.kicad_pcb'))
    positions=placement_check.actual_placement(board)
    separations=[{'rule':r,'gap_mm':round(min(placement_check.gap(positions[x],positions[y]) for x in a for y in b),3),'minimum_mm':minimum} for r,a,b,minimum in placement_check.RULES]
    assert all(s['gap_mm']>=s['minimum_mm'] for s in separations)
    # Regression: move only the in-memory IMU into the power section; the measured check must fail.
    imu=next(f for f in board.GetFootprints() if f.GetReference()=='U3')
    power=next(f for f in board.GetFootprints() if f.GetReference()=='Q1')
    imu.SetPosition(power.GetPosition());moved=placement_check.actual_placement(board)
    assert min(placement_check.gap(moved['U3'],moved[r]) for r in placement_check.POWER)<40
    report={'kicad':pcbnew.GetBuildVersion(),'result':'pass','regulator_pads':3,'gps_legacy_pads':9,'gps_legacy_mounting_holes':2,
            'regulator_dxf_header_centres_mm':centres,'erc_violations':0,'fixture_drc_violations':0,'board_physical_drc_violations':0,
            'board_unconnected_items':len(drc['unconnected_items']),'missing_footprints':['U5'],'nets_checked':len(nets),'intentional_no_connects':len(nc),
            'separations':separations,'manual_move_regression':'pass: moving IMU in memory fails PC1',
            'routing':placement_check.routing_metrics(positions),
            'footprint_sha256':{n:hashlib.sha256((LIB/(n+'.kicad_mod')).read_bytes()).hexdigest() for n in (REG,GPS)},
            'scope':'Nominal regulator source geometry and legacy GPS comparison only; #5440 revision/physical fit, retention and remaining routing are NOT approved.'}
    (OUT/'footprint-check.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
