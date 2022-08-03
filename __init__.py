import bpy
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty
from bpy.utils import register_class, unregister_class
from bpy.types import Panel, Operator, WindowManager
from bpy_extras.io_utils import ImportHelper
import os, sys
import inspect
from blender_customs.blender_customs import *
os.system('cls')
BLANK_TUPLE = (('None','',''),)

bl_info = {
	"name": "Blender Customs",
	"author": "banan039",
	"version": (0, 0, 2),
	"blender": (2, 90, 0),
	"category": "Import",
	"location": "Object properties",
	"wiki_url": "https://github.com/banan039pl/blender_customs",
	"description": "Various functions for automating work with meshes, armatures and vertex groups"
}


"""Buttons"""
class Buttons_Local:
    
    class OT_scene_to_json_filebrowser(Operator, ImportHelper):
        """Save scene locations, rotations and scales to json file"""
        bl_idname = "scene_to_json.open_filebrowser"
        bl_label = "Save scene locations, rotations and scales to json file"

        def execute(self, context):
            ff = str(self.filepath)
            if ff:
                if not ff.lower().endswith('.json'):
                    ff += '.json'
                scene_to_json(ff)
            return {'FINISHED'}
    
    class transfer_weights_OT_filebrowser(Operator, ImportHelper):
        """Merge and rename vertex groups basing on input dictionary or json file"""
        bl_idname = "transfer_weights.open_filebrowser"
        bl_label = "Merge and rename vertex groups basing on input dictionary or json file"

        def execute(self, context):
            ff = str(self.filepath)
            sc = context.scene
            arm1 = bpy.data.objects.get(sc.armatures1)
            arm2 = bpy.data.objects.get(sc.armatures2)
            if ff and arm1 and arm2:
                transfer_weights_from_dict(ff,arm1,arm2)
            return {'FINISHED'}
        
    
    class rename_meshes_to_md5_dds_OT_op(Operator):
        bl_idname = 'rename_meshes_to_md5_dds.vgs_op'
        bl_label = 'Renaming meshes to md5 hash of dds texture. Proceed?'
        bl_description = """Renames meshes to md5 hash of dds texture assigned to its material. 
                            Meshes with no materials or with materials with no dds images are skipped."""
        
        def execute(self, context):
            meshes_to_texture_md5()
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    
    class clear_scene_OT_vgs_op(Operator):
        bl_idname = 'clear_scene.vgs_op'
        bl_label = 'This operation CANNOT be undone! Proceed?'
        bl_description = """Remove all objects, meshes, materials and images from current scene"""
        
        def execute(self, context):
            remove_all()
            #bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD')
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    class apply_armatures_OT_vgs_op(Operator):
        bl_idname = 'apply_armatures.vgs_op'
        bl_label = ''
        bl_description = """Duplicates armature modifier for meshes connected to selected armature, applies original and sets current pose as rest pose selected armature"""
        
        def execute(self, context):
            arm_name = context.scene.armatures
            if arm_name:
                arm = bpy.data.objects.get(arm_name)
                if arm:
                    apply_arm_changes(arm, Context=context)
            return {'FINISHED'}

    class reset_broken_mats_OT_vgs_op(Operator):
        bl_idname = 'reset_broken_mats.vgs_op'
        bl_label = ''
        bl_description = """Fixes odd looking materials for meshes on scene"""
        
        def execute(self, context):
            reset_broken_mats()
            return {'FINISHED'}
    
    class split_objs_by_material_OT_vgs_op(Operator):
        bl_idname = 'split_objs_by_material.vgs_op'
        bl_label = ''
        bl_description = """Splits meshes by materials"""
        
        def execute(self, context):
            if context.scene.all_meshes:
                objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
            else:
                objs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
            if objs: separate_by_materials(objs=objs)
            return {'FINISHED'}
    
    class apply_transform_OT_vgs_op(Operator):
        bl_idname = 'apply_transform.vgs_op'
        bl_label = 'Applying transform for multiple objects. Proceed?'
        bl_description = """Apply transform for mesh objects"""
        
        def execute(self, context):
            if context.scene.all_meshes:
                objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
            else:
                objs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
            if objs: apply_transform(objs=objs)
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    class merge_meshes_OT_vgs_op(Operator):
        bl_idname = 'merge_meshes_.vgs_op'
        bl_label = ''
        bl_description = """Merges meshes in current scene. Select \"By name\" in order
        to merge only duplicated meshes"""
        
        def execute(self, context):
            if context.scene.by_name:
                merge_by_names()
            if context.scene.all_meshes:
                objs = [ob for ob in bpy.data.objects if ob.type == 'MESH']
            else:
                objs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
            merge_objs(objs)
            return {'FINISHED'}
    
    class scale_scene_OT_vgs_op(Operator):
        bl_idname = 'scale_scene.vgs_op'
        bl_label = 'Current scene will be scaled. Proceed?'
        bl_description = """Scale entire scene"""
        
        def execute(self, context):
            wm = context.window_manager
            w = [wm.scale_scene_x,wm.scale_scene_x,wm.scale_scene_x]
            scale_scene(w, Context=context)
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)



    class meshes_to_images_OT_vgs_op(Operator):
        bl_idname = 'meshes_to_images.vgs_op'
        bl_label = ''
        bl_description = """Renames all meshes to the names of their assigned textures. Meshes with no materials are unaffected"""
        
        def execute(self, context):
            meshes_to_tex_names()
            return {'FINISHED'}

    class set_weight_OT_vgs_op(Operator):
        bl_idname = 'set_weight.vgs_op'
        bl_label = ''
        bl_description = """Sets weight to selected mesh"""
        
        def execute(self, context):
            wm = context.window_manager
            set_weight(bpy.context.view_layer.objects.active.name, context.scene.vgs_for_setting, wm.vg_set_val)
            return {'FINISHED'}

    class merge_uvs_OT_vgs_op(Operator):
        bl_idname = 'merge_uvs.vgs_op'
        bl_label = ''
        bl_description = """Renames all UV maps to UVMap"""
        
        def execute(self, context):
            merge_uvs()
            return {'FINISHED'}

    class merge_n_remove_OT_vgs_op(Operator):
        bl_idname = 'merge_n_remove.vgs_op'
        try:
            c = bpy.context.view_layer.objects.active.name
        except:
            c = ''
        bl_label = f'Merging vgs for {c}. Proceed?'
        bl_description = """Merges 2 vertex groups into 1"""
        
        def execute(self, context):
            sc = context.scene
            ob_name = bpy.context.view_layer.objects.active.name
            if sc.vg1 and sc.vg2 and ob_name and sc.vg1!=sc.vg2:
                merge_n_remove(ob_name, sc.vg1, sc.vg2)
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)

    class reset_all_dummy_vgs_OT_vgs_op(Operator):
        bl_idname = 'reset_all_dummy_vgs.vgs_op'
        bl_label = ''
        bl_description = """Removes vertex groups from all meshes if no vertice is weighted to them"""
        
        def execute(self, context):
            if context.scene.all_meshes:
                remove_all_dummy_vgs()
            else:
                for ob in [ob.name for ob in bpy.context.selected_objects if ob.type == 'MESH']:
                    remove_dummy_vgs(ob)
            return {'FINISHED'}

    class remove_all_vgs_OT_vgs_op(Operator):
        bl_idname = 'remove_all_vgs.vgs_op'
        bl_label = f'This will remove all vertex groups, proceed?'
        bl_description = """Removes all vertex groups from currently selected meshes"""
        
        def execute(self, context):
            if context.scene.all_meshes:
                objs = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
            else:
                objs = [ob.name for ob in bpy.context.selected_objects if ob.type == 'MESH']
            for ob in objs:
                ob.vertex_groups.clear()
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    class transform_by_ob_OT_vgs_op(Operator):
        bl_idname = 'transform_by_ob.vgs_op'
        bl_label = f'Transforming scene by object. Proceed?'
        bl_description = """Transforms entire scene by active object"""
        
        def execute(self, context):
            for ob in bpy.context.selected_objects:
                transform_by_ob(ob.name)
                break
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    class leave_1_mat_OT_vgs_op(Operator):
        bl_idname = 'leave_1_mat.vgs_op'
        bl_label = f'Removing all materials from objects except for the 1st. Proceed?'
        bl_description = """Removes all materials from all meshes, except for the first one"""
        
        def execute(self, context):
            leave_1_mat()
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
    
    class normalize_vgs_OT_vgs_op(Operator):
        bl_idname = 'normalize_vgs.vgs_op'
        bl_label = f'About to normalize vertex groups. Proceed?'
        bl_description = """Merges all vertex groups with duplicate names (vg.001->vg) for all mesh objects"""
        
        def execute(self, context):
            normalize_vgs()
            return {'FINISHED'}
        
        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(self)
        
    class scale_bones_OT_vgs_op(Operator):
        bl_idname = 'scale_bones.vgs_op'
        bl_label = f'Scale bones for current armature'
        bl_description = """Scale bones for current armature"""
        
        def execute(self, context):
            sc = context.scene
            wm = context.window_manager
            bones = [b.strip() for b in sc.bones_names.split(',') if b]
            arm = bpy.data.objects.get(sc.armatures1)
            w = [wm.scale_bones_x,wm.scale_bones_y,wm.scale_bones_z]
            scale_bones(bones, w, arm, inherit_scale=False)
            return {'FINISHED'}
        

