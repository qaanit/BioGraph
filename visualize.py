from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import configparser

class GraphVisualizer:
    def __init__(self):
        self.graph = None
        self.G = nx.MultiDiGraph()

    def connect_to_neo4j(self, config_file):
        """Use configuration (.ini) file to extract connection arguments using configparser
        and establish connection to database"""

        config = configparser.ConfigParser()
        config.read(config_file)

        protocol = config.get('connection', 'protocol')
        url = config.get('connection', 'url')
        port = config.get('connection', 'port')
        username = config.get('database', 'user')
        password = config.get('database', 'password')
        uri = f"{protocol}://{url}:{port}"

        self.graph = Graph(uri, auth=(username, password))

    def query_subgraph(self, model_id):
        """Query graph to return all relationships and nodes"""

        query = f"""
        MATCH (n)-[r]->(m)
        WHERE n.tag = '{model_id}'
        RETURN n, r, m
        """
        return self.graph.run(query)

    @staticmethod
    def is_noisy(name):
        """Use other property of graph if name is unlegable"""
        return len(name) > 20 or not name.isalnum()

    def build_graph(self, result):
        """Create a new graph for visualization using relationships and nodes from query"""
        self.G.clear()

        # connect new nodes with edges 
        for record in result:
            try:
                source = record['n']
                target = record['m']
                relationship = record['r']

                source_name = source['name'] if not self.is_noisy(source['name']) else source["metaid"]
                target_name = target['name'] if not self.is_noisy(target['name']) else target["metaid"]

                self.G.add_edge(source_name, target_name, type=type(relationship).__name__)
            
            except ValueError as e: # Do not add Empty nodes
                pass

    def draw_and_style_graph(self):
        """Draw graphs and add styling to graph and make more neat"""

        plt.figure(figsize=(15, 8))
        pos = nx.spring_layout(self.G, k=0.5, seed=42)
        node_sizes = [self.G.degree(node) * 300 for node in self.G.nodes()]
        node_colors = list(mcolors.TABLEAU_COLORS.values())
        node_color_map = {node: random.choice(node_colors) for node in self.G.nodes()}
        edge_colors = mcolors.to_rgba("gray", alpha=0.5)
        edge_labels = nx.get_edge_attributes(self.G, 'type')
        
        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos,
                               node_size=node_sizes,
                               node_color=[node_color_map[node] for node in self.G.nodes()],
                               edgecolors="black",
                               linewidths=2,
                               alpha=0.85)

        # Draw relationships 
        nx.draw_networkx_edges(self.G, pos,
                               width=1,
                               alpha=0.6,
                               edge_color=edge_colors,
                               arrows=True,
                               arrowsize=20)

        # Draw Labels of nodes and relationships
        nx.draw_networkx_labels(self.G, pos,
                                font_size=8,
                                font_color="black",
                                font_weight="bold")

        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=6)

        # Create plot and set plot parameters
        plt.gca().set_facecolor((0.95, 0.95, 1))
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        plt.title(f"Model: {self.model_id}", size=24, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()

    def visualize(self, model_id, config_file="localhost.ini"):
        """
        Method to be used by other classes

        parameters:
            model_id: name of biomodel to draw
            config_file: name of file with server soncfiguration

        returns: None -> but while graph is open, other operations are paused
        """

        self.model_id = model_id
        self.connect_to_neo4j(config_file)
        result = self.query_subgraph(model_id)
        self.build_graph(result)
        self.draw_and_style_graph()
        plt.show()


if __name__ == "__main__":
    # Example Usage with default config
    visualizer = GraphVisualizer()
    visualizer.visualize("BIOMD0000000003")