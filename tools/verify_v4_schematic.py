"""Check the draft v4 schematic: native ERC, exported netlist and BOM.

Run with ordinary Python 3; the optional first argument selects kicad-cli.exe.
EXPECTED below is written net-by-net from SENSOR_CONNECTION_MAP.md and
POWER_ARCHITECTURE.md, independently of the part-by-part generator table.
"""
from pathlib import Path
import csv,hashlib,io,json,subprocess,sys,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SCH=ROOT/'Native_KiCad_v4/PTERODACTYL_v4.kicad_sch'
OUT=ROOT/'docs/validation/2026-10-19/step5-schematic'

EXPECTED={
    'VBAT_IN':{'J1.1','F1.1'},
    'VBAT_FUSED':{'F1.2','Q1.3'},
    'VBAT_PROT':{'Q1.2','D1.1','J2.1','TP1.1'},
    'Q1_GATE':{'Q1.1','D1.2','R1.1'},
    'VBAT_SW':{'J2.2','C1.1','R2.1','U2.VIN'},
    'VBAT_SENSE':{'R2.2','R3.1','C2.1','U1.26','TP10.1'},
    '+5V':{'U2.VOUT','U1.VIN','C3.1','C4.1','TP2.1'},
    '+3V3':{'U1.3.3V_1','U1.3.3V_2','FB1.1','J4.1','TP3.1'},
    'SENSOR_3V3':{'FB1.2','C5.1','C6.1','C7.1','C8.1','C9.1','C10.1','C11.1','U3.1','U4.1','U5.VIN','TP4.1'},
    'GND':{'J1.2','R1.2','C1.2','R3.2','C2.2','U2.GND','C3.2','C4.2','C5.2','C6.2','C7.2','C8.2','C9.2','C10.2','C11.2',
           'U1.GND1','U1.GND2','U1.GND3','U3.3','U4.3','U5.GND','D2.1','D3.1','D4.1','D5.1','SW1.1','SW2.2','J3.2','J4.2','TP5.1'},
    'I2C_SDA':{'U1.18','U3.4','U4.5','TP6.1'},
    'I2C_SCL':{'U1.19','U3.5','U4.4','TP7.1'},
    'GPS_TXD':{'U5.TX','U1.7','TP8.1'},
    'GPS_RXD':{'U1.8','U5.RX','TP9.1'},
    'IMU_RST':{'U1.9','U3.6'},
    'STATUS1':{'U1.2','R4.1'},'STATUS2':{'U1.3','R5.1'},'STATUS3':{'U1.4','R6.1'},'STATUS4':{'U1.5','R7.1'},
    'LED1_A':{'R4.2','D2.2'},'LED2_A':{'R5.2','D3.2'},'LED3_A':{'R6.2','D4.2'},'LED4_A':{'R7.2','D5.2'},
    'SW_MODE':{'U1.30','SW1.2'},'BTN_USER':{'U1.31','SW2.1'},'PBF_SENSE':{'U1.32','J3.1'},
    'SPARE_0':{'U1.0','J4.3'},'SPARE_1':{'U1.1','J4.4'},'SPARE_14':{'U1.14','J4.5'},
    'SPARE_15':{'U1.15','J4.6'},'SPARE_16':{'U1.16','J4.7'},'SPARE_17':{'U1.17','J4.8'},
}
# Deliberately unconnected, each with a documented reason.
EXPECTED_NC={
    'U2.EN':'internal pull-up keeps regulator enabled',
    'U3.2':'BNO055 3Vo regulator output','U3.7':'PS0 onboard pull-down','U3.8':'PS1 onboard pull-down',
    'U3.9':'INT unused (polling)','U3.10':'ADR onboard pull-down (0x28)',
    'U4.2':'MS8607 3Vo regulator output',
    'U5.3V3_OUT':'GPS regulator output','U5.EN':'onboard enable default','U5.VBAT':'no backup supply from carrier',
    'U5.FIX':'fix read from NMEA','U5.PPS':'not used for initial timestamp plan',
    'SW1.3':'unused throw',
}
UNUSED_TEENSY={'6','10','11','12','13','20','21','22','23','24','25','27','28','29','33','34','35','36','37','38','39','40','41'}
EXPECTED_NC.update({'U1.'+p:'spare Teensy pin, no carrier connection' for p in UNUSED_TEENSY})
NO_FOOTPRINT={'U2':'regulator pinout not yet verified','U5':'exact #5440 geometry pending (M01)'}


def main():
    cli=sys.argv[1] if len(sys.argv)>1 else 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
    OUT.mkdir(parents=True,exist_ok=True)
    erc=OUT/'erc.json';net=OUT/'netlist.xml';bom=OUT/'bom.csv'
    subprocess.run([cli,'sch','erc','--format','json','--severity-all','--output',str(erc),str(SCH)],check=True,capture_output=True)
    subprocess.run([cli,'sch','export','netlist','--format','kicadxml','--output',str(net),str(SCH)],check=True,capture_output=True)
    subprocess.run([cli,'sch','export','bom','--output',str(bom),'--fields','Reference,Value,Footprint,MPN,Notes,${DNP},${QUANTITY}',
                    '--labels','Refs,Value,Footprint,MPN,Notes,DNP,Qty','--group-by','Value,Footprint,MPN,${DNP}',
                    '--sort-field','Reference',str(SCH)],check=True,capture_output=True)
    subprocess.run([cli,'sch','export','pdf','--output',str(OUT/'PTERODACTYL_v4.pdf'),str(SCH)],check=True,capture_output=True)
    violations=[v for s in json.loads(erc.read_text())['sheets'] for v in s['violations']]
    root=ET.parse(net).getroot()
    nets={};nc=set()
    for n in root.iter('net'):
        nodes={x.get('ref')+'.'+x.get('pin') for x in n.iter('node')}
        name=n.get('name').lstrip('/')
        if name.startswith('unconnected-('):nc|=nodes
        else:nets[name]=nodes
    comps={c.get('ref'):c for c in root.iter('comp')}
    problems=[]
    for name,nodes in EXPECTED.items():
        if nets.get(name)!=nodes:problems.append(('net',name,sorted(nodes^nets.get(name,set()))))
    for name in set(nets)-set(EXPECTED):problems.append(('unexpected net',name,sorted(nets[name])))
    if nc!=set(EXPECTED_NC):problems.append(('no-connect set',sorted(nc^set(EXPECTED_NC))))
    for ref,c in comps.items():
        fp=c.findtext('footprint') or ''
        if (fp=='')!=(ref in NO_FOOTPRINT) and not ref.startswith('H'):problems.append(('footprint',ref,fp))
    teensy=comps['U1'].findtext('footprint')
    result={'schematic_sha256':hashlib.sha256(SCH.read_bytes()).hexdigest(),'erc_violations':len(violations),
            'erc_types':sorted({v['type'] for v in violations}),'nets_checked':len(EXPECTED),'intentional_no_connects':len(EXPECTED_NC),
            'components':len(comps),'teensy_footprint':teensy,'parts_without_footprint':NO_FOOTPRINT,
            'problems':problems,'result':'pass' if not problems and not violations else 'fail',
            'scope':'Native ERC, exported netlist against an independent expected net list, and BOM export. '
                    'Not a simulation, part-rating approval or physical test.'}
    (OUT/'schematic-check.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    for p in (net,bom):p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    assert not violations,violations[:3]
    assert not problems,problems
    print('PASS: ERC 0 violations; %d nets and %d intentional no-connects match; %d components.'%(len(EXPECTED),len(EXPECTED_NC),len(comps)))


if __name__=='__main__':main()
