from neo4jsbml import arrows, connect, sbml

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
    curatedOnly:
        Only adds curated models to the database.    
    
    Methods:
    --------
    __init__(config_path, folder, modelisation_path):
        Initializes the Database with the provided configuration.
    
    load_and_import_model(model_id):
        Loads an SBML model by id, maps it, and imports it into Neo4j.
    
    import_models(range_start, range_end):
        Imports multiple SBML models into Neo4j over a specified range of indices.
    """
    
    def __init__(self, config_path, folder, modelisation_path, curatedOnly):
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
        self.curatedOnly = curatedOnly
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

    def check_model_updates(): # TODO
        pass
    

if __name__ == "__main__":
    model = SbmlDatabase("localhost.ini", "biomodels", "L3V2.7-1.json", curatedOnly=False)
    model.import_models(1, 5) 