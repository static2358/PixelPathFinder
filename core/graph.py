from PIL import Image


class Graph:
    """
    Represente une image sous forme de graphe.
    - Chaque pixel est un sommet identifie par des indices (i, j)
    - Les aretes connectent les pixels voisins (4-connexite)
    - Le poids d'une arete est la difference d'intensite entre 2 pixels
    """
    
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, image_path):
        """Conversion de l'image en matrice 2D de niveaux de gris"""
        image = Image.open(image_path).convert('L')
        self.width, self.height = image.width, image.height
        self.pixels = [[image.getpixel((j, i)) for j in range(self.width)] 
                       for i in range(self.height)]

    def is_valid_pixel(self, i, j):
        """Verifie si un pixel est dans les limites de l'image"""
        return 0 <= i < self.height and 0 <= j < self.width

    def get_pixel_value(self, i, j):
        """Retourne la valeur du pixel (i, j) en grayscale"""
        if not self.is_valid_pixel(i, j):
            raise ValueError(f"Coordonnees invalides: ({i}, {j})")
        return self.pixels[i][j]

    def get_neighbors(self, i, j):
        """Retourne la liste des voisins d'un pixel (i, j)"""
        return [(i + di, j + dj) for di, dj in self.DIRECTIONS 
                if self.is_valid_pixel(i + di, j + dj)]

    def get_edge_weight(self, pixel1, pixel2):
        """Retourne le poids de l'arete reliant deux pixels"""
        return abs(self.pixels[pixel1[0]][pixel1[1]] - self.pixels[pixel2[0]][pixel2[1]])

    def get_dimensions(self):
        """Retourne les dimensions de l'image (hauteur, largeur)"""
        return (self.height, self.width)

    def get_total_vertices(self):
        """Retourne le nombre de pixels de l'image"""
        return self.height * self.width