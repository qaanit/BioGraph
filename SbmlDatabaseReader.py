# :| 
# DO NOT CONTINUE
# Found better way -- uses neo4jsbml connection instead of neo4j
# This way is obolete becasuse it needs a new connection, while other doesn't
# hours wasted = 5
# ---------------------------------------------------------

import configparser
from neo4j import GraphDatabase
from neo4jsbml import connect

class SbmlDatabaseReader:

    def __init__(self) -> None:

        # Load configuration from localhost.ini
        config = configparser.ConfigParser()
        config.read('localhost.ini')

        # Extract connection details
        protocol = config.get('connection', 'protocol')
        url = config.get('connection', 'url')
        port = config.get('connection', 'port')
        username = config.get('database', 'user')
        password = config.get('database', 'password')


        # Construct the URI
        uri = f"{protocol}://{url}:{port}"

        # Create a driver instance
        self.driver = GraphDatabase.driver(uri, auth=(username, password))


    def __del__(self):
        self.driver.close()


    def run_query(self, query, parameters=None):
        # Function to run a query

        with self.driver.session() as session:
            result = session.run(query, parameters)
            return list(result)

    def check_model_exist():
        pass




# Example query
query = """
    MATCH (n) WHERE n.tag="BIOMD0000000001" RETURN (n)
    """

reader = SbmlDatabaseReader()
results = reader.run_query(query)

# Print the results
for result in results:
    print(result[0]['name'])
# Close the connection when done
