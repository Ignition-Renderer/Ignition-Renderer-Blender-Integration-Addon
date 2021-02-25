import bpy, bpy_extras, math, json, os
from . import exceptions

class IgnitionFileLoader(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Takes care of loading in the .ignition file into your blender proejct."""
    bl_idname = "object.ignitionfileloader"
    bl_label = "Load Ignition File"
    bl_options = {'REGISTER'}

    filter_glob: bpy.props.StringProperty(default="*.ignition", options={"HIDDEN"})

    filepath = "" # removing undefined var error
    def menu_func(self, context):
        self.layout.operator(IgnitionFileLoader.bl_idname)

    def execute(self, context):
        bpy.context.scene.render.engine = "CYCLES"
        filename, extension = os.path.splitext(self.filepath)
        path = '\\'.join(self.filepath.split("\\")[:-1])
        if extension != ".ignition":
            raise exceptions.NotAnIgnitionFile("This specified file was not a .ignition file")
        
        with open(filename+extension) as ignition:
            
            currentSettings = ""
            indents = 0
            ignitJson = {"materials":[], "meshes":[]}
            currentObjFile = ""

            def checkBegin(stringToCheck, check):
                return stringToCheck.startswith("\t"*indents + check)
            for line in ignition.read().splitlines():
                # Json conversion
                
                if checkBegin(line, "#"):
                    continue

                if line == "}":
                    indents -= 1
                    currentSettings = ""
                    continue

                if line == "{":
                    indents += 1
                    continue
                

                if indents == 0:
                    currentSettings = line
                    continue
                
                if checkBegin(line, "file"):
                    currentObjFile = line.split()[1]

                if currentSettings != "":
                    
                    for vals in line.split()[1:]:
                        itemVal = [f for f in vals if f in "0 1 2 3 4 5 6 7 8 9".split()]
                        if not any([currentSettings.startswith("material"), (currentSettings == "mesh")]):
                            if currentSettings not in ignitJson.keys():
                                ignitJson[currentSettings] = {}
                            if len(line.split()[1:]) == 1: # only one value
                                if itemVal == []: # no numbers
                                    ignitJson[currentSettings][line.split()[0]] = line.split()[1]
                                    break
                                else:
                                    ignitJson[currentSettings][line.split()[0]] = float(line.split()[1])
                                    break
                            else:
                                if itemVal == []:
                                    ignitJson[currentSettings][line.split()[0]] = line.split()[1:]
                                    break
                                else:
                                    ignitJson[currentSettings][line.split()[0]] = [float(x) for x in line.split()[1:]]
                                    break
                        else:
                            inMatList = False
                            index = 0
                            listType = "materials" if currentSettings.startswith("material") else "meshes"
                            for checkIfInMatList in range(len(ignitJson[listType])):
                                if listType == "materials":
                                    if ignitJson["materials"][checkIfInMatList]["name"] == currentSettings.split()[1]:
                                        inMatList = True
                                        index = checkIfInMatList
                                        break
                                elif listType == "meshes":
                                    if line.split()[0] == "file":
                                        break
                                    else:
                                        if ignitJson["meshes"][checkIfInMatList]["file"] == currentObjFile:
                                            inMatList = True
                                            index = checkIfInMatList
                                            break
                                        
                            
                            if not inMatList:
                                if listType == "materials":
                                    ignitJson["materials"].append({"name":currentSettings.split()[1]})
                                elif listType == "meshes":
                                    ignitJson["meshes"].append({"file":currentObjFile})

                            index = len(ignitJson[listType])-1
                            if len(line.split()[1:]) == 1: # only one value
                                if itemVal == []: # no numbers
                                    print(index, ignitJson[listType])
                                    ignitJson[listType][index][line.split()[0]] = line.split()[1]
                                    break
                                else:
                                    ignitJson[listType][index][line.split()[0]] = float(line.split()[1])
                                    break
                            else:
                                if itemVal == []:
                                    ignitJson[listType][index][line.split()[0]] = line.split()[1:]
                                    break
                                else:
                                    ignitJson[listType][index][line.split()[0]] = [float(x) for x in line.split()[1:]]
                                    break

        # debugging
        json.dump(ignitJson, open(r"C:\Users\rapha\Desktop\ignition_beta_win32\ex.json", 'w'))
        
                
        # json -> blender
        bpy.context.scene.render.engine = "CYCLES"

        scene = bpy.context.scene
        ## RENDERER SETTINGS
        scene.render.resolution_x = ignitJson["Renderer"]["resolution"][0]
        scene.render.resolution_y = ignitJson["Renderer"]["resolution"][1]

        scene.cycles.max_bounces, scene.cycles.diffuse_bounces, scene.cycles.glossy_bounces, scene.cycles.transparent_max_bounces, scene.cycles.transmission_bounces = [ignitJson["Renderer"]["maxDepth"] for _ in range(5)]

        # tile width/tile height do not have a setting existant inside of Blender. (tiles are defaulted to 64x64)

        scene.use_nodes = True

        envText = None
        if not "Environment Texture" in scene.world.node_tree.nodes.keys():
            scene.world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        
        envText = scene.world.node_tree.nodes["Environment Texture"]
        
        envText.image = bpy.data.images.load(path+"\\"+ignitJson["Renderer"]["envMap"])
        scene.world.node_tree.links.new(envText.outputs[0], scene.world.node_tree.nodes["Background"].inputs[0])

        scene.world.node_tree.nodes["Background"].inputs[1].default_value = ignitJson["Renderer"]["hdrMultiplier"]

        ## CAMERA SETTINGS
        if "Camera" not in scene.objects.keys():
            cameraDat = bpy.data.cameras.new("Camera")
            scene.collection.objects.link(bpy.data.objects.new("Camera", cameraDat))

        camera = scene.objects["Camera"]
        scene.camera = camera

        camera.location = ignitJson["Camera"]["position"]

        if [e for e in scene.objects.keys() if e.startswith("Empty")] == []:
            empty = bpy.data.objects.new("Empty", None)
            scene.collection.objects.link(empty)

        # im so fucking stupid and i hate this line of code so fucking much
        empty = scene.objects[[e for e in scene.objects.keys() if e.startswith("Empty")][0]]
        empty.location = ignitJson["Camera"]["lookAt"]

        if "Track To" not in camera.constraints.keys():
            camera.constraints.new("TRACK_TO")

        camera.constraints["Track To"].target = empty
        bpy.data.cameras["Camera"].angle  = math.radians(ignitJson["Camera"]["fov"])

        ## MATERIALS

        return {"FINISHED"}

def ignitionNode():
    bpy.data.node_groups.new("IgnitionDefault", "WorldNodeTree")