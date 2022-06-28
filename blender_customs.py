import hashlib
import bpy
import sys
import json
import os
os.system('cls')
#for mat in bpy.data.materials: # fix transparent materials
 #   mat.blend_method = 'OPAQUE'

def dict_to_file(file, x, sort_keys=True, indent=4):
    """Dump dictionary to json file"""
    with open(file, 'w') as f:
        json.dump(x, f, indent=indent, sort_keys=sort_keys)

def file_to_dict(file):
    """Dump json file to dict variable"""
    with open(file) as f:
        return json.load(f)

def rev_json(data):
    """Reverses dictionary (some data may be lost in the process!)"""
    return {item : key for key, item in data.items()}

def scene_to_json(dest_file):
    """Backup all meshes location, rotation and scales to json file"""
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type=='MESH']:
        name = ob.name[:-4] if '.' in ob.name else ob.name
        if name not in res:
            res[name] = []
        tmp = {
            "location": [x for x in ob.location],
            "rotation": [x for x in ob.rotation_euler],
            "scale": [x for x in ob.scale]
        }
        res[name].append(tmp)
    with open(dest_file, 'w') as fp:
        json.dump(res, fp)

def reset_broken_mats():
    """fix transparent materials"""
    for mat in bpy.data.materials: 
        mat.blend_method = 'OPAQUE'

def move_objects(objs, wector):
    """Move list of objects by vector"""
    for ob in objs:
        if wector:
            ob.location.x += float(wector[0])
            ob.location.y += float(wector[1])
            ob.location.z += float(wector[2])

def separate_by_materials(objs=None):
    """Select objects, go to edit mode, select all, split by materials"""
    if objs is None:
        objs = [ob for ob in bpy.data.objects if ob.type=='MESH']
    if objs:
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objs:
            ob.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.object.mode_set(mode='OBJECT')

def merge_objs(objs, rename_uvs=True):
    """Merge objects from provided list"""
    bpy.ops.object.select_all(action='DESELECT')
    if len(objs) >= 2: 
        if rename_uvs:
            merge_uvs(objs)
        bpy.context.view_layer.objects.active = objs[0]
        for ob in objs:
            ob.select_set(True)
        bpy.ops.object.join()
        bpy.ops.object.select_all(action='DESELECT')

def merge_all_objs():
    """Merge all mesh objects from scene"""
    objs = [ob for ob in bpy.data.objects if ob.type=='MESH']
    merge_objs(objs)

