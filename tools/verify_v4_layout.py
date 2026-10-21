"""Read-only native validation of the targeted v4 layout cleanup.

Run with KiCad's Python. Does not regenerate or save the source board.
All schematic footprints, including GPS, must be present and connected.
"""
from pathlib import Path
import collections
import hashlib
import json
import math
import subprocess
import sys
import pcbnew
import check_v4_pcb as placement

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else ROOT / 'work/v4-layout-validation'


def key(layer, point):
    return layer, point.x, point.y


def bus_order(board, net, host_pin, env_pin, imu_pin):
    """Check actual copper graph, including PTH layer changes at module pads.

    This board uses straight segments with junctions at endpoints. DRC separately
    checks physical connectivity. Removing U4's pad must separate U1 from U3.
    """
    graph = collections.defaultdict(set)
    def join(a, b):
        graph[a].add(b)
        graph[b].add(a)
    length = 0
    for t in board.GetTracks():
        if t.GetNetname() != net:
            continue
        if t.GetClass() == 'PCB_VIA':
            join(key(pcbnew.F_Cu, t.GetPosition()), key(pcbnew.B_Cu, t.GetPosition()))
        else:
            join(key(t.GetLayer(), t.GetStart()), key(t.GetLayer(), t.GetEnd()))
            length += pcbnew.ToMM(t.GetLength())
    pads = {}
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == net:
                pads[f.GetReference(), p.GetNumber()] = p.GetPosition()
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    join(key(pcbnew.F_Cu, p.GetPosition()), key(pcbnew.B_Cu, p.GetPosition()))
    start = key(pcbnew.F_Cu, pads['U1', host_pin])
    end = key(pcbnew.F_Cu, pads['U3', imu_pin])
    cut = {key(layer, pads['U4', env_pin]) for layer in (pcbnew.F_Cu, pcbnew.B_Cu)}
    def reaches(blocked):
        seen = set(blocked)
        pending = [start]
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            if node == end:
                return True
            seen.add(node)
            pending.extend(graph[node] - seen)
        return False
    return {'net': net, 'length_mm': round(length, 3),
            'host_to_imu_connected': reaches(set()),
            'environment_pad_is_on_host_to_imu_path': reaches(set()) and not reaches(cut)}


def main():
    cli = sys.argv[1] if len(sys.argv) > 1 else 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([cli, 'pcb', 'drc', '--format', 'json', '--severity-all',
                    '--schematic-parity', '--refill-zones', '--output', str(OUT/'drc.json'), str(PCB)], check=True)
    drc = json.loads((OUT/'drc.json').read_text())
    assert not drc['violations'], drc['violations']
    assert not drc['unconnected_items'], drc['unconnected_items']
    assert not drc['schematic_parity'], drc['schematic_parity']
    board = pcbnew.LoadBoard(str(PCB))
    gps = next(f for f in board.GetFootprints() if f.GetReference() == 'U5')
    assert str(gps.GetFPID().GetLibItemName()) == 'Adafruit_GPS_5440_Carrier'
    pins = {p.GetNumber(): p for p in gps.Pads() if p.GetNumber()}
    names = ('PPS', 'VIN', 'GND', 'RX', 'TX', 'FIX', 'VBAT', 'EN', '3V3_OUT')
    assert set(pins) == set(names)
    nets = {'VIN': '/SENSOR_3V3', 'GND': 'GND', 'RX': '/GPS_RXD', 'TX': '/GPS_TXD'}
    for i, name in enumerate(names):
        p = pins[name]
        assert abs(pcbnew.ToMM(p.GetPosition().x) - 163.036) < 1e-5
        assert abs(pcbnew.ToMM(p.GetPosition().y) - (87.867 - 2.54*i)) < 1e-5
        assert p.GetNetname() == nets.get(name, 'unconnected-(U5-Pad%s)' % name)
        assert abs(pcbnew.ToMM(p.GetDrillSize().x) - 1.04) < 1e-5
    holes = [p for p in gps.Pads() if not p.GetNumber()]
    assert len(holes) == 2
    assert sorted((round(pcbnew.ToMM(p.GetPosition().x), 3), round(pcbnew.ToMM(p.GetPosition().y), 3)) for p in holes) == [(192.754, 67.547), (192.754, 87.867)]
    assert all(p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH and abs(pcbnew.ToMM(p.GetDrillSize().x) - 2.7) < 1e-5 for p in holes)
    buses = [bus_order(board, '/I2C_SDA', '18', '5', '4'), bus_order(board, '/I2C_SCL', '19', '4', '5')]
    assert all(v['environment_pad_is_on_host_to_imu_path'] and v['length_mm'] <= 150 for v in buses), buses
    positions = placement.actual_placement(board)
    separations = [{'rule': rule, 'gap_mm': round(min(placement.gap(positions[a], positions[b]) for a in aa for b in bb), 3), 'minimum_mm': minimum}
                   for rule, aa, bb, minimum in placement.RULES]
    assert all(v['gap_mm'] >= v['minimum_mm'] for v in separations), separations
    routing = placement.routing_metrics(positions, board)
    assert not routing['thin_power_nets'] and not routing['inner_plane_tracks'] and not routing['tracks_in_envelopes']
    pads = {(f.GetReference(), p.GetNumber()): (p.GetPosition().x, p.GetPosition().y) for f in board.GetFootprints() for p in f.Pads()}
    cap_gap = math.dist(pads['C2', '1'], pads['U1', '26']) / 1e6
    # Carrier-layout target, not a claim about the Teensy's internal ADC route.
    assert cap_gap <= 5, cap_gap
    planes = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.GetLayer() in (pcbnew.In1_Cu, pcbnew.In2_Cu)]
    assert {z.GetLayer() for z in planes} == {pcbnew.In1_Cu, pcbnew.In2_Cu}
    # Keep the owning track container alive while accessing SWIG item wrappers.
    tracks = board.GetTracks()
    ground_vias = [v for v in tracks if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND']
    assert len(ground_vias) >= 3
    assert all(z.GetFilledPolysList(z.GetLayer()).Contains(v.GetPosition()) for z in planes for v in ground_vias)
    report = {'result': 'pass', 'baseline_review_commit': 'e2664ad', 'pcb_sha256': hashlib.sha256(PCB.read_bytes()).hexdigest(),
              'physical_drc_violations': 0, 'unconnected_present_footprints': 0, 'missing_footprints': [],
              'i2c': buses, 'adc_cap_to_carrier_pin_mm': round(cap_gap, 3), 'adc_carrier_target_mm': 5,
              'ground_vias_connected_to_both_inner_planes': len(ground_vias), 'routing': routing, 'separations': separations,
              'scope': 'All 51 footprints present, including user-visually-accepted GPS carrier. Manufacturer/stackup, physical fit, holder clearance, retention, ADC accuracy, rise time and interference still need review or hardware measurements.'}
    (OUT/'layout-check.json').write_text(json.dumps(report, indent=2)+'\n', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
