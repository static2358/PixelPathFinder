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

    
    