def update_vgs_list(self, context):
    try: 
        vgs = bpy.context.view_layer.objects.active.vertex_groups
        t = sorted([(v.name, v.name,v.name) for v in vgs])
        return t if t else BLANK_TUPLE
    except:
        return BLANK_TUPLE

def update_vgs_list_2(self, context):
    try:
        vg1 = context.scene.vg1
        vgs = bpy.context.view_layer.objects.active.vertex_groups
        t = sorted([(v.name, v.name,v.name) for v in vgs if v.name!=vg1])
        return t if t else BLANK_TUPLE
    except:
        return BLANK_TUPLE

def update_vgs_list_for_setting(self, context):
    ob = bpy.context.view_layer.objects.active
    if ob and ob.type == 'MESH':
        armature_mods = [mdf.name for mdf in ob.modifiers if mdf.type == 'ARMATURE']
        if armature_mods:
            armature_mod = armature_mods[0]
            armature = bpy.data.objects.get(armature_mod)
            if armature:
                t = sorted([(b.name, b.name, b.name) for b in armature.data.bones if b.name])
                return t if t else BLANK_TUPLE
    return BLANK_TUPLE

def update_armatures(self, context):
    t = [(ob.name, ob.name, ob.name) for ob in bpy.data.objects if ob.type == 'ARMATURE']
    return t if t else BLANK_TUPLE

