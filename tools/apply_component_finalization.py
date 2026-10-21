"""One-time, hash-guarded targeted edit from the October 21 research checkpoint.

No routing generator. Replaces only selected footprint graphics/fields, two
connector pad positions/sizes and the attached endpoints. Original UUIDs remain.
Run with KiCad Python. See COMPONENT_IMPLEMENTATION.md for limitations.
"""
from pathlib import Path
import copy, hashlib, json, re, sys, uuid
from sexpr import Sym, parse, dump, find, first
from component_selections import SELECTIONS

ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb'
SCH=PCB.with_suffix('.kicad_sch')
LIB=ROOT/'Native_KiCad_v11/Pterodactyl_Modules.pretty'
STD=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
OUT=ROOT/'docs/validation/2026-10-21/component-finalization'

def children_spans(text):
    depth=0;quoted=False;escape=False;start=None
    for i,c in enumerate(text):
        if quoted:
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(':
            depth+=1
            if depth==2:start=i
        elif c==')':
            if depth==2:yield start,i+1
            depth-=1

def patch_children(path, edit):
    text=path.read_text(encoding='utf-8'); replacements=[]
    for a,b in children_spans(text):
        node=parse(text[a:b]); old=copy.deepcopy(node)
        edit(node)
        if old!=node:replacements.append((a,b,dump(node,1)))
    for a,b,s in reversed(replacements):text=text[:a]+s+text[b:]
    path.write_text(text,encoding='utf-8',newline='\n')

def props(node):return {p[1]:p for p in find(node,'property')}

def setprop(node,key,value,sch=False):
    p=props(node).get(key)
    if p:p[2]=value;return
    template=copy.deepcopy(props(node).get('Datasheet') or props(node)['Value'])
    template[1:3]=[key,value]
    if sch:
        effects=first(template,'effects')
        if not first(effects,'hide'): effects.append([Sym('hide'),Sym('yes')])
    else:
        if not first(template,'hide'):template.append([Sym('hide'),Sym('yes')])
    node.append(template)

def line(a,b,layer,width):
    return [Sym('fp_line'),[Sym('start'),*a],[Sym('end'),*b],
            [Sym('stroke'),[Sym('width'),width],[Sym('type'),Sym('solid')]],
            [Sym('layer'),layer]]

def rect(x0,y0,x1,y1,layer,width):
    pts=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    return [line(pts[i],pts[(i+1)%4],layer,width) for i in range(4)]

def local_footprint(name,template,graphics=None,description=''):
    fp=parse((STD/template).read_text());fp[1]=name
    # No inaccurate inherited 3-D body; assembly height is documented explicitly.
    fp[:]=[n for n in fp if not isinstance(n,list) or n[0] not in ('model','embedded_fonts')]
    if description:first(fp,'descr')[1]=description
    if graphics is not None:
        fp[:]=[n for n in fp if not isinstance(n,list) or not str(n[0]).startswith('fp_')]
        fp.extend(graphics)
    for n in fp:
        if isinstance(n,list) and first(n,'uuid'): n.remove(first(n,'uuid'))
    (LIB/(name+'.kicad_mod')).write_text(dump(fp)+'\n',encoding='utf-8')
    return fp

def main():
    assert hashlib.sha256(PCB.read_bytes()).hexdigest().upper()=='DDE1328DAAAE48DD68CEA94614225AFFD30146D519A74F4DC4634C406FDE1C2C','Unexpected PCB: do not overwrite newer work'
    assert hashlib.sha256(SCH.read_bytes()).hexdigest().upper()=='8D9B97B5AAE8D6748F6A39C655AE1744B5E6A638695D5E95620061C31768EEF7','Unexpected schematic'
    OUT.mkdir(parents=True,exist_ok=True)
    custom={}
    for suffix,thickness in [('100n',3.18),('10u',4.07)]:
        name='KEMET_C322_'+suffix+'_P5.00mm'
        graphics=rect(-.04,-thickness/2,5.04,thickness/2,'F.Fab',.1)
        graphics+=rect(-1.05,-thickness/2-.25,6.05,thickness/2+.25,'F.CrtYd',.05)
        # Top/bottom body strokes avoid through-hole pad openings.
        graphics += [line((-.04,y),(5.04,y),'F.SilkS',.15) for y in (-thickness/2-.12,thickness/2+.12)]
        custom[name]=local_footprint(name,'Capacitor_THT.pretty/C_Disc_D5.0mm_W2.5mm_P5.00mm.kicad_mod',graphics,
                                   'KEMET C322 maximum body; H6.6 mm; 5.00 mm holes inside 5.08 +/-0.78 mm lead tolerance')
    name='Vishay_MRS16_P7.62mm'
    graphics=rect(2.01,-.8,5.61,.8,'F.Fab',.1)+rect(-1.05,-1.05,8.67,1.05,'F.CrtYd',.05)
    graphics+=rect(1.9,-.92,5.72,.92,'F.SilkS',.15)
    custom[name]=local_footprint(name,'Resistor_THT.pretty/R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal.kicad_mod',graphics,'MRS16 D1.6 L3.6 max, formed lead pitch >=5 mm. Pads retained at 7.62 mm.')
    name='Panasonic_EEUFR1E101_P2.50mm'
    custom[name]=local_footprint(name,'Capacitor_THT.pretty/CP_Radial_D6.3mm_P2.50mm.kicad_mod',description='EEUFR1E101 D6.3 mm nominal, H11.2 mm nominal; no generic 7 mm 3-D model. Allow datasheet sleeve and height tolerance.')
    name='Molex_0022272021_AISLER'
    f=local_footprint(name,'Connector_Molex.pretty/Molex_KK-254_AE-6410-02A_1x02_P2.54mm_Vertical.kicad_mod',description='Molex SDAE-6410-N, 22-27-2021. Local AISLER annulus adaptation: 1.90 x 2.19 pad, 1.19 drill.')
    for p in find(f,'pad'):first(p,'size')[1:]=[1.90,2.19]
    custom[name]=f
    for name,f in custom.items():
        for g in f:
            if isinstance(g,list) and first(g,'layer') and first(g,'layer')[1]=='F.SilkS' and first(g,'stroke'):first(first(g,'stroke'),'width')[1]=.15
        (LIB/(name+'.kicad_mod')).write_text(dump(f)+'\n',encoding='utf-8')
    changes=[]; endpoints={}
    def board_edit(node):
        if node[0]=='footprint':
            ref=props(node)['Reference'][2];fields=SELECTIONS.get(ref,{})
            if 'Footprint' in fields:
                name=fields['Footprint'].split(':')[1]
                fp=custom.get(name) or parse((LIB/(name+'.kicad_mod')).read_text())
                node[1]=fields['Footprint']
                node[:]=[n for n in node if not isinstance(n,list) or (not str(n[0]).startswith('fp_') and n[0]!='model')]
                node.extend(copy.deepcopy([n for n in fp if isinstance(n,list) and str(n[0]).startswith('fp_')]))
                for g in node:
                    if isinstance(g,list) and str(g[0]).startswith('fp_'):g.append([Sym('uuid'),str(uuid.uuid4())])
                first(node,'descr')[1]=first(fp,'descr')[1]
                if ref in ('J1','J2'):
                    origin=first(node,'at'); assert float(origin[3])==90
                    for p in find(node,'pad'):
                        first(p,'size')[1:]=[1.90,2.19];first(p,'drill')[1]=1.19
                        if p[1]=='2':
                            old=(float(origin[1]),round(float(origin[2])-2.5,6))
                            new=(old[0],round(float(origin[2])-2.54,6));endpoints[old]=new
                            first(p,'at')[1]=2.54;changes.append({'pad':ref+'.2','old_mm':old,'new_mm':new})
            for k,v in fields.items():
                if k!='Footprint':setprop(node,k,v)
        if node[0]=='segment':
            for key in ('start','end'):
                p=first(node,key);xy=tuple(float(x) for x in p[1:3])
                if xy in endpoints:p[1:3]=endpoints[xy];changes.append({'segment':first(node,'uuid')[1],'endpoint':key,'old_mm':xy,'new_mm':p[1:3]})
        # Enforce actual silk stroke/text thickness, not just project defaults.
        def silk(n):
            if not isinstance(n,list):return
            layer=first(n,'layer')
            if layer and layer[1] in ('F.SilkS','B.SilkS'):
                stroke=first(n,'stroke')
                if stroke and first(stroke,'width') and float(first(stroke,'width')[1])<.15:first(stroke,'width')[1]=.15
                effects=first(n,'effects')
                if effects:
                    font=first(effects,'font');th=first(font,'thickness')
                    if th and float(th[1])<.15:th[1]=.15
            for child in n:
                if isinstance(child,list):silk(child)
        silk(node)
    patch_children(PCB,board_edit)
    def schematic_edit(node):
        if node[0]!='symbol' or 'Reference' not in props(node):return
        for k,v in SELECTIONS.get(props(node)['Reference'][2],{}).items():setprop(node,k,v,sch=True)
    patch_children(SCH,schematic_edit)
    project=PCB.with_suffix('.kicad_pro');p=json.loads(project.read_text());ds=p['board']['design_settings']
    ds['rules'].update(min_clearance=.125,min_hole_to_hole=.3,min_silk_clearance=.125,min_text_thickness=.15)
    ds['defaults'].update(silk_line_width=.15,silk_text_thickness=.15)
    project.write_text(json.dumps(p,indent=2)+'\n')
    (OUT/'targeted-edits.json').write_text(json.dumps(changes,indent=2)+'\n')
    print('Targeted component fields/footprints and AISLER minima applied. Run refill, DRC, parity and preservation audit.')

if __name__=='__main__':main()
