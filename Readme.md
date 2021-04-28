# Introduction
This repo contains set of useful python functions for working in blender.

# Installation
Copy all ``*.py`` files to ``<blender.exe_path>/<blender_version>/python/lib/site-packages``. For me it is: 
```D:\Program Files\Blender Foundation\Blender 2.91\2.91\python\lib\site-packages```

# Usage
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
- ``transfer_weights_w_weight(obname, vgname2, WEIGHT)`` : sets weight to WEIGHT float value on all vertices on mesh object named obname,
- ``transfer_weights(ob, vgname1, vgname2)`` : same as merge_vgs, with additional input validation,
- ``get_parents_bones_list()`` : returns list of lists of all parents bones to existing bones (iterates on all armature objects),
- ``pair_rest_bones(data)`` : returns bones unedited by ``transfer_weights_from_json()``
- ``transfer_weights_from_json(json_file)`` : converts all meshes vertex groups on scene to new armature type, basing on json input; vertex groups not specified in json input will be merged with closest parent bone in new armature type;
- ``merge_n_remove(obname, vgname1, vgname2)`` : same as merge_vgs, but vgname2 is removed from mesh,
- ``remove_dummy_vgs(obname)`` : removes all vertex groups from mesh named obname, leaving only those who has at least 1 vertice with weight > 0.0,
- ``remove_all_dummy_vgs()`` : same as remove_dummy_vgs, but for all meshes on scene
## weights_paints
-``paint()`` : converts all vertex groups to vertex colors, examples:

![alt text](https://cdn.discordapp.com/attachments/316759796340621323/835942906883342367/unknown.png)

![alt text](https://media.discordapp.net/attachments/316759796340621323/835939628992168006/unknown.png)The colors are choosen randomly

-``weights_to_json()`` : return weights of all vertices of all mesh type objects on scene in json format,




