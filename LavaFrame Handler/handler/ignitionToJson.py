def IgnitionToJson(filepath):
    with open(filepath) as ignition:
        currentSettings = ""
        indents = 0
        ignitJson = {"materials":[], "meshes":[], "lights":[]}
        newItemIndexLIGHTS = 0
        newItemIndexMESH = 0
        def checkBegin(stringToCheck, check):
            return stringToCheck.startswith("\t"*indents + check)
        lineItem = -1
        for line in ignition.read().splitlines():
            lineItem += 1

            print(f"line {lineItem}: {line}\ncurrentSettings:{currentSettings}\nnewItemIndexLIGHTS:{newItemIndexLIGHTS}\nnewItemIndexMESH:{newItemIndexMESH}\nindents:{indents}")
            # Json conversion
            
            # lazy space character remover lol
            if ''.join(line.split()) == "":
                continue

            if checkBegin(line, "#"):
                continue

            if line.startswith("}"):
                indents -= 1
                if currentSettings == "mesh":
                    newItemIndexMESH += 1
                elif currentSettings == "light":
                    newItemIndexLIGHTS += 1

                currentSettings = ""
                continue

            if line.startswith("{"):
                indents += 1
                continue

            if indents == 0:
                currentSettings = line
                continue

            if currentSettings != "":
                
                for vals in line.split()[1:]:
                    itemVal = [f for f in vals if f not in "0 1 2 3 4 5 6 7 8 9 . -".split()]
                    if not any([currentSettings.startswith("material"), (currentSettings.startswith("mesh")), (currentSettings.startswith("light"))]):
                        if currentSettings not in ignitJson.keys():
                            ignitJson[currentSettings] = {}
                        if len(line.split()[1:]) == 1: # only one value
                            if itemVal != []: # no letters
                                ignitJson[currentSettings][line.split()[0]] = line.split()[1]
                                break
                            else:
                                ignitJson[currentSettings][line.split()[0]] = float(line.split()[1])
                                break
                        else:
                            if itemVal != []:
                                ignitJson[currentSettings][line.split()[0]] = line.split()[1:]
                                break
                            else:
                                ignitJson[currentSettings][line.split()[0]] = [float(x) for x in line.split()[1:]]
                                break
                    else:
                        inMatList = False
                        index = 0
                        listType = "materials" if currentSettings.startswith("material") else "lights" if currentSettings.startswith("light") else "meshes"
                        for checkIfInMatList in range(len(ignitJson[listType])):
                            if listType == "materials":
                                if ignitJson["materials"][checkIfInMatList]["name"] == currentSettings.split()[1]:
                                    inMatList = True
                                    index = checkIfInMatList
                                    break
                        
                        if listType == "meshes":
                            if len(ignitJson["meshes"]) == newItemIndexMESH:
                                ignitJson["meshes"].append({})
                        elif listType == "lights":
                            if len(ignitJson["lights"]) == newItemIndexLIGHTS:
                                ignitJson["lights"].append({})
                        
                        if not inMatList:
                            if listType == "materials":
                                ignitJson["materials"].append({"name":currentSettings.split()[1]})

                        index = len(ignitJson[listType])-1
                        if len(line.split()[1:]) == 1: # only one value
                            if itemVal != []: # no letters
                                print(index, ignitJson[listType])
                                ignitJson[listType][index][line.split()[0]] = line.split()[1]
                                break
                            else:
                                ignitJson[listType][index][line.split()[0]] = float(line.split()[1])
                                break
                        else:
                            if itemVal != []:
                                ignitJson[listType][index][line.split()[0]] = line.split()[1:]
                                break
                            else:
                                ignitJson[listType][index][line.split()[0]] = [float(x) for x in line.split()[1:]]
                                break
    return ignitJson