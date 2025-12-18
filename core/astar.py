import heapq
import time
import math


"""
    Implémente l'algorithme de A* pour trouver le plus court chemin dans un graphe correspondant a une image
"""
class AStar:


    # Initialise A* avec un graphe
    def __init__(self, graph):
        self.graph = graph
    

    # Heuristique Chebyshev
    # Plus petite que Manhattan, meilleur compromis vitesse/precision
    def _heuristic(self, pixel, goal):
        i1, j1 = pixel
        i2, j2 = goal
        return max(abs(i1 - i2), abs(j1 - j2))
    

    # Retourne le plus court chemin entre deux pixels
    def find_shortest_path(self, start, end):

        start_time = time.time()
        
        if not self.graph.is_valid_pixel(start[0], start[1]):
            raise ValueError(f"Pixel de départ invalide: {start}")
        if not self.graph.is_valid_pixel(end[0], end[1]):
            raise ValueError(f"Pixel d'arrivée invalide: {end}")
        
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}
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
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
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
            'algorithm': 'A*'
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