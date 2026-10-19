"""Generate draft carrier footprints from the recorded Adafruit CAD geometry.

Run with Python 3 from any directory. Geometry derivatives: CC BY-SA 3.0,
attributed to Adafruit Industries; see Native_KiCad_v11/Pterodactyl_Modules_LICENSE.txt.
This does not edit the schematic or PCB and does not approve physical fit.
"""
from pathlib import Path
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.pretty'
DATA = ROOT / 'docs/reference/step3-cad-geometry.json'
SPECS = [
    ('Adafruit_BNO055_2472_Carrier', 'Adafruit-BNO055-Breakout-PCB/Adafruit BNO055.brd',
     [('JP1', ['VIN', '3Vo', 'GND', 'SDA', 'SCL', 'RST']),
      ('JP2', ['PS0', 'PS1', 'INT', 'ADR'])], 26.67, 20.32),
    ('Adafruit_MS8607_4716_Carrier', 'Adafruit-MS8607-PCB/Adafruit MS8607.brd',
     [('JP2', ['VIN', '3Vo', 'GND', 'SCL', 'SDA'])], 25.4, 17.78),
]


def num(v):
    return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'


def xy(p):
    return f'{num(p[0])} {num(p[1])}'


def generate():
    boards = {b['file']: b for b in json.loads(DATA.read_text())['boards']}
    LIB.mkdir(parents=True, exist_ok=True)
    mapping = []
    for name, source, headers, width, height in SPECS:
        board = boards[source]
        by_header = {h['element']: h for h in board['headers']}
        origin = by_header[headers[0][0]]['pads'][0]
        ox, oy = origin['x'], origin['y']

        def transform(x, y):
            return (float(x) - ox, oy - float(y))

        out = [f'(footprint "{name}"', '  (version 20241229)',
               '  (generator "pterodactyl_module_generator")', '  (layer "F.Cu")',
               f'  (descr "DRAFT header carrier; derived from Adafruit {source}; physical fit and hardware selection pending")',
               '  (tags "module carrier draft Adafruit")', '  (attr through_hole)',
               f'  (fp_text reference "REF**" (at {xy(transform(width/2, height+2))}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
               f'  (fp_text value "{name}" (at {xy(transform(width/2, height+3.5))}) (layer "F.Fab") (effects (font (size 0.65 0.65) (thickness 0.1))))']

        def line(a, b, layer, thickness=0.1):
            out.append(f'  (fp_line (start {xy(a)}) (end {xy(b)}) (stroke (width {thickness}) (type default)) (layer "{layer}"))')

        # Preserve every board layer-20 line/arc on fabrication layer, including
        # the MS8607 internal region. Never turn a module outline into carrier cuts.
        for w in board['outline']:
            x1, y1, x2, y2 = [float(w[k]) for k in ('x1', 'y1', 'x2', 'y2')]
            a, b = transform(x1, y1), transform(x2, y2)
            angle = float(w.get('curve', 0))
            if angle:
                # Arc midpoint in Eagle's Y-up system; transform flips handedness.
                theta = math.radians(angle)
                dx, dy = x2-x1, y2-y1
                cx = (x1+x2)/2 - dy/(2*math.tan(theta/2))
                cy = (y1+y2)/2 + dx/(2*math.tan(theta/2))
                vx, vy = x1-cx, y1-cy
                mid = transform(cx+vx*math.cos(theta/2)-vy*math.sin(theta/2),
                                cy+vx*math.sin(theta/2)+vy*math.cos(theta/2))
                out.append(f'  (fp_arc (start {xy(a)}) (mid {xy(mid)}) (end {xy(b)}) (stroke (width 0.1) (type default)) (layer "F.Fab"))')
            else:
                line(a, b, 'F.Fab')

        # Provisional 1 mm assembly margin. Not an antenna, thermal or magnetic keepout.
        corners = [transform(-1, -1), transform(width+1, -1),
                   transform(width+1, height+1), transform(-1, height+1)]
        for a, b in zip(corners, corners[1:]+corners[:1]):
            line(a, b, 'F.CrtYd', 0.05)

        pad_number = 0
        for header, labels in headers:
            pads = by_header[header]['pads']
            assert len(pads) == len(labels)
            for p, label in zip(pads, labels):
                pad_number += 1
                pos = transform(p['x'], p['y'])
                shape = 'rect' if pad_number == 1 else 'circle'
                out.append(f'  (pad "{pad_number}" thru_hole {shape} (at {xy(pos)}) (size 1.8 1.8) (drill 1.04) (layers "*.Cu" "*.Mask"))')
                # Place labels vertically toward the module interior, on Fab only.
                label_y = pos[1] - 3.1 if p['y'] < height/2 else pos[1] + 3.1
                out.append(f'  (fp_text user "{pad_number}:{label}" (at {num(pos[0])} {num(label_y)} 90) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))')
                mapping.append({'footprint': name, 'pad': pad_number, 'function': label,
                                'source_header': header, 'source_pad': p['pad'], 'source_net': p['net'],
                                'x_mm': num(pos[0]), 'y_mm': num(pos[1])})

        # Carrier fastener clearance proposal. Module CAD holes are 2.5 mm.
        # Drill sizing and the 3 mm radius screw-head envelope require hardware review.
        for h in board['headers']:
            if 'MOUNTINGHOLE' not in h['package']:
                continue
            p = h['pads'][0]
            pos = transform(p['x'], p['y'])
            out.append(f'  (pad "" np_thru_hole circle (at {xy(pos)}) (size 2.7 2.7) (drill 2.7) (layers "*.Cu" "*.Mask"))')
            out.append(f'  (fp_circle (center {xy(pos)}) (end {xy((pos[0]+3, pos[1]))}) (stroke (width 0.1) (type default)) (fill none) (layer "Dwgs.User"))')

        # Visible pin-one locator kept clear of the copper pad.
        for a,b in [((-0.8, 1.4),(0.8,1.4)), ((0.8,1.4),(0,2.1)), ((0,2.1),(-0.8,1.4))]:
            line(a,b,'F.SilkS',0.15)
        note_y = (15.9, 14.1) if 'MS8607' in name else (11.0, 9.3)
        for text, y in zip(('DRAFT', 'NO PARTS UNDER MODULE'), note_y):
            out.append(f'  (fp_text user "{text}" (at {xy(transform(width/2, y))}) (layer "Dwgs.User") (effects (font (size 0.65 0.65) (thickness 0.1))))')
        out.append(')')
        (LIB / f'{name}.kicad_mod').write_text('\n'.join(out)+'\n', encoding='utf-8', newline='\n')

    with (ROOT/'docs/reference/step3-carrier-pad-map.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(mapping[0]))
        writer.writeheader()
        writer.writerows(mapping)
    print(f'Generated {len(SPECS)} draft footprints and {len(mapping)} pad mappings.')


if __name__ == '__main__':
    generate()
