SBML Model Pipeline to Neo4j Database
Project Overview
This project allows users to create a pipeline for SBML models from an existing database (BioModels) to a local or public Neo4j server. It converts SBML models to graph format and stores them in the database using a specified schema. Users can then perform queries to find specific compounds, and graph matching can be used to find similar SBML models beyond text-based comparisons. A GUI is available to make the process user-friendly, and BioModels can be visualized directly through it.
Installation
Conda Environment
A Conda environment is required due to the dependency on neo4jsbml.
conda install -c conda-forge neo4jsbml
Python Dependencies
All dependencies are listed in the requirements.txt file. Install them with:
pip install -r requirements.txt
Key dependencies include:
- Requests – for downloading BioModels from the BioModels database
- PyQt6 – for the main user interface
- Py2neo, NetworkX, matplotlib – for graph visualization
The main project can be cloned from the GitLab repository or downloaded. Pulls and forks need to be authorized by the owners for changes.
Neo4j Configuration File
A localhost.ini Neo4j configuration file is required to set up the server and provide connection details such as:
- Protocol
- URL
- Port
- User
- Password
- Database name
Refer to the Neo4j installation guide for more help: https://neo4j.com/docs/operations-manual/current/installation/.
Running the GUI
On startup, if a database is set to load in config.py, a specified number of BioModels will be downloaded, converted to graphs, and loaded into the Neo4j database automatically. Once completed, the main GUI will launch.
GUI Features
- **Upload File Button**: Use the OS interface to select one or more SBML files to import into the database.
- **File Viewer Panel**: Displays all manually added SBML models.
- **Search Button**: Search for a BioModel in the database based on its name.
- **Change Schema Button**: Switch the schema used to convert SBML models to graphs. Preloaded schemas from the BioModels database can be used, and custom schemas should be named custom.json and placed in the appropriate folder.
- **Delete Button**: Select a BioModel to delete from the database.
- **Merge Models Button**: Select two BioModels and merge them based on common nodes. If no common nodes exist, the models will remain separate. The merged model can be visualized.
- **View Graphs Button**: Visualize a specific BioModel in a graphical plot.
- **Advanced Search Button**: Search for specific species or compounds and view corresponding BioModels.
- **Find Similar Models Button**: Apply a graph matching algorithm to all BioModels and return the highest matching models with their accuracy.
Using the API
The database is split into five main sections:
1. BioModels Downloader Class
2. SBML Database Query Class
3. SBML Database Class
4. Graph Visualizer Class
5. GUI Class
Adding Queries
The current iteration has limited querying functions. The user may want to add more specific queries for their use case. The Query class acts as a helper class and handles all database queries. Only one instance should be used at a time. A connection to the database is passed from the database class and used to make queries and return data.
To maintain consistency, new query functions should have similar names as those in the database class. A list of advanced queries, not yet implemented due to schema limitations, can be found in queries.txt.
General Configuration File
The config.py file contains various constants. Some advanced project options are not provided in the GUI but are available in the configuration file. Changing these constants will automatically apply the changes to the project.
Folder Structure
The configuration file also manages folder organization, ensuring consistency across the project. Any changes in the configuration file will propagate throughout the entire project.
Extending the GUI
All components of the GUI are stored as PyQt6 widgets within the main FileUploader class. Although the GUI was not designed to be extended initially, it is functional as specified.
Choosing a Database
The database URL and the number of models to download can be changed in the config.py file. All models will be downloaded in parallel for better performance.
Keeping Models Up to Date
An option in the configuration file ensures that the latest BioModels are used and re-uploaded to the database. However, enabling this option significantly slows down the program and is not recommended.
Changing the Graph Matching Algorithm Weights
You can adjust the structure vs. data weighting in the configuration file to search for different properties among the graphs.
