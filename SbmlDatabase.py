from neo4jsbml import arrows, connect, sbml
from BiomodelsDownloader import BiomodelsDownloader
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
            Path to the JSON file defining the modelisation.
        """
        self.config_path = config_path
        self.folder = folder
        self.modelisation_path = modelisation_path
        self.connection = connect.Connect.from_config(path=config_path) # Connection object to interact with the Neo4j database.
        self.arr = arrows.Arrows.from_json(path=modelisation_path)
        

    def load_and_import_model(self, model_id) -> None:
        """
        Loads an SBML model by index, maps it, and imports it into Neo4j.
        
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
        path_model = self.folder + "/" + model_id + ".xml"
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
        Query the current database, to see if model exists
            -- used to removed old models when it is updated
            -- prevent duplicate models

        Return:
            bool: True if model is found, False if not found
        """

        query = f"""MATCH (n) WHERE n.tag="{model_id}" RETURN (n)"""
        
        result = self.connection.query(query, expect_data=True)
        
        # Empty results
        if not result:
            return False
        
        return True

    
    def delete_model(self, model_id) -> None:
        """
        Queries database to delete a model based on tag
            -- deletes all nodes and relationships belonging to a node is 
        """

        query = f"""MATCH (n) WHERE n.tag="{model_id}" DETACH DELETE n"""
        self.connection.query(query, expect_data=False)
        
    
    def compare_models(self, model_id1, model_id2) -> int:
        """
        This Graph mathcing algorithm compares the similarity between two biomodels in graph format and returns a similarity score. 
        ONlY WORKS ON NON MERGED GRAPHS
        Works in a single query by taking into account, structure of the graph and node data as follows:
            1) Select weighting of structure vs child nodes
            2) Get/Match the two models being compared
            3) Count the nodes and relationships of each model -> traversal handled by neo4j
            4) Structural similarity is calculated by diffence in nodes and relationships independantly
            5) Child node similarity is the combination of nodes and edges/relationships eg. A HAS_SPECIES B
            6) This is compared by mathing lists of these relationships to each other
            7) The final similarity score is the weighted sum of structure and child nodes similarity

        Return:
            int: Similarity score calculation of two models. Accuracy between 0 and 1
        """

        STRUCTURE_WEIGHTING = 0.5
        CHILDREN_WEIGHTING = 0.5

        query = f"""
            // Define parameters for the two graphs to compare
            WITH '{model_id1}' AS graph1_id, '{model_id2}' AS graph2_id

            // Define weights for different similarity aspects (adjust as needed)
            WITH graph1_id, graph2_id,
                {STRUCTURE_WEIGHTING} AS w_structure,
                {CHILDREN_WEIGHTING} AS w_children

            // Compare nodes
            MATCH (n1:Model {{tag: graph1_id}})
            MATCH (n2:Model {{tag: graph2_id}})

            // Compare number of nodes and relationships
            WITH n1, n2, w_structure, w_children,
                count{{(n1)-[:HAS_COMPARTMENT|HAS_UNITDEFINITION|HAS_SPECIES|HAS_REACTION*]->(_)}} AS n1_elements,
                count{{(n2)-[:HAS_COMPARTMENT|HAS_UNITDEFINITION|HAS_SPECIES|HAS_REACTION*]->(_)}} AS n2_elements,
                count{{(n1)-[:HAS_COMPARTMENT|HAS_UNITDEFINITION|HAS_SPECIES|HAS_REACTION*]-(_)}} AS n1_relationships,
                count{{(n2)-[:HAS_COMPARTMENT|HAS_UNITDEFINITION|HAS_SPECIES|HAS_REACTION*]-(_)}} AS n2_relationships

            // Calculate structural similarity
            WITH n1, n2, w_structure, w_children,
                CASE WHEN n1_elements = n2_elements AND n1_relationships = n2_relationships THEN 1.0
                    ELSE (
                        (1.0 - abs(n1_elements - n2_elements) / toFloat(n1_elements + n2_elements)) * 0.5 +
                        (1.0 - abs(n1_relationships - n2_relationships) / toFloat(n1_relationships + n2_relationships)) * 0.5
                    )
                END AS structural_similarity

            // Compare child nodes (Compartments, Species, Reactions, etc.)
            MATCH (n1)-[:HAS_COMPARTMENT|HAS_SPECIES|HAS_REACTION]->(child1)
            MATCH (n2)-[:HAS_COMPARTMENT|HAS_SPECIES|HAS_REACTION]->(child2)
            WHERE labels(child1) = labels(child2)

            WITH n1, n2, w_structure, w_children,
                structural_similarity,
                collect(child1) AS children1, collect(child2) AS children2

            // Calculate child node similarity
            WITH n1, n2, w_structure, w_children,
                structural_similarity,
                children1, children2,
                size(children1) AS total_children

            UNWIND children2 AS c2
            WITH n1, n2, w_structure, w_children,
                structural_similarity,
                children1, total_children, collect(c2.id) AS children2_ids

            // calculation
            WITH n1, n2, w_structure, w_children,
                structural_similarity,
                total_children,
                CASE WHEN total_children > 0
                    THEN toFloat(size([c1 IN children1 WHERE c1.id IN children2_ids])) / total_children
                    ELSE 1.0
                END AS children_similarity

            // Calculate final similarity score
            WITH 
                structural_similarity * w_structure +
                children_similarity * w_children
                AS similarity_score

            RETURN similarity_score
            """

        result = self.connection.query(query, expect_data=True) # this accuracy is not parsed
        if result == []: return 0
        accuracy = result[0]['similarity_score']

        return accuracy
    

    def search_for_compartment(self, compartment) -> list:
        """
        Queries Database to find all models that has constains a specific compartment.
            
        Return:
            list: A list of all unique matching models
        """

        query = f"""
                MATCH (m:Model)-[:HAS_COMPARTMENT]->(c:Compartment)
                WHERE c.id = "{compartment}"
                RETURN m
                """
        result = self.connection.query(query, expect_data=True)

        if not result:
            print("No models found")
            return
    
        matching_models = set()

        for model in result:
            matching_models.add(model["m"]["name"])

        return list(matching_models)


    def search_for_compound(self, compound) -> list:
        """
            Queries Database to find all models that has a contains a specific species/compound.
            
            Return:
                list: A list of all unique matching models
        """

        query = f"""
                MATCH (m:Model)-[:HAS_SPECIES]->(s:Species)
                WHERE s.id = "{compound}"
                RETURN m
                """
        result = self.connection.query(query, expect_data=True)

        if not result:
            print("No models found")
            return
        
        matching_models = set()

        for model in result:
            matching_models.add(model["m"]["name"])

        return list(matching_models)


    def search_compound_in_compartment(self, compound, compartment) -> list:
        """
        Queries Database to find all models that has contains a specific species in a specific compartment.
            
        Return:
            list: A list of all unique matching models
        """

        query = f"""
                MATCH (m:Model)-[:HAS_SPECIES]->(s:Species)-[:IN_COMPARTMENT]->(c:Compartment)
                WHERE s.id = "{compound}" AND c.id = "{compartment}"
                RETURN m
                """

        result = self.connection.query(query, expect_data=True)

        if not result:
            print("No models found")
            return
        
        matching_models = set()

        for model in result:
            matching_models.add(model["m"]["name"])

        return list(matching_models)


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
        query = f"""
                MATCH (m:Model) Return (m.tag);
                """

        all_models = []
        result = self.connection.query(query, expect_data=True)

        for model in result:
            all_models.append(model["(m.tag)"])

        # Remove merged models whose tag is the same 
        return sorted(list(set(all_models)))


    def find_all_similar(self, model_id, MODEL_LIMIT=-1) -> tuple:
        """DOCS"""

        similar_models = []
        all_models = self.find_all_models()

        for model in all_models:
            if "-" in model: continue

            accuracy = self.compare_models(model_id, model)
            similar_models.append((model, round(accuracy * 100, 2)))
        
        similar_models = sorted(similar_models, key=lambda x: x[1], reverse=True)

        if MODEL_LIMIT != -1:
            return similar_models[:MODEL_LIMIT]

        return similar_models
    

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
    # This will convert the sbml to graph format based on provided schema and loads them directly to connected neo4j server
    database = SbmlDatabase("localhost.ini", "biomodels", "Schemas/default_schema.json")
    database.import_models(model_list=models)
    
    # Find all models
    # print(database.find_all_models())
    
    print(database.find_all_similar("BIOMD0000000001", 5))
    exit()
    database.merge_biomodels("BIOMD0000000003", "BIOMD0000000004")
    database.load_and_import_model("BIOMD0000000003")
    database.load_and_import_model("BIOMD0000000004")
    database.load_and_import_model("BIOMD0000000005")

    # Search for compund
    print(database.search_for_compound("C"))
    
    # Search for compartment
    print(database.search_for_compartment("cell"))

    # Search for compound in compartment
    print(database.search_compound_in_compartment(compound="C", compartment="cell"))

    # Compare two models using graph traversal algorithms
    print(database.compare_models("BIOMD0000000003", "BIOMD0000000004"))

    

    # test for up   dating models
    #database.import_models(["BIOMD0000000001"])

    # Test to see if load_and_import, delete_model and check_model_exists()
    # database.load_and_import_model("BIOMD0000000001")
    #print(database.check_model_exist("BIOMD0000000001"))
    # database.delete_model("BIOMD0000000001")
    #print(database.check_model_exists("BIOMD0000000001"))
