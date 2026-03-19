from collections import defaultdict
import networkx as nx  
import pygame

class CatanGraph:
    def __init__(self):
        self.adj = defaultdict(list)  # {node: [voisins]}
        self.adj_hex_node = defaultdict(list)
        self.nodes = 54
        self._init_catan_graph()
        self.built = {}
        players_nodes = {1: [], 2: [], 3: [], 4: []}
        for i in range(self.nodes):
            self.built[i] = False
    
    def _init_catan_graph(self):
        # Template hexagonal exact (54 nodes, 72 edges)
        template = nx.hexagonal_lattice_graph(3, 4)
        for u, v in template.edges():
            self.add_edge(u, v)
    
    def add_edge(self, node1, node2):
        if node2 not in self.adj[node1]:
            self.adj[node1].append(node2)
        if node1 not in self.adj[node2]:
            self.adj[node2].append(node1)
    def add_adj_hex_to_node(self, node_id, hex_obj):
        if hex_obj not in self.adj_hex_node[node_id]:
            self.adj_hex_node[node_id].append(hex_obj)
    
    def get_hexes_for_node(self, node):
        return self.adj_hex_node[node]
    
    def get_neighbors(self, node):
        return self.adj[node]
    
    def get_num_edges(self):
        return sum(len(neighs) for neighs in self.adj.values()) // 2  # /2 car bidir
    def get_distance(self, node1, node2):
        return nx.shortest_path_length(self, node1, node2)
    def can_build(self, node):
        for neigh in self.adj[node]:
            for neigh2 in self.adj[neigh]:
                if neigh2 != node:
                    if self.built[neigh2] == True:
                        return False
        return True
    def build(self, node):
        if self.can_build(node):
            self.built[node] = True
    def is_built(self, node):
        return self.built[node]
class Hex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.resource = None
        self.number = None
        self.nodes = []
    def connect_nodes_to_hex(self, graph):
        # Offsets pour les 6 coins d'un hex (coordonnées axiales "flat-top")
        hex_offsets = [
            (self.x, self.y + 1),    # Nord
            (self.x + 1, self.y),    # Nord-Est
            (self.x + 1, self.y - 1),# Sud-Est
            (self.x, self.y - 1),    # Sud
            (self.x - 1, self.y),    # Sud-Ouest
            (self.x - 1, self.y + 1) # Nord-Ouest
        ]
        self.nodes = []
        for dx, dy in hex_offsets:
            node_id = self.hex_to_node_id(dx, dy)  # Ta fonction de mapping (voir ci-dessous)
            if 0 <= node_id < graph.nodes:
                self.nodes.append(node_id)
                graph.add_adj_hex_to_node(node_id, self)  # Méthode dans CatanGraph    
    def hex_to_node_id(self, x, y):
    # Mapping approx pour Catan (ligne y * cols_nodes + x*2 ou lookup)
        cols = 7  # ~ nodes par ligne
        return y * cols + x * 2  # Ex: ajuste pour 0-53

    def add_node(self, node):
        self.nodes.append(node)
    def get_nodes(self):
        return self.nodes
    def get_resource(self):
        return self.resource
    def get_number(self):
        return self.number
    def set_resource(self, resource):
        self.resource = resource
    def set_number(self, number):
        self.number = number
    


def init_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 128, 0))  # Fond vert
        # Dessine hex ici (voir hexLib ou tutoriel Catan)
        pygame.display.flip()
        clock.tick(60)
def quit_game():
    pygame.quit()
def main():
    graph = CatanGraph()
    hexes = [Hex(i//5, i%5) for i in range(19)]
    for h in hexes:
        print(f"Calling connect for Hex {h.x},{h.y}")
        h.connect_nodes_to_hex(graph)
if __name__ == "__main__":
    main()

