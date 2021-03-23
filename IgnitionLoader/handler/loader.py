import bpy, bpy_extras, os, math, json
from . import exceptions, ignitionToJson

class IgnitionFileLoader(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Takes care of loading in the .ignition file into your blender project."""
    bl_idname = "ignition.loader"
    bl_label = "Open Ignition File"
    bl_options = {'REGISTER', "UNDO"} # removing all objects is a destructive action! Ability to undo is nice

    filter_glob: bpy.props.StringProperty(default="*.ignition", options={"HIDDEN"})

    filepath = "" # removing undefined var error

    def execute(self, context):
        bpy.context.scene["IGNITION_FILEPATH"] = self.filepath
        # clear all objects
        for obj in bpy.context.scene.objects:
            mesh = bpy.data.objects[obj.name]
            bpy.data.objects.remove(mesh)

        bpy.context.scene.render.engine = "CYCLES"
        filename, extension = os.path.splitext(self.filepath)
        path = '\\'.join(self.filepath.split("\\")[:-1])
        if extension != ".ignition":
            raise exceptions.NotAnIgnitionFile("This specified file was not a .ignition file")
        
        ignitJson = ignitionToJson.IgnitionToJson(filename+extension)
        bpy.context.scene["IGNITION_JSONDATA"] = json.dumps(ignitJson)

        # debugging
        # json.dump(ignitJson, open(r"C:\Users\MYUSER\Desktop\ignition_beta_win32\ex.json", 'w'))
        
                
        # json -> blender

        bpy.context.scene.render.engine = "CYCLES"
        scene = bpy.context.scene
        ## RENDERER SETTINGS
        scene.render.resolution_x = ignitJson["Renderer"]["resolution"][0]
        scene.render.resolution_y = ignitJson["Renderer"]["resolution"][1]

        scene.cycles.max_bounces, scene.cycles.diffuse_bounces, scene.cycles.glossy_bounces, scene.cycles.transparent_max_bounces, scene.cycles.transmission_bounces = [ignitJson["Renderer"]["maxDepth"] for _ in range(5)]

        # tile width/tile height do not have a setting existant inside of Blender. (tiles are defaulted to 64x64)

        scene.use_nodes = True

        
        if ignitJson["Renderer"].get("envMap") is not None:
            envText = None
            if not "Environment Texture" in scene.world.node_tree.nodes.keys():
                scene.world.node_tree.nodes.new("ShaderNodeTexEnvironment")
            
            envText = scene.world.node_tree.nodes["Environment Texture"]
            envText.image = bpy.data.images.load(path+"\\"+ignitJson["Renderer"]["envMap"])
            scene.world.node_tree.links.new(envText.outputs[0], scene.world.node_tree.nodes["Background"].inputs[0])
        else:
            if "Environment Texture" in scene.world.node_tree.nodes.keys():
                scene.world.node_tree.nodes.remove(scene.world.node_tree.nodes["Environment Texture"])
            scene.world.node_tree.nodes["Background"].inputs[0].default_value = [0, 0, 0, 1]

        if ignitJson["Renderer"].get("hdrMultiplier") is not None:
            scene.world.node_tree.nodes["Background"].inputs[1].default_value = ignitJson["Renderer"]["hdrMultiplier"]

        ## CAMERA SETTINGS
        if "Camera" not in scene.objects.keys():
            cameraDat = bpy.data.cameras.new("Camera")
            scene.collection.objects.link(bpy.data.objects.new("Camera", cameraDat))

        camera = scene.objects["Camera"]
        scene.camera = camera


        # blender why you gotta switch Y and Z like that
        camera.location = (ignitJson["Camera"]["position"][0], -ignitJson["Camera"]["position"][2], ignitJson["Camera"]["position"][1])

        if [e for e in scene.objects.keys() if e.startswith("Empty")] == []:
            empty = bpy.data.objects.new("Empty", None)
            scene.collection.objects.link(empty)

        # im so fucking stupid and i hate this line of code so fucking much
        empty = scene.objects[[e for e in scene.objects.keys() if e.startswith("Empty")][0]]
        empty.location = (ignitJson["Camera"]["lookAt"][0], -ignitJson["Camera"]["lookAt"][2], ignitJson["Camera"]["lookAt"][1])

        if "Track To" not in camera.constraints.keys():
            camera.constraints.new("TRACK_TO")

        camera.constraints["Track To"].target = empty
        cameraDat.angle  = math.radians(ignitJson["Camera"]["fov"])

        ## MATERIALS

        if "IgnitionDefault" not in bpy.data.node_groups.keys():
            ignitionNode() # create new ignition Node
        else:
            ignitionNode(bpy.data.node_groups["IgnitionDefault"]) # overwrite exisitng one in case some users are funny and decide to temper with it

        for mat in ignitJson["materials"]:
            if mat["name"] in bpy.data.materials:
                material = bpy.data.materials[mat["name"]]
            else:
                material = bpy.data.materials.new(mat["name"])
            material.use_nodes = True
            matnode = material.node_tree

            matnode.nodes.clear()
            matOut = matnode.nodes.new("ShaderNodeOutputMaterial")

            grp = matnode.nodes.new("ShaderNodeGroup")
            grp.node_tree = bpy.data.node_groups['IgnitionDefault']
            grp.location = (-200, 0)

            material.node_tree.links.new(grp.outputs[0], matOut.inputs[0])

            for val in mat.keys():
                if val == "name":
                    continue
                if val == "color":
                    grp.inputs["albedo"].default_value = mat[val] + [1]
                elif val == "albedoTexture":
                    imageTex = material.node_tree.nodes.new("ShaderNodeTexImage")
                    imageTex.location = (-800, 0)
                    imageTex.image = bpy.data.images.load(path+"\\"+mat[val])
                    material.node_tree.links.new(imageTex.outputs[0], grp.inputs[0])
                    continue
                if val not in grp.inputs.keys():
                    continue
                if val in ["extinction","albedo"]:
                    grp.inputs[val].default_value = mat[val] + [1]
                else:
                    grp.inputs[val].default_value = mat[val]
                
        ## MESHES
        for mesh in ignitJson["meshes"]:
            bpy.ops.import_scene.obj(filepath=path + '\\' + mesh["file"])
            
            for selected in bpy.context.selected_objects:
                if "position" in mesh.keys():
                    selected.location = (mesh["position"][0], -mesh["position"][2], mesh["position"][1])
                
                if "scale" in mesh.keys():
                    selected.scale = mesh["scale"]
                if "material" in mesh.keys():
                    if selected.data.materials:
                        # assign to 1st material slot
                        selected.data.materials[0] = bpy.data.materials[mesh["material"]]
                    else:
                        # no slots
                        selected.data.materials.append(bpy.data.materials[mesh["material"]])
            
        # for obj in bpy.data.objects:
        #     obj.scale = (0.01, 0.01, 0.01)

        ## LIGHTS

        for light in ignitJson["lights"]:
            if light["type"] == "Sphere":
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5)
                bpy.context.selected_objects[0].location = (light["position"][0], -light["position"][2], light["position"][1])
                bpy.context.selected_objects[0].scale = [light["radius"]]*3
                lightMat = bpy.data.materials.new("lightMat")
                lightMat.use_nodes = True
                lightMat.node_tree.nodes.clear()
                matOut = lightMat.node_tree.nodes.new("ShaderNodeOutputMaterial")
                emission = lightMat.node_tree.nodes.new("ShaderNodeEmission")
                emission.location = (-200, 0)
                col = (
                    light["emission"][0]/max(light["emission"]),
                    light["emission"][1]/max(light["emission"]),
                    light["emission"][2]/max(light["emission"])
                )
                colStrength = max(light["emission"])
                lightMat.node_tree.links.new(emission.outputs[0], matOut.inputs[0])
                # col = colorsys.rgb_to_hsv(col[0], col[1], col[2])
                col = bpy_extras.node_shader_utils.rgb_to_rgba(col)
                emission.inputs[0].default_value = col
                emission.inputs[1].default_value = colStrength
                bpy.context.selected_objects[0].data.materials.append(lightMat)
            elif light["type"] == "Quad":
                lightv1 = light["v1"]
                lightv2 = light["v2"]
                bpy.ops.mesh.primitive_plane_add(size=1)

                selectedPlane = bpy.context.selected_objects[0]
                selectedPlane.scale[0] = abs(lightv1[0] - lightv2[0])
                selectedPlane.scale[1] = abs(lightv1[2] - lightv2[2])

                selectedPlane.location = (
                    (lightv1[0]+lightv2[0])/2,
                    -(lightv1[2]+lightv2[2])/2,
                    light["position"][1]
                )
                
                lightMat = bpy.data.materials.new("lightMat")
                lightMat.use_nodes = True
                lightMat.node_tree.nodes.clear()
                matOut = lightMat.node_tree.nodes.new("ShaderNodeOutputMaterial")
                emission = lightMat.node_tree.nodes.new("ShaderNodeEmission")
                emission.location = (-200, 0)
                lightMat.node_tree.links.new(emission.outputs[0], matOut.inputs[0])

                col = (
                    light["emission"][0]/max(light["emission"]),
                    light["emission"][1]/max(light["emission"]),
                    light["emission"][2]/max(light["emission"])
                )
                col = bpy_extras.node_shader_utils.rgb_to_rgba(col)
                colStrength = max(light["emission"])

                emission.inputs[0].default_value = col
                emission.inputs[1].default_value = colStrength

                selectedPlane.data.materials.append(lightMat)



        return {"FINISHED"}

# this is garbage please do not use this please please please fix this oh god please no 
# this is the worst code i've ever written I couldn't think of a way to automate this 
# please do not use this in your code please I swear fix it
def ignitionNode(group:bpy.types.NodeTree=None):
    if group is None:
        group = bpy.data.node_groups.new("IgnitionDefault", "ShaderNodeTree")
    else:
        group.nodes.clear()
        group.inputs.clear()
        group.outputs.clear()
    nodeIn = group.nodes.new("NodeGroupInput")
    nodeIn.location = (-500, 0)
    nodeOut = group.nodes.new('NodeGroupOutput')
    nodeOut.location = (350, 0)
    
    group.inputs.new("NodeSocketColor",         "albedo")
    group.inputs.new("NodeSocketColor",         "albedoTexture")
    group.inputs.new("NodeSocketColor",         "emission")
    group.inputs.new("NodeSocketFloatFactor",   "metallic")
    group.inputs.new("NodeSocketFloatFactor",   "roughness")
    group.inputs.new("NodeSocketFloatFactor",   "specular")
    group.inputs.new("NodeSocketFloatFactor",   "specularTint")
    group.inputs.new("NodeSocketFloatFactor",   "subsurface")
    group.inputs.new("NodeSocketFloatFactor",   "anisotropic")
    group.inputs.new("NodeSocketFloatFactor",   "sheen")
    group.inputs.new("NodeSocketFloatFactor",   "sheenTint")
    group.inputs.new("NodeSocketFloatFactor",   "clearcoat")
    group.inputs.new("NodeSocketFloatFactor",   "clearcoatRoughness")
    group.inputs.new("NodeSocketFloatFactor",   "transmission")
    group.inputs.new("NodeSocketFloat",         "ior")
    group.inputs.new("NodeSocketColor",         "extinction")                       
    group.inputs.new("NodeSocketColor",         "metalicRoughnessTexture")#-------TODO
    group.inputs.new("NodeSocketColor",         "normalTexture")
    
    group.outputs.new("NodeSocketShader", "BSDF")
    
    for x in range(3, 14):
        group.inputs[x].min_value = 0
        group.inputs[x].max_value = 1

    group.inputs["specular"].default_value = 0.5
    group.inputs["roughness"].default_value = 0.5
    group.inputs["ior"].default_value = 1.45
    group.inputs["extinction"].default_value = [1, 1, 1, 1]
    group.inputs["albedo"].default_value = [1, 1, 1, 1]

    group.inputs["albedoTexture"].hide_value = True
    group.inputs["metalicRoughnessTexture"].hide_value = True
    group.inputs["normalTexture"].hide_value = True


    bsdf = group.nodes.new("ShaderNodeBsdfPrincipled")
    mixRgb = group.nodes.new("ShaderNodeMixRGB")
    mixRgb.location = (-260, -360)

    group.links.new(nodeOut.inputs[0], bsdf.outputs[0])

    group.links.new(bsdf.inputs[0], mixRgb.outputs[0])
    group.links.new(nodeIn.outputs["albedo"], mixRgb.inputs[1])
    group.links.new(nodeIn.outputs["extinction"], mixRgb.inputs[2])
    group.links.new(nodeIn.outputs["transmission"], mixRgb.inputs[0])
    
    group.links.new(nodeIn.outputs["emission"], bsdf.inputs["Emission"])
    group.links.new(nodeIn.outputs["metallic"], bsdf.inputs["Metallic"])
    group.links.new(nodeIn.outputs["roughness"], bsdf.inputs["Roughness"])
    group.links.new(nodeIn.outputs["specular"], bsdf.inputs["Specular"])
    group.links.new(nodeIn.outputs["specularTint"], bsdf.inputs["Specular Tint"])
    group.links.new(nodeIn.outputs["subsurface"], bsdf.inputs["Subsurface"])
    group.links.new(nodeIn.outputs["anisotropic"], bsdf.inputs["Anisotropic"])
    group.links.new(nodeIn.outputs["sheen"], bsdf.inputs["Sheen"])
    group.links.new(nodeIn.outputs["sheenTint"], bsdf.inputs["Sheen Tint"])
    group.links.new(nodeIn.outputs["clearcoat"], bsdf.inputs["Clearcoat"])
    group.links.new(nodeIn.outputs["clearcoatRoughness"], bsdf.inputs["Clearcoat Roughness"])
    group.links.new(nodeIn.outputs["transmission"], bsdf.inputs["Transmission"])
    group.links.new(nodeIn.outputs["ior"], bsdf.inputs["IOR"])
    group.links.new(nodeIn.outputs["normalTexture"], bsdf.inputs["Normal"])


