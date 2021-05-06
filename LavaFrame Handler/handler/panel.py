from bpy.types import (
    Panel,
    Operator
)
import bpy
from . import loader, writer

class LavaFrameDefaultNode(Operator):
    """Create the default inition node"""
    bl_idname = "LavaFrame.node"
    bl_label = "Create Default LavaFrame Node"
    bl_options = {'REGISTER'}

    def execute(self, context:bpy.context):
        
        loader.LavaFrameNode(None if "LavaFrameDefault" not in bpy.data.node_groups.keys() else bpy.data.node_groups["LavaFrameDefault"])
        
        return {"FINISHED"}
class FileHandlerPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LavaFrame"
    bl_label = "File Handler"
    bl_idname = "LavaFrame.fileHandlePanel"


    def draw(self, context):
        layout = self.layout
        layout.operator(loader.LavaFrameFileLoader.bl_idname)
        layout.operator(writer.LavaFrameFileWriter.bl_idname)

class NodeHandler(Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "LavaFrame"
    bl_label = "Node Handler"
    bl_idname = "LavaFrame.nodeHandlePanel"


    def draw(self, context):
        layout = self.layout

        layout.operator(LavaFrameDefaultNode.bl_idname)
        