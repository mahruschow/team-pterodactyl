"""Editable CadQuery model; dimensions in millimetres. Run with cadquery installed."""
from pathlib import Path
import json, math, hashlib, sys
import cadquery as cq
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
BOARD = 97.79
BOARD_T = 1.6
OUTER = BOARD + 8
INNER = OUTER - 16
BASE = 3.0
PCB_UNDERSIDE = 13.0
POST_D = 7.0
LOWER_POST_D = 9.0
HOLE_D = 3.4
HEAD_D = 6.4
HEAD_DEPTH = 3.2
# Actual H1-H4 centers from the native KiCad file, translated about the
# outline center (148.5011,105.0036); CAD Y points up, opposite KiCad Y.
HOLES = [(-45.0851,45.0846),(45.0849,45.0846),
         (-45.0851,-45.0854),(45.0849,-45.0854)]

holder = cq.Workplane('XY').rect(OUTER, OUTER).extrude(BASE).edges('|Z').fillet(3)
opening = cq.Workplane('XY').rect(INNER, INNER).extrude(BASE+1).edges('|Z').fillet(4)
holder = holder.cut(opening)
for x,y in HOLES:
    holder = holder.union(cq.Workplane('XY').center(x,y).circle(LOWER_POST_D/2).extrude(4))
    holder = holder.union(cq.Workplane('XY').workplane(offset=3).center(x,y).circle(POST_D/2).extrude(10))
    holder = holder.cut(cq.Workplane('XY').center(x,y).circle(HOLE_D/2).extrude(PCB_UNDERSIDE+1))
    holder = holder.cut(cq.Workplane('XY').center(x,y).circle(HEAD_D/2).extrude(HEAD_DEPTH))
holder = holder.clean()
assert holder.val().isValid() and len(holder.solids().vals()) == 1
cq.exporters.export(holder, str(OUT/'Pterodactyl-holder.step'))
cq.exporters.export(holder, str(OUT/'Pterodactyl-holder.stl'), tolerance=0.05, angularTolerance=0.12)

board = cq.Workplane('XY').workplane(offset=PCB_UNDERSIDE).rect(BOARD, BOARD).extrude(BOARD_T).edges('|Z').fillet(3.81)
for x,y in HOLES:
    board=board.cut(cq.Workplane('XY').workplane(offset=PCB_UNDERSIDE).center(x,y).circle(1.6).extrude(BOARD_T))
assert holder.intersect(board).val().Volume() < 1e-6
assembly=cq.Assembly(name='Pterodactyl_holder_with_reference_PCB')
assembly.add(holder, name='PRINT_THIS_holder', color=cq.Color(0.12,0.33,0.47))
assembly.add(board, name='REFERENCE_ONLY_unpopulated_PCB', color=cq.Color(0.12,0.5,0.28))
assembly.save(str(OUT/'Holder-with-reference-PCB.step'))

mesh=trimesh.load_mesh(OUT/'Pterodactyl-holder.stl')
assert mesh.is_watertight and mesh.is_winding_consistent
assert len(mesh.split()) == 1 and mesh.volume > 0
assert np.allclose(mesh.extents,[OUTER,OUTER,PCB_UNDERSIDE],atol=.001)
reimport=cq.importers.importStep(str(OUT/'Pterodactyl-holder.step'))
assert reimport.val().isValid() and len(reimport.solids().vals())==1
assert abs(reimport.val().Volume()-holder.val().Volume())<1e-4

fig=plt.figure(figsize=(13,7.3),facecolor='#f6f8fb')
def draw(ax,show_board=False):
    triangles=mesh.triangles
    normals=mesh.face_normals
    light=np.array([-.3,-.4,.85]);light/=np.linalg.norm(light)
    intensity=.56+.44*np.maximum(0,normals@light)
    colors=np.c_[np.array([.17,.42,.57])[None,:]*intensity[:,None],np.ones(len(triangles))]
    ax.add_collection3d(Poly3DCollection(triangles,facecolors=colors,edgecolors='none'))
    if show_board:
        verts,faces=board.val().tessellate(.1)
        va=np.array([[v.x,v.y,v.z] for v in verts]); fa=np.array(faces)
        ax.add_collection3d(Poly3DCollection(va[fa],facecolors=(.16,.65,.39,.28),edgecolors='none'))
        ax.text(0,0,17,'PCB reference\ncomponents omitted',ha='center',fontsize=10,color='#165335')
    ax.set(xlim=(-57,57),ylim=(-57,57),zlim=(0,32))
    ax.set_box_aspect((114,114,32)); ax.view_init(elev=29,azim=-55)
    ax.set_axis_off();ax.set_facecolor('#f6f8fb')
ax=fig.add_subplot(121,projection='3d');draw(ax)
ax.set_title('Printable open frame',fontsize=15,pad=-8,color='#18344b')
ax=fig.add_subplot(122,projection='3d');draw(ax,True)
ax.set_title('PCB mounted on four supports',fontsize=15,pad=-8,color='#18344b')
fig.suptitle('PTERODACTYL · PCB holder',fontsize=23,fontweight='bold',color='#18344b',y=.97)
fig.text(.5,.08,'105.79 × 105.79 × 13 mm  |  90.17 mm hole spacing  |  10 mm clearance above frame',ha='center',fontsize=12,color='#18344b')
fig.text(.5,.035,'Concept for assembly / bench use · existing PCB unchanged · physical fit not yet checked',ha='center',fontsize=10,color='#566674')
plt.subplots_adjust(left=0,right=1,bottom=.12,top=.87,wspace=-.15)
fig.savefig(OUT/'Pterodactyl-holder-preview.png',dpi=180,facecolor=fig.get_facecolor())
result={'units':'mm','outer_dimensions':[OUTER,OUTER,PCB_UNDERSIDE],
 'pcb_dimensions':[BOARD,BOARD,BOARD_T],'hole_centers':HOLES,'through_hole_diameter':HOLE_D,
 'head_recess_diameter':HEAD_D,'head_recess_depth':HEAD_DEPTH,
 'support_contact_diameter':POST_D,'clearance_above_frame':10,
 'solid_volume_mm3':holder.val().Volume(),'watertight_stl':True,'stl_single_body':True,
 'step_reimport_valid':True,'reference_pcb_intersection_mm3':0,
 'scope':'Geometry and file checks only; component/hardware interference and physical printed fit not proven.'}
(OUT/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
