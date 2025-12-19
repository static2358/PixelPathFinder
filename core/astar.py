import heapq
import time
import math


class AStar:
    """Implemente l'algorithme A* pour trouver le plus court chemin dans un graphe image"""

    HEURISTICS = {
        'intensity': 'Intensite',
        'manhattan': 'Manhattan',
        'euclidean': 'Euclidienne',
        'chebyshev': 'Chebyshev'
    }

    def __init__(self, graph, heuristic='intensity'):
        self.graph = graph
        self.heuristic = heuristic
        self._goal_intensity = None

    def _get_heuristic_value(self, pixel, goal):
        """Retourne la valeur de l'heuristique selon le type choisi"""
        if self.heuristic == 'manhattan':
            return abs(pixel[0] - goal[0]) + abs(pixel[1] - goal[1])
        elif self.heuristic == 'euclidean':
            return math.sqrt((pixel[0] - goal[0])**2 + (pixel[1] - goal[1])**2)
        elif self.heuristic == 'chebyshev':
            return max(abs(pixel[0] - goal[0]), abs(pixel[1] - goal[1]))
        else:  # intensity
            return abs(self.graph.get_pixel_value(*pixel) - self._goal_intensity)

    def find_shortest_path(self, start, end):
        """Retourne le plus court chemin entre deux pixels"""
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
        """Valide les pixels de depart et d'arrivee"""
        if not self.graph.is_valid_pixel(*start):
            raise ValueError(f"Pixel de depart invalide: {start}")
        if not self.graph.is_valid_pixel(*end):
            raise ValueError(f"Pixel d'arrivee invalide: {end}")

    def _reconstruct_path(self, predecessors, start, end):
        """Reconstruit le chemin entre le pixel de depart et le pixel d'arrivee"""
        if end not in predecessors and end != start:
            return []
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        return path