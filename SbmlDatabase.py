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
    
    import_models(model_list):
        Imports multiple SBML models into Neo4j.

    check_model_exists(model_id):
        check if database contains a model

    delete_model(model_id):
        deltes model from databse

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
        
        NB! Load and import models uses neo4jsbml 
        -- connection is loaded via this package
        -- it uses a single neo4jsbml connection established in the constructor

        model_id : int
            Name/Number of the model to be imported
        """

        # RESOLVE CONFLICTS -- Database needs to be queried -- remove old model and continue as usual
        if self.check_model_exists(model_id):
            self.delete_model(model_id)
            print(f"Deleting old model {model_id}")

        # ADD NEW MODELS
        path_model = self.folder + "/" + model_id + ".xml"
        tag = model_id # Inlcude model version 
        sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model, tag=tag)

        # Mapping sbml to graph
        nod = sbm.format_nodes(nodes=self.arr.nodes)
        rel = sbm.format_relationships(relationships=self.arr.relationships)

        # Import graph into Neo4j
        self.connection.create_nodes(nodes=nod)
        self.connection.create_relationships(relationships=rel)

        return
    

    def import_models(self, model_list):
        """
        Imports multiple SBML models into Neo4j specified by a list containing model numbers

        """

        if not model_list:
            print("No new models added")
            return


        for model in model_list:
            self.load_and_import_model(model)

        return

    def check_model_exists(self, model_id):

        """
        Query the current database, to see if model exists
            -- used to removed old models when it is updated
            -- prevent duplicate models

        Return:
            bool: True if model is found, False if not found
        """

        query = f"""MATCH (n) WHERE n.tag="{model_id}" RETURN (n)"""
        
        result = self.connection.query(query, expect_data=True)
        
        if not result:
            return False
        else:
            return True

    
    def delete_model(self, model_id):
        """
        Queries database to delete a model based on tag
            -- deletes all nodes and relationships belonging to a node is 
        """

        query = f"""MATCH (n) WHERE n.tag="{model_id}" DETACH DELETE n"""
        self.connection.query(query, expect_data=False)
        
        

if __name__ == "__main__":

    # These models are all downloaded from the biomodels database
    downloader = BiomodelsDownloader(threads=5, curatedOnly=True)
    models = downloader.verifiy_models() # will download all models
    # returns a list of all new models downloaded or updated

    """
    model.load_and_import_model() # manually add model by file name
    this is how the user can add their own models / pipeline
    """

    # Creating Server with given schema, and neo4j configs [folder is where biomodels xml are stored and loaded]
    database = SbmlDatabase("localhost.ini", "biomodels", "L3V2.7-1.json")
    
    # This will convert the sbml to graph format based on provided schema and loads them directly to connected neo4j server
    
    # test for updating models
    # database.import_models(["BIOMD0000000001"])

    # Test to see if load_and_import, delete_model and check_model_exists()
    #database.load_and_import_model("BIOMD0000000001")
    #print(database.check_model_exist("BIOMD0000000001"))
    #database.delete_model("BIOMD0000000001")
    #print(database.check_model_exists("BIOMD0000000001"))
