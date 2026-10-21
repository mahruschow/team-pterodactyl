// Run inside the Codex artifact-session JavaScript tool. Creates a NEW workbook.
// Component-finalization snapshot: 2026-10-21. Prototype planning, not qualification.
await artifactSession.run(async ({ workbook, session }) => {
  const summary = workbook.worksheets.add('Budget summary');
  const power = workbook.worksheets.add('Power');
  const cost = workbook.worksheets.add('Cost and mass');
  const navy='#20364D', blue='#245C9C', amber='#FFF2CC', muted='#596579';
  function base(s,last,col) {
    s.showGridLines=false;
    s.getRange(`A1:${col}${last}`).format.font={name:'Arial',size:10,color:'#222B35'};
    s.getRange(`A1:${col}${last}`).format.rowHeight=23;
    s.getRange(`A1:${col}${last}`).format.verticalAlignment='center';
    s.getRange(`A1:${col}${last}`).format.columnWidth=15;
    s.getRange(`A1:A${last}`).format.columnWidth=43;
    s.getRange(`A2:${col}2`).format.font={name:'Arial',size:15,bold:true,color:navy};
  }
  function header(s,range) {
    s.getRange(range).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:34};
  }
  function input(s,range,fmt='0.00') {
    s.getRange(range).format.fill=amber;s.getRange(range).format.font.color=blue;
    s.getRange(range).setNumberFormat(fmt);
  }
  function f(s,cell,formula) {s.getRange(cell).formulas=[[formula]];}
  function v(s,cell,value) {s.getRange(cell).values=[[value]];}
  base(power,72,'L'); base(cost,42,'L'); base(summary,34,'F');
  v(power,'A2','PTERODACTYL power budget');
  v(power,'A3','Planning allowances, not measured limits. 600 MHz, continuous logging; no telemetry or heater.');
  power.getRange('A4:I4').values=[['Load / reference','Qty','Rail V','Avg mA/unit','Peak mA/unit','Avg load W','5 V avg mA','5 V peak mA','Supply group']];
  header(power,'A4:I4');power.getRange('B4:I4').format.rowHeight=34;
  power.getRange('B5:E11').values=[[1,5,150,250],[1,3.3,30,200],[1,3.3,20,25],[1,3.3,35,50],[1,3.3,2,5],[4,3.3,null,null],[1,3.3,1,3]];
  const loads=['Teensy 4.1 base / U1','microSD card / U1 socket','BNO055 #2472 / U3','GPS #5440 / U5','MS8607 #4716 / U4','Status LEDs / D2–D5','I2C + control pull-ups'];
  power.getRange('A5:A11').values=loads.map(x=>[x]);
  power.getRange('I5:I11').values=[['Controller'],['Onboard SD'],['External'],['External'],['External'],['External'],['External']];
  f(power,'D10','=(C10-$B$29)/$B$30*1000');f(power,'E10','=D10');
  for(let r=5;r<=11;r++) {
    f(power,`F${r}`,`=IF(COUNT(B${r}:E${r})=4,B${r}*C${r}*D${r}/1000,"Missing")`);
    f(power,`G${r}`,`=IF(COUNT(B${r}:E${r})=4,B${r}*D${r},"Missing")`);
    f(power,`H${r}`,`=IF(COUNT(B${r}:E${r})=4,B${r}*E${r},"Missing")`);
  }
  power.getRange('K4:L4').values=[['Basis / action','Source, checked 2026-10-20']];header(power,'K4:L4');
  power.getRange('K5:L11').values=[
    ['150/250 mA allowances excluding card/sensors. PJRC text cites 4.0, not a 4.1 maximum. Measure firmware load.','https://www.pjrc.com/store/teensy41.html'],
    ['30/200 mA provisional; card model not chosen. Obtain write/inrush limits and measure.','Engineering assumption; no selected-card datasheet'],
    ['20/25 mA breakout allowances. Bosch lists 12.3 mA for chip 9DOF; allowance includes board overhead.','https://www.bosch-sensortec.com/media/boschsensortec/downloads/promotion_material/product-selector-en.pdf'],
    ['35/50 mA allowances. Published navigation/acquisition: 29/34 mA. Internal antenna only.','https://www.adafruit.com/product/5440'],
    ['2/5 mA breakout allowances; do not equate sensor low-power figure with whole-board current.','https://www.adafruit.com/product/4716'],
    ['All four on continuously, Vf=2 V assumption, 680 ohm fitted values. Actual duty likely lower.','Current v4 schematic R4–R7/D2–D5; firmware config.h'],
    ['1/3 mA combined allowance; verify parallel breakout pull-ups and asserted input loads.','Current v4 schematic; engineering assumption']
  ];
  input(power,'B5:E9');input(power,'B10:C10');input(power,'B11:E11');
  power.getRange('B5:B11').setNumberFormat('0');power.getRange('C5:C11').setNumberFormat('0.0');
  power.getRange('F5:F13').setNumberFormat('0.000');power.getRange('G5:H20').setNumberFormat('0.0');
  v(power,'A13','Total load / current');
  for(const c of ['F','G','H'])f(power,`${c}13`,`=IF(COUNT(${c}5:${c}11)=7,SUM(${c}5:${c}11),"Missing")`);
  power.getRange('A13:I13').format.font.bold=true;
  power.getRange('A15:A20').values=[['5 V regulator output power (W)'],['Added 5 → 3.3 V LDO heat (W)'],['External 3.3 V current (mA)'],['External 3.3 V guidance (mA)'],['External current headroom (mA)'],['3.3 V added load including SD (mA)']];
  f(power,'D15','=IF(ISNUMBER(G13),5*G13/1000,"Missing")');f(power,'E15','=IF(ISNUMBER(H13),5*H13/1000,"Missing")');
  f(power,'D16','=IF(COUNT(G6:G11)=6,(5-3.3)*SUM(G6:G11)/1000,"Missing")');f(power,'E16','=IF(COUNT(H6:H11)=6,(5-3.3)*SUM(H6:H11)/1000,"Missing")');
  f(power,'D17','=IF(COUNT(G7:G11)=5,SUM(G7:G11),"Missing")');f(power,'E17','=IF(COUNT(H7:H11)=5,SUM(H7:H11),"Missing")');
  v(power,'D18',250);v(power,'K18','PJRC external-pin recommendation; onboard SD still contributes to regulator heating.');v(power,'L18','https://www.pjrc.com/store/teensy41.html');
  f(power,'D19','=IF(ISNUMBER(D17),D18-D17,"Missing")');f(power,'E19','=IF(ISNUMBER(E17),D18-E17,"Missing")');
  f(power,'D20','=IF(COUNT(G6:G11)=6,SUM(G6:G11),"Missing")');f(power,'E20','=IF(COUNT(H6:H11)=6,SUM(H6:H11),"Missing")');
  v(power,'K15','3.3 V loads draw approximately the same current through the Teensy linear regulator.');
  v(power,'K16','This heat is already included in 5 V input power. Do not add it twice.');
  power.getRange('D15:E16').setNumberFormat('0.000');power.getRange('D17:E20').setNumberFormat('0.0');
  power.getRange('A23:C23').values=[['Editable assumptions','Value','Unit']];header(power,'A23:C23');
  const parameters=[
    ['Buck-boost efficiency',.85,'%'],['Protection / wiring efficiency',.97,'%'],['Usable battery-energy fraction',.70,'%'],['Energy reserve',.25,'%'],['Battery-side auxiliary allowance',.005,'W'],['LED forward-voltage assumption',2,'V'],['LED series resistance',680,'ohm'],['Required total powered runtime',null,'h'],['Selected battery nominal voltage',null,'V'],['Minimum battery terminal voltage',null,'V'],['Selected battery / protection',null,'part number']
  ];power.getRange('A24:C34').values=parameters;input(power,'B24:B34');power.getRange('B24:B27').setNumberFormat('0%');power.getRange('B28').setNumberFormat('0.000');power.getRange('B34').setNumberFormat('@');
  power.getRange('K24:L34').values=[
    ['85% planning value, not a guaranteed efficiency floor. Confirm at chosen battery voltage/load.','https://www.pololu.com/product/2836'],
    ['3% path-loss allowance; replace with selected fuse/MOSFET/wiring losses.','Engineering assumption'],
    ['70% usable-energy placeholder for cold/cutoff/aging. Not battery-specific qualification.','Engineering assumption; minimum temperature unresolved'],
    ['25% additional energy reserve; proposed, not team-approved.','Engineering assumption'],
    ['5 mW for divider/gate bias/leakage; converter quiescent loss is included in efficiency.','Current v4 R1=100k, R2+R3=122k; engineering allowance'],
    ['2 V assumed for low-Vf indicators; verify selected LED datasheets.','Current v4 schematic notes'],
    ['Current fitted resistor value.','Current v4 schematic R4–R7'],
    ['Include preparation, flight, recovery wait and reserve policy. Lead has not specified hours.','Lead reply supplied by Saadat, 2026-10-20'],
    ['Leave blank until pack is selected; mAh comparisons require a voltage.','Open battery decision'],
    ['Must include discharge behavior and temperature; converter VIN must exceed 3 V at startup after drops.','https://www.pololu.com/product/2836'],
    ['Pack protection / undervoltage cutoff and charging method must be specified.','S9V11F5 has no built-in low-voltage cutoff: https://www.pololu.com/product/2836/specs']
  ];
  power.getRange('A37:A43').values=[['Battery input power (W)'],['Nameplate energy per runtime hour (Wh/h)'],['Required nameplate energy (Wh)'],['Required nominal pack capacity (Ah)'],['Peak battery current at minimum V (A)'],['Current candidate PTC hold rating (A)'],['PTC review']];
  for(const [out,load] of [['D37','D15'],['E37','E15']])f(power,out,`=IF(AND(ISNUMBER(${load}),COUNT(B24:B25)=2,ISNUMBER(B28),B24>0,B24<=1,B25>0,B25<=1,B28>=0),(${load}/B24+B28)/B25,"Missing/invalid")`);
  f(power,'D38','=IF(AND(ISNUMBER(D37),COUNT(B26:B27)=2,B26>0,B26<=1,B27>=0),D37*(1+B27)/B26,"Missing/invalid")');
  f(power,'D39','=IF(AND(ISNUMBER(D38),ISNUMBER(B31),B31>0),D38*B31,"Set runtime")');
  f(power,'D40','=IF(AND(ISNUMBER(D39),ISNUMBER(B32),B32>0),D39/B32,"Set runtime/voltage")');
  f(power,'D41','=IF(AND(ISNUMBER(E37),ISNUMBER(B33),B33>0),E37/B33,"Set minimum voltage")');v(power,'D42',.7);
  f(power,'D43','=IF(ISNUMBER(D41),IF(D41>D42,"Review peak / trip curve","Check derating / trip curve"),"Choose battery first")');
  v(power,'K37','Peak is a simultaneous-load screening allowance, not a measured maximum or inrush waveform.');
  v(power,'K38','Battery input W × (1 + reserve) ÷ usable energy fraction. Runtime is separate.');
  v(power,'K42','0.7 A hold is not a hard instantaneous trip limit. Check time-current curve and temperature.');
  power.getRange('D37:E42').setNumberFormat('0.000');
  power.getRange('A46:D46').values=[['Example terminal V','Average battery A','Peak battery A','Existing PTC screening']];header(power,'A46:D46');
  for(const [i,volts] of [3,3.7,5,7.4].entries()) {const r=47+i;v(power,`A${r}`,volts);f(power,`B${r}`,`=IF(ISNUMBER($D$37),$D$37/A${r},"Missing")`);f(power,`C${r}`,`=IF(ISNUMBER($E$37),$E$37/A${r},"Missing")`);f(power,`D${r}`,`=IF(ISNUMBER(C${r}),IF(C${r}>$D$42,"Review peak / trip curve","Check derating / trip curve"),"Missing")`);}
  v(power,'A52','Voltage examples are not selected batteries. 3 V at the pack leaves no startup margin after losses.');
  v(power,'A53','Actual card current, thermal behavior, minimum temperature and powered duration remain unverified.');
  power.getRange('B47:C50').setNumberFormat('0.000');
  power.getRange('D5:E11').conditionalFormats.addCustom('OR(NOT(ISNUMBER(D5)),D5<0)',{fill:'#FCE4D6'});
  power.getRange('D19:E19').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{fill:'#FCE4D6',font:{color:'#9C0006'}}});
  power.getRange('K1:K56').format.columnWidth=105;power.getRange('L1:L56').format.columnWidth=100;
  power.getRange('D1:E56').format.columnWidth=23;power.freezePanes.freezeRows(4);

  v(cost,'A2','PTERODACTYL cost and mass');v(cost,'A3','One assembled prototype; USD. Blank inputs remain missing. Nothing ordered. Prices checked 2026-10-20.');
  cost.getRange('A4:I4').values=[['Item / scope','Qty','Unit cost $','Line cost $','Unit mass g','Line mass g','Cost basis','Mass basis','References']];header(cost,'A4:I4');
  const items=[
    ['Teensy 4.1 DEV-16771',1,31.5,7,'Listed price','Allowance','U1','https://www.sparkfun.com/teensy-4-1.html','Mass allowance only; no card or headers.'],
    ['Adafruit BNO055 #2472',1,34.95,3,'Listed price','Published','U3','https://www.adafruit.com/product/2472','Published board mass; confirm assembled header basis.'],
    ['Adafruit MS8607 #4716',1,14.95,2,'Listed price','Allowance','U4','https://www.adafruit.com/product/4716','Whole breakout mass allowance, not sensor-package mass.'],
    ['Adafruit GPS #5440',1,29.95,9,'Listed price','Published','U5','https://www.adafruit.com/product/5440','Published product mass; no optional coin cell or external antenna.'],
    ['Pololu S9V11F5 #2836',1,6.95,.5,'Listed price','Published','U2','https://www.pololu.com/product/2836','0.5 g without pins per /specs; quote may require backorder.'],
    ['Carrier PCB, one installed',1,null,35,'Quote needed','Allowance','PCB','Current approximately 98 × 98 mm, 4-layer layout','Mass allowance; thickness/stackup and fabrication batch minimum not final.'],
    ['Module socket/header mating rows',7,null,1.5,'Quote needed','Allowance','75 positions','docs/MODULE_ASSEMBLY_PLAN.md','Two 24-pin + 6 + 4 + 5 + 9 + 3-pin rows. Check included loose headers before buying.'],
    ['Passive/protection component lot',1,null,8,'MPNs needed','Allowance','R1–R7, C1–C11, D1, FB1, F1, Q1','Current v4 schematic; 22 components','Select exact ratings/footprint-compatible MPNs; lot mass estimate.'],
    ['Low-Vf indicator LEDs',4,null,.3,'MPNs needed','Allowance','D2–D5','Current v4 schematic','Four 5 mm LEDs; resistors counted in passive lot.'],
    ['Carrier connectors',4,null,1,'MPNs needed','Allowance','J1–J4','Current v4 schematic','Battery, panel switch, PBF jumper, spare header.'],
    ['Onboard controls',2,null,1,'MPNs needed','Allowance','SW1–SW2','Current v4 schematic','Slide switch and pushbutton.'],
    ['Test points',10,null,.1,'MPNs needed','Allowance','TP1–TP10','Current v4 schematic','Choose populated testpoint hardware or review pad-only change.'],
    ['microSD card',1,null,.5,'Select card','Allowance','U1 socket','No exact card selected','Capacity, write current, temperature and endurance need selection.'],
    ['External power switch',1,null,4,'Select switch','Allowance','J2 harness','Current v4 power architecture','Select DC rating and enclosure mounting.'],
    ['Wiring / mating plugs lot',1,null,10,'Quote needed','Allowance','Harness','Assembly plan pending','Avoid double counting carrier connector bodies.'],
    ['Retention / spacers / screws lot',1,null,10,'Select hardware','Allowance','Modules and H1–H4','docs/MODULE_ASSEMBLY_PLAN.md','All carrier and module mounting hardware; verify magnetism and installed fit.'],
    ['Battery pack / protection',1,null,null,'Select battery','Missing','Battery','Power sheet and team runtime decision','No pack purchased or selected; include holder/protection mass.'],
    ['Enclosure',1,null,null,'Design/quote','Missing','Enclosure','Lead: as small as possible while functional','Define dimensions after battery, connector and retention decisions.'],
    ['Insulation / vent / payload mounting',1,null,null,'Define scope','Missing','Integration','Operating environment and payload mounting pending','Enter zero only if explicitly unnecessary; not currently zero.'],
    ['Shipping / minimum-order extras',1,null,0,'Quote needed','Not flown','Procurement','Supplier carts not created','Include fabrication lot minimum and extra purchased units here; exclude from flight mass.'],
    ['Taxes / duties',1,null,0,'Quote needed','Not flown','Procurement','Destination and final order pending','Actual payable taxes, not assumed zero.'],
    ['Prototype spares / rework',1,null,0,'Agree allowance','Not flown','Procurement','Team purchasing decision pending','Extra procurement allowance; not installed flight mass.']
  ];
  cost.getRange('K4:L4').values=[['Source / basis','Notes']];header(cost,'K4:L4');
  for(const [i,item] of items.entries()){const r=5+i;const [name,q,price,mass,pbasis,mbasis,refs,source,note]=item;
    cost.getRange(`A${r}:I${r}`).values=[[name,q,price,null,mass,null,pbasis,mbasis,refs]];
    cost.getRange(`K${r}:L${r}`).values=[[source,note]];
    f(cost,`D${r}`,`=IF(COUNT(B${r},C${r})=2,B${r}*C${r},"Missing")`);
    f(cost,`F${r}`,`=IF(COUNT(B${r},E${r})=2,B${r}*E${r},"Missing")`);
  }
  cost.getRange('A29:A35').values=[['Known-cost subtotal only ($)'],['Full prototype procurement ($)'],['Missing cost lines'],['Mass subtotal with inputs (g)'],['Complete installed mass (g)'],['Missing mass lines'],['Published module mass subset (g)']];
  f(cost,'D29','=SUM(D5:D26)');f(cost,'D30','=IF(COUNT(D5:D26)=22,SUM(D5:D26),"Incomplete")');f(cost,'D31','=22-COUNT(D5:D26)');
  f(cost,'F32','=SUM(F5:F26)');f(cost,'F33','=IF(COUNT(F5:F26)=22,SUM(F5:F26),"Incomplete")');f(cost,'F34','=22-COUNT(F5:F26)');f(cost,'F35','=SUMIFS(F5:F26,H5:H26,"Published")');
  v(cost,'K29','Only five module prices are populated; this is not a complete build cost.');
  v(cost,'K32','Subtotal includes allowances; battery, enclosure and integration mass are missing.');
  v(cost,'A37','Amber cells are editable inputs. Published masses, engineering allowances and missing values are distinguished.');
  v(cost,'A38','Confirm price, stock, exact MPNs, batch minimums and included headers before ordering. No order placed.');
  v(cost,'A39','Reference budget from the lead is a different payload. Its pumps/heaters, two-hour duration and 37 Wh pack are excluded.');
  input(cost,'B5:C26');input(cost,'E5:E26');cost.getRange('B5:B26').setNumberFormat('0');cost.getRange('C5:D30').setNumberFormat('$#,##0.00;($#,##0.00);"–"');cost.getRange('E5:F35').setNumberFormat('0.0');cost.getRange('F34').setNumberFormat('0');
  cost.getRange('C5:C26').conditionalFormats.add('containsBlanks',{format:{fill:'#FCE4D6'}});cost.getRange('E5:E26').conditionalFormats.add('containsBlanks',{format:{fill:'#FCE4D6'}});
  cost.getRange('G1:H42').format.columnWidth=20;cost.getRange('I1:I42').format.columnWidth=31;cost.getRange('K1:K42').format.columnWidth=65;cost.getRange('L1:L42').format.columnWidth=105;cost.freezePanes.freezeRows(4);

  v(summary,'A2','PTERODACTYL budget review');v(summary,'A3','October 20, 2026 | Current routed v4 logger | Planning draft');
  summary.getRange('A5:D5').values=[['Metric','Value','Unit','Meaning']];header(summary,'A5:D5');
  const metrics=[
    ['5 V average load',"='Power'!D15",'W','Includes added 3.3 V linear-regulator loss'],
    ['Battery average input',"='Power'!D37",'W','85% conversion + 97% path-efficiency assumptions'],
    ['Battery peak screening input',"='Power'!E37",'W','Assumed simultaneous loads; measure startup/write peaks'],
    ['Known-cost subtotal',"='Cost and mass'!D29",'USD','Excludes all currently unpriced items'],
    ['Complete procurement budget',"='Cost and mass'!D30",'USD','Needs exact parts, battery, PCB quote and purchasing extras'],
    ['Mass subtotal with inputs',"='Cost and mass'!F32",'g','Includes allowances; see missing mass lines'],
    ['Complete installed mass',"='Cost and mass'!F33",'g','Complete only when all mass inputs are supplied']
  ];for(const [i,[label,formula,unit,note]] of metrics.entries()){const r=6+i;v(summary,`A${r}`,label);f(summary,`B${r}`,formula);v(summary,`C${r}`,unit);v(summary,`D${r}`,note);}
  summary.getRange('B6:B8').setNumberFormat('0.00');summary.getRange('B9:B10').setNumberFormat('$#,##0.00');summary.getRange('B11:B12').setNumberFormat('0.0');
  summary.getRange('A15:C15').values=[['Total powered runtime (h)','Battery energy used (Wh)','Nameplate energy target (Wh)']];header(summary,'A15:C15');
  for(const [i,h] of [2,3,4,6].entries()){const r=16+i;v(summary,`A${r}`,h);f(summary,`B${r}`,`=IF(ISNUMBER('Power'!D37),A${r}*'Power'!D37,"Missing")`);f(summary,`C${r}`,`=IF(ISNUMBER('Power'!D38),A${r}*'Power'!D38,"Missing")`);}
  input(summary,'A16:A19','0.0');summary.getRange('B16:C19').setNumberFormat('0.00');
  v(summary,'D16','Examples, not approved mission durations.');v(summary,'D17','Nameplate target includes 25% reserve and 70% usable energy.');v(summary,'D18','Temperature/cutoff derating must be replaced with pack-specific evidence.');
  summary.getRange('A22:B22').values=[['Team review / follow-up','Review status as of 2026-10-20']];header(summary,'A22:B22');
  summary.getRange('A23:B29').values=[
    ['Runtime and operating temperature','Unconfirmed'],['Battery pack and cutoff','Unselected'],['SD model / measured current','Unverified'],['0.7 A PTC and power path','Review against low-voltage peak current'],['Package dimensions','Minimize after battery and mechanical review'],['Quoted cost / measured mass','Incomplete'],['Release readiness','No fabrication or battery approval implied']
  ];
  v(summary,'A31','Next: confirm powered hours and temperature; select/test SD and battery; quote remaining parts; weigh/dry-fit modules.');
  v(summary,'A32','The existing 51-footprint PCB is unchanged by this budget work.');
  summary.getRange('B1:B34').format.columnWidth=39;summary.getRange('C1:C34').format.columnWidth=29;summary.getRange('D1:D34').format.columnWidth=85;
  for(const s of [summary,power,cost])s.getRange('A1:L1').format.rowHeight=10;
  v(cost,'K29','Subtotal excludes unpriced items; full procurement cost is shown separately.');
  v(cost,'K32','Subtotal includes allowances; missing mass lines are counted below.');
  power.getRange('D10:E10').setNumberFormat('0.00');
  power.getRange('D14:E14').values=[['Average','Peak allowance']];
  power.getRange('D36:E36').values=[['Average','Peak allowance']];
  power.getRange('D14:E14').format.font.bold=true;
  power.getRange('D36:E36').format.font.bold=true;
  for(const [s,ranges] of [[power,['K5:L11','K24:L34']],[cost,['K5:L26']]]) {
    for(const range of ranges) {s.getRange(range).format.wrapText=true;s.getRange(range).format.rowHeight=46;}
  }
  // Confirmed runtime update, Saadat, 2026-10-20; reserve/temperature assumptions remain open.
  v(power,'B31',3);
  power.getRange('K31:L31').values=[['Three-hour required total powered runtime; budget includes separate energy reserve.','Saadat confirmation in chat, 2026-10-20']];
  v(power,'A53','Runtime: 3 h confirmed. Actual card current, thermal behavior and operating temperature remain unverified.');
  summary.getRange('A13:D13').values=[['Required runtime energy target',null,'Wh','3 h confirmed; includes proposed reserve and usable-energy allowances']];
  f(summary,'B13',"='Power'!D39");summary.getRange('B13').setNumberFormat('0.00');summary.getRange('A13:D13').format.font.bold=true;
  v(summary,'D16','3 h is the confirmed runtime; other durations are comparisons.');
  v(summary,'B23','3 h confirmed; temperature open');
  v(summary,'A31','Next: confirm operating temperature; select/test SD and battery; quote remaining parts; weigh/dry-fit modules.');
