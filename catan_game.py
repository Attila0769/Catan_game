from collections import defaultdict
import networkx as nx  
import pygame
import math
import random


#Global varaibles and constants to build the game
HEX_SIZE = 60 
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
RESOURCES = ["Wood"]*4 + ["Wheat"]*4 + ["Sheep"]*4 + ["Brick"]*3 + ["Ore"]*3 + ["Desert"]
NUMBERS = [2,12] + [3,4,5,6,8,9,10,11]*2
RESOURCE_COLORS = {
    "Wood":    (34, 100, 34),
    "Wheat":   (210, 180, 50),
    "Sheep":   (120, 200, 80),
    "Brick":   (180, 70, 40),
    "Ore":     (120, 120, 140),
    "Desert":  (210, 190, 130),
}

PORT_POSITIONS = [
    (0, -2, 4),   # haut
    (2, -1, 5),   # haut-droite
    (2,  0, 0),   # droite
    (1,  1, 1),   # bas-droite  (attention : q+r <= 2)
    (-1, 2, 1),   # bas
    (-2, 2, 2),   # bas-gauche
    (-2,1, 3),   # gauche
    (-1,-1, 3),   # haut-gauche
    (1, -2, 5),   # haut (2ème)
]

PORT_TYPES = ["3:1"]*4 + ["Wood", "Wheat", "Sheep", "Brick", "Ore"]

EDGES = [
  (0, 1),
  (0, 7),
  (1, 2),
  (2, 3),
  (2, 9),
  (3, 4),
  (4, 5),
  (4, 11),
  (5, 6),
  (6, 13),
  (7, 8),
  (8, 9),
  (8, 16),
  (9, 10),
  (10, 11),
  (10, 18),
  (11, 12),
  (12, 13),
  (12, 20),
  (13, 14),
  (14, 22),
  (15, 16),
  (15, 23),
  (16, 17),
  (17, 18),
  (17, 25),
  (18, 19),
  (19, 20),
  (19, 27),
  (20, 21),
  (21, 22),
  (21, 29),
  (23, 24),
  (24, 25),
  (24, 31),
  (25, 26),
  (26, 27),
  (26, 33),
  (27, 28),
  (28, 29),
  (28, 35),
  (29, 30),
  (30, 37),
  (31, 32),
  (32, 33),
  (33, 34),
  (34, 35),
  (35, 36),
  (36, 37),
]

class CatanGraph:
    def __init__(self):
        self.adj = defaultdict(set)
        self.adj, self.hexes, self.node_positions = build_graph()
        self.built = {i: False for i in range(54)}
        self._build_from_edges()
        self.harbor = {i: None for i in range(54)}

    def _build_from_edges(self):
        for u, v in EDGES:
            self.adj[u].add(v)
            self.adj[v].add(u)

    def get_neighbors(self, node):
        return self.adj[node]

    def can_build(self, node):
        for neigh in self.adj[node]:
            if self.built[neigh]:
                return False
        return True

    def build(self, node):
        if self.can_build(node):
            self.built[node] = True
            return True
        return False
class Hex:
    def __init__(self, q,r,nodes):
        self.q = q
        self.r = r  
        self.nodes = nodes
        self.resource = None
        self.number = None

    def get_nodes(self):
        return self.nodes
    
def draw_hex(screen, font, hex_obj, node_positions):
    # Récupère les positions pixel des 6 coins dans l'ordre
    corners = [node_positions[n] for n in hex_obj.nodes]
    color = RESOURCE_COLORS.get(hex_obj.resource, (200, 200, 200))
    pygame.draw.polygon(screen, color, corners)
    pygame.draw.polygon(screen, (0, 0, 0), corners, 2)  # bordure noire
    
    
    # Centre du hex = moyenne des coins
    cx = sum(p[0] for p in corners) / 6
    cy = sum(p[1] for p in corners) / 6
    
    # Dessine le nombre sur le centre
    if hex_obj.number is not None:
        text = font.render(str(hex_obj.number), True, (0, 0, 0))
        rect = text.get_rect(center=(cx, cy))
        screen.blit(text, rect)