def scale_scene(w):
    """Scale all objects in a scene then scale them"""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.transform.resize(value=w, orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.select_all(action='DESELECT')

def apply_transform(objs=None):
    """Apply all transforms to list of objects"""
    bpy.ops.object.select_all(action='DESELECT')
    if objs is None: objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    if not objs: return
    bpy.context.view_layer.objects.active = objs[0]
    for ob in objs:
        ob.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')

def file_to_md5(file):
    """Return MD5 hash of a file in hex format"""
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest().upper() 

def fix_dds_textures(main_path):
    """Change all materials primary dds image (if exists) to png file named by dds file MD5 hash"""
    for mat in bpy.data.materials:
        mat.blend_method = 'OPAQUE'
    for mat in [mat for mat in bpy.data.materials if  mat and mat.node_tree]:
        print(mat.name)
        for x in [x for x in mat.node_tree.nodes if x.type=='TEX_IMAGE' and not '.0' in x.name]:
            dds = x.image.filepath
            if dds.lower().endswith('dds'):
                tex_name = file_to_md5(dds)+ '.png'
                tex_fullpath = os.path.join(main_path, tex_name)
                im = bpy.data.images.get(tex_name)
                if im is None:
                    im = bpy.data.images.load(tex_fullpath)
                x.image = im
                mat.name = tex_name[:-4]
  
def meshes_to_tex_names():
    """Rename objects to the image from the first found material slot"""
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for mat_slot in [mat_slot for mat_slot in ob.material_slots if mat_slot and mat_slot.material.node_tree]:
            for t in [os.path.basename(x.image.filepath) for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE' and not '.0' in x.name]:
                ob.name = t
                ob.data.name = t

def merge_by_names():
    """Merge all duplicated mesh objects on the scene"""
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH' and ob.name.count('.') > 1]:
        ob.name = ob.name.split('.')[0]
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH' and '.' not in ob.name[-4:]]:
        objs = [ob1 for ob1 in bpy.data.objects if ob1.type == 'MESH' and ob1.name.startswith(ob.name)]
        merge_objs(objs)
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH' and '.' in ob.name[-4:]]:
        ob.name = ob.name.split('.')[0] # Remove all .xxx from object names
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        ob.data.name = ob.name # Rename meshes to objects names
    


def transform_by_ob(obname):
    """Transform entire scene by a specific object"""
    root_ob = bpy.data.objects[obname]
    wector = [float(root_ob.location.x), float(root_ob.location.y), float(root_ob.location.z)]
    wector = [x*(-1) for x in wector]
    objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    move_objects(objs, wector)
    #apply_transform()

def leave_1_mat():
    """Remove all materials slots from meshes, except for the last one"""
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
         size = len([mat_slot for mat_slot in ob.material_slots])
         if size > 1:
             for i in range(size-1):
                ob.data.materials.pop()
                 


def get_meshes_by_armature(arm):
    """Return list of mesh objects that has armature modifier pointing to armature object arm"""
    res = []
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        mods = [m for m in ob.modifiers if m.type == 'ARMATURE']
        if mods:
            if mods[0].object == arm:
                res.append(ob)
    return res

def update_bones_dict(data, input_arm, dest_arm, objs):
    """Add missing bone keys to data dict, which is used for converting input armature to dest. armature.
    Closest parent bone is assigned to input bone or root bone if none can be found"""
    missing_vals = []
    keys = list(data)
    root_bone = [b for b in dest_arm.data.bones if b.parent is None][0] # get root bone
    for ob in objs:
        missing_vals += [vg.name for vg in ob.vertex_groups if vg.name not in keys]
    if missing_vals:
        for bone_name in [b for b in list(set(missing_vals)) if input_arm.data.bones.get(b,'')]:
            bone = input_arm.data.bones.get(bone_name)
            parent_bone = bone.parent
            while True:
                if parent_bone.name in keys:
                    data[bone_name] = data[parent_bone.name]
                    print(f'{bone_name} paired with {data[parent_bone.name]}')
                    break
                elif parent_bone is None or parent_bone.name==root_bone.name:
                    data[bone_name] = root_bone.name
                    break
                parent_bone = parent_bone.parent
    return data

def merge_vgs(ob, vgname1, vgname2):
    """Merge vertex groups"""
    if (vgname1 in ob.vertex_groups and vgname2 in ob.vertex_groups): 
        print(f'Merging vg {vgname1} -> {vgname2} in {ob.name}')
        vgroup = ob.vertex_groups.get(vgname2)   
        
        n_verts = float(len(ob.data.vertices))
        for id, vert in enumerate(ob.data.vertices):
            update_progress('Merging', (float(id))/n_verts)
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            A = B = 0
            if ob.vertex_groups[vgname1].index in available_groups:
                A = ob.vertex_groups[vgname1].weight(id)
            if ob.vertex_groups[vgname2].index in available_groups:
                B = ob.vertex_groups[vgname2].weight(id)

            # only add to vertex group is weight is > 0
            sum = A + B
            if sum > 0:
                vgroup.add([id], sum ,'REPLACE')
        update_progress('Merging', 1)

def merge_n_remove(obname, vgname1, vgname2):
    """Merge vertex groups then remove the first one"""
    ob = bpy.data.objects[obname] if isinstance(obname, str) else obname 
    if ob is not None: 
        merge_vgs(ob, vgname1, vgname2)
        vgn = ob.vertex_groups.get(vgname1)
        if vgn:
            ob.vertex_groups.remove(vgn) 

def set_weight(obname, vgname2, WEIGHT):
    """Set specified weight for all vertices in given mesh object"""
    ob = bpy.data.objects[obname] if isinstance(obname, str) else obname 
    if ob is None:
        print(f'No object named {obname} found in the scene, exiting')
    else:
        if ob.vertex_groups.get(vgname2) is None:
            ob.vertex_groups.new(name=vgname2)
        vgroup = ob.vertex_groups.get(vgname2)   
        
        n_verts = float(len(ob.data.vertices))
        for id, vert in enumerate(ob.data.vertices):
            update_progress('Merging', (float(id))/n_verts)
            vgroup.add([id], WEIGHT ,'REPLACE')
        update_progress('Merging', 1)
    
    
def update_progress(job_title, progress, length=30):
    """Progress bar for various functions"""
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

def remove_dummy_vgs(obname):
    """Removes vertex groups if none of the meshes' vertices are weighted to them"""
    ob = bpy.data.objects.get(obname)
    if ob and ob.type == 'MESH': 
        for vgn in ob.vertex_groups:
            if not any(vgn.index in [g.group for g in v.groups] for v in ob.data.vertices):
                ob.vertex_groups.remove(vgn) 

def remove_all_dummy_vgs():
    """Removes vertex groups if none of the meshes' vertices are weighted to them, 
    works for all mesh objects in the scene"""
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for vgn in ob.vertex_groups:
            if not any(vgn.index in [g.group for g in v.groups] for v in ob.data.vertices):
                print(f'Removing vg {vgn.name} in {ob.name}')
                ob.vertex_groups.remove(vgn) 


def normalize_vgs():
    """Merges all vertex groups with duplicate names (vg.001->vg) for all mesh objects"""
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for vg in [vg for vg in ob.vertex_groups if '.0' not in vg.name]:
            for i in range(1,100):
                vg_to_merge = ob.vertex_groups.get(f'{vg.name}.{str(i).zfill(3)}')
                if vg_to_merge:
                    merge_n_remove(ob, vg_to_merge.name, vg.name)
                #else:
                #    break

def merge_uvs(objs=None):
    """Renames all UV maps for all mesh objects. Useful for objects merging"""
    if objs is None:
        objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    for ob in objs:
        for uvmap in ob.data.uv_layers:
            uvmap.name = 'UVMap'

def separate_by_materials(objs=None):
    """Select objects, go to edit mode, select all, split by materials"""
    if objs is None:
        objs = [ob for ob in bpy.data.objects if ob.type=='MESH']
    if objs:
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objs:
            ob.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.object.mode_set(mode='OBJECT')

def transfer_weights_from_dict(input_data, input_arm, dest_arm):
    """Merge and rename vertex groups basing on input dictionary or json file"""
    # Get input data
    if isinstance(input_data, str):
        data = file_to_dict(input_data)
    else:
        data = input_data
    # Get only meshes which have armature modifier tied to input armature
    objs = get_meshes_by_armature(input_arm)
    remove_all_dummy_vgs()
    data = update_bones_dict(data, input_arm, dest_arm, objs) # Update missing keys
    keys = list(data)
    items = [item for key, item in data.items()]
    # Merge vgs
    for ob in objs:
        vgns = [vg.name for vg in ob.vertex_groups]
        for item in items:
            root_vg = ''
            for vg in [e for e in vgns if e in keys and data[e] == item]:
                if root_vg: 
                    merge_n_remove(ob.name, vg, root_vg)
                else:
                    root_vg = vg
    # rename remaining vgs
    for ob in objs:
        for vg in [vg for vg in ob.vertex_groups if data.get(vg.name,'')]:
            vg.name = data[vg.name]
    # Set armature modifier to dest. armature
    for ob in objs:
        for mod in [m for m in ob.modifiers if m.type == 'ARMATURE']:
            mod.object = dest_arm
            break
    # Check if any vertex group was not processed
    missing_vals = []
    for ob in objs:
        missing_vals += [vg.name for vg in ob.vertex_groups if vg.name in keys]
    n = ',\n    '
    if missing_vals:
        s = f'Warning! There are some unmerged vertex groups:\n{n.join(missing_vals)}'
    else:
        s = f'All vertex groups for meshes:\n{n.join([ob.name for ob in objs])}\n'
        s+= f'linked to armature {input_arm.name} were merged correctly'
    print(s)
    return s
    

def rotate_bone(bones, angles, arm=None, apply_rest=False, rot_mode='XYZ'):
    """Rotate bones from list of strings by specific value"""
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    if len(angles) >= 3:
        if arm is None:
            arms = [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']
        else:
            arms = [arm]
        for armature in arms:
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            for bone_name in [b for b in bones if b and armature.pose.bones.get(b)]:
                bone = armature.pose.bones.get(bone_name)
                bone.rotation_mode = rot_mode
                for i in range(3):
                    bone.rotation_euler.rotate_axis(rot_mode[i], math.radians(angles[i]))
            bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print(f'Vector {str(angles)} is invalid for rotation mode {rot_mode}')

def scale_bones(bones, scales, arm=None, inherit_scale=False):
    """Scale bones from list by given vector of floats"""
    if len(scales) >= 3:
        if arm is None:
            arms = [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']
        else:
            arms = [arm]
        for a in arms:
            for bone in a.data.bones:
                bone.use_inherit_scale = inherit_scale
            for bone in [a.pose.bones.get(b) for b in bones if b in a.pose.bones]:
                bone.scale = (scales[0], scales[1], scales[2])
    else:
        print(f'Vector {str(scales)} is invalid')
        
def apply_arm_changes(arm, Context=None):
    """Duplicate armature modifier in mesh objects tied linked to arm armature, apply it,
    then set pose as rest pose"""
    objs = get_meshes_by_armature(arm)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    if Context is None: # Context==bpy.context
        """If context is default"""
        for ob in objs:
            mods = [m for m in ob.modifiers if m.type == 'ARMATURE']
            if mods:
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                bpy.ops.object.modifier_copy(modifier=mods[0].name)
                mods_upd = [m for m in ob.modifiers if m.type == 'ARMATURE']
                bpy.ops.object.modifier_apply(modifier=mods_upd[0].name)
                ob.select_set(False)
    else:
        """A wacky workaround when fuction used in UI. Backs up all modifiers to dict,
        removes non-armature modifiers, applies the rest, then restores modifiers"""
        mods = {} # used for modifiers backup
        for ob in objs:
            mods[ob] = {}
            for m in ob.modifiers:
                mods[ob][m.name] = {}
                properties = [p.identifier for p in m.bl_rna.properties if not p.is_readonly]
                mods[ob][m.name]['Properties'] = {prop:getattr(m, prop) for prop in properties}
                mods[ob][m.name]['Type'] = m.type
            for m in [m for m in ob.modifiers if m.type != 'ARMATURE']:
                ob.modifiers.remove(m) # remove non-armature modifiers
            Context.view_layer.objects.active = ob # doesnt work with UI, but it stays nonetheless
            ob.select_set(True)
        bpy.ops.object.convert(target='MESH') # Applies all modifiers
        bpy.ops.object.select_all(action='DESELECT')
        for ob, item in mods.items(): # restore from backup
            for mod_name, data in item.items():
                mod_new = ob.modifiers.new(mod_name, data['Type'])
                for prop, attr in data['Properties'].items():
                    setattr(mod_new, prop, attr) # restore modifier's original attributes
    bpy.ops.object.select_all(action='DESELECT')
    # Apply pose as rest pose for armature arm
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.armature_apply(selected=False)
    bpy.ops.object.mode_set(mode='OBJECT')
            
def textures_to_dict():
    """Return dictionary of all meshes on scene with their respective materials and
    image textures filepaths"""
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        res[ob.name] = {}
        for mat_slot in [mat_slot for mat_slot in ob.material_slots if mat_slot and mat_slot.material.node_tree]:
            res[ob.name][mat_slot.material.name] = [x.image.filepath for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE']              
    return res


def remove_all(excluded=['scenes', 'texts']):
    """Remove images, armatures, materials, meshes, objects, textures from scene"""
    for asset_type in ['images','armatures','materials','meshes','objects','textures']:
        if not asset_type in excluded:
            data = getattr(bpy.data, asset_type)
            try:
                for elem in data:
                    data.remove(elem)
            except:
                print('Skipping asset: {}'.format(asset_type))