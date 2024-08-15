from neo4jsbml import arrows, connect, sbml
from BiomodelsDownloader import BiomodelsDownloader

class SbmlDatabase:
    """
    A class to handle the process of importing SBML models into a Neo4j database.

    Attributes:
    -----------
    config_path : str
        Path to the Neo4j configuration file.
    folder : str
        Directory where the SBML models are stored.
    modelisation_path : str
        Path to the JSON file defining the modelisation/schema. 
      
    
    Methods:
    --------
    __init__(config_path, folder, modelisation_path):
        Initializes the Database with the provided configuration.
    
    load_and_import_model(model_id):
        Loads an SBML model by id, maps it, and imports it into Neo4j.
    
    import_models(range_start, range_end):
        Imports multiple SBML models into Neo4j over a specified range of indices.
    """
    
    def __init__(self, config_path, folder, modelisation_path):
        """
        Initializes Database with the provided configuration.
        
        Parameters:
        -----------
        config_path : str
            Path to the Neo4j configuration file.
        folder : str
            Directory where the SBML models are stored.
        modelisation_path : str
            Path to the JSON file defining the modelisation.
        """
        self.config_path = config_path
        self.folder = folder
        self.modelisation_path = modelisation_path
        self.connection = connect.Connect.from_config(path=config_path) # Connection object to interact with the Neo4j database.
        self.arr = arrows.Arrows.from_json(path=modelisation_path)
        

    def load_and_import_model(self, model_id):
        """
        Loads an SBML model by index, maps it, and imports it into Neo4j.

        model_id : int
            Name/Number of the model to be imported
        """

        path_model = self.folder + "/" + model_id
        tag = path_model
        sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model, tag=tag)

        # Mapping
        nod = sbm.format_nodes(nodes=self.arr.nodes)
        rel = sbm.format_relationships(relationships=self.arr.relationships)

        # Import into Neo4j
        self.connection.create_nodes(nodes=nod)
        self.connection.create_relationships(relationships=rel)


    def import_models(self, range_start, range_end):
        """
        Imports multiple SBML models into Neo4j over a specified range of indices.

        range_start : int
            Starting index for the SBML models.
        range_end : int
            Ending index for the SBML models.
        """
        for i in range(range_start, range_end + 1):
            model_id = f"BIOMD{i:010}.xml"
            self.load_and_import_model(model_id=model_id)

    def check_model_updates(): # TODO: verify that each model is latest version
        pass
    

if __name__ == "__main__":

    # These models are all downloaded from the biomodels database
    downloader = BiomodelsDownloader(num_models=20, threads=5, curatedOnly=True)
    downloader.run() 

    """
    model.load_and_import_model() # manually add model by file name
    this is how the user can add their own models / pipeline
    """

    # Creating Server with given schema, and neo4j configs [folder is where biomodels xml are stored and loaded]
    model = SbmlDatabase("localhost.ini", "biomodels", "L3V2.7-1.json")
    
    # This will convert the sbml to graph format based on provided schema and loads them directly to connected neo4j server
    model.import_models(1, 20) 