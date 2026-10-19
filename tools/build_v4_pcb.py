"""Create the draft v4 PCB from the v4 schematic netlist and the Step 4 floor plan.

Run with KiCad Python; optional first argument selects kicad-cli. Writes
Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb (placement + ground planes, no tracks).
Overwrites that board, so only use it before routing or hand edits begin.

U2 (regulator) and U5 (GPS) have no verified footprints: they are drawn as
labelled keep-out envelopes and their pads are absent from the board.
"""
from pathlib import Path
import json,subprocess,sys,tempfile,xml.etree.ElementTree as ET
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
PRJ=ROOT/'Native_KiCad_v4'
SCH=PRJ/'PTERODACTYL_v4.kicad_sch'
PCB=PRJ/'PTERODACTYL_v4.kicad_pcb'
LEGACY=ROOT/'Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pcb'
STD=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
LOCAL={'Pterodactyl_Modules':ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'}

# Courtyard (or body) top-left in board-local mm, rotation degrees.
# Module, GPS and power-region positions follow PLACEMENT_AND_INTERFERENCE.md.
PLACE={
    'U3':(1.0,8.0,0),'U4':(32.0,3.0,0),'U1':(0.5,65.46,180),
    'C6':(1.0,31.0,0),'C7':(9.5,31.0,0),'C8':(32.0,23.5,0),'C9':(40.0,23.5,0),
    'C10':(61.0,36.5,0),'C11':(69.0,36.5,0),'FB1':(32.0,28.5,0),'C5':(45.5,29.0,0),
    'D2':(1.0,37.0,0),'D3':(8.5,37.0,0),'D4':(16.0,37.0,0),'D5':(23.5,37.0,0),
    'R4':(1.0,45.0,0),'R5':(12.0,45.0,0),'R6':(1.0,48.6,0),'R7':(12.0,48.6,0),
    'SW2':(24.0,45.0,0),'SW1':(36.0,45.0,0),'J3':(48.0,45.0,0),'J4':(35.0,54.0,90),
    'J1':(90.0,56.0,90),'F1':(81.5,56.0,0),'Q1':(81.5,60.5,0),'D1':(66.0,56.0,0),'R1':(66.0,59.5,0),
    'J2':(90.0,66.0,90),'C1':(82.0,66.0,0),'R2':(66.0,63.5,0),'R3':(66.0,66.8,0),'C2':(82.0,74.0,0),
    'C3':(66.0,84.5,0),'C4':(73.2,86.0,0),
}
for i in range(10):PLACE['TP%d'%(i+1)]=(1.0+i*4.2,60.0,0)
ENVELOPES={  # reference: (x, y, w, h, label)
    'U5':(60.5,8.0,36.2,27.3,'U5 GPS #5440 envelope 34.2x25.3 +1 mm - footprint pending M01'),
    'U2':(80.5,78.0,9.6,13.4,'U2 Pololu S9V11F5 7.6x11.4 +1 mm - footprint pending pinout check'),
}
EDGE_MARGIN=0.5
HOLE_KEEPOUT=4.0


def mm(v):return round(pcbnew.ToMM(v),3)
def pt(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))


def box(fp):
    fp.BuildCourtyardCaches()
    c=fp.GetCourtyard(pcbnew.F_CrtYd)
    b=c.BBox() if c.OutlineCount() else fp.GetBoundingBox(False)
    return [mm(b.GetLeft()),mm(b.GetTop()),mm(b.GetRight()),mm(b.GetBottom())]


def netlist(cli):
    out=Path(tempfile.mkdtemp())/'v4.xml'
    subprocess.run([cli,'sch','export','netlist','--format','kicadxml','--output',str(out),str(SCH)],check=True,capture_output=True)
    return ET.parse(out).getroot()


def rect(board,layer,x0,y0,x1,y1,width=0.1):
    s=pcbnew.PCB_SHAPE(board);s.SetShape(pcbnew.SHAPE_T_RECT);s.SetStart(pt(x0,y0));s.SetEnd(pt(x1,y1))
    s.SetLayer(layer);s.SetWidth(pcbnew.FromMM(width));board.Add(s)


def text(board,layer,x,y,body,size=1.0):
    t=pcbnew.PCB_TEXT(board);t.SetText(body);t.SetPosition(pt(x,y));t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size),pcbnew.FromMM(size)));board.Add(t)


