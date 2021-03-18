from bpy.types import (
    Panel,
    Operator
)
import bpy
from . import loader, writer

class IgnitionDefaultNode(Operator):
    """Create the default inition node"""
    bl_idname = "ignition.node"
    bl_label = "Create Default Ignition Node"
    bl_options = {'REGISTER'}

    def execute(self, context:bpy.context):
        
        loader.ignitionNode(None if "IgnitionDefault" not in bpy.data.node_groups.keys() else bpy.data.node_groups["IgnitionDefault"])
        
        return {"FINISHED"}
class FileHandlerPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Ignition"
    bl_label = "File Handler"
    bl_idname = "ignition.fileHandlePanel"


    def draw(self, context):
        layout = self.layout
        layout.operator(loader.IgnitionFileLoader.bl_idname)
        layout.operator(writer.IgnitionFileWriter.bl_idname)

class NodeHandler(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Ignition"
    bl_label = "Node Handler"
    bl_idname = "ignition.nodeHandlePanel"


    def draw(self, context):
        layout = self.layout

        layout.operator(IgnitionDefaultNode.bl_idname)
        