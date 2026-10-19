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


def main():
    router=sys.argv[1];passes=sys.argv[2] if len(sys.argv)>2 else '40'
    java=sys.argv[3] if len(sys.argv)>3 else 'java'
    command=[java,'-jar',router] if router.endswith('.jar') else [router]
    board=pcbnew.LoadBoard(str(PCB))
    for t in list(board.GetTracks()):board.Remove(t)
    work=Path(tempfile.mkdtemp());dsn=work/'v4.dsn';ses=work/'v4.ses';raw=work/'router.log'
    assert pcbnew.ExportSpecctraDSN(board,str(dsn)),'DSN export failed'
    command+=['-de',str(dsn),'-do',str(ses),'--router.autorouter.max_passes='+passes,
              '--usage_and_diagnostic_data.disable_analytics=true']
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
