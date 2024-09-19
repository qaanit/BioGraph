import config

"""Helper Class to SbmlDatabse, Handles all query functions for class"""

class SbmlDatabaseQueries():
    """
    Methods:
    ------------

    check_model_exists(model_id):
        Check if database contains a model.

    compare_models(model_id1, model_id2):
        Calculates similarity between two models.

    search_for_compartment(compartment):        
        Finds models that have a specific compartment.

    search_for_compund(compound):
        Finds models that contains a specific compund.
    
    search_compound_in_compartment(compound, compartment):
        Finds models that contains specific species in a specific compartment.
    """

    def __init__(self, connection):
        """Connection from creating sbmldatabase is passed and reused"""
        self.connection = connection
    
        
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
        
        # Empty results -- not found
        if not result:
            return False
        
        return True
    
    def compare_models(self, model_id1, model_id2):
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

        STRUCTURE_WEIGHTING = config.STRCUTURE_WEIGHTING
        CHILDREN_WEIGHTING = config.NODE_WEIGHTING

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
    

    def search_for_compartment(self, compartment):
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

  
    def search_for_compund(self, compound):
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


    def search_for_compound_in_compartment(self, compound, compartment):
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
    

    def find_all_models(self):
        """Returns a list of all models present in the database"""

        query = f"""
                MATCH (m:Model) Return (m.tag);
                """

        all_models = []
        result = self.connection.query(query, expect_data=True)

        for model in result:
            all_models.append(model["(m.tag)"])

        # Remove merged models whose tag is the same 
        return sorted(list(set(all_models)))


    def find_all_similar(self, model_id, MODEL_LIMIT=-1):
        """
            1)Queries to find all models in database
            2)Checks accuracy score against all models
            3)Sorts list based on accuracy
            4)Returns models with the highest accuracy rating

            Returns:
                list[tuple()] -> list of models with their accuracy [(model_id, accuracy)]
        """

        similar_models = []
        all_models = self.find_all_models()

        # Remove merged models from comparison
        for model in all_models:    
            if "-" in model: continue

            accuracy = self.compare_models(model_id, model)
            similar_models.append((model, round(accuracy * 100, 2)))
        
        similar_models = sorted(similar_models, key=lambda x: x[1], reverse=True)

        if MODEL_LIMIT != -1:
            return similar_models[:MODEL_LIMIT]

        return similar_models