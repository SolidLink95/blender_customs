import os, sys,requests
from tkinter import Tcl
from os import listdir
from os.path import isfile, join
from ctypes import windll
import string
os.system('cls')

def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


def dirs_to_list(mypath=os.getcwd()):
    return [f for f in listdir(mypath) if not isfile(join(mypath, f))]

def sort_files_like_windows(mylist):
    return Tcl().call('lsort', '-dict', mylist)

def getListOfFiles(dirName=os.getcwd()):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles
    

def get_blender_path():
    drives = get_drives()
    drive = ''
    for d in drives:
        if os.path.exists(f'{d}:\\Program Files\\Blender Foundation'):
            drive = d
            break
    if not drive: sys.exit("Could not find Blender installed on this machine. Please install blender_customs manually")
    PATH = 'C:\\Program Files\\Blender Foundation'
    ver = sort_files_like_windows(dirs_to_list(PATH))[-1]
    PATH = os.path.join(PATH, ver)
    v = sort_files_like_windows(dirs_to_list(PATH))[0]
    PATH = os.path.join(PATH, v)
    return PATH
    
def update_from_git():
    PATH = os.path.join(get_blender_path(), 'python\\lib\\site-packages')
    b_c = 'https://raw.githubusercontent.com/banan039pl/blender_customs/master/blender_customs.py'
    r = requests.get(b_c, allow_redirects=True)
    bc = os.path.join(PATH, 'blender_customs.py')
    wp = os.path.join(PATH, 'weights_paints.py')
    
    with open(bc, 'wb') as f:
        f.write(r.content)
    
    w_p = 'https://raw.githubusercontent.com/banan039pl/blender_customs/master/weights_paints.py'
    r = requests.get(w_p, allow_redirects=True)
    with open(wp, 'wb') as f:
        f.write(r.content)
    print(f'Successfully updated files: \n{bc} \nand \n{wp}')
    
    
def scales():
    PATH = 'C:\\Program Files\\Blender Foundation'
    ver = sort_files_like_windows(dirs_to_list(PATH))[-1]
    PATH = os.path.join(PATH, ver)
    v = sort_files_like_windows(dirs_to_list(PATH))[0]
    PATH = os.path.join(PATH, v)
    init_py = os.path.join(PATH,'scripts\\addons\\io_scene_fbx\\__init__.py')
    with open(init_py, 'r') as f: data = f.read()
    with open(init_py + '.backup', 'w') as f: f.write(str(data))
    
    s1 = """    global_scale: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=1.0,
            )"""
    s2 = """    global_scale: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=100.0,
            )"""
    data = data.replace(s1, s2)
    
    s1 = """    global_scale: FloatProperty(
            name="Scale",
            description="Scale all data (Some importers do not support scaled armatures!)",
            min=0.001, max=1000.0,
            soft_min=0.01, soft_max=1000.0,
            default=1.0,
            )"""
    s2 = """    global_scale: FloatProperty(
            name="Scale",
            description="Scale all data (Some importers do not support scaled armatures!)",
            min=0.001, max=1000.0,
            soft_min=0.01, soft_max=1000.0,
            default=0.01,
            )"""        
    
    data = data.replace(s1, s2)
    
    s1 = """    add_leaf_bones: BoolProperty(
            name="Add Leaf Bones",
            description="Append a final bone to the end of each chain to specify last bone length "
                        "(use this when you intend to edit the armature from exported data)",
            default=True # False for commit!
            )"""
    s2 = """    add_leaf_bones: BoolProperty(
            name="Add Leaf Bones",
            description="Append a final bone to the end of each chain to specify last bone length "
                        "(use this when you intend to edit the armature from exported data)",
            default=False # False for commit!
            )"""
    
    data = data.replace(s1, s2)
            
    with open(init_py, 'w') as f: f.write(data)
    
update_from_git()
#scales()