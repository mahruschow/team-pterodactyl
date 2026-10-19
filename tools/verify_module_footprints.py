"""Read generated footprints through KiCad and compare against recorded source CAD.

Run with KiCad's Python (pcbnew required). Writes a portable evidence report.
Does not change hardware design files. Physical fit and electrical behavior need
separate verification. The generator is not imported by this check.
"""
from pathlib import Path
import hashlib
import json
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.pretty'
SOURCE = ROOT / 'docs/reference/step3-cad-geometry.json'
OUT = ROOT / 'docs/validation/2026-10-18/step3-footprints'


def close(a, b):
    assert abs(a-b) < 0.00001, (a, b)


def main():
    data = {b['file']: b for b in json.loads(SOURCE.read_text())['boards']}
    definitions = [
        ('Adafruit_BNO055_2472_Carrier', 'Adafruit-BNO055-Breakout-PCB/Adafruit BNO055.brd', ['JP1','JP2'], 10),
        ('Adafruit_MS8607_4716_Carrier', 'Adafruit-MS8607-PCB/Adafruit MS8607.brd', ['JP2'], 5),
    ]
    report = {'kicad_version': pcbnew.GetBuildVersion(),
              'source_geometry_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'scope': 'Native load and source coordinate/pin ordering, drill and pad-count checks; not physical fit or circuit validation',
              'footprints': []}
    for name, source, headers, count in definitions:
        fp = pcbnew.FootprintLoad(str(LIB), name)
        assert fp is not None, name
        board = data[source]
        by_header = {h['element']: h for h in board['headers']}
        source_pads = [p for h in headers for p in by_header[h]['pads']]
        origin = source_pads[0]
        pads = list(fp.Pads())
        numbered = {p.GetNumber(): p for p in pads if p.GetNumber()}
        holes = [p for p in pads if not p.GetNumber()]
        assert len(numbered) == count and len(pads) == count+4
        assert set(numbered) == {str(i) for i in range(1,count+1)}
        details=[]
        for index, source_pad in enumerate(source_pads,1):
            pad = numbered[str(index)]
            assert pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
            x,y = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
            close(x, source_pad['x']-origin['x'])
            close(y, origin['y']-source_pad['y'])
            close(pcbnew.ToMM(pad.GetDrillSize().x),1.04)
            close(pcbnew.ToMM(pad.GetSize().x),1.8)
            close(pcbnew.ToMM(pad.GetSize().y),1.8)
            details.append({'pad':str(index),'source_net':source_pad['net'],'x_mm':x,'y_mm':y})
        expected_holes=sorted((round(h['pads'][0]['x']-origin['x'],5),round(origin['y']-h['pads'][0]['y'],5))
                              for h in board['headers'] if 'MOUNTINGHOLE' in h['package'])
        actual_holes=[]
        for pad in holes:
            assert pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
            close(pcbnew.ToMM(pad.GetDrillSize().x),2.7)
            actual_holes.append((round(pcbnew.ToMM(pad.GetPosition().x),5),round(pcbnew.ToMM(pad.GetPosition().y),5)))
        assert sorted(actual_holes)==expected_holes
        report['footprints'].append({'name':name,'sha256':hashlib.sha256((LIB/(name+'.kicad_mod')).read_bytes()).hexdigest(),
                                     'electrical_pad_count':count,'mounting_hole_count':len(holes),'pads':details,'result':'pass'})
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'source-coordinate-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: both footprints load in KiCad; all 15 electrical pads and 8 mounting positions match source CAD.')


if __name__ == '__main__':
    main()
