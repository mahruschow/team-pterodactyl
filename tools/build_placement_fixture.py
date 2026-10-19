"""Step 4 draft placement fixture and separation checks.

Run with KiCad Python. The optional first argument selects kicad-cli.
Copies only the legacy outline and mounting-hole positions into a new
isolated fixture; never writes the main project PCB. Placeholders for the
GPS envelope and power section are planning boxes, not footprints.
"""
from pathlib import Path
import hashlib,json,math,subprocess,sys
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pcb'
LIB=ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'
OUT=ROOT/'docs/validation/2026-10-19/step4-placement'
HOLE_KEEPOUT_R=4.0  # M3 head/washer allowance around each legacy hole centre

# Courtyard top-left targets in board-local mm (origin = outline top-left).
MODULES=[
    ('U_IMU','Adafruit_BNO055_2472_Carrier',0,(1.0,8.0)),
    ('U_ENV','Adafruit_MS8607_4716_Carrier',0,(32.0,3.0)),
    ('U_MCU','Teensy41_SSW_Carrier',180,(0.5,65.46)),
]
# Planning boxes: (reference, label, x, y, w, h) in board-local mm.
BOXES=[
    ('Z_GPS','GPS #5440 envelope 34.2x25.3 +1 mm, UNVERIFIED',60.5,8.0,36.2,27.3),
    ('Z_PWR','Power entry/regulation/monitor region',81.0,58.0,15.8,30.0),
]
# (rule, a, b, minimum edge-to-edge mm, reason)
RULES=[
    ('P1','U_IMU','Z_PWR',40.0,'magnetometer vs regulator/inductor and battery current'),
    ('P2','U_IMU','U_MCU',25.0,'magnetometer vs Teensy/SD supply current'),
    ('P3','Z_GPS','U_MCU',20.0,'GPS vs processor/SD digital activity'),
    ('P4','Z_GPS','Z_PWR',20.0,'GPS vs switching regulator noise'),
    ('P5','U_ENV','U_MCU',25.0,'pressure/temperature sensor vs Teensy heat'),
    ('P6','U_ENV','Z_PWR',25.0,'pressure/temperature sensor vs regulator heat'),
    ('P7','U_IMU','Z_GPS',20.0,'magnetometer vs GPS current and coin-cell holder'),
]


def mm(n):return round(pcbnew.ToMM(n),3)
def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
def rect_gap(a,b):
    dx=max(b[0]-a[2],a[0]-b[2],0);dy=max(b[1]-a[3],a[1]-b[3],0)
    return round(math.hypot(dx,dy),2)
def point_rect(p,r):
    dx=max(r[0]-p[0],p[0]-r[2],0);dy=max(r[1]-p[1],p[1]-r[3],0)
    return round(math.hypot(dx,dy),2)


def courtyard(fp,origin):
    fp.BuildCourtyardCaches()
    b=fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    return (mm(b.GetLeft())-origin[0],mm(b.GetTop())-origin[1],mm(b.GetRight())-origin[0],mm(b.GetBottom())-origin[1])


