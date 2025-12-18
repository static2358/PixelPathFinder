import heapq
import time


"""
    Implémente l'algorithme de Dijkstra pour trouver le plus court chemin dans un graphe correspondant a une image
"""
class Dijkstra:


    # Initialise le constructeur dijkstra avec le graphe correnspodant a l'image
    def __init__(self, graph):
        self.graph = graph
    

    # Retourne le plus court chemin entre deux pixels
    def find_shortest_path(self, start, end):

        start_time = time.time()

        if not self.graph.is_valid_pixel(start[0], start[1]):
            raise ValueError(f"Pixel de départ invalide: {start}")
        if not self.graph.is_valid_pixel(end[0], end[1]):
            raise ValueError(f"Pixel d'arrivée invalide: {end}")
        
        distances = {}
        distances[start] = 0
        predecessors = {}
        visited = set()
        visited_steps = []
        priority_queue = [(0, start)]
        nodes_visited = 0

        while priority_queue:
            current_distance, current_pixel = heapq.heappop(priority_queue)

            if current_pixel in visited:
                continue

            visited.add(current_pixel)
            visited_steps.append(current_pixel)
            nodes_visited += 1

            if current_pixel == end:
                break

            i, j = current_pixel
            neighbors = self.graph.get_neighbors(i, j)

            for neighbor in neighbors:
                if neighbor in visited:
                    continue

                edge_weight = self.graph.get_edge_weight(current_pixel, neighbor)
                new_distance = current_distance + edge_weight

                old_distance = distances.get(neighbor, float('inf'))

                if new_distance < old_distance:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_pixel
                    heapq.heappush(priority_queue, (new_distance, neighbor))

        path = self._reconstruct_path(predecessors, start, end)

        execution_time = time.time() - start_time

        return {
            'path': path,
            'distance': distances.get(end, float('inf')),
            'nodes_visited': nodes_visited,
            'visited_set': visited,
            'visited_steps': visited_steps,
            'execution_time': execution_time,
            'algorithm': 'Dijkstra'
        }
    

    # Reconstruit le chemin entre le pixel de départ et le pixel d’arrivée 
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