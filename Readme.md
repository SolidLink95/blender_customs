# Introduction

This repo contains set of useful python functions for working in blender.

# Installation

Run ``python setup.py`` as an administrator

OR

Copy all ``*.py`` files to ``<blender.exe_path>/<blender_version>/python/lib/site-packages``. For me it is: 
```D:\Program Files\Blender Foundation\Blender 2.91\2.91\python\lib\site-packages```

# Example usage

In blender go to ``Scripting`` tab and write 

```
import blender_customs, weights_paints

weights_paints.paint()
blender_customs.merge_uvs()
```

# Functions description

## blender_customs

- 	``merge_uvs()`` : renames all UV maps of all meshes on scene to ``UVMap``; useful for meshes merging;

- ``rotate_bone(bones, angles,apply_rest=False)`` :  rotates bones in all armatures on scene; bone is skipped if does not exist in armature:

-- bones : array of bones names to rotate in string ,

-- angles: ``[X,Y,Z]`` array in degrees,

--apply_rest: if set to True, the rotation will affect the rest pose (False by default)

- ``scale_bones(bones, X=1.0, Y=1.0, Z=1.0, inherit_scale = False)`` :  scale bones in all armatures on scene; bone is skipped if does not exist in armature:
-- bones : array of bones names to rotate in string ,

-- X, Y, Z : float dimensions which bones are scaled (1.0 by default)

--inherit_scale : if set to True, all children bones will be affected by scaling (False by default)

- ``file_to_json(file)`` : dumps file to json,
- ``json_to_file(file, x)`` : dumps json to file,
- ``update_progress(job_title, progress)`` : function for progress bar,
- ``rev_json(data)`` : reverses json (does not validate duplicates),
- ``merge_vgs(ob, vgname1, vgname2)`` : merges 2 vertex groups vgname1 and vgname2 in mesh type object ob;
- ``set_weight(obname, vgname2, WEIGHT)`` : sets weight to WEIGHT float value on all vertices on mesh object named obname,
- ``transfer_weights(ob, vgname1, vgname2)`` : same as merge_vgs, with additional input validation,
- ``get_parents_bones_list()`` : returns list of lists of all parents bones to existing bones (iterates on all armature objects),
- ``pair_rest_bones(data)`` : returns bones unedited by ``transfer_weights_from_json()``
- ``textures_to_json()`` : returns json with all meshes, its materials and textures full filepaths. 

Example:

```
{
    "Arm_225__Mt_Upper_225": {
        "Mt_Upper_225.003": [
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Armor_225_Upper_Alb.png",
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Armor_225_Upper_Spm.png"
        ]
    },
    "Belt_225__Mt_Belt_225": {
        "Mt_Belt_225.003": [
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Armor_225_Belt_Alb.png",
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Armor_225_Belt_Spm.png"
        ]
    },
    "Skin_225__Mt_Upper_Skin": {
        "Mt_Upper_Skin.003": [
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Link_Skin_Alb.png",
            "C:\\Users\\user\\Documents\\botw\\work\\Armor_225_Upper.dae\\Link_Skin_Spm.png"
        ]
    }
}
```

- ``transfer_weights_from_json(json_file)`` : converts all meshes vertex groups on scene to new armature type, basing on json input; vertex groups not specified in json input will be merged with closest parent bone in new armature type;

Input json example:


```
{
	"WAIST": "Waist",
	"SPINE2": "Spine_2",
	"SPINE3": "Spine_2",
	"SPINE1": "Spine_1",
	"CLAVICLEROLL_R": "Spine_2",
	"CLAVICLEROLL_L": "Spine_2",
	"THIGH_L": "Leg_1_L",
	"CLANK_L": "Leg_2_L",
	"THIGH_R": "Leg_1_R",
	"CLANK_R": "Leg_2_R",
	"CLAVICLE_R": "Clavicle_R",
	"CLAVICLE_L": "Clavicle_L",
	"SHOULDER_R": "Arm_1_R",
etc.
```

- ``merge_n_remove(obname, vgname1, vgname2)`` : same as merge_vgs, but vgname2 is removed from mesh,

- ``remove_dummy_vgs(obname)`` : removes all vertex groups from mesh named obname, leaving only those who has at least 1 vertice with weight > 0.0,

- ``remove_all_dummy_vgs()`` : same as remove_dummy_vgs, but for all meshes on scene
## weights_paints

-``paint()`` : converts all vertex groups to vertex colors, examples:

![alt text](https://cdn.discordapp.com/attachments/316759796340621323/835942906883342367/unknown.png)

![alt text](https://media.discordapp.net/attachments/316759796340621323/835939628992168006/unknown.png)The colors are choosen randomly

-``weights_to_json()`` : return weights of all vertices of all mesh type objects on scene in json format, example:
```
{
    "Kargon": {
        "0": {
            "Bone_LR_Clavicle_L": 0.2980392277240753,
            "Bone_LR_Spine2": 0.7019608020782471
        },
        "1": {
            "Bone_LR_Clavicle_L": 0.24705882370471954,
            "Bone_LR_Spine2": 0.7529411911964417
        },
        "2": {
            "Bone_LR_Clavicle_L": 0.2980392277240753,
            "Bone_LR_Spine2": 0.7019608020782471
        }, etc
```

- ``merge_all_meshes()`` : merges all meshes on scene into a single mesh
- ``remove_all_vertex_colors()`` : removes all vertex colors layers from all meshes
- ``textures_to_json()`` : return json for all meshes, its materials and textures full paths. Example:

```{'arms': {'Mt_Sword_001_0_Guardian': ['F:\\Sync\\Sleeping_Guardian7_DIFF.6.png']}}```

- ``meshes_to_images()`` : renames meshes to the texture name of their first material (meshes with no materials are skipped)

- ``rename_bones_vgs(s, skip_bones=\[\])`` : appends a string ``s`` to all bones names and vertex groups, excluding names included in ``skip_bones`` list

- ``reset_broken_mats(mode='fbx')`` : sometimes materials are broken/inside out, this function changes them to default blender materials. Choose mode ``fbx`` for imported fbx files and any other string (``dae``, empty string, etc) for other mode.

- ``mods_to_json()`` : returns all meshes and their modifiers in json format. Example:

```

{
   "War.001":["Armature.001"],
   "War.002":["Armature.001"],
   "War.003":["Armature.001"],
   "War.004":["Armature.001"],
   "War.005":["Armature.001"]
}

```

