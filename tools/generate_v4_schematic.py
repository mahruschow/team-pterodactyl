"""Generate the draft v4 carrier schematic project from the connection table.

Run with ordinary Python 3; the first argument may select kicad-cli.exe
(used only to upgrade a copy of the older module symbol library for
embedding). Writes Native_KiCad_v4/ only. The imported v3.8 project is
read, never modified.

Connections are made with labels, power symbols and no-connect flags at
pin endpoints, so every intended connection is explicit in this file.
"""
from pathlib import Path
import copy,json,subprocess,sys,tempfile,uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sexpr import Sym,parse,dump,find,first

ROOT=Path(__file__).resolve().parents[1]
V11=ROOT/'Native_KiCad_v11'
OUT=ROOT/'Native_KiCad_v4'
NAME='PTERODACTYL_v4'
KICAD_SYMBOLS=Path('C:/Program Files/KiCad/10.0/share/kicad/symbols')
NS=uuid.UUID('5b0f6a52-6c43-4f0e-9d3b-7e2f1c0a4d11')
G=2.54

POWER_NETS={'GND':'power:GND','+5V':'power:+5V','+3V3':'power:+3V3'}
NC=None

# (ref, lib_id, value, footprint, position in 2.54 mm grid units, {pin: net or NC}, extra fields, dnp)
PARTS=[
    # Battery input and protection
    ('J1','Connector_Generic:Conn_01x02','Battery','Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',(14,24),
     {'1':'VBAT_IN','2':'GND'},{'MPN':'JST B2B-XH-A (candidate)','Notes':'Battery connector; final type follows battery choice (D02)'},False),
    ('F1','Device:Polyfuse','PTC 0.7A hold','Fuse:Fuse_Bourns_MF-RHT070',(24,24),
     {'1':'VBAT_IN','2':'VBAT_FUSED'},{'MPN':'Bourns MF-RHT070 (candidate)','Notes':'Verify voltage rating >= max battery voltage'},False),
    ('Q1','Transistor_FET:Q_PMOS_GSD','IRLML6402','Package_TO_SOT_SMD:SOT-23',(36,24),
     {'1':'Q1_GATE','2':'VBAT_PROT','3':'VBAT_FUSED'},{'MPN':'IRLML6402TRPBF (candidate)','Notes':'Reverse-polarity protection; verify Vds >= 20 V, Vgs rating vs D1 clamp'},False),
    ('D1','Device:D_Zener','10V','Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal',(50,24),
     {'1':'VBAT_PROT','2':'Q1_GATE'},{'MPN':'BZX79-C10 (candidate)','Notes':'Clamps Q1 gate-source voltage'},False),
    ('R1','Device:R','100k','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(62,24),
     {'1':'Q1_GATE','2':'GND'},{},False),
    ('J2','Connector_Generic:Conn_01x02','Power switch','Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',(74,24),
     {'1':'VBAT_PROT','2':'VBAT_SW'},{'MPN':'JST B2B-XH-A (candidate)','Notes':'Off-board panel switch rated >= 1 A DC; location follows enclosure (D06)'},False),
    ('C1','Device:C_Polarized','47u 25V','Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',(84,24),
     {'1':'VBAT_SW','2':'GND'},{},False),
    ('R2','Device:R','100k 1%','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(94,24),
     {'1':'VBAT_SW','2':'VBAT_SENSE'},{'Notes':'Battery sense divider top'},False),
    ('R3','Device:R','22k 1%','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(104,24),
     {'1':'VBAT_SENSE','2':'GND'},{'Notes':'16 V in -> 2.89 V at ADC'},False),
    ('C2','Device:C','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(114,24),
     {'1':'VBAT_SENSE','2':'GND'},{},False),
    ('U2','Pterodactyl_v4:Pololu_S9V11F5_Logical','Pololu S9V11F5','',(136,24),
     {'VIN':'VBAT_SW','GND':'GND','VOUT':'+5V','EN':NC},{'MPN':'Pololu #2836','Notes':'5 V buck-boost, 2-16 V in. Footprint pending pinout verification. EN left at internal pull-up'},False),
    # 5 V and 3.3 V distribution
    ('C3','Device:C_Polarized','100u 10V','Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',(14,52),{'1':'+5V','2':'GND'},{'Notes':'At Teensy VIN'},False),
    ('C4','Device:C','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(24,52),{'1':'+5V','2':'GND'},{},False),
    ('FB1','Device:FerriteBead','Ferrite','Inductor_THT:L_Axial_L5.0mm_D3.6mm_P10.00mm_Horizontal_Murata_BL01RN1A2A2',(34,52),
     {'1':'+3V3','2':'SENSOR_3V3'},{'MPN':'Murata BL01RN1A2A2 (candidate)','Notes':'Verify current rating > 200 mA'},False),
    ('C5','Device:C','10u','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(44,52),{'1':'SENSOR_3V3','2':'GND'},{},False),
    ('C6','Device:C','10u','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(54,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U3 BNO055 VIN'},False),
    ('C7','Device:C','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(64,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U3 BNO055 VIN'},False),
    ('C8','Device:C','10u','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(74,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U4 MS8607 VIN'},False),
    ('C9','Device:C','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(84,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U4 MS8607 VIN'},False),
    ('C10','Device:C','10u','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(94,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U5 GPS VIN'},False),
    ('C11','Device:C','100n','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',(104,52),{'1':'SENSOR_3V3','2':'GND'},{'Notes':'At U5 GPS VIN'},False),
    # Status LEDs (low forward-voltage colours for 3.3 V drive)
    ('R4','Device:R','680','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(116,52),{'1':'STATUS1','2':'LED1_A'},{},False),
    ('R5','Device:R','680','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(126,52),{'1':'STATUS2','2':'LED2_A'},{},False),
    ('R6','Device:R','680','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(136,52),{'1':'STATUS3','2':'LED3_A'},{},False),
    ('R7','Device:R','680','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',(146,52),{'1':'STATUS4','2':'LED4_A'},{},False),
    ('D2','Device:LED','Red','LED_THT:LED_D5.0mm',(96,90),{'1':'GND','2':'LED1_A'},{'Notes':'Vf about 2 V; about 1.9 mA'},False),
    ('D3','Device:LED','Yellow','LED_THT:LED_D5.0mm',(96,94),{'1':'GND','2':'LED2_A'},{},False),
    ('D4','Device:LED','Green','LED_THT:LED_D5.0mm',(96,98),{'1':'GND','2':'LED3_A'},{'Notes':'Use a low-Vf green (about 2.1 V), not a 3 V InGaN part'},False),
    ('D5','Device:LED','Orange','LED_THT:LED_D5.0mm',(96,102),{'1':'GND','2':'LED4_A'},{},False),
    # Controller and modules
    ('U1','Pterodactyl_v4:Teensy41_Carrier','Teensy 4.1','Pterodactyl_Modules:Teensy41_SSW_Carrier',(30,86),
     {'VIN':'+5V','GND1':'GND','GND2':'GND','GND3':'GND','3.3V_1':'+3V3','3.3V_2':'+3V3',
      '2':'STATUS1','3':'STATUS2','4':'STATUS3','5':'STATUS4','7':'GPS_TXD','8':'GPS_RXD','9':'IMU_RST',
      '18':'I2C_SDA','19':'I2C_SCL','26':'VBAT_SENSE','30':'SW_MODE','31':'BTN_USER','32':'PBF_SENSE',
      '0':'SPARE_0','1':'SPARE_1','14':'SPARE_14','15':'SPARE_15','16':'SPARE_16','17':'SPARE_17'},
     {'MPN':'PJRC Teensy 4.1','Notes':'Cut VUSB/VIN pads before external power. Remaining pins intentionally unused'},False),
    ('U3','Pterodactyl_Modules:Adafruit_BNO055_2472','Adafruit BNO055 #2472','Pterodactyl_Modules:Adafruit_BNO055_2472_Carrier',(66,80),
     {'1':'SENSOR_3V3','2':NC,'3':'GND','4':'I2C_SDA','5':'I2C_SCL','6':'IMU_RST','7':NC,'8':NC,'9':NC,'10':NC},
     {'MPN':'Adafruit 2472','Notes':'I2C 0x28. PS0/PS1/ADR use onboard pull-downs; INT unused; 3Vo not connected'},False),
    ('U4','Pterodactyl_Modules:Adafruit_MS8607_4716','Adafruit MS8607 #4716','Pterodactyl_Modules:Adafruit_MS8607_4716_Carrier',(66,100),
     {'1':'SENSOR_3V3','2':NC,'3':'GND','4':'I2C_SCL','5':'I2C_SDA'},{'MPN':'Adafruit 4716','Notes':'I2C 0x40/0x76; 3Vo not connected'},False),
    ('U5','Pterodactyl_Modules:Adafruit_PA1616D_5440_Logical','Adafruit PA1616D #5440','',(100,80),
     {'VIN':'SENSOR_3V3','GND':'GND','TX':'GPS_TXD','RX':'GPS_RXD','3V3_OUT':NC,'EN':NC,'VBAT':NC,'FIX':NC,'PPS':NC},
     {'MPN':'Adafruit 5440','Notes':'Footprint pending M01 (exact #5440 geometry). EN at onboard default; VBAT/FIX/PPS unused'},False),
    # User inputs (D10 still open) and expansion
    ('SW1','Switch:SW_SPDT','Mode','Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q',(124,84),
     {'2':'SW_MODE','1':'GND','3':NC},{'MPN':'C&K OS102011MS2Q (candidate)','Notes':'Logic-level input, internal pull-up; role open (D10)'},False),
    ('SW2','Switch:SW_Push','User','Button_Switch_THT:SW_PUSH_6mm',(124,90),{'1':'BTN_USER','2':'GND'},{'Notes':'Internal pull-up; role open (D10)'},False),
    ('J3','Connector_Generic:Conn_01x02','Pull-before-flight','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',(124,96),
     {'1':'PBF_SENSE','2':'GND'},{'Notes':'Jumper/pull-pin to GND; role open (D10)'},False),
    ('J4','Connector_Generic:Conn_01x08','Spare I/O','Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical',(150,86),
     {'1':'+3V3','2':'GND','3':'SPARE_0','4':'SPARE_1','5':'SPARE_14','6':'SPARE_15','7':'SPARE_16','8':'SPARE_17'},
     {'Notes':'DNP by default; replaces legacy U$1/U$2 expansion. 3.3 V logic only'},True),
]
TEST_POINTS=['VBAT_PROT','+5V','+3V3','SENSOR_3V3','GND','I2C_SDA','I2C_SCL','GPS_TXD','GPS_RXD','VBAT_SENSE']
# Nets with a real source that ERC cannot see through passive/generic pins.
PWR_FLAGS={'GND':'battery return',
           'SENSOR_3V3':'+3V3 through FB1','VBAT_SW':'battery through protection and switch'}
NOTES=[
    (6,5,'PTERODACTYL v4 carrier - DRAFT generated from tools/generate_v4_schematic.py. Connections by label; see docs/POWER_ARCHITECTURE.md.'),
    (6,7,'Battery -> J1 -> F1 -> Q1 (reverse protection) -> J2 panel switch -> VBAT_SW -> U2 5 V buck-boost -> +5V -> Teensy VIN.'),
    (6,9,'U2 and U5 have no footprint yet: U2 pinout and U5 (#5440) geometry must be verified first (M01).'),
    (6,11,'Teensy: cut the VUSB/VIN pads before applying external power (PJRC). +3V3 is the Teensy 3.3 V output (250 mA external max).'),
    (6,13,'I2C at 100 kHz for bring-up (see PLACEMENT_AND_INTERFERENCE.md). No GPIO may exceed 3.3 V.'),
]


def netclass(name,track,clearance,via,drill,priority):
    return {'name':name,'track_width':track,'clearance':clearance,'via_diameter':via,'via_drill':drill,
            'microvia_diameter':0.3,'microvia_drill':0.1,'diff_pair_width':0.2,'diff_pair_gap':0.25,'diff_pair_via_gap':0.25,
            'wire_width':6,'bus_width':12,'line_style':0,'priority':priority,
            'pcb_color':'rgba(0, 0, 0, 0.000)','schematic_color':'rgba(0, 0, 0, 0.000)'}


# Power class: 0.5 mm tracks for battery/supply nets (about 0.7 A regulator startup).
NET_SETTINGS={'meta':{'version':4},
    'classes':[netclass('Default',0.25,0.2,0.6,0.3,2147483647),netclass('Power',0.5,0.25,0.8,0.4,0)],
    'netclass_patterns':[{'netclass':'Power','pattern':p} for p in
                         ['/VBAT_IN','/VBAT_FUSED','/VBAT_PROT','/VBAT_SW','+5V','+3V3','/SENSOR_3V3']]}


def uid(*parts):return str(uuid.uuid5(NS,'/'.join(parts)))


def at(x,y,a=0):return [Sym('at'),round(x,4),round(y,4),a]


def font(size=1.27):return [Sym('effects'),[Sym('font'),[Sym('size'),size,size]]]


def load_library(path):
    tree=parse(path.read_text(encoding='utf-8'))
    return {s[1]:s for s in find(tree,'symbol')}


def libraries(cli):
    tmp=Path(tempfile.mkdtemp())
    upgraded=tmp/'Pterodactyl_Modules.kicad_sym'
    subprocess.run([cli,'sym','upgrade','--output',str(upgraded),str(V11/'Pterodactyl_Modules.kicad_sym')],check=True,capture_output=True)
    return {
        'Pterodactyl_Modules':load_library(upgraded),
        'Pterodactyl_v4':load_library(OUT/'Pterodactyl_v4.kicad_sym'),
    }


def standard(lib,cache={}):
    if lib not in cache:cache[lib]=load_library(KICAD_SYMBOLS/(lib+'.kicad_sym'))
    return cache[lib]


def pins(symbol):
    result={}
    def walk(node):
        for x in node:
            if isinstance(x,list):
                if x and x[0]=='pin':
                    a=first(x,'at');result[first(x,'number')[1]]=(float(a[1]),float(a[2]),int(float(a[3])) if len(a)>3 else 0,str(x[1]))
                else:walk(x)
    walk(symbol);return result


TEENSY_TYPES={'VIN':'power_in','GND1':'power_in','GND2':'power_in','GND3':'power_in','3.3V_1':'power_out','3.3V_2':'passive'}
STD_SYMBOLS=['Device','Transistor_FET','Switch','Connector','Connector_Generic','Mechanical','power']
STD_FOOTPRINTS=['Connector_JST','Fuse','Package_TO_SOT_SMD','Diode_THT','Resistor_THT','Capacitor_THT','Inductor_THT',
                'LED_THT','Button_Switch_THT','Connector_PinHeader_2.54mm','TestPoint','MountingHole']


def teensy_symbol():
    """Imported v3.8 Teensy graphics and pin positions with electrical pin types corrected.

    3.3V_2 is passive: both 3.3 V pins are the same onboard regulator output,
    and two power outputs on one net would be an ERC conflict.
    """
    s=copy.deepcopy(load_library(V11/'PTERODACTYL_v3.8_v11-eagle-import.kicad_sym')['TEENSY41_SIMPLE'])
    def walk(node):
        for x in node:
            if isinstance(x,list) and x:
                if x[0]=='symbol' and isinstance(x[1],str):x[1]=x[1].replace('TEENSY41_SIMPLE','Teensy41_Carrier')
                if x[0]=='pin':x[1]=Sym(TEENSY_TYPES.get(first(x,'number')[1],'bidirectional'))
                walk(x)
    walk(s);s[1]='Teensy41_Carrier'
    for p in find(s,'property'):
        if p[1]=='Value':p[2]='Teensy41_Carrier'
        if p[1]=='Footprint':p[2]='Pterodactyl_Modules:Teensy41_SSW_Carrier'
        if p[1]=='Description':p[2]='Teensy 4.1 on SSW sockets; pin positions from imported v3.8 symbol, power pin types corrected'
    return s


def write_power_library():
    """v4 library: logical regulator (named pins avoid asserting an unverified pin order) and curated Teensy."""
    pin=lambda kind,x,y,a,n:[Sym('pin'),Sym(kind),Sym('line'),at(x,y,a),[Sym('length'),5.08],
        [Sym('name'),n,font()],[Sym('number'),n,font()]]
    prop=lambda k,v,y,hide=False:[Sym('property'),k,v,at(0,y,0)]+([[Sym('hide'),Sym('yes')]] if hide else [])+[font()]
    sym=[Sym('symbol'),'Pololu_S9V11F5_Logical',[Sym('pin_numbers'),[Sym('hide'),Sym('yes')]],
        [Sym('pin_names'),[Sym('offset'),1.016]],[Sym('exclude_from_sim'),Sym('no')],[Sym('in_bom'),Sym('yes')],[Sym('on_board'),Sym('yes')],
        prop('Reference','U',8.89),prop('Value','Pololu_S9V11F5_Logical',6.35),prop('Footprint','',0,True),
        prop('Datasheet','https://www.pololu.com/product/2836',0,True),
        prop('Description','DRAFT logical 5 V step-up/step-down regulator module, 2-16 V input; physical pin order not yet verified',0,True),
        [Sym('symbol'),'Pololu_S9V11F5_Logical_0_1',[Sym('rectangle'),[Sym('start'),-7.62,5.08],[Sym('end'),7.62,-5.08],
            [Sym('stroke'),[Sym('width'),0.254],[Sym('type'),Sym('default')]],[Sym('fill'),[Sym('type'),Sym('background')]]]],
        [Sym('symbol'),'Pololu_S9V11F5_Logical_1_1',pin('power_in',-12.7,2.54,0,'VIN'),pin('input',-12.7,-2.54,0,'EN'),
            pin('power_out',12.7,2.54,180,'VOUT'),pin('power_in',0,-10.16,90,'GND')],
        [Sym('embedded_fonts'),Sym('no')]]
    lib=[Sym('kicad_symbol_lib'),[Sym('version'),20251024],[Sym('generator'),'kicad_symbol_editor'],[Sym('generator_version'),'10.0'],sym,teensy_symbol()]
    (OUT/'Pterodactyl_v4.kicad_sym').write_text(dump(lib)+'\n',encoding='utf-8',newline='\n')


class Sheet:
    def __init__(self,libs):
        self.libs=libs;self.lib_symbols={};self.items=[];self.sheet=uid('sheet');self.power_count=0

    def lib_symbol(self,lib_id):
        if lib_id not in self.lib_symbols:
            lib,name=lib_id.split(':')
            source=self.libs[lib] if lib in self.libs else standard(lib)
            s=copy.deepcopy(source[name])
            assert first(s,'extends') is None,lib_id
            s[1]=lib_id;self.lib_symbols[lib_id]=s
        return self.lib_symbols[lib_id]

    def place(self,ref,lib_id,value,footprint,x,y,rot=0,fields=None,dnp=False,in_bom=True):
        s=self.lib_symbol(lib_id)
        props={p[1]:p for p in find(s,'property')}
        node=[Sym('symbol'),[Sym('lib_id'),lib_id],at(x,y,rot),[Sym('unit'),1],[Sym('body_style'),1],
              [Sym('exclude_from_sim'),Sym('no')],[Sym('in_bom'),Sym('yes' if in_bom else 'no')],[Sym('on_board'),Sym('yes')],
              [Sym('in_pos_files'),Sym('yes')],[Sym('dnp'),Sym('yes' if dnp else 'no')],[Sym('uuid'),uid('sym',ref)]]
        values={'Reference':ref,'Value':value,'Footprint':footprint,'Datasheet':props.get('Datasheet',[0,0,''])[2],
                'Description':props.get('Description',[0,0,''])[2]}
        values.update(fields or {})
        for k,v in values.items():
            lp=props.get(k);px,py=(float(first(lp,'at')[1]),float(first(lp,'at')[2])) if lp else (0,0)
            hidden=k not in ('Reference','Value') or (lp is not None and first(lp,'hide') is not None and first(lp,'hide')[1]=='yes')
            prop=[Sym('property'),k,v,at(x+px,y-py,0)]
            if hidden:prop.append([Sym('hide'),Sym('yes')])
            prop+=[[Sym('show_name'),Sym('no')],[Sym('do_not_autoplace'),Sym('no')],font()]
            node.append(prop)
        for number in pins(s):node.append([Sym('pin'),number,[Sym('uuid'),uid('pin',ref,number)]])
        node.append([Sym('instances'),[Sym('project'),NAME,[Sym('path'),'/'+self.sheet,[Sym('reference'),ref],[Sym('unit'),1]]]])
        self.items.append(node)
        return {n:(x+p[0],y-p[1],p[2]) for n,p in pins(s).items()}

    def label(self,net,x,y,angle):
        a=(angle+180)%360
        justify=[Sym('justify'),Sym('right' if a in (180,270) else 'left'),Sym('bottom')]
        self.items.append([Sym('label'),net,at(x,y,a),[Sym('fields_autoplaced'),Sym('yes')],font()+[justify],[Sym('uuid'),uid('label',net,str(x),str(y))]])

    def power(self,net,x,y,angle,lib_id=None):
        lib_id=lib_id or POWER_NETS[net]
        base=270 if lib_id=='power:GND' else 90
        rot=((angle+180)-base)%360
        self.power_count+=1;ref='#PWR%03d'%self.power_count if lib_id!='power:PWR_FLAG' else '#FLG%03d'%self.power_count
        self.place(ref,lib_id,net if lib_id!='power:PWR_FLAG' else 'PWR_FLAG','',x,y,rot,in_bom=False)

    def no_connect(self,x,y):
        self.items.append([Sym('no_connect'),at(x,y)[:3],[Sym('uuid'),uid('nc',str(x),str(y))]])

    def text(self,x,y,body):
        self.items.append([Sym('text'),body,[Sym('exclude_from_sim'),Sym('no')],at(x,y,0),font(1.524)+[[Sym('justify'),Sym('left'),Sym('bottom')]],[Sym('uuid'),uid('text',body)]])

    def connect(self,net,x,y,angle):
        if net is NC:self.no_connect(x,y)
        elif net in POWER_NETS:self.power(net,x,y,angle)
        else:self.label(net,x,y,angle)


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
    OUT.mkdir(exist_ok=True)
    write_power_library()
    sheet=Sheet(libraries(cli))
    table={}
    for ref,lib_id,value,footprint,(gx,gy),mapping,fields,dnp in PARTS:
        endpoints=sheet.place(ref,lib_id,value,footprint,gx*G,gy*G,fields=fields,dnp=dnp)
        unused=set(endpoints)-set(mapping)
        if ref=='U1':mapping=dict(mapping,**{p:NC for p in sorted(unused)})  # sorted: stable output
        assert set(mapping)==set(endpoints),(ref,set(endpoints)^set(mapping))
        for number,net in mapping.items():
            x,y,a=endpoints[number];sheet.connect(net,x,y,a)
        table[ref]={'lib_id':lib_id,'value':value,'footprint':footprint,'dnp':dnp,'pins':mapping}
    for i,net in enumerate(TEST_POINTS):
        ref='TP%d'%(i+1);endpoints=sheet.place(ref,'Connector:TestPoint',net,'TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm',(14+i*9)*G,108*G)
        x,y,a=endpoints['1'];sheet.connect(net,x,y,a);table[ref]={'pins':{'1':net}}
    for i in range(4):
        sheet.place('H%d'%(i+1),'Mechanical:MountingHole','M3','MountingHole:MountingHole_3.2mm_M3',(100+i*4)*G,108*G,in_bom=False)
    for i,(net,why) in enumerate(PWR_FLAGS.items()):
        x,y=(100+i*10)*G,66*G
        sheet.power(net,x,y,90,'power:PWR_FLAG')
        if net in POWER_NETS:sheet.power(net,x,y,270)
        else:sheet.label(net,x,y,270)
    for gx,gy,body in NOTES:sheet.text(gx*G,gy*G,body)
    root=[Sym('kicad_sch'),[Sym('version'),20260306],[Sym('generator'),'eeschema'],[Sym('generator_version'),'10.0'],
          [Sym('uuid'),sheet.sheet],[Sym('paper'),'A3'],
          [Sym('title_block'),[Sym('title'),'PTERODACTYL v4 carrier - DRAFT'],[Sym('date'),'2026-10-19'],[Sym('rev'),'4.0-draft'],
           [Sym('comment'),1,'Generated by tools/generate_v4_schematic.py - not fabrication-approved']],
          [Sym('lib_symbols')]+list(sheet.lib_symbols.values())]+sheet.items+[
          [Sym('sheet_instances'),[Sym('path'),'/',[Sym('page'),'1']]],[Sym('embedded_fonts'),Sym('no')]]
    (OUT/(NAME+'.kicad_sch')).write_text(dump(root)+'\n',encoding='utf-8',newline='\n')
    (OUT/(NAME+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':NAME+'.kicad_pro','version':3},'net_settings':NET_SETTINGS},indent=2)+'\n',newline='\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table\n\t(version 7)\n'
        '\t(lib (name "Pterodactyl_Modules") (type "KiCad") (uri "${KIPRJMOD}/../Native_KiCad_v11/Pterodactyl_Modules.kicad_sym") (options "") (descr "Draft module pin contracts"))\n'
        '\t(lib (name "Pterodactyl_v4") (type "KiCad") (uri "${KIPRJMOD}/Pterodactyl_v4.kicad_sym") (options "") (descr "Draft v4 regulator and Teensy symbols"))\n'
        +''.join('\t(lib (name "%s") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/%s.kicad_sym") (options "") (descr "KiCad standard"))\n'%(n,n) for n in STD_SYMBOLS)+')\n',newline='\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table\n\t(version 7)\n'
        '\t(lib (name "Pterodactyl_Modules") (type "KiCad") (uri "${KIPRJMOD}/../Native_KiCad_v11/Pterodactyl_Modules.pretty") (options "") (descr "Draft carrier footprints"))\n'
        +''.join('\t(lib (name "%s") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty") (options "") (descr "KiCad standard"))\n'%(n,n) for n in STD_FOOTPRINTS)+')\n',newline='\n')
    (OUT/'connection-table.json').write_text(json.dumps({'generated_by':'tools/generate_v4_schematic.py','pwr_flags':PWR_FLAGS,'parts':table},indent=1)+'\n',newline='\n')
    print('Wrote %s with %d parts, %d test points.'%(NAME,len(PARTS),len(TEST_POINTS)))


if __name__=='__main__':main()
