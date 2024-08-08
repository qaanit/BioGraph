from biomodels_restful_api_client import services as bmservices


model = bmservices.get_model_info("BIOMD0000000900")

# print(model) # print all parameters

submissionId = model['submissionId']
publicationId = model['publicationId'] # could be needed for downloading model

print(submissionId, publicationId)

# biomodels api gives header of SBML file and other info as above
# cannot actually download
