import bpy,os,random,json
from blender_customs import rotate_bone,remove_all_dummy_vgs,json_to_file,update_progress,merge_uvs
os.system('cls')


def get_colors():
    colors = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        if ob is None: continue
        for vgn in ob.vertex_groups:
            if vgn is None: continue
            if vgn.name in colors: continue
            colors[vgn.name] = [random.random(),random.random(),random.random(),1.0]
    return colors

def get_color_for_vert(ob, vert, weights, colors):
    res_color = [0.0,0.0,0.0]
    for vg in weights[ob.name][vert]:
        for i in range(3):
            res_color[i] += colors[vg][i] * weights[ob.name][vert][vg]
    return (res_color[0], res_color[1], res_color[2], 1.0)
        

def paint():
    weights = weights_to_json()
    colors = get_colors()
    polygons = get_polygons()
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        if not ob.vertex_groups: continue
        if ob.data.vertex_colors: vcol_layer = ob.data.vertex_colors.active
        else: vcol_layer = ob.data.vertex_colors.new()
        
        n_vert = float(len(ob.data.vertices))
        for i in range(len(ob.data.vertices)):
            update_progress(f'Enumerating colors for {ob.name} ', float(i)/n_vert)
            if not i in weights[ob.name]: continue
            color_vertex(ob, i, get_color_for_vert(ob, i, weights, colors), vcol_layer, polygons)
        update_progress(f'Enumerating colors for {ob.name} done ', 1)
            

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
        res[ob.name] = {      }
        n_verts = float(len(ob.data.vertices))
        for id, vert in enumerate(ob.data.vertices):
            update_progress(f'Enumerating weights for {ob.name} ', (float(id))/n_verts)
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            for vgn in ob.vertex_groups:
                if vgn is None: continue
                if ob.vertex_groups[vgn.name].index in available_groups:
                    if not id in res[ob.name]: res[ob.name][id] = {}
                    if not vgn.name in res[ob.name][id]: res[ob.name][id][vgn.name] = {}
                    res[ob.name][id][vgn.name] = ob.vertex_groups[vgn.name].weight(id)
        update_progress(f'Enumerating weights for {ob.name} done', 1)
    return res

def get_polygons():
    res = {}
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        res[ob.name] = {      }
        for poly in ob.data.polygons:
            for loop_index in poly.loop_indices:
                loop_vert_index = ob.data.loops[loop_index].vertex_index
                if not loop_vert_index in res[ob.name]: res[ob.name][loop_vert_index] = []
                res[ob.name][loop_vert_index].append(loop_index)
    return res
            

def color_vertex(obj, vert, color,vcol_layer, polygons):
    mesh = obj.data 
    if vert in polygons[obj.name]:
        for loop_index in polygons[obj.name][vert]:
            vcol_layer.data[loop_index].color = color
            
def merge_all_meshes():
    merge_uvs()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        ob.select_set(True)
    bpy.ops.object.join()

def remove_all_vertex_colors():
    for ob in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
        for vertexcolor in ob.data.vertex_colors:
            vertexcolor.active = True
            bpy.ops.mesh.vertex_color_remove() 


#json_to_file('D:\\Shared_Files\\Sync\\JSON\\weights.json', weights_to_json())
#color_to_vertices(color_to_vertices)
#remove_all_dummy_vgs()
#remove_all_vertex_colors()
#paint()
#merge_all_meshes()
            