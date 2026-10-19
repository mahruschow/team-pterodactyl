# Step 3 — module assembly proposal and closure gates

October 18, 2026. This is a reviewable prototype proposal, not an order list or a flight-qualified assembly. Exact spreadsheet products remain unchanged. Main schematic and PCB integration belongs to Step 5.

## Sensor connector selection

Use female sockets on the carrier and downward-facing male headers on the BNO055/MS8607 modules. Populate both BNO055 rows, including electrically unused pins. Keep the modules removable for bench troubleshooting, with separate mechanical retention.

| Location | Carrier socket, quantity 1 | Module header, quantity 1 |
| --- | --- | --- |
| BNO055 JP1, 6 positions | Samtec SSW-106-01-L-S | Samtec HTSW-106-07-L-S |
| BNO055 JP2, 4 positions | Samtec SSW-104-01-L-S | Samtec HTSW-104-07-L-S |
| MS8607 JP2, 5 positions | Samtec SSW-105-01-L-S | Samtec HTSW-105-07-L-S |

These are configured series part-number proposals; stock, cost and exact orderable configuration have not been confirmed. Do not substitute the supplied generic headers without checking dimensions. The selected families use 2.54 mm pitch and 0.635 mm square mating posts; HTSW is the high-temperature header option. The -07 header has a 5.84 mm mating post, 2.54 mm solder tail and 10.92 mm total length. Its inferred insulator thickness is 2.54 mm. [Samtec TSW/HTSW catalog](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf).

SSW -01 sockets have a nominal 8.51 mm body height, 2.64 mm solder tail, and 3.68–6.35 mm insertion range. Single-row body width is 2.41 mm, with length 2.54 × positions + 0.51 mm. The single-row recommended PCB pattern specifies 1.04 mm holes. Both draft carrier footprints now use that drill with 1.8 mm pads; nominal radial annulus is 0.38 mm. Confirm finished-hole tolerance and annular-ring requirements with the fabricator. [SSW catalog](https://suddendocs.samtec.com/catalog_english/ssw_th.pdf), [SSW single-row footprint, revision A](https://suddendocs.samtec.com/prints/ssw-s.pdf).

Teensy now has a separately reviewed two-row SSW-124 socket carrier and a candidate HTSW header arrangement; see TEENSY_MECHANICAL_REVIEW.md. Its fully seated spacing is nominally 11.05 mm. The sensor 12 mm standoff scheme does not apply to Teensy. GPS retains its exact-geometry gate.

## Height and retention proposal

For the two sensor modules, target **12 mm from carrier top surface to module underside** using four insulating spacers per module. Start the fit review with M2 through-fasteners, spacer outside diameter at most 4 mm, and head/washer outside diameter at most 6 mm. Carrier holes remain 2.7 mm NPTH; module holes in the source CAD are 2.5 mm. This is a size envelope, not a qualified fastener part number. Final polymer, thread engagement, torque, creep, temperature and vibration retention need team review; do not assume generic nylon hardware is flight-qualified. Avoid assuming stainless hardware is nonmagnetic.

Nominal connector calculation: fully seated spacing is 8.51 + 2.54 = 11.05 mm. At 12 mm spacing, the body gap is 0.95 mm and post engagement is 5.84 − 0.95 = **4.89 mm**, inside the stated insertion range. This calculation excludes manufacturing tolerances and board bow. A fully seated connector cannot be forced into a shorter spacer stack. Check worst-case engagement and fit before fixing a spacer part number.

No carrier components underneath either module in the initial layout. Count actual underside parts and solder protrusions; 12 mm spacing is not a measured clearance result. Keep sockets level during soldering, check module orientation against pad 1/VIN, and support the board without bending it when tightening hardware. Do not connect a carrier rail to the breakout's 3Vo output.

## Symbols ready for schematic integration

The `Pterodactyl_Modules` symbol library now contains `Adafruit_BNO055_2472` and `Adafruit_MS8607_4716`, with the matching carrier footprint field populated. VIN/GND are power inputs, 3Vo is a power output, SDA/SCL are bidirectional (including clock stretching), controls are inputs, and INT is an output. No pins are hidden or pre-marked no-connect. Apply the reviewed unused-pin dispositions explicitly in Step 5.

Native KiCad SVG export passed. An independent checker verified all 15 pin functions/types, CSV mappings, assigned footprint names and native-loaded pad numbers. [Symbol evidence](validation/2026-10-18/step3-symbols/symbol-contract-check.json). This is a library contract check, not ERC of a wired circuit. Reproduce with KiCad Python: `tools/verify_module_symbols.py`; pass the CLI path as its first argument if needed.

### GPS logical symbol

`Pterodactyl_Modules:Adafruit_PA1616D_5440_Logical` represents nine reviewed interface functions. Pin identifiers are signal names (VIN, GND, TX, RX, 3V3_OUT, EN, VBAT, FIX, PPS), not asserted physical positions. The duplicated pin-number text is hidden; names remain visible. `3V3_OUT` denotes the breakout pin printed 3.3V. It is a regulator output, separate from VIN; TX/FIX/PPS are outputs, RX/EN inputs, and VBAT a power input. The footprint field is intentionally blank. Native SVG load and all nine logical names/types pass. A future physical footprint must map to these names explicitly or use a reviewed symbol revision. [Adafruit pin functions](https://learn.adafruit.com/adafruit-ultimate-gps/pinouts), [selected product](https://www.adafruit.com/product/5440).

## Remaining closure record

| ID | Evidence needed | Who/action | Gate |
| --- | --- | --- | --- |
| M01 | Exact #5440 revision, header order/coordinates, holes, antenna and underside holder dimensions | Lead/team obtain manufacturer drawing or actual board; PCB designer compares every coordinate | Before GPS footprint assignment and placement approval |
| M02 | Nominal geometry verified; draft SSW carrier, uniform drills, courtyard and component keepout implemented/tested; installed access and retention remain open | Team/PCB designer fit [Teensy assembly](TEENSY_MECHANICAL_REVIEW.md) to chosen enclosure | Before Teensy mechanical approval |
| M03 | Exact socket/header configurations, tolerances, spacer/fastener part numbers and assembled height | PCB designer/team review this proposal with selected enclosure and hardware | Before placement freeze |
| M04 | Module revision photos, pin-one orientation, hole alignment, underside/access clearance, strain-free retention | Team dry-fit actual modules; record measurements and reviewer/date below | Before prototype fabrication approval |

Record for each module: product/revision ___; measurement method ___; header pitch/order ___; hole centers/diameters ___; carrier-to-module spacing ___; underside minimum gap ___; connector engagement ___; USB/SD/antenna/sensor access ___; retention ___; deviations ___; reviewer/date ___. For printed templates, verify a known dimension with a ruler before checking fit.

Unsent manufacturer question for M01: “Could you provide a dimensioned PCB drawing or CAD for Adafruit #5440 PA1616D GPS + GLONASS, including the current preinstalled battery-holder revision? We need header pad order and coordinates, mounting-hole centers/diameters, PCB outline/thickness, and antenna/underside component envelopes. The public Ultimate GPS board file we found identifies PA6H and dates from 2017. Please confirm which drawing matches #5440.” No inquiry has been sent.

Step 3's interface work and two sensor library contracts are ready for review. Mechanical sign-off remains open at M01–M04. **Step 4 interference/placement planning can proceed using draft envelopes**, with these constraints carried forward; final placement cannot be approved until the applicable gates close. Battery sizing and main ERC/DRC cleanup remain later work.
