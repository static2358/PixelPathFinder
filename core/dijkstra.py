import heapq
import time


class Dijkstra:
    """Implemente l'algorithme de Dijkstra pour trouver le plus court chemin dans un graphe image"""

    def __init__(self, graph):
        self.graph = graph

    def find_shortest_path(self, start, end):
        """Retourne le plus court chemin entre deux pixels"""
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