power.getRange('A35:C35').values=[['Minimum battery operating temperature',-40,'°C']];
  power.getRange('B35').setNumberFormat('0');
  power.getRange('B35').format.fill='#FFF2CC';
  power.getRange('B35').format.font.color='#245C9C';
  power.getRange('K35:L35').values=[['Lead requirement replaces earlier -45 °C estimate; cold capability still needs verification.','Lead reply supplied by Saadat, 2026-10-20']];
  power.getRange('K35:L35').format.wrapText=true;power.getRange('K35:L35').format.rowHeight=46;
  power.getRange('L26').values=[['Engineering assumption; usable capacity at -40 °C is not yet verified']];
  power.getRange('A53').values=[['Requirements: 3 h and -40 °C battery minimum. Actual current, cold capacity and thermal behavior remain unverified.']];
  summary.getRange('A23:B23').values=[['Runtime / minimum battery temperature','3 h / -40 °C confirmed']];
  summary.getRange('B27').values=[['Custom casing CAD after layout; fit review open']];
  summary.getRange('A31').values=[['Next: select/test battery and SD; verify soldered sensor headers; quote parts; design casing around final layout.']];
  cost.getRange('A11').values=[['Module interconnect rows; mixed mounting']];
  cost.getRange('E11').values=[[null]];
  cost.getRange('H11').values=[['Missing']];
  cost.getRange('K11:L11').values=[['Saadat assembly update, 2026-10-20; docs/MODULE_ASSEMBLY_PLAN.md','BNO055, MS8607 and GPS: headers soldered at both boards; exact lengths/clearance TBD. Teensy/regulator method unchanged. Prior socket mass withdrawn.']];
  cost.getRange('K11:L11').format.rowHeight=62;
  // Applied component selections; unknown procurement, cutoff and fit remain blank.
  v(power,'B25',.90);
  v(power,'B29',1.8125);
  f(power,'E10','=3');
  v(power,'B32',6);
  v(power,'B34','4 x L91 series / BH4AAW');
  v(power,'A29','Mean LED Vf at 2 mA (typical)');
  power.getRange('K6:L6').values=[['Kingston SDCIT2/8GB selected for prototype; 30/200 mA remain allowances, not published limits.','https://www.kingston.com/datasheets/SDCIT2_en.pdf']];
  power.getRange('K10:L10').values=[['All four on: typical Vf red 1.70, yellow 1.85, green 1.90, orange 1.80 V at 2 mA. Peak 3 mA/LED is an allowance.','Kingbright WP7113LID, WP7113LYD, WP7113LGD, WP7113LSECK/J4 datasheets; tools/component_selections.py']];
  power.getRange('K25:L25').values=[['90% provisional path efficiency replaces optimistic 97%; neither is a cold guarantee. See resistance screening below.','MF-RHT070-0 R1max 0.8 ohm after trip at 23 C; AO3401A 85 milliohm max at Vgs=-2.5 V, 25 C']];
  v(power,'K29','Mean of selected LED typical Vf values; no guaranteed current bound at cold or resistor/rail tolerances.');
  power.getRange('K32:L32').values=[['Four series primary lithium AA cells, 1.5 V nominal each. No charging.','https://data.energizer.com/pdfs/L91GL0225.pdf']];
  power.getRange('K34:L34').values=[['BH4AAW holder drawing rated -40 to +140 C; harness, cell retention and any pack-side protection still need validation.','https://www.batteryholders.com/uploads/parts/BH4AAW/datasheets/BH4AAW-datasheet.pdf']];
  v(power,'K42','MF-RHT070-0 hold: 0.95 A at -40 C, 0.70 A at 23 C, 0.62 A at 40 C. Hold is not instantaneous trip current.');
  v(power,'A56','Power-path resistance screening — illustrative terminal voltages, not discharge qualification');
  power.getRange('A58:C58').values=[['Total series resistance allowance',1,'ohm']];input(power,'B58');
  v(power,'K58','1.0 ohm = 0.8 PTC + 0.085 Q1 + 0.115 wiring/contact allowance. Not a guaranteed cold maximum.');
  v(power,'L58','https://bourns.com/docs/product-datasheets/mf-rht.pdf | https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf');
  power.getRange('A60:H60').values=[['Pack terminal V','Avg module W','Peak module W','Avg battery A','Peak battery A','Peak path loss W','Peak module VIN','Startup screening']];header(power,'A60:H60');
  for(const [i,volts] of [6,4.8,4].entries()) {
    const r=61+i;v(power,`A${r}`,volts);
    f(power,`B${r}`,'=$D$15/$B$24+$B$28');f(power,`C${r}`,'=$E$15/$B$24+$B$28');
    for(const [dest,load] of [['D','B'],['E','C']]) f(power,`${dest}${r}`,`=IF(AND(A${r}>0,$B$58>=0,A${r}^2>=4*$B$58*${load}${r}),2*${load}${r}/(A${r}+SQRT(A${r}^2-4*$B$58*${load}${r})),"No stable point")`);
    f(power,`F${r}`,`=IF(ISNUMBER(E${r}),E${r}^2*$B$58,"Unavailable")`);
    f(power,`G${r}`,`=IF(ISNUMBER(E${r}),A${r}-E${r}*$B$58,"Unavailable")`);
    f(power,`H${r}`,`=IF(ISNUMBER(G${r}),IF(G${r}>=3,"Above 3 V threshold","Below 3 V startup"),"Unavailable")`);
  }
  power.getRange('B61:G63').setNumberFormat('0.000');power.getRange('H60:H63').format.columnWidth=26;
  v(power,'A65','Constant-power calculation: Vpack I = Pmodule + I²R. Cell internal loss is excluded; voltage is at pack terminals.');
  v(power,'A66','A 3 V startup threshold is necessary, not sufficient. Test cold startup, SD peaks, PTC heating and end-of-discharge recovery.');
  power.getRange('K58:L58').format.wrapText=true;power.getRange('K58:L58').format.rowHeight=52;
  v(cost,'A14','Populated carrier connectors');v(cost,'B14',3);v(cost,'I14','J1–J3; J4 DNP');
  v(cost,'L14','J1/J2 0022272021; J3 candidate HTSW-102-07-T-S. 1 g/unit remains an allowance; harness plugs counted separately.');
  v(cost,'A16','Bare plated test pads');v(cost,'C16',0);v(cost,'E16',0);v(cost,'G16','No purchased part');v(cost,'H16','PCB included');v(cost,'L16','No test-pin hardware. Pad copper is included in PCB mass.');
  v(cost,'A17','Kingston SDCIT2/8GB');v(cost,'G17','Quote needed');v(cost,'K17','https://www.kingston.com/datasheets/SDCIT2_en.pdf');v(cost,'L17','Industrial microSD -40 to +85 C. 0.5 g allowance; exact write/inrush maximum and cold endurance unverified.');
  v(cost,'A21','4 L91 cells + BH4AAW holder');v(cost,'E21',75.05);v(cost,'G21','Quote needed');v(cost,'H21','Published + estimate');
  v(cost,'K21','Energizer L91: 15 g/cell; MPD BH4AAW: estimated 15.05 g, manufacturer drawings.');
  v(cost,'L21','60 g cells + 15.05 g wired holder. Excludes plug, added harness and retention (other rows). Complete pack not yet qualified.');
  v(cost,'L19','10 g allowance for added wire, plugs, crimps and strain relief. Excludes holder leads already counted in BH4AAW estimate.');
  v(cost,'G12','Quote needed');v(cost,'G13','Quote needed');v(cost,'G14','Quote / J3 review');
  v(cost,'L12','Selected MPNs in KiCad BOM; FB1 obsolete; replacement required. Seven MRS16 resistors: 0.875 g included within 8 g lot allowance.');
  v(cost,'L13','Selected low-current Kingbright MPNs in KiCad BOM; mass allowance remains unmeasured.');
  v(cost,'L10','98 x 98 mm carrier; AISLER 4-layer 1.6 mm 35 um ENIG target. 35 g remains a mass allowance.');
  v(summary,'A3','October 21, 2026 | Component finalization | Prototype planning draft');
  v(summary,'B22','Review status as of 2026-10-21');
  v(summary,'D7','85% conversion + provisional 90% path efficiency; see resistance screening');
  v(summary,'B24','4 L91 + BH4AAW candidate; cutoff/test open');
  v(summary,'B25','SDCIT2/8GB selected; current unmeasured');
  v(summary,'B29','ERC/DRC pass; parts/fit/cold gates open');
  v(summary,'A31','Next: resolve remaining part drawings, dry-fit and cold-test the complete battery/harness and logging assembly.');
  v(summary,'A32','KiCad selections applied by targeted edits; no flight qualification or purchasing approval implied.');
  summary.getRange('A23:B29').format.wrapText=true;summary.getRange('A23:B29').format.rowHeight=38;

  // First-prototype release scope and harness update, 2026-10-21.
  for (const [sheet, cell, value] of [
  [
    "Power",
    "B58",
    1.15
  ],
  [
    "Power",
    "K58",
    "1.15 ohm screen: 0.8 PTC + 0.085 Q1 + 0.10 pack fuse allowance + 0.165 wiring/switch/contact allowance. Not a guaranteed cold maximum."
  ],
  [
    "Power",
    "L58",
    "Bourns MF-RHT070; AO3401A; Littelfuse 251/253 sheet (025101.5MXL nominal 0.0823 ohm); docs/FIRST_PROTOTYPE_RELEASE.md"
  ],
  [
    "Power",
    "K34",
    "BH4AAW and four L91 cells selected for first build. Add insulated 025101.5MXL pack fuse; see assembly instructions. Runtime remains unmeasured."
  ],
  [
    "Cost and mass",
    "C18",
    11.07
  ],
  [
    "Cost and mass",
    "G18",
    "Supplier snapshot"
  ],
  [
    "Cost and mass",
    "I18",
    "C&K 7101SYZQE"
  ],
  [
    "Cost and mass",
    "K18",
    "https://www.digikey.com/en/products/detail/c-k/7101SYZQE/25966"
  ],
  [
    "Cost and mass",
    "L18",
    "USD 11.07 single-unit snapshot, 2026-10-21; tax/shipping excluded. -30 to +85 C, first room-temperature prototype. 4 g remains an allowance."
  ],
  [
    "Cost and mass",
    "G14",
    "Quote needed"
  ],
  [
    "Cost and mass",
    "L14",
    "J1/J2 0022272021; J3 HTSW-102-07-T-S with SNT-100-BK-T shunt. 1 g/unit is an allowance; harness plugs counted separately."
  ],
  [
    "Cost and mass",
    "L12",
    "All PCB MPNs selected for first prototype; FB1 Laird 28L0138-10R-10 replaces obsolete Murata. 8 g lot allowance includes 0.875 g MRS16 resistors."
  ],
  [
    "Cost and mass",
    "L15",
    "SW1 OS102011MS2QN1; SW2 PTS645SL50-2 LFS. Drawings/pin patterns checked for first prototype."
  ],
  [
    "Cost and mass",
    "L19",
    "10 g allowance for added wire, plugs, crimps, 025101.5MXL pack fuse, insulation and strain relief. Holder leads counted in BH4AAW. Tool cost not included."
  ],
  [
    "Cost and mass",
    "L11",
    "BNO055/MS8607/GPS: HTSW -15 pins soldered at both boards, 12 mm nominal spacing. Teensy/regulator: SSW -01 / HTSW -07. Mass remains unmeasured."
  ],
  [
    "Cost and mass",
    "L10",
    "AISLER TCVOYNZG rev1 processed: 97.79 x 97.79 mm, 4 layers, 1.6 mm, 35 um ENIG. 3 bare boards EUR 51.37 net provisional; not converted into this USD model."
  ],
  [
    "Budget summary",
    "A3",
    "October 21, 2026 | First prototype order preparation"
  ],
  [
    "Budget summary",
    "B24",
    "4 L91 + BH4AAW selected for first build"
  ],
  [
    "Budget summary",
    "B29",
    "PCB checks pass; AISLER checkout ready"
  ],
  [
    "Budget summary",
    "A31",
    "Next: sign in to AISLER, confirm delivered quote, order PCB and parts, then assemble the first prototype."
  ],
  [
    "Budget summary",
    "A32",
    "Physical testing, flight qualification and later revisions are outside the current project scope."
  ]
]) workbook.worksheets.getItem(sheet).getRange(cell).values=[[value]];
  v(summary,'B26','Retained for P1; low-voltage limits documented');
  v(summary,'B27','Casing deferred beyond first prototype');
  v(summary,'D10','Supplier quotes, tools, shipping and taxes remain incomplete');
  power.getRange('K58:L58').format.rowHeight=90;
  cost.getRange('K10:L21').format.rowHeight=90;
  workbook.recalculate();
  nodeRepl.write(await workbook.inspect({kind:'region',sheetId:'Budget summary',range:'A5:D19',maxChars:5500,tableMaxRows:20,tableMaxCols:4}));
  nodeRepl.write({sessionId:session.sessionId,costInputRows:items.length});
}, {artifactType:'spreadsheet'});
