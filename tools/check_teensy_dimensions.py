"""Read Teensy geometry with KiCad Python; preserves the main PCB and footprint.
Drawing dimensions are manually transcribed from the user-supplied PNG.
"""
from pathlib import Path
from collections import Counter
import hashlib,json
import pcbnew
r=Path(__file__).resolve().parents[1]
src=r/'docs/reference/dimensions_teensy41.png'
lib=r/'Native_KiCad_v11/PTERODACTYL_v3.8_v11-import-fps.pretty'
f=lib/'TEENSY41_SIMPLE.kicad_mod'
fp=pcbnew.FootprintLoad(str(lib),'TEENSY41_SIMPLE')
def mm(x):return round(pcbnew.ToMM(x),6)
def pads(fp):return sorted([{'number':p.GetNumber(),'x_mm':mm(p.GetPosition().x),'y_mm':mm(p.GetPosition().y),'drill_mm':mm(p.GetDrillSize().x),'size_mm':[mm(p.GetSize().x),mm(p.GetSize().y)]} for p in fp.Pads()],key=lambda p:(p['y_mm'],p['x_mm']))
ps=pads(fp)
rows={y:sorted(p['x_mm'] for p in ps if p['y_mm']==y) for y in sorted(set(p['y_mm'] for p in ps))}
assert len(ps)==48 and len(rows)==2
for y,x in rows.items():
    assert len(x)==24
    assert all(abs((b-a)-2.54)<1e-6 for a,b in zip(x,x[1:]))
assert abs(max(rows)-min(rows)-15.24)<1e-6
lines=[]
layers=Counter()
for g in fp.GraphicalItems():
    layers[g.GetLayerName()]+=1
    if isinstance(g,pcbnew.PCB_SHAPE):
        a,b=g.GetStart(),g.GetEnd()
        lines.append({'layer':g.GetLayerName(),'start':[mm(a.x),mm(a.y)],'end':[mm(b.x),mm(b.y)]})
board=pcbnew.LoadBoard(str(r/'Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pcb'))
matches=[]
for bfp in board.GetFootprints():
    if 'TEENSY' in str(bfp.GetFPID().GetLibItemName()).upper():
        ref=bfp.GetReference()
        bfp.SetOrientationDegrees(0)
        bfp.SetPosition(pcbnew.VECTOR2I(0,0))
        matches.append({'reference':ref,'library_item':str(bfp.GetFPID().GetLibItemName()),'pads_match_library':pads(bfp)==ps,'pads':pads(bfp)})
report={'review_date':'2026-10-18','kicad_version':pcbnew.GetBuildVersion(),
 'source':{'file':'docs/reference/dimensions_teensy41.png','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'provenance':'User-supplied PNG after PJRC browser access was blocked; no network retrieval','upstream_reference':'https://www.pjrc.com/teensy/dimensions_teensy41.png'},
 'footprint_sha256_normalized_lf':hashlib.sha256(f.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
 'drawing_manual_transcription_mm':{'board_length':60.96,'board_width_nominal':17.78,'board_width_tolerance':0.6,'board_thickness':1.57,'header_pitch':2.54,'header_row_separation':15.24,'first_header_x_from_board_left':1.27,'usb_overhang_side_view':0.7,'usb_top_height_from_board_surface':3.07},
 'native_pads':ps,'native_graphics_layers':dict(layers),'native_shapes':lines,'board_instances':matches,
 'scope':'Nominal edge header grid and board outline comparison; drawing alone does not approve header drills, electrical pin labels, assembled height, connector access or physical fit'}
out=r/'docs/validation/2026-10-18/teensy-dimension-check.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: 48 edge-header positions and pitch/row spacing; full comparison and open fit issues in docs/TEENSY_MECHANICAL_REVIEW.md.')
