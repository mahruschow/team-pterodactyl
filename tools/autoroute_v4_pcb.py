"""First-pass autoroute of the draft v4 PCB with Freerouting (Specctra DSN/SES round trip).

Run with KiCad Python:
    python.exe tools/autoroute_v4_pcb.py <freerouting-cli.exe | freerouting.jar> [max passes] [java.exe]
Freerouting is not stored in the repository: download an official release and check
it against the published checksums. The 2.5.0 .jar needs Java 25 or newer.

Removes existing tracks/vias first, so it replaces any earlier autoroute. Do not run
it after hand routing has started. The result is a starting point for review, not a
finished layout: the router knows clearances and net classes but not the Step 4
interference rules (PC6, PC11), which must be checked by hand.

Freerouting's anonymous analytics are disabled. If the router logs a Java exception
it is stopped immediately instead of waiting for the timeout (Freerouting 2.5.0's
Windows CLI build crashed this way on 2026-10-19; see docs/PCB_LAYOUT_V4.md).
"""
from pathlib import Path
import subprocess,sys,tempfile,time
import pcbnew

ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'
LOG=ROOT/'docs/validation/2026-10-19/step7-pcb/freerouting.log'
TIMEOUT_S=1800


def export_router_dsn(path):
    """Export a router-only copy of the board to Specctra DSN; the saved board is not changed.

    Runs in its own process (KiCad Python holds one loaded board per process).

    Specctra has no 'footprints only' keepout, so footprint rule areas that allow tracks
    (the Teensy carrier's no-parts-underneath area) would block tracks to the Teensy pins:
    drop them. Freerouting also ignores KiCad's board-edge clearance, so add outer-layer
    keep-out strips of that width along the board edges.
    """
    copy=pcbnew.LoadBoard(str(PCB))
    e=copy.GetBoardEdgesBoundingBox();x0,y0,x1,y1=e.GetLeft(),e.GetTop(),e.GetRight(),e.GetBottom()
    for z in copy.Zones():
        # Freerouting treats the inner no-tracks area as blocking vias too; the inner layers are
        # exported as power planes instead, and check_v4_pcb.py rejects any inner-layer track.
        if z.GetIsRuleArea() and z.GetZoneName()=='INNER_PLANES_NO_TRACKS':
            o=z.Outline();o.RemoveAllContours();o.NewOutline()
            for px,py in [(x0,y0),(x0+1000,y0),(x0+1000,y0+1000),(x0,y0+1000)]:o.Append(px,py)
    for fp in copy.GetFootprints():
        for z in fp.Zones():
            if z.GetIsRuleArea() and not z.GetDoNotAllowTracks():
                # Removing a footprint zone via Python crashes KiCad; shrink it into the edge strip instead.
                o=z.Outline();o.RemoveAllContours();o.NewOutline()
                for px,py in [(x0,y0),(x0+1000,y0),(x0+1000,y0+1000),(x0,y0+1000)]:o.Append(px,py)
    w=copy.GetDesignSettings().m_CopperEdgeClearance+pcbnew.FromMM(0.05)
    outer=pcbnew.LSET();outer.AddLayer(pcbnew.F_Cu);outer.AddLayer(pcbnew.B_Cu)
    for a,b,c,d in [(x0,y0,x1,y0+w),(x0,y1-w,x1,y1),(x0,y0,x0+w,y1),(x1-w,y0,x1,y1)]:
        z=pcbnew.ZONE(copy);z.SetIsRuleArea(True);z.SetLayerSet(outer)
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowPads(False)
        o=z.Outline();o.NewOutline()
        for px,py in [(a,b),(c,b),(c,d),(a,d)]:o.Append(px,py)
        copy.Add(z)
    for t in list(copy.GetTracks()):copy.Remove(t)  # last: SWIG type lookups misbehave after removals
    assert pcbnew.ExportSpecctraDSN(copy,str(path)),'DSN export failed'


def main():
    if sys.argv[1]=='--export-dsn':return export_router_dsn(sys.argv[2])
    router=sys.argv[1];passes=sys.argv[2] if len(sys.argv)>2 else '40'
    java=sys.argv[3] if len(sys.argv)>3 else 'java'
    command=[java,'-jar',router] if router.endswith('.jar') else [router]
    work=Path(tempfile.mkdtemp());dsn=work/'v4.dsn';ses=work/'v4.ses';raw=work/'router.log'
    subprocess.run([sys.executable,__file__,'--export-dsn',str(dsn)],check=True,capture_output=True)
    board=pcbnew.LoadBoard(str(PCB))  # SES import replaces all existing tracks and vias
    command+=['-de',str(dsn),'-do',str(ses),'--router.autorouter.max_passes='+passes,
              '--router.automatic_neckdown=false','--usage_and_diagnostic_data.disable_analytics=true']
    with raw.open('w',encoding='utf-8') as out:
        process=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,text=True)
        start=time.time();crashed=False
        while process.poll() is None:
            time.sleep(5)
            text=raw.read_text(encoding='utf-8',errors='replace')
            if 'Exception in thread' in text or time.time()-start>TIMEOUT_S:
                crashed=True;process.kill();process.wait();break
    text=raw.read_text(encoding='utf-8',errors='replace')
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.write_text('\n'.join(l.rstrip() for l in text.splitlines())+'\n',encoding='utf-8',newline='\n')
    assert not crashed and ses.exists(),'Freerouting failed or timed out; board unchanged. See '+str(LOG)
    assert pcbnew.ImportSpecctraSES(board,str(ses)),'SES import failed'
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB),board)
    tracks=[t for t in board.GetTracks() if t.GetClass()=='PCB_TRACK'];vias=[t for t in board.GetTracks() if t.GetClass()=='PCB_VIA']
    length=sum(pcbnew.ToMM(t.GetLength()) for t in tracks)
    print('Imported %d track segments (%.0f mm) and %d vias in %.0f s.'%(len(tracks),length,len(vias),time.time()-start))


if __name__=='__main__':main()