def update_armatures_2(self, context):
    t = [(ob.name, ob.name, ob.name) for ob in bpy.data.objects if ob.type == 'ARMATURE']
    t = [a for a in t if a[0]!=context.scene.armatures1]
    return t if t else BLANK_TUPLE

def updateStringParameter(self,context):
    # This def gets called when one of the properties changes state.
    print(self.bones_names) 

class MainPanel(Panel):
    """Main Panel for Blender_customs"""
    bl_label  = "Blender Customs"
    bl_idname = "Blender_Customs_PT_vgs"
    bl_category  = "Blender Customs"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout
        
        wm = context.window_manager
        
        row = layout.row()
        row.label(text='Current object: ' + bpy.context.view_layer.objects.active.name)
        
         
        row = layout.row()
        row.prop(context.scene, "armatures", text='')
        row.operator(Buttons_Local.apply_armatures_OT_vgs_op.bl_idname, text="Apply armature")
        
        layout.row().separator()
        row = layout.row()
        row.label(text='Set weight for mesh')
        
        row = layout.row()
        row.prop(context.scene, "vgs_for_setting", text='')
        row.prop(wm, "vg_set_val", text='')
        row.operator(Buttons_Local.set_weight_OT_vgs_op.bl_idname, text="Set weight")
        
        row = layout.row()
        row.label(text=f'Merging vertex groups')
        
        row = layout.row()
        #row.prop(context.scene, "vgs", text='')
        row.prop(context.scene, "vg1", text='')
        row.prop(context.scene, "vg2", text='')
        
        #row = layout.row()
        row.operator(Buttons_Local.merge_n_remove_OT_vgs_op.bl_idname, text="Merge")
        
        layout.row().separator()
        row = layout.row()
        row.prop(context.scene, "armatures1", text='')
        row.prop(context.scene, "armatures2", text='')
        row = layout.row()
        row.operator(Buttons_Local.transfer_weights_OT_filebrowser.bl_idname, text="Transfer weights from json")
        
        
        layout.row().separator()
        row = layout.row()
        row.prop(context.scene, "all_meshes", text='Work on all meshes')
        row = layout.row()
        row.operator(Buttons_Local.reset_all_dummy_vgs_OT_vgs_op.bl_idname, text="Clear unused vertex groups")
        row = layout.row()
        row.operator(Buttons_Local.normalize_vgs_OT_vgs_op.bl_idname, text="Normalize vertex groups")
        row = layout.row()
        row.operator(Buttons_Local.rename_meshes_to_md5_dds_OT_op.bl_idname, text="Rename meshes to dds md5")
        row.operator(Buttons_Local.meshes_to_images_OT_vgs_op.bl_idname, text="Rename meshes to images")
        row = layout.row()
        row.operator(Buttons_Local.split_objs_by_material_OT_vgs_op.bl_idname, text="Split meshes by materials")
        row = layout.row()
        row.operator(Buttons_Local.merge_meshes_OT_vgs_op.bl_idname, text="Merge meshes")
        row.prop(context.scene, "by_name", text='By name')
        row = layout.row()
        row.operator(Buttons_Local.apply_transform_OT_vgs_op.bl_idname, text="Apply transform")
        row.operator(Buttons_Local.transform_by_ob_OT_vgs_op.bl_idname, text="Transform by object")
        
        
        row = layout.row()
        row.operator(Buttons_Local.clear_scene_OT_vgs_op.bl_idname, text="Clear scene")
        row.operator(Buttons_Local.reset_broken_mats_OT_vgs_op.bl_idname, text="Fix broken materials")
        row = layout.row()
        row.operator(Buttons_Local.leave_1_mat_OT_vgs_op.bl_idname, text="Leave 1 material")
        row.operator(Buttons_Local.merge_uvs_OT_vgs_op.bl_idname, text="Merge UVs")
        row = layout.row()
        row.operator(Buttons_Local.remove_all_vgs_OT_vgs_op.bl_idname, text="Remove all vertex groups")
        
        layout.row().separator()
        row = layout.row()
        row.label(text='Scale bones')
        row = layout.row()
        row.prop(context.scene, "armatures1", text='')
        row = layout.row()
        row.prop(wm, "scale_bones_x", text='X')
        #row = layout.row()
        row.prop(wm, "scale_bones_y", text='Y')
        #row = layout.row()
        row.prop(wm, "scale_bones_z", text='Z')
        row = layout.row()
        row.prop(context.scene, "bones_names", icon='BONE_DATA')
        row = layout.row()
        row.operator(Buttons_Local.scale_bones_OT_vgs_op.bl_idname, text="Scale bones")
        
        
        #layout.use_property_split = True
        layout.row().separator()
        row = layout.row()
        row.operator(Buttons_Local.scale_scene_OT_vgs_op.bl_idname, text="Scale scene")
        #row = layout.row()
        row.prop(wm, "scale_scene_x", text='Value')
        #row = layout.row()
        #row.prop(wm, "scale_scene_y", text='Y')
        #row = layout.row()
        #row.prop(wm, "scale_scene_z", text='Z')
        #layout.use_property_split = False
        
        layout.row().separator()
        row = layout.row()
        row.operator(Buttons_Local.OT_scene_to_json_filebrowser.bl_idname, text="Save scene to json")
       
        
        
