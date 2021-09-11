import shutil
import bpy, os, math, random
from bpy_extras.io_utils import ExportHelper

class LavaFrameFileWriter(bpy.types.Operator, ExportHelper):
    """Will write the current blend file to a .LavaFrame file"""
    bl_idname = "lavaframe.writer"
    bl_label = "Save as LavaFrame File"
    bl_options = {"REGISTER"}

    filename_ext = ".LavaFrame"

    filepath = "" # remove undefined variable error
    def execute(self, context):
        folder = '\\'.join(self.filepath.split("\\")[:-1])
        LavaFrameSavedFileName = self.filepath.split("\\")[-1].split(".")[0]
        blendJson = {"materials":[], "lights":[], "meshes":[]}

        asset_folder = f"{LavaFrameSavedFileName}_assets\\"
        full_assets_path = f"{folder}\\{LavaFrameSavedFileName}_assets\\"
        if not os.path.exists(f"{folder}\\{LavaFrameSavedFileName}_assets"):
            os.mkdir(f"{folder}\\{LavaFrameSavedFileName}_assets")
        
        # RENDERER SETTINGS
        blendJson["Renderer"] = {}
        blendJson["Renderer"]["resolution"] = [bpy.data.scenes[0].render.resolution_x, bpy.data.scenes[0].render.resolution_y]
        blendJson["Renderer"]["maxDepth"] = bpy.data.scenes[0].cycles.max_bounces
        blendJson["Renderer"]["tileWidth"], blendJson["Renderer"]["tileHeight"] = 128, 128 # Blender does not have a setting for tile size

        for link in bpy.data.worlds[0].node_tree.links:
            if link.from_node.type == "TEX_ENVIRONMENT":
                # copy HDRI
                with open(link.from_node.image.filepath_from_user(), 'rb') as copyBytes:
                    newLoc = f"{folder}\\{''.join(LavaFrameSavedFileName.split())}_assets\\HDRI.{link.from_node.image.filepath.split('.')[-1]}"
                    currentHDRIBytes = copyBytes.read()
                    if not os.path.exists(newLoc):
                        os.mkdir('\\'.join(newLoc.split("\\")[:-1]))
                    open(newLoc, 'wb').write(currentHDRIBytes)
                blendJson["Renderer"]["envMap"] = f".\\{''.join(LavaFrameSavedFileName.split())}_assets\\HDRI.{link.from_node.image.filepath.split('.')[-1]}"

        for node in bpy.data.worlds[0].node_tree.nodes:
            if node.type == "BACKGROUND":
                blendJson["Renderer"]["hdriMultiplier"] = node.inputs[1].default_value

        # CAMERA SETTINGS
        currentCamera = bpy.data.cameras[bpy.data.scenes[0].camera.name]
        blendJson["Camera"] = {}
        blendJson["Camera"]["fov"] = (currentCamera.angle*180)/math.pi
        blendJson["Camera"]["pos"] = [bpy.data.scenes[0].camera.location[0],
                                     -bpy.data.scenes[0].camera.location[2],
                                      bpy.data.scenes[0].camera.location[1]]
        
        # oh boy here we go
        # ok so to get the point at which the camera
        # is looking at, I have to do 5 things;
        # 1. Create new empty
        # 2. Parent empty to camera (without inverse)
        # 3. Move empty -1 on Z axis
        # 4. Unparent empty and keep transform
        # 5. Get empty location, that's the point the camera is loooking at.
        # awfully complicated.

        # step 1
        objName = ''.join([chr(random.randint(0,255)) for x in range(10)])
        bpy.ops.object.empty_add(type='PLAIN_AXES') # empty is now selected
        bpy.context.object.name = objName # randomly generated name for later
        # step 2
        bpy.ops.object.select_all(action='DESELECT')

        bpy.data.objects[objName].select_set(True)
        bpy.ops.object.select_camera(extend=True)

        bpy.ops.object.parent_no_inverse_set() # empty object now is parented to camera

        bpy.ops.object.select_all(action='DESELECT')

        # Step 3
        bpy.data.objects[objName].location[2] -= 1 
        
        # Step 4
        bpy.data.objects[objName].select_set(True)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # catJAM IT WORKS
        blendJson["Camera"]["lookAt"] = [bpy.data.objects[objName].location[0],
                                        -bpy.data.objects[objName].location[2],
                                         bpy.data.objects[objName].location[1]]

        bpy.ops.object.delete()

        if currentCamera.dof.use_dof:
            blendJson["Camera"]["focalDistance"] = currentCamera.dof.focus_distance
            blendJson["Camera"]["aperture"] = currentCamera.dof.aperture_fstop


        # MATERIALS
        # I literally have no clue how I'll do materials.
        # I'm trying to figure out a way to take the blender
        # node tree and transform it to GLSL. If that doesn't
        # work then I'll have to force the default LavaFrame
        # node.

        # hello me from two months ago, congrats, you couldn't
        # figure it out. So I guess it's time to force the
        # default node.

        for mat in bpy.data.materials:
            mat:bpy.types.Material
            if mat.node_tree:
                for node in mat.node_tree.links:
                    node:bpy.types.NodeLink
                    
                    if node.to_node.type == 'OUTPUT_MATERIAL' and node.from_node.type == "GROUP":
                        if node.from_node.node_tree.name == "LavaFrameDefault":
                            a:bpy.types.NodeGroup = node.from_node
                            matJsonData = {
                                "name":mat.name
                            }
                            for key in a.inputs:
                                # a.inputs[key.name].default_value... what a mouthful
                                inputValue = a.inputs[key.name].default_value
                                print(f"{key.name}: {type(inputValue)}")
                                if type(inputValue) == float:
                                    if inputValue != 0:
                                        matJsonData[key.name] = inputValue
                                else:
                                    if key.name not in ["albedoTexture", "metallicRoughness", "normalTexture"]:
                                        col = [x for x in inputValue]
                                        if sum(col) != 1 and col[-1] == 1: # all alphas default to 1, if the sum is 1 and the alpha is 1 then the color is unused
                                            matJsonData[key.name] = col
                                    else:
                                        # this means that it is a TEXTURE input, so I have to check for an image node.
                                        if a.inputs[key.name].is_linked: # check if it is linked
                                            image_tex = [x.from_node for x in a.inputs[key.name].links if x.from_node.type == "TEX_IMAGE"]
                                            if image_tex != []:
                                                image_tex = image_tex[0]
                                                if image_tex.image:
                                                    img_name:str = image_tex.image.filepath.split("\\")[-1]
                                                    no_space_name = img_name.replace(' ', '_')
                                                    shutil.copyfile(os.path.abspath(image_tex.image.filepath.replace('//', '\\')), full_assets_path)
                                                    os.rename(f"{full_assets_path}\\{img_name}", f"{full_assets_path}\\{no_space_name}")
                                                    matJsonData[key.name] = f"{full_assets_path}\\{no_space_name}"

                            blendJson["materials"].append(matJsonData)
            else:
                print(f"{mat.name} has no node_tree property.")

            

        # JSON -> LAVAFRAME
        LavaFrameFile = ""
        for key in blendJson.keys():

            if type(blendJson[key]) == dict:
                LavaFrameFile += f'{key}\n{{\n'
                for val in blendJson[key].keys():
                    if type(blendJson[key][val]) == list:
                        LavaFrameFile += f"\t{val} {' '.join([str(x) for x in blendJson[key][val]])}\n"
                    else:
                        LavaFrameFile += f"\t{val} {blendJson[key][val]}\n"
                LavaFrameFile += "}\n"
            
            elif type(blendJson[key]) == list: # lists are ALWAYS a list of dicts.
                if key == "materials":
                    for x in range(len(blendJson[key])):
                        LavaFrameFile += f"material {blendJson[key][x]['name']}\n{{\n"

                        for val in blendJson[key][x].keys():
                            if val == 'name':
                                continue
                            if type(blendJson[key][x][val]) == list:
                                LavaFrameFile += f"\t{val} {' '.join([str(x) for x in blendJson[key][x][val]])}\n"
                            else:
                                LavaFrameFile += f"\t{val} {blendJson[key][x][val]}\n"
                        LavaFrameFile += "}\n"

        
        open(self.filepath, 'w').write(LavaFrameFile)

        return {"FINISHED"}