import bpy, os, json,sys, time
os.system('cls')

def merge_uvs():
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for uvmap in ob.data.uv_layers:
            uvmap.name = 'UVMap'

def print_weights():
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for id, vert in enumerate(ob.data.vertices):
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            for vgn in ob.vertex_groups:
                if vgn is None: continue
                if ob.vertex_groups[vgn.name].index in available_groups:
                    print(ob.name, vgn.name, id, ob.vertex_groups[vgn.name].weight(id))

def weights_to_json():
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        res[ob.name] = {
            "vertex_groups": {}
        }
        for id, vert in enumerate(ob.data.vertices):
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            for vgn in ob.vertex_groups:
                if vgn is None: continue
                if not vgn.name in res[ob.name]["vertex_groups"]: res[ob.name]["vertex_groups"][vgn.name] = []
                if ob.vertex_groups[vgn.name].index in available_groups:
                    res[ob.name]["vertex_groups"][vgn.name].append([id, ob.vertex_groups[vgn.name].weight(id)])
                    print(ob.name, vgn.name, id, ob.vertex_groups[vgn.name].weight(id))
                if res[ob.name]["vertex_groups"][vgn.name] == []: del res[ob.name]["vertex_groups"][vgn.name]
    return res


def rotate_bone(bones, angles, apply_rest=False):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        for bone_name in bones:
            bone = armature.pose.bones.get(bone_name)
            if bone is None:
                print(f'bone {bone_name} not found in {armature.name}')
                continue
            bone.rotation_mode = 'XYZ'
            if angles[0]: bone.rotation_euler.rotate_axis('X', math.radians(angles[0]))
            if angles[1]: bone.rotation_euler.rotate_axis('Y', math.radians(angles[1]))
            if angles[2]: bone.rotation_euler.rotate_axis('Z', math.radians(angles[2]))
            bpy.ops.object.mode_set(mode='OBJECT')
        if apply_rest: bpy.ops.pose.armature_apply(selected=False)


def scale_bones(bones, scales, inherit_scale = False):
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        if armature is None: continue
        for bone in armature.data.bones:
            if bone is None: continue
            bone.use_inherit_scale = inherit_scale
        for bone_name in bones:
            bone = armature.pose.bones.get(bone_name)
            if bone is None: continue
            bone.scale = (scales[0], scales[1], scales[2])


def file_to_json(file):
    return json.load(open(file)) 

def json_to_file(file, x):
    with open(file, 'w') as f:
        json.dump(x, f, indent=4, sort_keys=True)

def update_progress(job_title, progress):
    length = 30 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

def rev_json(data):
    res = { }
    for elem in data:
        res[data[elem]] = elem
    return res

def vgs_to_json_template(output_file):
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        if ob is None: continue
        for vgn in ob.vertex_groups:
            if vgn and vgn.name:
                res[vgn.name] = "asdf"
    json_to_file(output_file, res)
    
def merge_vgs(ob, vgname1, vgname2):
    if '.0' in vgname1[-4:]:
        vgname2 = vgname1[:-4]

    if not (vgname1 in ob.vertex_groups and vgname2 in ob.vertex_groups): return
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

def set_weight(obname, vgname2, WEIGHT):
    ob = bpy.context.scene.objects[obname]  
    if ob is None: return
    if ob.vertex_groups.get(vgname2) is None:
        ob.vertex_groups.new(name=vgname2)
    vgroup = ob.vertex_groups.get(vgname2)   
    
    n_verts = float(len(ob.data.vertices))
    for id, vert in enumerate(ob.data.vertices):
        update_progress('Merging', (float(id))/n_verts)
        available_groups = [v_group_elem.group for v_group_elem in vert.groups]
        if ob.vertex_groups[vgname2].index in available_groups:
            B = ob.vertex_groups[vgname2].weight(id)

        vgroup.add([id], WEIGHT ,'REPLACE')
    update_progress('Merging', 1)


def transfer_weights(ob, vgname1, vgname2):
    if ob is None or ob.type != 'MESH': return
    if not vgname1: return
    if not vgname2: return
    if ob.vertex_groups.get(vgname1) is None: return
    if ob.vertex_groups.get(vgname2) is None:
        ob.vertex_groups.new(name=vgname2)
    merge_vgs(ob, vgname1, vgname2)
    return
    
    
def rename_bones(data):
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        done = []
        for bone in armature.data.bones:
            pb = armature.pose.bones.get(bone.name)
            if pb is None: continue
            if bone.name in data:
                tmp = armature.pose.bones.get(data[bone.name])
                if not tmp:
                    pb.name = data[bone.name]
    #fix_00_bones()
    
def fix_00_bones():
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        for bone in armature.data.bones:
            pb = armature.pose.bones.get(bone.name)
            if pb is None: continue
            if '.0' in bone.name: bone.name = bone.name.split('.0')[0]

def get_parents_bones_list():
    bones = []
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        for bone in armature.data.bones:
            if armature.pose.bones.get(bone.name) is None: continue
            tmp = [bone.name]
            parent_bone = bone.parent
            for i in range(100):
                if parent_bone is None: break
                tmp.append(parent_bone.name)
                parent_bone = parent_bone.parent
            bones.append(tmp)
    return bones

def pair_rest_bones(data):
    bones = get_parents_bones_list()
    rev_data = rev_json(data)
    res = { }
    for bone in bones:
        if bone[0] in rev_data: continue
        direct_parent = ''
        for i in range(1, len(bone)):
            if bone[i] in rev_data:
                direct_parent = bone[i]
                break
        res[bone[0]] = direct_parent
    return res
    

