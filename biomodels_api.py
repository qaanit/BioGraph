from biomodels_restful_api_client import services as bmservices


model = bmservices.get_model_info("BIOMD0000000900")

# print(model) # print all parameters

submissionId = model['submissionId']
publicationId = model['publicationId'] # could be needed for downloading model

print(submissionId, publicationId)

# biomodels api gives header of SBML file and other info as above
# cannot actually download

'''
# actual biomodels api - downloads file into cache, (can read from cache - unkown path config)

import biomodels

for i in range(1, 10):

    metadata = biomodels.get_metadata(f"BIOMD00000000{i:02d}")
    # print(metadata) # view all files from model

    biomodels.get_file(f"BIOMD00000000{i:02d}_url.xml", model_id=f"BIOMD{i}")
    path = biomodels.get_file(metadata[0])
    
    print(path.read_text())



'''