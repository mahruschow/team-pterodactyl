"""Prototype selections, 2026-10-21. Not flight or procurement approval.

Imported by the schematic source without regenerating the routed design.
Electrical networks are deliberately absent: this table changes fields only.
"""
LOCAL = 'Pterodactyl_Modules:'
SELECTIONS = {}

def select(refs, mpn, source, **fields):
    for ref in refs.split():
        SELECTIONS[ref] = {'MPN': mpn, 'Datasheet': source,
                          'SelectionStatus': 'Prototype selection; hardware verification required', **fields}

select('C1 C3', 'EEUFR1E101', 'https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1E101',
       Value='100u 25V', Footprint=LOCAL+'Panasonic_EEUFR1E101_P2.50mm',
       Notes='100 uF 25 V; nominal D6.3 H11.2 mm, allow body tolerances. Cold startup/transients untested.')
select('C2 C4 C7 C9 C11', 'C322C104K5R5TA', 'https://search.kemet.com/component-documentation/download/specsheet/C322C104K5R5TA',
       Footprint=LOCAL+'KEMET_C322_100n_P5.00mm', Notes='100 nF 50 V X7R; max body 5.08 x 3.18 x 6.6 mm; 5.00 mm pitch within specified lead tolerance.')
select('C5 C6 C8 C10', 'C322C106K3R5TA', 'https://search.kemet.com/component-documentation/download/specsheet/C322C106K3R5TA',
       Footprint=LOCAL+'KEMET_C322_10u_P5.00mm', Notes='10 uF 25 V X7R; max body 5.08 x 4.07 x 6.6 mm; verify effective capacitance under bias/cold.')
select('J1 J2', '0022272021', 'https://www.molex.com/en-us/products/part-detail/22272021',
       Footprint=LOCAL+'Molex_0022272021_AISLER', Notes='KK254; -40 to +80 C; 0022012027 housing / 0008500113 contacts. Verify harness polarity, wire insulation and retention.')
select('Q1', 'AO3401A', 'https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf', Value='AO3401A', Footprint=LOCAL+'AO3401A_SOT23_AISLER',
       Notes='G1 S2 D3; source=VBAT_PROT, drain=VBAT_FUSED. Four L91 cells only; +/-12 V Vgs. No generic 16 V carrier input approval.')
select('D1', 'BZX79-C10,133', 'https://assets.nexperia.com/documents/data-sheet/BZX79.pdf',
       Notes='10 V nominal zener; low R1 bias does not guarantee a precise 10 V clamp.')
select('F1', 'MF-RHT070-0', 'https://bourns.com/docs/product-datasheets/mf-rht.pdf?sfvrsn=9bedf0c3_50',
       SelectionStatus='Prototype selection; startup, resistance loss and fault testing open',
       Notes='0.7 A hold at 23 C; 0.95 A at -40 C, 0.62 A at +40 C. 0.8 ohm R1max; 97% path efficiency is not guaranteed.')
select('FB1', '28L0138-10R-10', 'https://www.laird.com/sites/default/files/28l0138-10r-10-datasheet.pdf',
       Footprint=LOCAL+'Laird_28L0138_P10.00mm', Value='75R@100MHz',
       SelectionStatus='First prototype selection; drawing and electrical ratings reviewed',
       Notes='Laird axial ferrite; 5 A, 10 milliohm max DCR; -40 to +125 C. Max body L4.70 D3.76 mm, lead D0.69; form to 10 mm pitch without stressing body. Replaces obsolete Murata.')
for refs, value in [('R1 R2','1003'), ('R3','2202'), ('R4 R5 R6 R7','6800')]:
    select(refs, 'MRS16000C'+value+'FCT00', 'https://www.vishay.com/docs/28724/mrs16m25.pdf',
           Footprint=LOCAL+'Vishay_MRS16_P7.62mm',
           Notes='MRS16 1%, 0.4 W, -55 to +155 C; 5 mm minimum formed pitch fits 7.62 mm. MRS25 rejected: minimum pitch 10 mm. Stock/lifecycle recheck before purchase.')
for ref,mpn,file in [('D2','WP7113LID','WP7113LID'),('D3','WP7113LYD','WP7113LYD'),
                     ('D4','WP7113LGD','WP7113LGD'),('D5','WP7113LSECK/J4','WP7113LSECK-J4')]:
    select(ref,mpn,'https://www.kingbrightusa.com/images/catalog/SPEC/'+file+'.pdf',
           Notes='Low-current 5 mm LED, 680 ohm series resistor. Confirm A/K and body/flange clearance on receipt.')
select('SW1','OS102011MS2QN1','https://www.farnell.com/datasheets/1851186.pdf',
       SelectionStatus='First prototype selection; visual drawing and common pin verified',
       Notes='OS catalog page 36: electrical pitch 2 mm, anchors 8.2 mm, common 2. Logic input only. Older sheet -30 to +70 C; newer rating and long-term low-current contact reliability not qualified.')
select('SW2','PTS645SL50-2 LFS','https://datasheet.datasheetarchive.com/originals/dk/DKDS42/DSANUWW0042856.pdf',
       SelectionStatus='First prototype selection; straight-terminal drawing and contact pairs verified',
       Notes='Order exact legacy PTS645SL50-2 LFS: 5 mm actuator, 130 gf. 6.5 x 4.5 mm pins; top pair common, bottom pair common. Do not substitute ambiguous Y97 alias without confirming configuration.')
select('J3','HTSW-102-07-T-S','https://suddendocs.samtec.com/catalog_english/tsw_th.pdf',
       SelectionStatus='First prototype selection; header and mating shunt reviewed',
       Notes='Mate with SNT-100-BK-T shunt. 0.635 mm square post, 5.84 mm mating length. Removing shunt logs PBF_REMOVED launch marker; does not disconnect power.')
select('J4','DNP','',SelectionStatus='Do not populate',Notes='Spare 3.3 V I/O header; no purchased header in default assembly.')
for i in range(1,11):
    select('TP'+str(i),'PCB PAD ONLY','',SelectionStatus='Bare plated test pad; no purchased part',Notes='Probe existing plated pad; no test-pin hardware populated.')