def rect(parent,layer,x0,y0,x1,y1,width=.05):
    s=pcbnew.PCB_SHAPE(parent);s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(point(x0,y0));s.SetEnd(point(x1,y1));s.SetLayer(layer);s.SetWidth(pcbnew.FromMM(width))
    return s


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else str(Path(sys.executable).with_name('kicad-cli.exe'))
    OUT.mkdir(parents=True,exist_ok=True)
    legacy=pcbnew.LoadBoard(str(MAIN))
    edge=legacy.GetBoardEdgesBoundingBox()
    origin=(mm(edge.GetLeft()),mm(edge.GetTop()))
    size=(mm(edge.GetWidth()),mm(edge.GetHeight()))
    board=pcbnew.BOARD();board.SetCopperLayerCount(legacy.GetCopperLayerCount())
    for d in legacy.GetDrawings():
        if d.GetLayer()==pcbnew.Edge_Cuts:board.Add(d.Duplicate())
    holes=[]
    for fp in legacy.GetFootprints():
        if str(fp.GetFPID().GetLibItemName())=='HOLE':
            c=(mm(fp.GetPosition().x),mm(fp.GetPosition().y));holes.append((round(c[0]-origin[0],3),round(c[1]-origin[1],3)))
            ring=pcbnew.PCB_SHAPE(board);ring.SetShape(pcbnew.SHAPE_T_CIRCLE);ring.SetCenter(point(*c))
            ring.SetEnd(point(c[0]+HOLE_KEEPOUT_R,c[1]));ring.SetLayer(pcbnew.Dwgs_User);ring.SetWidth(pcbnew.FromMM(.1));board.Add(ring)
            h=pcbnew.FOOTPRINT(board);h.SetReference(fp.GetReference());h.SetPosition(point(*c))
            pad=pcbnew.PAD(h);pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH);pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetDrillSize(fp.Pads()[0].GetDrillSize());pad.SetSize(fp.Pads()[0].GetDrillSize());pad.SetLayerSet(pad.UnplatedHoleMask())
            pad.SetPosition(point(*c));h.Add(pad);h.Reference().SetVisible(False);h.Value().SetVisible(False);board.Add(h)
    assert len(holes)==4
    extents={}
    for ref,name,rot,(tx,ty) in MODULES:
        fp=pcbnew.FootprintLoad(str(LIB),name);assert fp is not None,name
        fp.SetReference(ref);fp.SetOrientationDegrees(rot);fp.SetPosition(point(*origin));board.Add(fp)
        cy=courtyard(fp,origin)
        fp.SetPosition(point(origin[0]+tx-cy[0],origin[1]+ty-cy[1]))
        extents[ref]=courtyard(fp,origin)
    for ref,label,x,y,w,h in BOXES:
        fp=pcbnew.FOOTPRINT(board);fp.SetReference(ref);fp.SetValue(label)
        fp.SetPosition(point(origin[0]+x+w/2,origin[1]+y+h/2))
        for layer in (pcbnew.F_CrtYd,pcbnew.F_Fab):
            fp.Add(rect(fp,layer,origin[0]+x,origin[1]+y,origin[0]+x+w,origin[1]+y+h))
        text=pcbnew.VECTOR2I(pcbnew.FromMM(1),pcbnew.FromMM(1))
        fp.Reference().SetLayer(pcbnew.F_Fab);fp.Reference().SetTextSize(text)
        fp.Reference().SetPosition(point(origin[0]+x+w/2,origin[1]+y+2))
        fp.Value().SetLayer(pcbnew.F_Fab);fp.Value().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
        if w<h:fp.Value().SetTextAngleDegrees(90)
        board.Add(fp);extents[ref]=(round(x,3),round(y,3),round(x+w,3),round(y+h,3))
    teensy=[f for f in board.GetFootprints() if f.GetReference()=='U_MCU'][0]
    allowances=[]
    for g in teensy.GraphicalItems():
        if g.GetLayer()==pcbnew.Dwgs_User and g.GetClass()=='PCB_SHAPE':
            b=g.GetBoundingBox();allowances.append((mm(b.GetLeft())-origin[0],mm(b.GetTop())-origin[1],mm(b.GetRight())-origin[0],mm(b.GetBottom())-origin[1]))
    checks=[]
    for ref,e in extents.items():
        margin=round(min(e[0],e[1],size[0]-e[2],size[1]-e[3]),2)
        hole=min(point_rect(c,e) for c in holes)
        checks.append({'rule':'E1','item':ref,'board_edge_margin_mm':margin,'minimum':0.5,'pass':margin>=0.5})
        checks.append({'rule':'E2','item':ref,'hole_centre_distance_mm':hole,'minimum':HOLE_KEEPOUT_R,'pass':hole>=HOLE_KEEPOUT_R})
    for rule,a,b,minimum,reason in RULES:
        gap=rect_gap(extents[a],extents[b])
        checks.append({'rule':rule,'a':a,'b':b,'edge_gap_mm':gap,'minimum':minimum,'reason':reason,'pass':gap>=minimum})
    pcb=OUT/'placement-fixture.kicad_pcb';report=OUT/'placement-fixture-drc.json'
    pcbnew.SaveBoard(str(pcb),board)
    subprocess.run([cli,'pcb','drc','--format','json','--severity-all','--output',str(report),str(pcb)],check=True)
    drc=json.loads(report.read_text())
    types=sorted({v['type'] for v in drc['violations']})
    subprocess.run([cli,'pcb','export','svg','--layers','Edge.Cuts,F.Cu,F.Fab,F.Courtyard,User.Drawings','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(OUT/'placement-fixture.svg'),str(pcb)],check=True)
    svg=OUT/'placement-fixture.svg'
    svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n',newline='\n')
    result={'kicad_version':pcbnew.GetBuildVersion(),
      'source_outline_sha256':hashlib.sha256(MAIN.read_bytes()).hexdigest(),
      'board_local_origin_mm':origin,'board_size_mm':size,'hole_centres_local_mm':holes,
      'courtyard_extents_local_mm':extents,'teensy_drawing_allowances_local_mm':allowances,
      'checks':checks,'drc_violation_types':types,'drc_unconnected':len(drc.get('unconnected_items',[])),
      'scope':'Draft placement envelopes and planning separations on the legacy outline. Not a layout, circuit, enclosure or interference validation.'}
    (OUT/'placement-check.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    failed=[c for c in checks if not c['pass']]
    assert not failed,failed
    assert types==[],types
    print('PASS: %d placement checks; fixture DRC clean.'%len(checks))
    for c in checks:print(' ',c)
    print('  allowances',allowances)


if __name__=='__main__':main()
