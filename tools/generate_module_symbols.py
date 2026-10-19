"""Generate draft module symbols from the reviewed carrier pad contract.

Run with ordinary Python 3. Does not modify the main schematic or PCB.
SCL is bidirectional to retain the possibility of I2C clock stretching in ERC.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.kicad_sym'


def generate():
    groups = {}
    with (ROOT / 'docs/reference/step3-carrier-pad-map.csv').open(newline='') as source:
        for row in csv.DictReader(source):
            groups.setdefault(row['footprint'], []).append(row)
    # GPS has reviewed logical functions but no approved #5440 physical footprint.
    # Named pin identifiers deliberately avoid claiming an unverified pin order.
    groups['Adafruit_PA1616D_5440_Logical'] = [
        {'pad':p,'function':p} for p in ['VIN','GND','TX','RX','3V3_OUT','EN','VBAT','FIX','PPS']]
    symbols = []
    for footprint, rows in groups.items():
        name = footprint.removesuffix('_Carrier')
        gps = 'PA1616D' in name
        product = '5440' if gps else ('2472' if 'BNO055' in name else '4716')
        assigned = '' if gps else 'Pterodactyl_Modules:'+footprint
        description = ('DRAFT logical GPS interface only; named pin identifiers; exact #5440 carrier geometry pending' if gps else
                       'DRAFT breakout module; VIN input and 3Vo output are separate; physical fit pending')
        top = 15.24 if len(rows) >= 9 else 7.62
        bottom = -top
        lines = [f'  (symbol "{name}"',
                 '    (pin_numbers hide)' if gps else '',
                 '    (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
                 f'    (property "Reference" "U" (at 0 {top+5.08} 0) (effects (font (size 1.27 1.27))))',
                 f'    (property "Value" "{name}" (at 0 {top+2.54} 0) (effects (font (size 1.27 1.27))))',
                 f'    (property "Footprint" "{assigned}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
                 f'    (property "Datasheet" "https://www.adafruit.com/product/{product}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
                 f'    (property "Description" "{description}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
                 f'    (symbol "{name}_0_1" (rectangle (start -12.7 {top}) (end 12.7 {bottom}) (stroke (width 0.254) (type default)) (fill (type background))))',
                 f'    (symbol "{name}_1_1"']
        for index, row in enumerate(rows):
            function = row['function']
            kind = {'VIN':'power_in', 'GND':'power_in', '3Vo':'power_out',
                    'SDA':'bidirectional', 'SCL':'bidirectional', 'INT':'output',
                    '3V3_OUT':'power_out', 'VBAT':'power_in', 'TX':'output', 'FIX':'output', 'PPS':'output'}.get(function, 'input')
            # Keep source order visible; outputs leave to the right.
            right = function in ('3Vo', 'INT', '3V3_OUT', 'TX', 'FIX', 'PPS')
            x, angle = (17.78, 180) if right else (-17.78, 0)
            y = top - 2.54 - index * 2.54
            lines.append(f'      (pin {kind} line (at {x} {y:.2f} {angle}) (length 5.08) (name "{function}" (effects (font (size 1.27 1.27)))) (number "{row["pad"]}" (effects (font (size 1.27 1.27)))))')
        lines += ['    )', '  )']
        symbols.append('\n'.join(lines))
    OUT.write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n' + '\n'.join(symbols) + '\n)\n', encoding='utf-8', newline='\n')
    print(f'Wrote {len(symbols)} draft module symbols.')


if __name__ == '__main__':
    generate()
