# Teensy 4.1 drawing comparison

Reviewed October 18, 2026 against the [PJRC drawing supplied by Saadat](reference/dimensions_teensy41.png). The PNG is preserved byte-for-byte with its SHA-256 in the [native measurement report](validation/2026-10-18/teensy-dimension-check.json). It was supplied locally; no blocked network route was used. Upstream reference: [PJRC dimension drawing](https://www.pjrc.com/teensy/dimensions_teensy41.png).

## Confirmed nominal geometry

KiCad 10.0.7 loaded `TEENSY41_SIMPLE` from the imported library. Its pad geometry also matches the instance U$3 on the main PCB after translation/rotation normalization in memory. Neither file was changed.

| Feature | Supplied drawing | Imported footprint | Finding |
| --- | --- | --- | --- |
| Board length | 60.96 mm | Outline X −29.337 to 31.623 mm | Matches nominal |
| Board width | 17.78 mm, marked ±0.6 mm | Outline Y −8.89 to +8.89 mm | Matches nominal; preserve tolerance in enclosure/clearance review |
| Edge headers | Two rows of 24 positions | 48 through-hole pads | Matches position count |
| Header pitch | 2.54 mm | All 23 intervals in each row are 2.54 mm | Matches |
| Header row separation | 15.24 mm | Y −7.62 to +7.62 mm | Matches |
| End pad to board edge | 1.27 mm at USB end; opposite end follows from length/grid | First/last centers X −28.067/30.353 mm | Both nominal margins 1.27 mm |

This is a geometric comparison. The dimension drawing has no electrical pin labels, so it does not independently verify VIN/GND/GPIO numbering. The interface/pin-function review remains in SENSOR_CONNECTION_MAP.md. Interior headers and underside pads shown in the drawing are not electrical pads in this simplified footprint; the proposed logger uses the side headers. Revisit them if the circuit later uses an interior connection.

## Findings in the imported footprint (retained baseline)

1. **Carrier drills are not approved.** Native readback found 47 drills of 0.85 mm and pin 10 at 0.90 mm. Corresponding pad sizes are 1.358 and 1.408 mm, respectively. The module dimension drawing does not specify the required carrier connector drill. For perspective, a nominal 0.635 mm square tail has a 0.898 mm diagonal, already larger than a 0.85 mm round hole before tolerances. A socket may have a different tail shape; select the exact Teensy connector and follow its recommended pattern. Do not copy sensor socket dimensions blindly or enlarge drills without reviewing pad annulus/routing.
2. **Mechanical outlines are only silkscreen.** All 232 imported graphics are on F.Silkscreen; no F.Fab or courtyard graphics were found. Add a usable module envelope, courtyard and appropriate underside/component restrictions during the footprint/layout update. A decorative outline does not enforce clearance.
3. **USB drawing detail differs.** The imported front outline extends 1.27 mm beyond the nominal board end, while the supplied side view labels 0.7 mm overhang. Its drawn width is 7.62 mm versus the drawing's 7.5 mm USB dimension. Treat the imported graphic as approximate, not a dimensioned connector model. Reserve the real plug body and insertion/removal path separately; a connector outline alone does not capture cable access.
4. **Height and access still need assembly review.** The drawing specifies 1.57 mm board thickness and a 3.07 mm USB height above the board surface. Add those to the selected carrier-to-module spacing when checking enclosure height. Underside additions, solder joints and actual module revision need inspection. The supplied drawing does not establish a complete installed microSD/card-removal envelope. Keep USB, microSD and the program button accessible and check them with actual parts.

## Gate status

The missing-drawing dependency and nominal board/side-header comparison are closed. The separate draft carrier below now addresses drill selection and footprint constraints. M02 retains installed USB/SD/underside access and retention checks; M03/M04 retain final parts/tolerances and physical fit. GPS M01 remains open.

The imported Teensy footprint and main schematic/PCB remain unchanged; the new carrier is a separate library asset. No new circuit ERC/DRC or physical fit test was performed. Step 4 interference planning can proceed with the confirmed nominal envelope and the listed clearance requirements.

## Draft carrier implementation

`Pterodactyl_Modules:Teensy41_SSW_Carrier` is now available for later schematic assignment. It preserves all 48 imported pad identifiers and XY positions, including the three distinct GND identifiers and two 3.3V identifiers; this does not approve the legacy power-net names as independent rails. The origin remains unchanged to simplify a reviewed replacement during Step 5. No interior header connections or invented mechanical holes were added.

The carrier uses two **SSW-124-01-L-S** 24-position sockets, with 1.04 mm drills and 1.8 mm copper pads on all 48 positions. These replace the mixed drill sizes in the draft, with a nominal 0.38 mm radial annulus. The socket bodies are shown on F.Fab. Source: [configured Samtec socket](https://www.samtec.com/products/ssw-124-01-l-s), [single-row recommended footprint](https://suddendocs.samtec.com/prints/ssw-s.pdf). Fabricator tolerance and procurement checks remain required.

Use two candidate HTSW-124-07-L-S module headers from the previously reviewed HTSW family. Their configured orderability must be confirmed; if the Teensy arrives with headers already fitted, check their post dimensions rather than assuming interchangeability. At full nominal seating, the proposed SSW/HTSW pair separates the carrier top and Teensy underside by 11.05 mm. This places the USB top at 11.05 + 1.57 + 3.07 = **15.69 mm above the carrier top**, before tolerances. This is not the overall assembly maximum or an enclosure specification. The 12 mm sensor standoff proposal does not apply automatically to Teensy. [TSW/HTSW dimensions](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf).

The draft includes a nominal module/USB F.Fab outline, F.CrtYd boundary and an **F.Cu component keepout** beneath the module. It rejects other front-side footprints while allowing tracks, vias and copper pours for signal routing and return planes. It is not a universal three-dimensional collision check: through-hole leads from the opposite side still require inspection. The courtyard conservatively includes socket ends, the USB body and allowance for board width. Drawing-layer USB/SD access boxes reserve proposed 15 × 12 mm and 20 × 16 mm working spaces respectively; these are planning allowances, not measured plug/card dimensions or enforced keepouts. Check the actual cable, card removal path and enclosure before fixing placement.

Teensy has no dedicated mounting holes in this proposal. Enclosure support or a suitable nonconductive retainer must resist extraction without pressing on components or preventing USB, card or button access. Do not drill the module or rely on socket friction as proven flight retention. Retainer geometry depends on the enclosure and remains an assembly gate.

Validation: all 48 pad identifiers/coordinates match the imported footprint; native reads confirm 1.04 mm drills, 1.8 mm pads, F.Fab/courtyard and the component rule area. Clear fixture and outside-component control each report **0 violations/0 unconnected items**. A deliberately intruding resistor produces `items_not_allowed` and `courtyards_overlap`, confirming that the rule area is enforced. Those two errors are expected test evidence, not a released board defect. [Check report](validation/2026-10-18/step3-teensy/carrier-check.json), [native preview](validation/2026-10-18/step3-teensy/Teensy41_SSW_Carrier.svg).

Reproduce with `tools/generate_teensy_carrier.py` using Python 3, followed by `tools/verify_teensy_carrier.py` with KiCad Python. The latter accepts optional CLI and installed standard-footprint-directory paths. Fixtures are netless test boards with default configured DRC categories; they do not supersede main-circuit ERC/DRC or physical tests.