def register():
    WindowManager.vg_set_val = FloatProperty(max=1.0, min=0.0)
    WindowManager.scale_scene_x = FloatProperty(max=1000.0, min=0.0001, default=100.0, step=5.0)
    WindowManager.scale_bones_x = FloatProperty(max=1000.0, min=0.0001, default=1.0, step=5.0)
    WindowManager.scale_bones_y = FloatProperty(max=1000.0, min=0.0001, default=1.0, step=5.0)
    WindowManager.scale_bones_z = FloatProperty(max=1000.0, min=0.0001, default=1.0, step=5.0)
    #WindowManager.scale_scene_z = FloatProperty(max=1000.0, min=0.0001, default=1.0)
    bpy.types.Scene.all_meshes = BoolProperty(name='all_meshes',description='Works on all meshes if selected', default=True)
    bpy.types.Scene.by_name = BoolProperty(name='by_name',description="Merge all duplicated meshes into one", default=True)
    bpy.types.Scene.vg1 = EnumProperty(items=update_vgs_list)
    bpy.types.Scene.vg2 = EnumProperty(items=update_vgs_list_2)
    bpy.types.Scene.vgs = EnumProperty(items=update_vgs_list)
    bpy.types.Scene.vgs_for_setting = EnumProperty(items=update_vgs_list_for_setting)
    bpy.types.Scene.armatures = EnumProperty(items=update_armatures)
    bpy.types.Scene.armatures1 = EnumProperty(items=update_armatures)
    bpy.types.Scene.armatures2 = EnumProperty(items=update_armatures_2)
    bpy.types.Scene.bones_names = StringProperty(name="", description="Type coma separated bones names", update=updateStringParameter)

    
    
    for cls in [cls for cls in dir(Buttons_Local) if not cls.startswith('_')]:
        cur_class = getattr(Buttons_Local, cls)
        if inspect.isclass(cur_class):
            print(f'Registering class: {cls}')
            register_class(cur_class)
    register_class(MainPanel)

def unregister():
    for cls in [cls for cls in dir(Buttons_Local) if not cls.startswith('_')]:
        cur_class = getattr(Buttons_Local, cls)
        if inspect.isclass(cur_class):
            print(f'Unegistering class: {cls}')
            unregister_class(cur_class)
    unregister_class(MainPanel)

if __name__ == '__main__':
    #scale_bones(['Arm_1_L', 'Arm_2_L'], [2,2,2], bpy.data.objects['Armature'], inherit_scale=False)
    register()