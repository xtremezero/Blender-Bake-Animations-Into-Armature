import bpy
from mathutils import Matrix

scene = bpy.context.scene
parent = bpy.context.active_object
children = list(parent.children)

# ---------- 1. Create the armature with one bone per child ----------
arm_data = bpy.data.armatures.new("CombinedArm")
arm = bpy.data.objects.new("CombinedArm", arm_data)
scene.collection.objects.link(arm)

bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = arm
arm.select_set(True)

bpy.ops.object.mode_set(mode='EDIT')
for c in children:
    b = arm_data.edit_bones.new(c.name)
    b.head = (0, 0, 0)
    b.tail = (0, 0, 0.1)

# ---------- 2. Copy Transforms constraints ----------
bpy.ops.object.mode_set(mode='POSE')
for c in children:
    con = arm.pose.bones[c.name].constraints.new('COPY_TRANSFORMS')
    con.target = c

# ---------- 3. Bake everything into one action ----------
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.nla.bake(
    frame_start=scene.frame_start,
    frame_end=scene.frame_end,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'},
)
bpy.ops.object.mode_set(mode='OBJECT')

if arm.animation_data and arm.animation_data.action:
    arm.animation_data.action.name = "CombinedAction"

# ---------- 4. Clear old animation and parent each child to its bone ----------
for c in children:
    bone = arm.data.bones[c.name]

    c.animation_data_clear()          # remove old action so it doesn't double-apply
    c.parent = None
    c.matrix_world = Matrix.Identity(4)

    c.parent = arm
    c.parent_type = 'BONE'
    c.parent_bone = bone.name
    # Bone parenting is relative to the bone's tail, so cancel that offset
    c.matrix_parent_inverse = Matrix.Translation((0, -bone.length, 0))

print("Done: baked", len(children), "objects into", arm.animation_data.action.name)a
