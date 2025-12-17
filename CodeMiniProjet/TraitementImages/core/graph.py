from PIL import Image


"""
    Représente une image sous forme de graphe.
    - Chaque pixel est un sommet identifié par des indices (i, j)
    - Les arêtes connectent les pixels voisins (4-connexité)
    - Le poids d'une arête est la différence d'intensité 2 pixels
"""
class Graph:

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    

    # Conversion de l'image en matrice 2d
    def __init__(self, image_path):
        image = Image.open(image_path).convert('L')
        
        self.width = image.width
        self.height = image.height
        
        self.pixels = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                pixel_value = image.getpixel((j, i))
                row.append(pixel_value)
            self.pixels.append(row)


    # vérifie si un pixel est valide 
    def is_valid_pixel(self, i, j):

        if i < 0 and i >= self.height:
            return False
        
        if j < 0 and j >= self.width:
            return False
        
        return True
    

    # Retourne la valeur du pixel (i, j) en grayscale
    def get_pixel_value(self, i, j):

        if not self.is_valid_pixel(i, j):
            raise ValueError(f"Coordonnées invalides: ({i}, {j})")
        
        return self.pixels[i][j]
    

    # Retourne la liste des voisins d'un pixel (i, j)
    def get_neighbors(self, i, j):

        neighbors = []

        for di, dj in self.DIRECTIONS:
            ni = i + di
            nj = j + dj

            if self.is_valid_pixel(ni, nj):
                neighbors.append((ni, nj))
        
        return neighbors
    

    # Retourne le poids de l'arête reliant deux pixels
    def get_edge_weight(self, pixel1, pixel2):

        i1, j1 = pixel1
        i2, j2 = pixel2

        intensity1 = self.get_pixel_value(i1, j1)
        intensity2 = self.get_pixel_value(i2, j2)

        return abs(intensity1 - intensity2)


    # Retourne les dimensions de l'image
    def get_dimensions(self):
        return (self.height, self.width)
    

    # Retourne le nombre de pixels de l'image (nombre de sommets du graphe)
    def get_total_vertices(self):
        return self.height * self.width


    



    
    