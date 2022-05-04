from surgicalverify import SurgicalVerify
print("start to verify")
JsonFile = "operativedata.json"
verify = SurgicalVerify("", "")
verify.ReadJson(JsonFile, False)
# verify.selectOptimalPoint()
verify.distanceAndAngleCompute(5)
# verify.UpdateExcel("verify.xlsx", "hangzhou_No5-WHY15")