"""Check native symbol loading and the electrical symbol/footprint contract.

Run with KiCad's Python, optionally passing the path to kicad-cli.exe.
Independent expected pin functions are deliberately not imported from generator.
Native exports demonstrate parsing, not ERC or mechanical approval.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.kicad_sym'
OUT = ROOT / 'docs/validation/2026-10-18/step3-symbols'
EXPECTED = {
    'Adafruit_BNO055_2472': ['VIN','3Vo','GND','SDA','SCL','RST','PS0','PS1','INT','ADR'],
    'Adafruit_MS8607_4716': ['VIN','3Vo','GND','SCL','SDA'],
    'Adafruit_PA1616D_5440_Logical': ['VIN','GND','TX','RX','3V3_OUT','EN','VBAT','FIX','PPS'],
}


def parse(source):
    tokens = iter(re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', source))
    def node(token):
        if token == '(':
            children = []
            for token in tokens:
                if token == ')':
                    return children
                children.append(node(token))
            raise ValueError('Unclosed expression')
        return json.loads(token) if token.startswith('"') else token
    result = node(next(tokens))
    assert next(tokens, None) is None
    return result


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def main():
    cli = sys.argv[1] if len(sys.argv) > 1 else str(Path(sys.executable).with_name('kicad-cli.exe'))
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([cli, 'sym', 'export', 'svg', '--output', str(OUT), str(LIB)], check=True)
    # KiCad SVG trailing spaces are cosmetic; keep repository diff checks clean.
    for svg in OUT.glob('*.svg'):
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n', newline='\n')
    source = ROOT / 'docs/reference/step3-carrier-pad-map.csv'
    with source.open(newline='') as stream:
        mapping = list(csv.DictReader(stream))
    symbols = {s[1]: s for s in children(parse(LIB.read_text()), 'symbol')}
    assert set(symbols) == set(EXPECTED)
    checks = []
    for name, functions in EXPECTED.items():
        symbol = symbols[name]
        pins = [p for unit in children(symbol, 'symbol') for p in children(unit, 'pin')]
        actual = {children(p, 'number')[0][1]: (children(p, 'name')[0][1], p[1]) for p in pins}
        gps = 'PA1616D' in name
        expected = {f:f for f in functions} if gps else {str(i): f for i, f in enumerate(functions, 1)}
        assert len(pins) == len(expected)
        assert {n:f for n,(f,kind) in actual.items()} == expected
        for number, (function, kind) in actual.items():
            required = {'VIN':'power_in','GND':'power_in','3Vo':'power_out',
                        'SDA':'bidirectional','SCL':'bidirectional','INT':'output',
                        '3V3_OUT':'power_out','VBAT':'power_in','TX':'output','FIX':'output','PPS':'output'}.get(function, 'input')
            assert kind == required, (name, number, kind)
        footprint = name + '_Carrier'
        properties = {p[1]:p[2] for p in children(symbol, 'property')}
        if gps:
            assert properties['Footprint'] == ''
            assert (OUT / (name+'_unit1.svg')).is_file()
            checks.append({'symbol':name,'footprint':None,'pins':actual,
                           'scope':'Logical interface only; no verified physical pad order or footprint','result':'pass'})
            continue
        assert properties['Footprint'] == 'Pterodactyl_Modules:' + footprint
        assert {row['pad']:row['function'] for row in mapping if row['footprint'] == footprint} == expected
        fp_file = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.pretty' / (footprint+'.kicad_mod')
        fp = pcbnew.FootprintLoad(str(fp_file.parent), footprint)
        assert fp is not None
        assert sorted(p.GetNumber() for p in fp.Pads() if p.GetNumber()) == sorted(expected)
        assert (OUT / (name+'_unit1.svg')).is_file()
        checks.append({'symbol':name,'footprint':footprint,'footprint_sha256':hashlib.sha256(fp_file.read_bytes()).hexdigest(),
                       'pins':actual,'result':'pass'})
    report = {'kicad_version':pcbnew.GetBuildVersion(), 'symbol_library_sha256':hashlib.sha256(LIB.read_bytes()).hexdigest(),
              'scope':'Native SVG export and symbol pin/function/type/default-footprint contract; not main schematic ERC or physical fit',
              'symbols':checks}
    (OUT/'symbol-contract-check.json').write_text(json.dumps(report,indent=2)+'\n', newline='\n')
    print('PASS: 15 sensor pins match CSV/native footprint pad numbers; 9 GPS logical pins pass, with footprint intentionally unassigned.')


if __name__ == '__main__':
    main()
