# SBML to Neo4j Pipeline

## Project Description

This project enables users to create a pipeline of SBML (Systems Biology Markup Language) models, from an existing database (BioModels) directly to a local/public server hosted by Neo4j. It works by converting SBML models to graph format and storing them in the database using a specified schema. This allows users to perform queries to find specific compounds. Graph matching can also be done to find similar SBML models beyond the current text comparisons. A GUI is provided to make it easier for users to interact with the project. BioModels can also be visualized from the GUI.

## Installation

### Conda Environment

Based on the dependency of neo4jsbl, a conda environment is required.

```
conda install -c conda-forge neo4jsbml
```

### Python Dependencies

All dependencies are listed in the `requirements.txt` file. Main dependencies include:

- Requests: for downloading biomodels from BioModels database
- PyQt6: for the main user interface
- Py2neo, NetworkX, Matplotlib: for graph visualization

Install dependencies using:

```
pip install -r requirements.txt
```

### Project Setup

The main project can be cloned directly from the GitLab repository or downloaded:

```
git clone https://gitlab.cs.uct.ac.za/prkraa002/capstone
```

Note: Pulls/Forks need to be authorized by owners for changes.

## Neo4j Configuration

A `localhost.ini` Neo4j config file is required to provide your own server and connection details:

- protocol
- url
- port
- user
- password
- name

If all details are correct, this is all that's needed to set up the server. If you have trouble setting up Neo4j, refer to their [official documentation](https://neo4j.com/docs/operations-manual/current/installation/).

## Running the GUI

To start the application:

```
python main.py
```

On startup, if a database has been set to load in `config.py`, a specified number of BioModels will be downloaded, converted to graphs, and loaded into the Neo4j database automatically. The main GUI will then launch once this is complete.

## Using the GUI

- **Upload File Button**: Select one or more SBML files to import to the database
- **File Viewer Panel**: Shows all manually added SBML models
- **Search Button**: Search for a biomodel in the database based on its name
- **Change Schema Button**: Change the schema that the database uses to convert SBML to graphs
- **Delete Button**: Select a biomodel to delete from the database
- **Merge Models Button**: Select two biomodels and merge them based on all common nodes
- **View Graphs Button**: Launch a visual plot of a specified biomodel
- **Advanced Search Button**: Search for specific species or compounds and view all corresponding biomodels
- **Find Similar Models Button**: Apply graph matching algorithm between all biomodels and return a list of the highest matching models along with their accuracy

## API Structure

The database is split into five main sections:

1. The BioModels downloader class
2. The SbmlDatabaseQuery class
3. The SbmlDatabase class
4. The GraphVisualizer class
5. The GUI class

## Adding Queries

The query class acts as a helper class and handles all queries to the database. Only one instance of it should be used at a time. A single connection to the database is passed from the database class to it, which can be used to make queries and return data.

## Configuration

The `config.py` file contains various constants for advanced option control. Change the values of these constants before opening the GUI for customized behavior.

## Extending the Project

### GUI Extension

All components of the GUI are stored as PyQt6 widgets with one main FileUploader class. The UI was designed to be simple and make the functionality of the project intuitive.

### Database Configuration

The database URL and the number of models to be downloaded can be changed in the `config.py` file. All models will be downloaded in parallel for optimization.

### Model Updates

There's an option in the configuration file to ensure that the latest BioModels are used and reuploaded to the database. However, this significantly slows down the program and is not recommended for regular use.

### Graph Matching Algorithm

The structure vs. data weighting for the graph matching algorithm can be adjusted in the configuration file. This helps to search for different properties among graphs.

## Contributing

For any changes or improvements, please create a pull request or fork the project. All contributions need to be authorized by the project owners.
