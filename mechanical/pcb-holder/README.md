# Pterodactyl open PCB holder

Quick holder concept for assembly and bench use. It is not the eventual flight enclosure. The PCB design was not changed.

## Files

- **Pterodactyl-holder.stl** — printable holder only, units millimetres.
- **Pterodactyl-holder.step** — solid CAD holder for import/editing.
- **Holder-with-reference-PCB.step** — assembly with a simplified bare PCB for positioning. The green PCB is reference geometry; do not print it. Components are not modeled.
- **create_pcb_holder.py** — editable CadQuery source; change parameters at the top. Requires cadquery, trimesh, numpy and matplotlib. Run `python create_pcb_holder.py` to regenerate files alongside the source, or pass an output directory.
- **geometry-check.json** — solid, mesh and export validation results.
- **Pterodactyl-holder-preview.png** — holder and reference board preview.

## Dimensions and mounting

The native P1 board is 97.79 x 97.79 x 1.6 mm. Its four 3.2 mm holes are spaced 90.17 mm in X and Y. Exact native hole centers, including sub-micron outline offsets, are used in the CAD model.

Holder overall dimensions: 105.79 x 105.79 x 13 mm. Frame thickness: 3 mm. The PCB underside rests at 13 mm, leaving 10 mm above the frame for underside leads. Four 7 mm diameter contact surfaces support the existing corner holes. The center and sides remain open.

Use four **M3 x 16 mm screws**, with heads no larger than 6.0 mm diameter and 3.0 mm high, and four matching nuts. Head recesses are 6.4 mm diameter x 3.2 mm deep; shaft holes are 3.4 mm diameter. Insert screws upward from the underside before placing the PCB, then fit the nuts above the PCB. Nonconductive hardware follows the PCB's existing mounting approach. Check the actual hardware dimensions before assembly; no threads are printed into the holder. Do not overtighten against the PCB or plastic supports.

The 3 mm frame lies flat on the print bed, supports upward. STL units are millimetres. Printer tolerances, shrinkage and horizontal-hole/bridge behavior depend on process; printed holes may need finishing. No particular printing material or cold-temperature rating has been qualified.

The file checks confirm a valid single solid, a closed manifold STL, STEP reimport and no overlap with the simplified bare-board reference. They do not prove printed fit or full component/hardware clearance. This holder carries only the PCB; the battery holder, switch bracket, cable strain relief and flight attachment are not included.

Native source: Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb, SHA-256 3939c94d0d2279776b6aff804f6814c09e275b59fea913cd9d96c8ba36f766a6.
