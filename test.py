
from biomodels_restful_api_client import services as bmservices

#print(bmservices.get_model_info("BIOMD0000000900"))
#bmservices.download("BIOMD0000000900","Bianca2013.xml")
#print(bmservices.get_model_files_info("BIOMD0000000900", "xml")) BIOMD0000000920

enteredmodel = input("Enter model number: ")
model = bmservices.get_model_info(enteredmodel)

name = model['name']

mname = name.split()

if mname[0] == name:
    mname = name.split("_")

filename = mname[0]

try:
    bmservices.download(enteredmodel,f"{filename}.xml")
except:
    bmservices.download(enteredmodel,f"{enteredmodel}_url.xml")

print(name)