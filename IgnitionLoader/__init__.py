import bpy, os, math
from .handler import loader

bl_info = {
    "name": "Ignition Loader",
    "blender":(2, 80, 0),
    "category": "Import-Export",
}

def register():
    bpy.utils.register_class(loader.IgnitionFileLoader)
    bpy.types.VIEW3D_MT_object.append(loader.IgnitionFileLoader.menu_func)

def unregister():
    bpy.utils.unregister_class(loader.IgnitionFileLoader)