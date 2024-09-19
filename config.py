# Constants
CHECK_UPDATED_BIOMODELS = False
DOWNLOADING_THREADS = 10
CURATED_ONLY = True
NUMBER_OF_MODELS_TO_DOWNLOAD_FROM_DATABASE = 10  # defualt is -1 = all models

# Accuracy Weighting of graph matching, Adds up to 1
NODE_WEIGHTING = 0.5
STRCUTURE_WEIGHTING = 0.5
TOTAL_MATCHING_GRAPHS = 10 # The number of top mathing models to RETURNS

# FOLDERS
BIOMODELS_DATABASE_FOLDER = "biomodels" # Folder where database biomodels are downloaded
SCHEMA_FOLDER = "Schemas"
CONFIGURATION_FILE = "localhost.ini"
DEFAULT_SCHEMA = "Schemas/default_schema.json"

# DATABASE
BIOMODELS_DATABASE = "https://www.ebi.ac.uk/biomodels/search/download" # URL for downloading files
METADATA_URL = "https://www.ebi.ac.uk/biomodels/model/files/{model}?format=json" # URL For checking model updates