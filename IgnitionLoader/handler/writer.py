import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    FloatProperty
)
from pathlib import Path


class IgnitionFileWriter(bpy.types.Operator, ExportHelper):
    """Will write the current blend file to a .ignition file"""
    bl_idname = "ignition.writer"
    bl_label = "Save as Ignition File"
    bl_options = {"REGISTER"}

    filename_ext = ".ignition"

    filepath = "" # remove undefined variable error
    def execute(self, context):
        
        folder = '\\'.join(self.filepath.split("\\")[:-1])
        ignitionSavedFileName = self.filepath.split("\\")[-1].split(".")[0]
        blendJson = {"materials":[], "lights":[], "meshes":[]}
        
        # RENDERER SETTINGS
        blendJson["Renderer"] = {}
        blendJson["Renderer"]["resolution"] = [bpy.data.scenes[0].render.resolution_x, bpy.data.scenes[0].render.resolution_x]
        blendJson["Renderer"]["maxDepth"] = bpy.data.scenes[0].cycles.max_bounces
        blendJson["Renderer"]["tileWidth"], blendJson["Renderer"]["tileHeight"] = 128, 128 # Blender does not have a setting for tile size

        for link in bpy.data.worlds[0].node_tree.links:
            if link.from_node.type == "TEX_ENVIRONMENT":
                # copy HDRI
                with open(link.from_node.image.filepath_from_user(), 'rb') as copyBytes:
                    newLoc = f"{folder}\\{ignitionSavedFileName}_assets\\HDRI.{link.from_node.image.filepath.split('.')[-1]}"
                    currentHDRIBytes = copyBytes.read()
                    if not os.path.exists(newLoc):
                        os.mkdir('\\'.join(newLoc.split("\\")[:-1]))
                    open(newLoc, 'wb').write(currentHDRIBytes)
                blendJson["Renderer"]["envMap"] = f"./{ignitionSavedFileName}_assets\\HDRI.{link.from_node.image.filepath.split('.')[-1]}"
                break

                
                
                


        return {"FINISHED"}

