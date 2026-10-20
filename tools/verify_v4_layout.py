"""Read-only native validation of the targeted v4 layout cleanup.

Run with KiCad's Python. Does not regenerate or save the source board.
GPS remains an explicit missing-footprint gate, even when connectivity is clean.
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
OUT = ROOT / 'docs/validation/2026-10-19/layout-review'


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
    assert len(drc['schematic_parity']) == 1 and drc['schematic_parity'][0]['description'].startswith('Missing footprint U5 ')
    board = pcbnew.LoadBoard(str(PCB))
    buses = [bus_order(board, '/I2C_SDA', '18', '5', '4'), bus_order(board, '/I2C_SCL', '19', '4', '5')]
    assert all(v['environment_pad_is_on_host_to_imu_path'] and v['length_mm'] <= 150 for v in buses), buses
    positions = placement.actual_placement(board)
    separations = [{'rule': rule, 'gap_mm': round(min(placement.gap(positions[a], positions[b]) for a in aa for b in bb), 3), 'minimum_mm': minimum}
                   for rule, aa, bb, minimum in placement.RULES]
    assert all(v['gap_mm'] >= v['minimum_mm'] for v in separations), separations
    routing = placement.routing_metrics(positions)
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
    report = {'result': 'pass', 'baseline_review_commit': '46f926a', 'pcb_sha256': hashlib.sha256(PCB.read_bytes()).hexdigest(),
              'physical_drc_violations': 0, 'unconnected_present_footprints': 0, 'missing_footprints': ['U5'],
              'i2c': buses, 'adc_cap_to_carrier_pin_mm': round(cap_gap, 3), 'adc_carrier_target_mm': 5,
              'ground_vias_connected_to_both_inner_planes': len(ground_vias), 'routing': routing, 'separations': separations,
              'scope': 'Current carrier layout only. GPS absent; manufacturer/stackup, fit, retention, ADC accuracy, rise time and interference need further review or hardware measurements.'}
    (OUT/'layout-check.json').write_text(json.dumps(report, indent=2)+'\n', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
