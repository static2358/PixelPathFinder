import heapq
import time
import math


"""
    Implémente l'algorithme de A* pour trouver le plus court chemin dans un graphe correspondant a une image
"""
class AStar:

    HEURISTICS = {
        'intensity': 'Intensité',
        'manhattan': 'Manhattan',
        'euclidean': 'Euclidienne',
        'chebyshev': 'Chebyshev'
    }

    # Initialise A* avec un graphe
    def __init__(self, graph, heuristic='intensity'):
        self.graph = graph
        self.heuristic = heuristic
        self._goal_intensity = None
    

    # Heuristique basée sur l'intensité
    # |intensité(pixel) - intensité(goal)| est une borne inférieure admissible
    def _intensity_heuristic(self, pixel, goal):
        intensity_current = self.graph.get_pixel_value(pixel[0], pixel[1])
        return abs(intensity_current - self._goal_intensity)
    

    # Heuristique Manhattan
    # Somme des distances horizontale et verticale
    def _manhattan_heuristic(self, pixel, goal):
        return abs(pixel[0] - goal[0]) + abs(pixel[1] - goal[1])
    

    # Heuristique Euclidienne
    # Racine carrée de la somme des carrés des distances
    def _euclidean_heuristic(self, pixel, goal):
        return math.sqrt((pixel[0] - goal[0])**2 + (pixel[1] - goal[1])**2)
    

    # Heuristique Chebyshev
    # Maximum des distances horizontale et verticale
    def _chebyshev_heuristic(self, pixel, goal):
        return max(abs(pixel[0] - goal[0]), abs(pixel[1] - goal[1]))
    

    # Retourne la valeur de l'heuristique selon le type choisi
    def _get_heuristic_value(self, pixel, goal):
        if self.heuristic == 'manhattan':
            return self._manhattan_heuristic(pixel, goal)
        elif self.heuristic == 'euclidean':
            return self._euclidean_heuristic(pixel, goal)
        elif self.heuristic == 'chebyshev':
            return self._chebyshev_heuristic(pixel, goal)
        else: 
            return self._intensity_heuristic(pixel, goal)
    

    # Retourne le plus court chemin entre deux pixels
    def find_shortest_path(self, start, end):

        start_time = time.time()
        
        if not self.graph.is_valid_pixel(start[0], start[1]):
            raise ValueError(f"Pixel de départ invalide: {start}")
        if not self.graph.is_valid_pixel(end[0], end[1]):
            raise ValueError(f"Pixel d'arrivée invalide: {end}")
        
        # Précalculer l'intensité du goal pour l'heuristique intensité
        self._goal_intensity = self.graph.get_pixel_value(end[0], end[1])
        
        g_score = {start: 0}
        f_score = {start: self._get_heuristic_value(start, end)}
        predecessors = {}
        visited = set()
        visited_steps = []
        priority_queue = [(f_score[start], 0, start)]
        
        while priority_queue:
            current_f, current_g, current_pixel = heapq.heappop(priority_queue)
            
            if current_pixel in visited:
                continue
            
            visited.add(current_pixel)
            visited_steps.append(current_pixel)
            
            if current_pixel == end:
                break
            
            i, j = current_pixel
            neighbors = self.graph.get_neighbors(i, j)
            
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                
                edge_weight = self.graph.get_edge_weight(current_pixel, neighbor)
                tentative_g = g_score[current_pixel] + edge_weight
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    predecessors[neighbor] = current_pixel
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._get_heuristic_value(neighbor, end)
                    heapq.heappush(priority_queue, (f_score[neighbor], tentative_g, neighbor))
        
        path = self._reconstruct_path(predecessors, start, end)
        
        execution_time = time.time() - start_time
        
        return {
            'path': path,
            'distance': g_score.get(end, float('inf')),
            'nodes_visited': len(visited),
            'visited_set': visited,
            'visited_steps': visited_steps,
            'execution_time': execution_time,
            'algorithm': 'A*',
            'heuristic': self.HEURISTICS.get(self.heuristic, self.heuristic)
        }
    
    def _reconstruct_path(self, predecessors, start, end):
        
        if end not in predecessors and end != start:
            return []
        
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = predecessors.get(current, None)
        
        path.reverse()
        return path