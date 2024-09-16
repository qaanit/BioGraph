from mainGUI import *
from SbmlDatabase import SbmlDatabase
from BiomodelsDownloader import BiomodelsDownloader


# These models are all downloaded from the biomodels database
downloader = BiomodelsDownloader(threads=5, curatedOnly=True)
models = downloader.verifiy_models() # will download all models
# returns a list of all new models downloaded or updated

"""
model.load_and_import_model() # manually add model by file name
this is how the user can add their own models / pipeline
"""

# Creating Server with given schema, and neo4j configs [folder is where biomodels xml are stored and loaded]
# This will convert the sbml to graph format based on provided schema and loads them directly to connected neo4j server
database = SbmlDatabase("localhost.ini", "biomodels", "default_schema.json")
database.import_models(model_list=models)


app = QApplication(sys.argv)
window = FileUploaderApp()
window.show()
sys.exit(app.exec())
