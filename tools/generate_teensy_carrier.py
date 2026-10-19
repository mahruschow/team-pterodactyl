"""Generate a draft Teensy carrier from the reviewed local PJRC drawing/grid.

Ordinary Python 3. Pin identifiers/positions are preserved from recorded native
readback for later schematic compatibility; no main design files are edited.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
NAME = 'Teensy41_SSW_Carrier'
LIB = ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'


def generate():
    data = json.loads((ROOT/'docs/validation/2026-10-18/teensy-dimension-check.json').read_text())
    pads = data['native_pads']
    assert len(pads) == 48
    out = [f'(footprint "{NAME}" (version 20241229) (generator "pterodactyl_module_generator")',
           ' (layer "F.Cu") (attr through_hole)',
           ' (descr "DRAFT Teensy 4.1 side-header carrier; two Samtec SSW-124-01-L-S sockets; PJRC drawing supplied locally; retention and physical fit pending")',
           ' (tags "Teensy 4.1 carrier draft SSW")']
    def text(kind, value, x, y, layer, size=1, rotation=0):
        out.append(f' (fp_text {kind} "{value}" (at {x} {y} {rotation}) (layer "{layer}") (effects (font (size {size} {size}) (thickness 0.12))))')
    def rect(x1,y1,x2,y2,layer,width=.1):
        out.append(f' (fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))')
    def line(x1,y1,x2,y2,layer,width=.15):
        out.append(f' (fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type default)) (layer "{layer}"))')
    text('reference','REF**',1.143,-12,'F.SilkS')
    text('value',NAME,1.143,12,'F.Fab')
    # Nominal module outline. No carrier cuts are created.
    rect(-29.337,-8.89,31.623,8.89,'F.Fab')
    # Socket bodies: 24*2.54+0.51 long and 2.41 wide, centered on rows.
    for y in (-7.62,7.62):
        rect(-29.592,y-1.205,31.878,y+1.205,'F.Fab')
    # USB planar reference derived from 0.7 overhang, 5.0 body length and 7.5 width.
    rect(-30.037,-3.75,-25.037,3.75,'F.Fab')
    text('user','USB',-27.537,0,'F.Fab',.75,90)
    # Courtyard includes socket ends, USB body and conservative board-width allowance.
    rect(-31.05,-10.5,32.9,10.5,'F.CrtYd',.05)
    text('user','DRAFT / SIDE HEADERS ONLY',1.143,-2,'Dwgs.User',.9)
    text('user','NO TOP-SIDE PARTS UNDER MODULE',1.143,0,'Dwgs.User',.8)
    text('user','VERIFY USB / SD ACCESS AND RETENTION',1.143,2,'Dwgs.User',.75)
    # Drawing-layer access guides are proposals, not guaranteed cable/card dimensions.
    rect(-45.037,-6,-30.037,6,'Dwgs.User')
    text('user','USB ACCESS',-37.537,0,'Dwgs.User',.8,90)
    rect(31.623,-8,51.623,8,'Dwgs.User')
    text('user','SD ACCESS',41.623,0,'Dwgs.User',.8,90)
    for p in pads:
        number,x,y = p['number'],p['x_mm'],p['y_mm']
        shape = 'rect' if number=='VIN' else 'circle'
        out.append(f' (pad "{number}" thru_hole {shape} (at {x} {y}) (size 1.8 1.8) (drill 1.04) (layers "*.Cu" "*.Mask"))')
        text('user',number,x,y+(-2.2 if y>0 else 2.2),'F.Fab',.55,90)
    for a,b in [((-28.867,-9.1),(-27.267,-9.1)),((-27.267,-9.1),(-28.067,-9.8)),((-28.067,-9.8),(-28.867,-9.1))]:
        line(*a,*b,'F.SilkS')
    # Blocks other front-side components, but retains routing/ground-plane freedom.
    # Component rule areas are excluded for their owning footprint by KiCad.
    out.append(''' (zone (net 0) (net_name "") (layer "F.Cu") (hatch edge 0.5)
      (connect_pads (clearance 0)) (min_thickness 0.25)
      (keepout (tracks allowed) (vias allowed) (pads allowed) (copperpour allowed) (footprints not_allowed))
      (fill (thermal_gap 0.3) (thermal_bridge_width 0.3))
      (polygon (pts (xy -30.037 -9.49) (xy 31.878 -9.49) (xy 31.878 9.49) (xy -30.037 9.49))))''')
    out.append(')')
    (LIB/(NAME+'.kicad_mod')).write_text('\n'.join(out)+'\n',encoding='utf-8',newline='\n')
    print('Generated draft Teensy carrier; 48 preserved pad identifiers/positions, 1.04 mm drills, courtyard and component rule area.')


if __name__=='__main__':
    generate()