def transfer_weights_from_json(json_file):
    remove_all_dummy_vgs()
    data = file_to_json(json_file)
    rename_bones(data)
    for elem in data:
        new_vg = data[elem]
        for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
            if not ob.vertex_groups: continue
            transfer_weights(ob, elem, new_vg)
    pairs = pair_rest_bones(data)
    for elem in pairs:
         new_vg = pairs[elem]
         for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
            if not ob.vertex_groups: continue
            transfer_weights(ob, elem, new_vg)
    #complete_vgroups()
    rev_data = rev_json(data)
    
    for elem in data:
        new_vg = data[elem]
        for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
            if ob is None: continue
            for vgn in ob.vertex_groups:
                if vgn is None: continue
                mtvg = not any(vgn.index in [g.group for g in v.groups] for v in ob.data.vertices)
                if not vgn.name in rev_data or mtvg:
                    print(f'Removing vg {vgn.name} in {ob.name}')
                    ob.vertex_groups.remove(vgn) 
    
    for elem in pairs:
         new_vg = pairs[elem]
         for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
            if ob is None: continue
            for vgn in ob.vertex_groups:
                if vgn is None: continue
                if not vgn.name in rev_data:
                    print(f'Removing vg {vgn.name} in {ob.name}')
                    ob.vertex_groups.remove(vgn) 
                                
                
def merge_n_remove(obname, vgname1, vgname2):
    ob = bpy.context.scene.objects[obname]  
    if ob is None: return
    merge_vgs(ob, vgname1, vgname2)
    vgn = ob.vertex_groups.get(vgname1)
    if vgn:
        ob.vertex_groups.remove(vgn) 

def remove_dummy_vgs(obname):
    ob = bpy.context.scene.objects[obname]  
    if ob is None or ob.type != 'MESH': return
    for vgn in ob.vertex_groups:
        if vgn is None: continue
        mtvg = not any(vgn.index in [g.group for g in v.groups] for v in ob.data.vertices)
        if mtvg:
            ob.vertex_groups.remove(vgn) 

def remove_all_dummy_vgs():
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        if ob is None: continue
        for vgn in ob.vertex_groups:
            if vgn is None: continue
            mtvg = not any(vgn.index in [g.group for g in v.groups] for v in ob.data.vertices)
            if mtvg:
                print(f'Removing vg {vgn.name} in {ob.name}')
                ob.vertex_groups.remove(vgn) 

def merge_all_meshes():
    merge_uvs()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        ob.select_set(True)
    bpy.ops.object.join()

def apply_arm_changes():
    merge_all_meshes()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    
    #for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
    for ob in bpy.data.objects:
        if ob.type != 'MESH': continue
        #if len(ob.modifiers) > 1: continue
        print(ob.name, len(ob.modifiers), ob.modifiers)
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        for mSrc in ob.modifiers:
            #bpy.ops.object.modifier_copy(modifier=mSrc.name)
            name = mSrc.name
            break
        bpy.ops.object.modifier_copy(modifier=mSrc.name)
        bpy.ops.object.modifier_apply(modifier=name)
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(False)
    for ob in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        arm = ob    
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply(selected=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        return

def test():
    merge_all_meshes()
    scale_bones(['Arm_1_L','Arm_1_R','Clavicle_Assist_L','Clavicle_Assist_R','','','Clavicle_L','Clavicle_R','','',''], [1,1.5,1.5])
    scale_bones(['Elbow_L','Elbow_R','Arm_2_L','Arm_2_R','Wrist_L','Wrist_R','Wrist_Assist_R','Wrist_Assist_L','','',''], [1,1.3,1.3])
    scale_bones(['Spine_2','Spine_1','Neck','Leg_1_L','Leg_1_R','Leg_2_L','Leg_2_R','Knee_L','Knee_R','',''], [1.25,1,1.25])
    scale_bones(['Ankle_L','Ankle_R','Ankle_Assist_R','','','','','','','Ankle_Assist_L',''], [1.25,1,1.25])

    #apply_arm_changes()

#test()
def textures_to_json():
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        #print(f'mesh: {ob.name}')
        res[ob.name] = { }
        for mat_slot in [mat_slot for mat_slot in ob.material_slots if mat_slot and mat_slot.material.node_tree]:
            #if mat_slot.material.node_tree:
            #print("material:" + str(mat_slot.material.name))
            res[ob.name][mat_slot.material.name] = []                
            for x in mat_slot.material.node_tree.nodes:
                if x.type=='TEX_IMAGE':
                    res[ob.name][mat_slot.material.name].append(x.image.filepath)
                    #print(" texture: "+str(x.image.filepath))
    return res

def meshes_to_images():
    data = textures_to_json()
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for mat in data[ob.name]:
            try:
                ob.name = os.path.basename(data[ob.name][mat][0])
                break
            except: pass

def move_bone(name, tab, fr_count):
    for ob in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        arm = ob    
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        for fr in range(fr_count):
            bpy.context.scene.frame_set(fr)
            #name = "Skl_Root"
            pb = ob.pose.bones.get(name) # None if no bone named name

            X = pb.location[0] + tab[0]
            Y = pb.location[1] + tab[1]
            Z = pb.location[2] + tab[2]
            pb.location = (X, Y, Z)
            pb.keyframe_insert("location", frame=fr)
        bpy.context.scene.frame_set(0)


#move_bone('Skl_Root', [0,-0.343088,0], 140)