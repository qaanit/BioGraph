from neo4jsbml import arrows, connect, sbml

# Either you have a configuration file or overwrite individually
# Either you have a configuration file or overwrite individually
path_config = "localhost.ini"
con = connect.Connect.from_config(path=path_config)

for i in range(1, 100):
    # Load model - Define a tag here if needed

    path_model = f"BIOMD{i:010}.xml"
    tag = path_model
    sbm = sbml.SbmlToNeo4j.from_sbml(path=path_model, tag=tag)

    # Load modelisation
    path_modelisation = "L3V2.7-1 (2).json"
    arr = arrows.Arrows.from_json(path=path_modelisation)

    # Mapping
    nod = sbm.format_nodes(nodes=arr.nodes)
    rel = sbm.format_relationships(relationships=arr.relationships)

    # Import into neo4j
    con.create_nodes(nodes=nod)
    con.create_relationships(relationships=rel)