def outline_zone(board,layer,net,origin,size):
    z=pcbnew.ZONE(board);z.SetLayer(layer);z.SetNet(net)
    poly=z.Outline();poly.NewOutline()
    for x,y in [(0,0),(size[0],0),(size[0],size[1]),(0,size[1])]:poly.Append(pcbnew.FromMM(origin[0]+x),pcbnew.FromMM(origin[1]+y))
    z.SetMinThickness(pcbnew.FromMM(0.25));z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL);board.Add(z)


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else str(Path(sys.executable).with_name('kicad-cli.exe'))
    root=netlist(cli)
    legacy=pcbnew.LoadBoard(str(LEGACY))
    e=legacy.GetBoardEdgesBoundingBox();origin=(mm(e.GetLeft()),mm(e.GetTop()));size=(mm(e.GetWidth()),mm(e.GetHeight()))
    board=pcbnew.CreateEmptyBoard() if hasattr(pcbnew,'CreateEmptyBoard') else pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    for d in legacy.GetDrawings():
        if d.GetLayer()==pcbnew.Edge_Cuts:board.Add(d.Duplicate())
    holes=[(mm(f.GetPosition().x)-origin[0],mm(f.GetPosition().y)-origin[1]) for f in legacy.GetFootprints()
           if str(f.GetFPID().GetLibItemName())=='HOLE']
    holes.sort(key=lambda h:(h[1],h[0]))
    for i,(x,y) in enumerate(holes):PLACE['H%d'%(i+1)]=('centre',x,y)
    nets={}
    for n in root.iter('net'):
        ni=pcbnew.NETINFO_ITEM(board,n.get('name'));board.Add(ni);nets[n.get('name')]=ni
    pad_net={(x.get('ref'),x.get('pin')):n.get('name') for n in root.iter('net') for x in n.iter('node')}
    placed={};missing=[]
    for c in root.iter('comp'):
        ref=c.get('ref');fpid=c.findtext('footprint') or ''
        if not fpid:missing.append(ref);continue
        lib,name=fpid.split(':')
        fp=pcbnew.FootprintLoad(str(LOCAL.get(lib,STD/(lib+'.pretty'))),name);assert fp is not None,fpid
        fp.SetFPID(pcbnew.LIB_ID(lib,name));fp.SetReference(ref);fp.SetValue(c.findtext('value') or '')
        fp.SetPath(pcbnew.KIID_PATH('/'+c.find('tstamps').text))
        properties={p.get('name') for p in c.iter('property')}
        fp.SetDNP('dnp' in properties)
        fp.SetExcludedFromBOM('exclude_from_bom' in properties)
        fields=[('Datasheet',c.findtext('datasheet') or ''),('Description',c.findtext('description') or '')]
        fields+=[(f.get('name'),f.text or '') for f in c.iter('field')]
        for key,value in fields:  # mirror schematic fields so the parity check is clean
            fp.SetField(key,value);fp.GetField(key).SetVisible(False)
        board.Add(fp)
        for pad in fp.Pads():
            net=pad_net.get((ref,pad.GetNumber()))
            if net:pad.SetNet(nets[net])
        spec=PLACE[ref]
        if spec[0]=='centre':
            fp.SetPosition(pt(origin[0]+spec[1],origin[1]+spec[2]))
        else:
            x,y,rot=spec;fp.SetOrientationDegrees(rot);fp.SetPosition(pt(*origin))
            b=box(fp);fp.SetPosition(pt(origin[0]+x+(origin[0]-b[0]),origin[1]+y+(origin[1]-b[1])))
        b=box(fp);placed[ref]=[round(b[0]-origin[0],2),round(b[1]-origin[1],2),round(b[2]-origin[0],2),round(b[3]-origin[1],2)]
        # Draft: references on the assembly (F.Fab) layer, centred on each part. Silkscreen
        # reference placement is a layout-review task (tightly packed rows collide on silk).
        label=fp.Reference();label.SetTextAngleDegrees(0);label.SetLayer(pcbnew.F_Fab)
        label.SetPosition(pt((b[0]+b[2])/2,(b[1]+b[3])/2));label.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8),pcbnew.FromMM(0.8)))
        label.SetTextThickness(pcbnew.FromMM(0.12))
        if ref.startswith('H'):label.SetVisible(False)
    assert sorted(missing)==sorted(ENVELOPES),missing
    for ref,(x,y,w,h,label) in ENVELOPES.items():
        x0,y0=origin[0]+x,origin[1]+y
        for layer in (pcbnew.F_Fab,pcbnew.F_CrtYd):rect(board,layer,x0,y0,x0+w,y0+h,0.05 if layer==pcbnew.F_CrtYd else 0.1)
        text(board,pcbnew.F_Fab,x0+w/2,y0+h/2,label.replace(' - ','\n'),0.8)
        # Keep footprints, tracks and vias out (PC10) until the real footprint exists; inner GND planes stay.
        z=pcbnew.ZONE(board);z.SetIsRuleArea(True);outer=pcbnew.LSET();outer.AddLayer(pcbnew.F_Cu);outer.AddLayer(pcbnew.B_Cu)
        z.SetLayerSet(outer);z.SetDoNotAllowFootprints(True)
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(False);z.SetDoNotAllowPads(False)
        z.SetZoneName(ref+'_ENVELOPE')
        o=z.Outline();o.NewOutline()
        for px,py in [(x0,y0),(x0+w,y0),(x0+w,y0+h),(x0,y0+h)]:o.Append(pcbnew.FromMM(px),pcbnew.FromMM(py))
        board.Add(z);placed[ref]=[x,y,x+w,y+h]
    gnd=nets['GND']
    for layer in (pcbnew.In1_Cu,pcbnew.In2_Cu):outline_zone(board,layer,gnd,origin,size)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    text(board,pcbnew.F_SilkS,origin[0]+48,origin[1]+size[1]-3,'PTERODACTYL v4 DRAFT - not for fabrication',1.2)
    board.SetFileName(str(PCB));pcbnew.SaveBoard(str(PCB),board)
    # Placement checks independent of DRC: board edge and mounting-hole clearance.
    problems=[]
    for ref,(x0,y0,x1,y1) in placed.items():
        if ref.startswith('H'):continue
        if ref!='U1' and min(x0,y0,size[0]-x1,size[1]-y1)<EDGE_MARGIN:problems.append(('edge',ref))
        for hx,hy in holes:
            dx=max(x0-hx,hx-x1,0);dy=max(y0-hy,hy-y1,0)
            if (dx*dx+dy*dy)**0.5<HOLE_KEEPOUT:problems.append(('hole',ref,hx,hy))
    (PRJ/'placement.json').write_text(json.dumps({'origin_mm':origin,'size_mm':size,'courtyards_local_mm':placed,'problems':problems},indent=1)+'\n',newline='\n')
    print('Placed %d footprints, %d envelopes, %d nets. Problems: %s'%(len(placed)-len(ENVELOPES),len(ENVELOPES),len(nets),problems))


if __name__=='__main__':main()
