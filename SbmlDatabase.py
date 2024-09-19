from neo4jsbml import arrows, connect, sbml
from BiomodelsDownloader import BiomodelsDownloader
from SbmlDatabaseQueries import SbmlDatabaseQueries
import os


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
        Check if database contains a model.

    delete_model(model_id):
        Deletes model from database.

    compare_models(model_id1, model_id2):
        Calculates similarity between two models.

    search_for_compartment(compartment):        
        Finds models that have a specific compartment.

    search_for_compund(compound):
        Finds models that contains a specific compund.
    
    search_compound_in_compartment(compound, compartment):
        Finds models that contains specific species in a specific compartment.

    change_schema(modelisation_path):
        Change schema that converts sbml to graphs
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
            Path to the JSON file defining the chema/modelisation.
        """
        self.config_path = config_path
        self.folder = folder
        self.modelisation_path = modelisation_path
        self.connection = connect.Connect.from_config(path=config_path) # Connection object to interact with the Neo4j database.
        self.arr = arrows.Arrows.from_json(path=modelisation_path)
        self.sbmlQueries = SbmlDatabaseQueries(connection=self.connection)

    def load_and_import_model(self, model_id, path=False) -> None:
        """
        Loads an SBML model by index, maps it, and imports it into Neo4j.
            - path means that the model id contains the whole path and its extension
        NB! Load and import models uses neo4jsbml 
        -- connection is loaded via this package
        -- it uses a single neo4jsbml connection established in the constructor

        model_id : int
            Name/Number of the model to be imported
        """

        # RESOLVE CONFLICTS -- Database queried to remove old model and continue as usual
        if self.check_model_exists(model_id):
            self.delete_model(model_id)
            print(f"Deleting old model {model_id}")

        # ADD NEW MODELS
        if not path:
            path_model = self.folder + "/" + model_id + ".xml"
        else:
            path_model = model_id 

        tag = model_id 
        sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model, tag=tag)

        # Mapping sbml to graph
        nod = sbm.format_nodes(nodes=self.arr.nodes)
        rel = sbm.format_relationships(relationships=self.arr.relationships)

        # Import graph into Neo4j
        self.connection.create_nodes(nodes=nod)
        self.connection.create_relationships(relationships=rel)


    def merge_biomodels(self, model_id1, model_id2) -> None:
        """
        Loads an 2 SBML models and merges them to one graph
            - uses database connection to add model

        model_id1 : int
            Name/Number of the first model to be merged

        model_id2 : int
            Name/Number of the second model to be merged
        """
        if not(self.check_model_exists(model_id=model_id1) and self.check_model_exists(model_id=model_id2)):
            return "MODEL\S IN MERGE NOT FOUND"

        tag = model_id1 + "-" + model_id2 # A merged models tag/name is both model tags combined

        if self.check_model_exists(tag):
            self.delete_model(tag)
            print(f"Deleting old model {tag}")

        # Specify location of two graphs
        path_model1 = self.folder + "/" + model_id1 + ".xml"
        path_model2 = self.folder + "/" + model_id2 + ".xml"

        # Mapping sbml to model1
        sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model1, tag=tag)
        nod = sbm.format_nodes(nodes=self.arr.nodes)
        rel = sbm.format_relationships(relationships=self.arr.relationships)

        # Import graph1 into Neo4j
        self.connection.create_nodes(nodes=nod)
        self.connection.create_relationships(relationships=rel)

        # Mapping sbml to model2
        sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model2, tag=tag)   
        nod = sbm.format_nodes(nodes=self.arr.nodes)
        rel = sbm.format_relationships(relationships=self.arr.relationships)

        # Import graph2 into Neo4j
        self.connection.create_nodes(nodes=nod)
        self.connection.create_relationships(relationships=rel)

        return tag

    def import_models(self, model_list) -> None:
        """
        Imports multiple SBML models into Neo4j specified by a list containing model numbers
        """

        if not model_list:
            print("No new models added")
            return

        for model in model_list:
            self.load_and_import_model(model)


    def check_model_exists(self, model_id) -> bool:
        """
        Returns True if models is in database otherwise False
            - Refer to SbmlDatabaseQueries.check_model_exists() for implementation details
        """
        return self.sbmlQueries.check_model_exists(model_id)
        
    
    def delete_model(self, model_id) -> None:
        """
        Queries database to delete a model based on tag
            - deletes all nodes and relationships belonging to a node
        """
        query = f"""MATCH (n) WHERE n.tag="{model_id}" DETACH DELETE n"""
        self.connection.query(query, expect_data=False)
        
    
    def compare_models(self, model_id1, model_id2) -> int:
        """
        Returns accuracy score percentage based on similarity between models
            - Refer to SbmlDatabaseQueries.compare_models() for implementation details
        """
        accuracy = self.sbmlQueries.compare_models(model_id1=model_id1, model_id2=model_id2)
        return accuracy
    

    def search_for_compartment(self, compartment) -> list:
        """
            Returns list of models that have a certain compartment
            - Refer to SbmlDatabaseQueries.search_for_compartment() for implementation details
        """
        matching_models = self.sbmlQueries.search_for_compartment(compartment)
        return matching_models

    def search_for_compound(self, compound) -> list:
        """
            Returns list of models that have a certain compund
            - Refer to SbmlDatabaseQueries.search_for_compound() for implementation details
        """
        matching_models = self.sbmlQueries.search_for_compund(compound)
        return matching_models


    def search_compound_in_compartment(self, compound, compartment) -> list:
        """
            Returns list of models that have a certain compund
            - Refer to SbmlDatabaseQueries.search_for_compound_in_compartment() for implementation details
        """
        matching_models = self.sbmlQueries.search_for_compound_in_compartment(compound, compartment)
        return matching_models


    def change_schema(self, modelisation_path):
        """Change schema of database. All following added models will use this schema. Old ones do not change."""

        if modelisation_path[-5:] != ".json":
            print("Invalid input provided")
            return 

        if not os.path.isfile(modelisation_path):
            print("Schema not found")
            return

        print("Schema changed to", modelisation_path)
        self.arr = arrows.Arrows.from_json(path=modelisation_path)


    def find_all_models(self) -> list:
        """
            Returns list of all models in database
            - Refer to SbmlDatabaseQueries.find_all_models() for implementation details
        """
        all_models = self.sbmlQueries.find_all_models()
        return all_models


    def find_all_similar(self, model_id, MODEL_LIMIT=-1) -> tuple:
        """
            Returns list of models that have the highest similartiy with a model provided
                -- returns a list of tuples containing (model_id, accuracy)
            - Refer to SbmlDatabaseQueries.find_all_similar() for implementation details
        """
        similar_models = self.sbmlQueries.find_all_similar(model_id=model_id, MODEL_LIMIT=MODEL_LIMIT)
        return similar_models


if __name__ == "__main__":

    # These models are all downloaded from the biomodels database
    downloader = BiomodelsDownloader(threads=5, curatedOnly=True)
    models = downloader.verifiy_models(10) # will download all models
    # returns a list of all new models downloaded or updated

    """
    The following is example usage of the class functionality, should not be used when imported
    """

    # Creating Server with given schema, and neo4j configs [folder is where biomodels xml are stored and loaded]
    # This will convert the sbml to graph format based on provided schema and loads them directly to connected neo4j server
    database = SbmlDatabase("localhost.ini", "biomodels", "Schemas/default_schema.json")
    database.import_models(model_list=models)
    database.merge_biomodels("BIOMD0000000003", "BIOMD0000000004")

    # Find all models
    # Test loading
    print(database.find_all_models())
    print(database.find_all_similar("BIOMD0000000001", 5))
    database.load_and_import_model("BIOMD0000000003")
    database.load_and_import_model("BIOMD0000000004")
    database.load_and_import_model("BIOMD0000000005")
    database.delete_model("BIOMD0000000003-BIOMD0000000004")

    # Search for compund
    print(database.search_for_compound("C"))
    
    # Search for compartment
    print(database.search_for_compartment("cell"))

    # Search for compound in compartment
    print(database.search_compound_in_compartment(compound="C", compartment="cell"))

    # Compare two models using graph traversal algorithms
    print(database.compare_models("BIOMD0000000003", "BIOMD0000000004"))

    # test for up   dating models
    database.import_models(["BIOMD0000000001"])

    # Test to see if load_and_import, delete_model and check_model_exists()
    database.load_and_import_model("BIOMD0000000001")
    print(database.check_model_exist("BIOMD0000000001"))
    database.delete_model("BIOMD0000000001")
    print(database.check_model_exists("BIOMD0000000001"))
    