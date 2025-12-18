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
    

    # Heuristique Manhattan, estimation du coût jusqu'à l'arrivée
    # Admissible car ne surestime jamais le coût réel
    def _heuristic(self, pixel, goal):
        i1, j1 = pixel
        i2, j2 = goal
        return abs(i1 - i2) + abs(j1 - j2)
    

    # Retourne le plus court chemin entre deux pixels
    def find_shortest_path(self, start, end):

        start_time = time.time()
        
        if not self.graph.is_valid_pixel(start[0], start[1]):
            raise ValueError(f"Pixel de départ invalide: {start}")
        if not self.graph.is_valid_pixel(end[0], end[1]):
            raise ValueError(f"Pixel d'arrivée invalide: {end}")
        
        # g_score = coût réel depuis le départ
        g_score = {start: 0}
        
        # f_score = g_score + heuristique
        f_score = {start: self._heuristic(start, end)}
        
        # Predecesseurs pour reconstruire le chemin
        predecessors = {}
        
        # Ensemble des nœuds visités
        visited = set()
        
        # File de priorité : (f_score, g_score, pixel)
        # On ajoute g_score pour départager les égalités
        priority_queue = [(f_score[start], 0, start)]
        
        while priority_queue:
            current_f, current_g, current_pixel = heapq.heappop(priority_queue)
            
            # Ignorer si déjà visité
            if current_pixel in visited:
                continue
            
            visited.add(current_pixel)
            
            # Arrivée trouvée
            if current_pixel == end:
                break
            
            # Explorer les voisins
            i, j = current_pixel
            neighbors = self.graph.get_neighbors(i, j)
            
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                
                # Calculer le nouveau g_score
                edge_weight = self.graph.get_edge_weight(current_pixel, neighbor)
                tentative_g = g_score[current_pixel] + edge_weight
                
                # Mettre à jour si meilleur chemin trouvé
                if tentative_g < g_score.get(neighbor, float('inf')):
                    predecessors[neighbor] = current_pixel
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
                    heapq.heappush(priority_queue, (f_score[neighbor], tentative_g, neighbor))
        
        # Reconstruire le chemin
        path = self._reconstruct_path(predecessors, start, end)
        
        execution_time = time.time() - start_time
        
        return {
            'path': path,
            'distance': g_score.get(end, float('inf')),
            'nodes_visited': len(visited),
            'execution_time': execution_time,
            'algorithm': 'A*'
        }
    
    def _reconstruct_path(self, predecessors, start, end):
        # Reconstruit le chemin à partir des prédécesseurs
        
        if end not in predecessors and end != start:
            return []
        
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = predecessors.get(current, None)
        
        path.reverse()
        return path