def draw_port(screen, font, port_type, node_a, node_b, node_positions):
    # node_positions : {node_id -> (x, y)}
    ax, ay = node_positions[node_a]
    bx, by = node_positions[node_b]

    # ligne du port (vert vif ici)
    color = RESOURCE_COLORS.get(port_type, (200, 200, 200))

    pygame.draw.line(screen, color, (ax, ay), (bx, by), 20)

    # milieu du segment
    mx = (ax + bx) / 2
    my = (ay + by) / 2

    # label texte
    if "3:1" in port_type:
        label = "3:1"
    else:
        # port_type = "2:1 Wood" etc.
        label = "2:1 " + port_type

    text = font.render(label, True, (255, 255, 255))
    rect = text.get_rect(center=(mx, my))
    screen.blit(text, rect)

    
def init_game(hexes, node_positions,ports):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font("freesansbold.ttf", 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE] == True:
                running = False
        
        screen.fill((0, 64, 128))
        
        for h in hexes:
            draw_hex(screen, font, h, node_positions)
        for (a, b), port_type in ports.items():
            draw_port(screen, font, port_type, a, b, node_positions)

        
        pygame.display.flip()
        clock.tick(60)


def axial_to_pixel(q, r, size):
    """Flat-top hex : formule du site redblobgames"""
    x = size * (3/2 * q)
    y = size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    return (x, y)

def hex_corners(cx, cy, size):
    """Les 6 coins d'un hex flat-top, dans l'ordre"""
    corners = []
    for i in range(6):  
        angle = math.radians(60 * i)  # 0°, 60°, 120°...
        x = cx + size * math.cos(angle)
        y = cy + size * math.sin(angle)
        corners.append((round(x, 1), round(y, 1)))  # round pour éviter les flottants ≠
    return corners

def catan_hex_coords():
    coords = []
    for q in range(-2, 3):
        for r in range(-2, 3):
            if abs(q)<=2 and abs(r)<=2 and abs(-q-r) <= 2:   # ← contrainte hexagonale
                coords.append((q, r))
    return coords  # 19 hexes

def build_graph():
    hex_coords = catan_hex_coords()
    
    node_id = {}   # (x_pixel, y_pixel) → int
    adj = {}       # int → set of int
    hexes = []     # liste des 19 hex, chacun = [node_id x6]
    
    cx_offset, cy_offset = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # centre de l'écran
    
    for q, r in hex_coords:
        cx, cy = axial_to_pixel(q, r, HEX_SIZE)
        cx += cx_offset
        cy += cy_offset
        
        corners = hex_corners(cx, cy, HEX_SIZE)
        hex_nodes = []
        
        for pos in corners:
            # Crée le noeud seulement s'il n'existe pas déjà
            if pos not in node_id:
                nid = len(node_id)
                node_id[pos] = nid
                adj[nid] = set()
            hex_nodes.append(node_id[pos])
        
        # Arêtes = coins consécutifs du hex
        for i in range(6):
            a = hex_nodes[i]
            b = hex_nodes[(i + 1) % 6]
            adj[a].add(b)
            adj[b].add(a)
        
        hexes.append(hex_nodes)
    
    return adj, hexes, node_id
def generate_ports(graph,hexes):
    ports = {}
    types = list(PORT_TYPES)
    random.shuffle(types)

    for (q, r, direction), port_type in zip(PORT_POSITIONS, types):
        hex_ = get_hex(q, r, hexes)
        if hex_ is None:
            print("NO HEX FOR PORT:", (q, r, direction))
            continue

        nodes = hex_.get_nodes()
        a = nodes[direction]
        b = nodes[(direction + 1) % 6]
        # Assign the ports to nodes in Graph.ports. Dict{node: port_type}.
        # a et b sont déjà des node_id → pas besoin de node_positions_inv ici
        ports[(a, b)] = port_type

    return ports

def get_hex(q, r, hexes):
    for hex in hexes:
        if hex.q == q and hex.r == r:
            return hex
    return None
def quit_game():
    pygame.quit()
def main():
    graph = CatanGraph()
    node_positions = {nid: pos for pos, nid in graph.node_positions.items()}

    hexes = []
    for i, (q, r) in enumerate(catan_hex_coords()):
        hexes.append(Hex(q, r, graph.hexes[i]))
    
    random.shuffle(NUMBERS)
    random.shuffle(RESOURCES)
    random.shuffle(PORT_TYPES)
    for hex in hexes:
        hex.resource = RESOURCES.pop()
        if hex.resource == "Desert":
            hex.number = None  
        else:
            hex.number = NUMBERS.pop()

    ports = generate_ports(graph,hexes)
    print(ports)
    init_game(hexes, node_positions,ports)
if __name__ == "__main__":
    main()

