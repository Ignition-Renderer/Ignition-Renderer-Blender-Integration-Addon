import bpy, os, math
from .handler import loader, writer, panel

bl_info = {
    "name": "Lavaframe Loader",
    "blender":(2, 80, 0),
    "category": "Import-Export",
}

# commented lines below are due to the fact that they were for TESTING purposes. If you want to mess around with them go ahead lol
classes = [
    loader.LavaFrameFileLoader,
    writer.LavaFrameFileWriter,
    panel.LavaFrameDefaultNode,
    panel.FileHandlerPanel,
    panel.NodeHandler,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(panel.FileHandlerPanel.draw)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)