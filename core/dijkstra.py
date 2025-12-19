"""Module implementant l'algorithme de Dijkstra pour la recherche de chemin.

Ce module fournit une implementation de l'algorithme de Dijkstra optimisee
pour la recherche du plus court chemin dans un graphe represenant une image.
"""

import heapq
import time


class Dijkstra:
    """Implementation de l'algorithme de Dijkstra pour graphes images.

    L'algorithme trouve le chemin de cout minimal entre deux pixels d'une image,
    ou le cout est base sur les differences d'intensite entre pixels adjacents.
    Utilise une file de priorite (heap) pour une complexite optimale.

    Attributes:
        graph (Graph): Instance du graphe image sur lequel effectuer la recherche.

    Example:
        >>> from core.graph import Graph
        >>> graph = Graph("image.png")
        >>> dijkstra = Dijkstra(graph)
        >>> result = dijkstra.find_shortest_path((0, 0), (100, 100))
        >>> print(f"Chemin trouve: {len(result['path'])} pixels")
    """

    def __init__(self, graph):
        """Initialise l'algorithme avec un graphe.

        Args:
            graph (Graph): Instance du graphe image a parcourir.
        """
        self.graph = graph

    def find_shortest_path(self, start, end):
        """Trouve le plus court chemin entre deux pixels.

        Utilise l'algorithme de Dijkstra avec file de priorite pour trouver
        le chemin de cout minimal base sur les differences d'intensite.

        Args:
            start (tuple[int, int]): Coordonnees (i, j) du pixel de depart.
            end (tuple[int, int]): Coordonnees (i, j) du pixel d'arrivee.

        Returns:
            dict: Dictionnaire contenant les resultats:
                - path (list[tuple]): Liste ordonnee des pixels du chemin.
                - distance (float): Cout total du chemin.
                - nodes_visited (int): Nombre de noeuds explores.
                - visited_set (set): Ensemble des pixels visites.
                - visited_steps (list): Ordre de visite des pixels.
                - execution_time (float): Temps d'execution en secondes.
                - algorithm (str): Nom de l'algorithme ("Dijkstra").

        Raises:
            ValueError: Si les pixels de depart ou d'arrivee sont invalides.
        """
        start_time = time.time()
        self._validate_pixels(start, end)
        
        distances = {start: 0}
        predecessors = {}
        visited = set()
        visited_steps = []
        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_pixel = heapq.heappop(priority_queue)

            if current_pixel in visited:
                continue

            visited.add(current_pixel)
            visited_steps.append(current_pixel)

            if current_pixel == end:
                break

            for neighbor in self.graph.get_neighbors(*current_pixel):
                if neighbor in visited:
                    continue

                new_distance = current_distance + self.graph.get_edge_weight(current_pixel, neighbor)

                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_pixel
                    heapq.heappush(priority_queue, (new_distance, neighbor))

        return {
            'path': self._reconstruct_path(predecessors, start, end),
            'distance': distances.get(end, float('inf')),
            'nodes_visited': len(visited),
            'visited_set': visited,
            'visited_steps': visited_steps,
            'execution_time': time.time() - start_time,
            'algorithm': 'Dijkstra'
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