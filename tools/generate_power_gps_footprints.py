"""Build module-carrier libraries only; never regenerate the routed PCB.

Pololu dimensions: official reg20a drawing (inch dimensions converted to mm).
GPS: legacy Adafruit CAD, visually accepted by Saadat on 2026-10-20; physical fit pending. CC BY-SA 3.0;
see Native_KiCad_v11/Pterodactyl_Modules_LICENSE.txt and footprint notes.
"""
from pathlib import Path
import json, math

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'Native_KiCad_v11/Pterodactyl_Modules.pretty'
REG = 'Pololu_S9V11F5_SSW_Carrier'
GPS = 'Adafruit_GPS_5440_Carrier'


def xy(p):
    return ' '.join(f'{v:.6f}'.rstrip('0').rstrip('.') or '0' for v in p)


def start(name, description):
    return [f'(footprint "{name}" (version 20241229) (generator "pterodactyl_module_generator")',
            ' (layer "F.Cu") (attr through_hole)', f' (descr "{description}")']


def text(out, label, pos, layer='F.Fab', size=.65, kind='user'):
    out.append(f' (fp_text {kind} "{label}" (at {xy(pos)}) (layer "{layer}") (effects (font (size {size} {size}) (thickness .1))))')


def line(out, a, b, layer='F.Fab', width=.1):
    out.append(f' (fp_line (start {xy(a)}) (end {xy(b)}) (stroke (width {width}) (type default)) (layer "{layer}"))')


def rectangle(out, bounds, layer, width=.1):
    x0,y0,x1,y1=bounds
    points=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    for a,b in zip(points,points[1:]+points[:1]): line(out,a,b,layer,width)


def pad(out, name, pos, square=False):
    out.append(f' (pad "{name}" thru_hole {"rect" if square else "circle"} (at {xy(pos)}) (size 1.8 1.8) (drill 1.04) (layers "*.Cu" "*.Mask"))')


def keepout(out, bounds):
    x0,y0,x1,y1=bounds
    out.append(' (zone (net 0) (net_name "") (layer "F.Cu") (hatch edge .5)'
               ' (connect_pads (clearance 0)) (min_thickness .25)'
               ' (keepout (tracks allowed) (vias allowed) (pads allowed) (copperpour allowed) (footprints not_allowed))'
               ' (fill (thermal_gap .3) (thermal_bridge_width .3))'
               f' (polygon (pts (xy {x0} {y0}) (xy {x1} {y0}) (xy {x1} {y1}) (xy {x0} {y1}))))')


def save(name, out):
    (LIB / (name+'.kicad_mod')).write_text('\n'.join(out+[')'])+'\n', encoding='utf-8', newline='\n')


def regulator():
    out=start(REG,'Pololu 2836 reg20a; top/inductor side up, header along bottom, VIN left/GND centre/VOUT right. Three-pin SSW socket proposal; installed fit/retention pending.')
    body=(-1.27,-10.16,6.35,1.27)
    rectangle(out,body,'F.Fab')
    rectangle(out,(-2.27,-11.16,7.35,2.27),'F.CrtYd',.05)
    # SSW-103 single-row body 3*2.54+0.51 = 8.13 mm, width 2.41 mm.
    rectangle(out,(-1.525,-1.205,6.605,1.205),'F.Fab')
    for i,name in enumerate(('VIN','GND','VOUT')):
        pad(out,name,(i*2.54,0),square=name=='GND')
        text(out,name,(i*2.54,4.5 if name=='GND' else 3.1),'F.SilkS',.8)
    text(out,'REF**',(2.54,-12.2),'F.SilkS',.8,'reference')
    text(out,'S9V11F5',(2.54,-8.3),'F.Fab',.65,'value')
    text(out,'INDUCTOR SIDE UP',(2.54,-5.6),'F.Fab',.55)
    text(out,'NO PARTS UNDER',(2.54,-3.8),'Dwgs.User',.55)
    keepout(out,body)
    save(REG,out)


def gps():
    boards=json.loads((ROOT/'docs/reference/step3-cad-geometry.json').read_text())['boards']
    board=next(b for b in boards if b['file']=='Adafruit-Ultimate-GPS/Adafruit Ultimate GPS.brd')
    header=next(h for h in board['headers'] if h['element']=='JP1')
    origin=header['pads'][0]
    def transform(x,y): return (float(x)-origin['x'],origin['y']-float(y))
    out=start(GPS,'Adafruit 5440 carrier; legacy PA6H CAD 70430c1 geometry visually accepted by Saadat 2026-10-20. Physical fit/holder clearance pending. CC BY-SA 3.0, Adafruit Industries/Limor Fried.')
    for w in board['outline']:
        x1,y1,x2,y2=[float(w[k]) for k in ('x1','y1','x2','y2')]
        a,b=transform(x1,y1),transform(x2,y2)
        angle=float(w.get('curve',0))
        if angle:
            t=math.radians(angle); dx,dy=x2-x1,y2-y1
            cx=(x1+x2)/2-dy/(2*math.tan(t/2)); cy=(y1+y2)/2+dx/(2*math.tan(t/2))
            vx,vy=x1-cx,y1-cy
            mid=transform(cx+vx*math.cos(t/2)-vy*math.sin(t/2),cy+vx*math.sin(t/2)+vy*math.cos(t/2))
            out.append(f' (fp_arc (start {xy(a)}) (mid {xy(mid)}) (end {xy(b)}) (stroke (width .1) (type default)) (layer "F.Fab"))')
        else: line(out,a,b)
    labels={'1PPS':'PPS','VIN':'VIN','GND':'GND','RX':'RX','TX':'TX','FIX':'FIX','VBACKUP':'VBAT','ENABLE':'EN','3.3V':'3V3_OUT'}
    for p in header['pads']:
        name=labels[p['net']]; pos=transform(p['x'],p['y'])
        pad(out,name,pos,square=name=='PPS')
        # Names preserve the logical symbol's identifiers; they are not numeric ordering claims.
        text(out,name,(pos[0],-3.0),'F.Fab',.45)
    for h in board['headers']:
        if 'MOUNTINGHOLE' not in h['package']: continue
        p=h['pads'][0]; pos=transform(p['x'],p['y'])
        out.append(f' (pad "" np_thru_hole circle (at {xy(pos)}) (size 2.7 2.7) (drill 2.7) (layers "*.Cu" "*.Mask"))')
        out.append(f' (fp_circle (center {xy(pos)}) (end {xy((pos[0]+3,pos[1]))}) (stroke (width .1) (type default)) (fill none) (layer "Dwgs.User"))')
    rectangle(out,(-23.86,-33.258,3.54,3.032),'F.CrtYd',.05)
    rectangle(out,(-21.845,-1.205,1.525,1.205),'F.Fab')  # candidate SSW-109 body
    keepout(out,(-22.86,-32.258,2.54,2.032))
    text(out,'REF**',(-10.16,-34.5),'F.SilkS',1,'reference')
    text(out,GPS,(-10.16,-21),'F.Fab',.5,'value')
    text(out,'GPS #5440',(-10.16,-17),'F.SilkS',.85)
    text(out,'FIT / HOLDER CHECK PENDING',(-10.16,-14),'Dwgs.User',.8)
    text(out,'NO PARTS UNDER MODULE',(-10.16,-11),'Dwgs.User',.7)
    save(GPS,out)


if __name__=='__main__':
    regulator(); gps()
    print('Created regulator and GPS carrier footprints; GPS visual acceptance only, physical fit pending; no board edits.')
