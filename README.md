Project Description: 

This project allows a user to create a pipeline of sbml models, from an existing database (bio models) directly to a local/public server hosted by neo4j. It works by converting sbml models to graph format and storing them in the database using a specified schema. This allows us to perform queries to find specific compounds. Graph matching can also be done to find similar sbml models beyond the current text comparisons. A GUI exists to make it easier for the user to use this project. Biomodels can also be visualized from the GUI. 
 

INSTALLATION: 

Conda environment: Based on the dependency of neo4jsbl, a conda environment is required. 

Python Dependencies, these are all listed in the requirements.txt: 

Requests – for downloading biomodels from biomodels database 

Pyqt6 – for main user interface 

Py2neo, networkx, matplotlib – for graph visualization 

The main project can be cloned directly from the GitLab repository or downloaded. 

Pulls/Forks need to be authorized by owners for changes. 
 

NEO4J CONFIGURATION FILE 

A localhost.ini neo4j config file is required to provide your own server and connection details: 

protocol ,url, port ,password ,user ,password,name 

If all details are correct, this is all too done to setup the server.  If you have trouble setting up neo4j refer to their website: https://neo4j.com/docs/operations-manual/current/installation/. 

 
RUNNING THE GUI: 

On startup, whether a database has been set to load in config.py, a specified number of Biomodels will be downloaded and converted to graphs and loaded into the neo4j database automatically. The main GUI will then launch once this is complete. 

USING THE GUI: 

Upload file Button: Using the Operating System Interface, select one or more sbml files to import to the database 

File viewer panel: Shows all manually added sbml models. 

Search Button:  Search for a biomodel in the database based on its name. 

Change Schema Button: Change schema that the database uses to convert sbml to graphs. The schemas are preloaded from the biomodels database, custom schemas should be named custom.json and be placed in the appropriate folder. (Schemas) 

Delete Button: Select a biomodel to delete from the database. 

Merge Models Button: Select two biomodels and merge them based on all common nodes. If there are no common nodes, the biomodels will be separate. It can be visualized. 

View Graphs Button: Launch a visual plot of a specified biomodel. 

Advanced Search Button: Search for specific species or compounds and view all corresponding biomodels. 

Find Similar Models Button: Apply graph matching algorithm between all biomodels, and return a list of the highest matching models along with their accuracy 

USING THE API: The database is split up into five main sections: 

The biomodels downloader class 

The SbmlDatabaseQuery class  

The SbmlDatabase class 

The GraphVisualizer class 

The GUI class 

ADDING QUEURIES: 

The current iteration has few querying functions, and the user may like more specific queries for their use case. The query class acts as a helper class and handles all queries to the database. Only one instance of it should be used at a time. A single connection to the database is passed from the database class to it, which can be used to make queries and return data. Use a similarly named function inside the database class for consistency. There is a list of more advanced queries that we have used but have not been implemented in queries.txt. This is due to not all schemas supporting certain properties. 

GENERAL CONFIGURATION FILE: 

config.py is a python file that contains various constants. Some more advanced option control over the project have not been provided in the GUI, so it has been placed in a config file. Change the value of these constants and they will automatically be used by the project. This configuration file works by default and should be changed before opening the GUI.  

FOLDERS 

The main design into implementing a configuration file was folder management. This helps to create consistency among all files and folders in the projects, and a change here will propagate throughout the whole project. 

EXTENDING THE GUI 

All components of the GUI are stored as pyqt6 widgets with one main FileUploader class. This UI was meant to be simple and just to make functionality of the project intuitive. The GUI was not designed to be extended from the start, however, still works as specified. 

CHOOSING DATABASE 

The database url can be changed and the number of models to be downloaded in the project configuration file, config.py. All models will be downloaded in parallel for more optimization. 

KEEPING MODELS UP TO DATA 

There is an option in the configuration file to make sure that the, latest biomodels are used and reuploaded to the database. This however significantly slows down the program and is advised not to use. 

CHANGING THE GRAPH MATCHING ALGORITHM WEIGHTS 

The structure vs data weighting can be changed in the configuration file. This helps to search for different properties among graphs. 
