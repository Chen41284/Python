import os
from surgicalverify import SurgicalVerify
import json
import numpy as np
import copy
import datetime


def verifyInterface(inputDirectory : str, outputDirectory : str):
    ImagePath = inputDirectory + "/Image"

    verify = SurgicalVerify(ImagePath, outputDirectory)
    ImplantWidth = 4.1
    ImplantLength = 12
    ImplantArea = "46"

    JsonFile = inputDirectory + "/operativedata.json"
    print("JsonFile: ", JsonFile)
    with open(JsonFile, 'r', encoding='utf-8') as f:
        try:
            info_dict = json.load(f)
            ImplantWidth = float(info_dict['ImplantInfo']['Diameter'])
            ImplantLength = int(info_dict['ImplantInfo']['Length'])
            ImplantArea = info_dict['ImplantInfo']['Area']
            print(info_dict['ImplantInfo']['Diameter'])
            print(info_dict['ImplantInfo']['Length'])
            print(info_dict['ImplantInfo']['Area'])
        except:
            print("cannot read or update json file")

    # verify.setsortThreshold(3)
    verify.setImplantWidth(ImplantWidth)
    verify.setImplantLength(ImplantLength)
    verify.setImplantArea(ImplantArea)
    verify.setdetectImplant(True)
    verify.setsolid(True)
    verify.setJsonFile(JsonFile)
    verify.ReadJson(JsonFile)
    # verify.setOperativeStage('preoperative')
    verify.setOperativeStage('postoperative')
    verify.AutoDetect()


