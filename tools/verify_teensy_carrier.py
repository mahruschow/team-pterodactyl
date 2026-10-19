"""Native geometry and positive/negative component-keepout checks.

Run with KiCad Python. The optional first argument selects kicad-cli;
the second selects KiCad's standard footprint-library directory.
Writes isolated fixtures only, never the main project PCB.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'
NAME='Teensy41_SSW_Carrier'
OUT=ROOT/'docs/validation/2026-10-18/step3-teensy'


def mm(n):return round(pcbnew.ToMM(n),6)
def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
def coordinates(fp):return {p.GetNumber():(mm(p.GetPosition().x),mm(p.GetPosition().y)) for p in fp.Pads()}


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else str(Path(sys.executable).with_name('kicad-cli.exe'))
    standard=Path(sys.argv[2]) if len(sys.argv)>2 else Path(sys.executable).parents[1]/'share/kicad/footprints'
    OUT.mkdir(parents=True,exist_ok=True)
    old=pcbnew.FootprintLoad(str(ROOT/'Native_KiCad_v11/PTERODACTYL_v3.8_v11-import-fps.pretty'),'TEENSY41_SIMPLE')
    fp=pcbnew.FootprintLoad(str(LIB),NAME)
    assert fp is not None
    assert coordinates(fp)==coordinates(old)
    assert len(list(fp.Pads()))==48
    for p in fp.Pads():
        assert p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH
        assert mm(p.GetDrillSize().x)==mm(p.GetDrillSize().y)==1.04
        assert mm(p.GetSize().x)==mm(p.GetSize().y)==1.8
    positions=coordinates(fp)
    for y in (-7.62,7.62):
        xs=sorted(x for x,py in positions.values() if py==y)
        assert len(xs)==24
        assert all(abs(x-(-28.067+i*2.54))<1e-6 for i,x in enumerate(xs))
    layers=[g.GetLayer() for g in fp.GraphicalItems()]
    assert pcbnew.F_Fab in layers and pcbnew.F_CrtYd in layers
    zones=list(fp.Zones())
    assert len(zones)==1 and zones[0].GetIsRuleArea()
    assert zones[0].GetDoNotAllowFootprints()
    assert not zones[0].GetDoNotAllowTracks()
    assert not zones[0].GetDoNotAllowZoneFills()
    assert not zones[0].GetDoNotAllowVias()
    results=[]
    for case,position in [('clear',None),('component_outside',(135,90)),('component_inside',(80,60))]:
        board=pcbnew.BOARD()
        placed=pcbnew.FootprintLoad(str(LIB),NAME)
        placed.SetReference('U1');placed.SetPosition(point(80,60));board.Add(placed)
        if position:
            test=pcbnew.FootprintLoad(str(standard/'Resistor_SMD.pretty'),'R_0603_1608Metric')
            assert test is not None
            test.SetReference('R_TEST');test.SetPosition(point(*position));board.Add(test)
        for a,b in [((25,25),(155,25)),((155,25),(155,110)),((155,110),(25,110)),((25,110),(25,25))]:
            edge=pcbnew.PCB_SHAPE();edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetStart(point(*a));edge.SetEnd(point(*b));edge.SetLayer(pcbnew.Edge_Cuts);edge.SetWidth(pcbnew.FromMM(.05));board.Add(edge)
        pcb=OUT/(case+'.kicad_pcb');report=OUT/(case+'-drc.json')
        pcbnew.SaveBoard(str(pcb),board)
        subprocess.run([cli,'pcb','drc','--format','json','--severity-all','--output',str(report),str(pcb)],check=True)
        drc=json.loads(report.read_text())
        types=[v['type'] for v in drc['violations']]
        if case=='component_inside':
            assert 'items_not_allowed' in types,types
        else:
            assert types==[],(case,types)
        results.append({'case':case,'violation_types':types,'expected_rejection':case=='component_inside','result':'pass'})
    subprocess.run([cli,'fp','export','svg','--footprint',NAME,'--layers','F.Cu,F.SilkS,F.Fab,F.CrtYd,Dwgs.User','--output',str(OUT),str(LIB)],check=True)
    svg=OUT/(NAME+'.svg');assert svg.exists()
    svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n',newline='\n')
    report={'kicad_version':pcbnew.GetBuildVersion(),'footprint_sha256':hashlib.sha256((LIB/(NAME+'.kicad_mod')).read_bytes()).hexdigest(),
      'preserved_pad_count':48,'drill_mm':1.04,'pad_size_mm':1.8,'tests':results,
      'scope':'Native geometry, isolated fixture DRC and deliberate keepout intrusion; not circuit, physical fit or retention validation'}
    (OUT/'carrier-check.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print('PASS: 48 pad positions/identifiers preserved; isolated controls clear; intruding component rejected by rule area.')


if __name__=='__main__':main()
