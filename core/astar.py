"""Module implementant l'algorithme A* pour la recherche de chemin.

Ce module fournit une implementation de l'algorithme A* avec plusieurs
heuristiques disponibles pour la recherche de chemin dans un graphe image.
"""

import heapq
import time
import math


class AStar:
    """Implementation de l'algorithme A* pour graphes images.

    L'algorithme A* combine le cout reel du chemin avec une heuristique
    pour guider la recherche vers la destination de maniere plus efficace
    que Dijkstra. Plusieurs heuristiques sont disponibles.

    Attributes:
        graph (Graph): Instance du graphe image sur lequel effectuer la recherche.
        heuristic (str): Type d'heuristique utilisee ('intensity', 'manhattan',
            'euclidean', 'chebyshev').
        HEURISTICS (dict): Mapping des identifiants d'heuristiques vers leurs noms.

    Example:
        >>> from core.graph import Graph
        >>> graph = Graph("image.png")
        >>> astar = AStar(graph, heuristic='manhattan')
        >>> result = astar.find_shortest_path((0, 0), (100, 100))
        >>> print(f"Chemin trouve: {len(result['path'])} pixels")
    """

    HEURISTICS = {
        'intensity': 'Intensite',
        'manhattan': 'Manhattan',
        'euclidean': 'Euclidienne',
        'chebyshev': 'Chebyshev'
    }

    def __init__(self, graph, heuristic='intensity'):
        """Initialise l'algorithme avec un graphe et une heuristique.

        Args:
            graph (Graph): Instance du graphe image a parcourir.
            heuristic (str, optional): Type d'heuristique a utiliser.
                Options: 'intensity', 'manhattan', 'euclidean', 'chebyshev'.
                Defaults to 'intensity'.
        """
        self.graph = graph
        self.heuristic = heuristic
        self._goal_intensity = None

    def _get_heuristic_value(self, pixel, goal):
        """Calcule la valeur heuristique entre un pixel et la destination.

        Args:
            pixel (tuple[int, int]): Coordonnees du pixel courant.
            goal (tuple[int, int]): Coordonnees du pixel destination.

        Returns:
            float: Valeur heuristique estimant le cout restant.

        Note:
            Les heuristiques disponibles sont:

            - intensity: Difference d'intensite avec le pixel destination.
            - manhattan: Distance de Manhattan (somme des differences absolues).
            - euclidean: Distance euclidienne (racine carree de la somme des carres).
            - chebyshev: Distance de Chebyshev (maximum des differences absolues).
        """
        if self.heuristic == 'manhattan':
            return abs(pixel[0] - goal[0]) + abs(pixel[1] - goal[1])
        elif self.heuristic == 'euclidean':
            return math.sqrt((pixel[0] - goal[0])**2 + (pixel[1] - goal[1])**2)
        elif self.heuristic == 'chebyshev':
            return max(abs(pixel[0] - goal[0]), abs(pixel[1] - goal[1]))
        else:
            return abs(self.graph.get_pixel_value(*pixel) - self._goal_intensity)

    def find_shortest_path(self, start, end):
        """Trouve le plus court chemin entre deux pixels avec A*.

        Utilise l'algorithme A* avec l'heuristique configuree pour trouver
        un chemin optimal plus rapidement que Dijkstra dans la plupart des cas.

        Args:
            start (tuple[int, int]): Coordonnees (i, j) du pixel de depart.
            end (tuple[int, int]): Coordonnees (i, j) du pixel d'arrivee.

        Returns:
            dict: Dictionnaire contenant les resultats:
                - path (list[tuple]): Liste ordonnee des pixels du chemin.
                - distance (float): Cout total du chemin (g-score).
                - nodes_visited (int): Nombre de noeuds explores.
                - visited_set (set): Ensemble des pixels visites.
                - visited_steps (list): Ordre de visite des pixels.
                - execution_time (float): Temps d'execution en secondes.
                - algorithm (str): Nom de l'algorithme ("A*").
                - heuristic (str): Nom de l'heuristique utilisee.

        Raises:
            ValueError: Si les pixels de depart ou d'arrivee sont invalides.
        """
        start_time = time.time()
        self._validate_pixels(start, end)
        self._goal_intensity = self.graph.get_pixel_value(*end)
        
        g_score = {start: 0}
        predecessors = {}
        visited = set()
        visited_steps = []
        priority_queue = [(self._get_heuristic_value(start, end), 0, start)]
        
        while priority_queue:
            _, current_g, current_pixel = heapq.heappop(priority_queue)
            
            if current_pixel in visited:
                continue
            
            visited.add(current_pixel)
            visited_steps.append(current_pixel)
            
            if current_pixel == end:
                break
            
            for neighbor in self.graph.get_neighbors(*current_pixel):
                if neighbor in visited:
                    continue
                
                tentative_g = g_score[current_pixel] + self.graph.get_edge_weight(current_pixel, neighbor)
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    predecessors[neighbor] = current_pixel
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._get_heuristic_value(neighbor, end)
                    heapq.heappush(priority_queue, (f, tentative_g, neighbor))
        
        return {
            'path': self._reconstruct_path(predecessors, start, end),
            'distance': g_score.get(end, float('inf')),
            'nodes_visited': len(visited),
            'visited_set': visited,
            'visited_steps': visited_steps,
            'execution_time': time.time() - start_time,
            'algorithm': 'A*',
            'heuristic': self.HEURISTICS.get(self.heuristic, self.heuristic)
        }

    def _validate_pixels(self, start, end):
        """Valide les pixels de depart et d'arrivee.

        Args:
            start (tuple[int, int]): Coordonnees du pixel de depart.
            end (tuple[int, int]): Coordonnees du pixel d'arrivee.

        Raises:
            ValueError: Si un des pixels est en dehors des limites de l'image.
        """
        if not self.graph.is_valid_pixel(*start):
            raise ValueError(f"Pixel de depart invalide: {start}")
        if not self.graph.is_valid_pixel(*end):
            raise ValueError(f"Pixel d'arrivee invalide: {end}")

    def _reconstruct_path(self, predecessors, start, end):
        """Reconstruit le chemin a partir des predecesseurs.

        Parcourt le dictionnaire des predecesseurs en remontant de la fin
        vers le debut pour reconstituer le chemin complet.

        Args:
            predecessors (dict): Dictionnaire {pixel: predecesseur}.
            start (tuple[int, int]): Pixel de depart.
            end (tuple[int, int]): Pixel d'arrivee.

        Returns:
            list[tuple[int, int]]: Liste ordonnee des pixels du chemin,
                ou liste vide si aucun chemin n'existe.
        """
        if end not in predecessors and end != start:
            return []
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        return path