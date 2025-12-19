"""Module de representation d'une image sous forme de graphe.

Ce module fournit la classe Graph qui permet de convertir une image
en une structure de graphe pour les algorithmes de recherche de chemin.
"""

from PIL import Image


class Graph:
    """Represente une image sous forme de graphe pour la recherche de chemin.

    Chaque pixel de l'image devient un sommet du graphe identifie par ses
    coordonnees (i, j). Les aretes connectent les pixels voisins selon une
    4-connexite (haut, bas, gauche, droite). Le poids d'une arete correspond
    a la difference d'intensite en niveaux de gris entre deux pixels adjacents.

    Attributes:
        width (int): Largeur de l'image en pixels.
        height (int): Hauteur de l'image en pixels.
        pixels (list[list[int]]): Matrice 2D des valeurs de gris (0-255).
        DIRECTIONS (list[tuple[int, int]]): Directions de deplacement (4-connexite).

    Example:
        >>> graph = Graph("image.png")
        >>> graph.get_pixel_value(10, 20)
        128
        >>> graph.get_neighbors(10, 20)
        [(9, 20), (11, 20), (10, 19), (10, 21)]
    """

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, image_path):
        """Initialise le graphe a partir d'une image.

        Charge l'image, la convertit en niveaux de gris et stocke les valeurs
        des pixels dans une matrice 2D.

        Args:
            image_path (str): Chemin vers le fichier image a charger.

        Raises:
            FileNotFoundError: Si le fichier image n'existe pas.
            PIL.UnidentifiedImageError: Si le fichier n'est pas une image valide.
        """
        image = Image.open(image_path).convert('L')
        self.width, self.height = image.width, image.height
        self.pixels = [[image.getpixel((j, i)) for j in range(self.width)] 
                       for i in range(self.height)]

    def is_valid_pixel(self, i, j):
        """Verifie si les coordonnees correspondent a un pixel valide.

        Args:
            i (int): Coordonnee ligne (verticale) du pixel.
            j (int): Coordonnee colonne (horizontale) du pixel.

        Returns:
            bool: True si le pixel est dans les limites de l'image, False sinon.
        """
        return 0 <= i < self.height and 0 <= j < self.width

    def get_pixel_value(self, i, j):
        """Retourne la valeur d'intensite d'un pixel.

        Args:
            i (int): Coordonnee ligne du pixel.
            j (int): Coordonnee colonne du pixel.

        Returns:
            int: Valeur de gris du pixel (0-255).

        Raises:
            ValueError: Si les coordonnees sont en dehors de l'image.
        """
        if not self.is_valid_pixel(i, j):
            raise ValueError(f"Coordonnees invalides: ({i}, {j})")
        return self.pixels[i][j]

    def get_neighbors(self, i, j):
        """Retourne la liste des pixels voisins valides.

        Utilise une 4-connexite (haut, bas, gauche, droite).

        Args:
            i (int): Coordonnee ligne du pixel.
            j (int): Coordonnee colonne du pixel.

        Returns:
            list[tuple[int, int]]: Liste des coordonnees (i, j) des voisins valides.
        """
        return [(i + di, j + dj) for di, dj in self.DIRECTIONS 
                if self.is_valid_pixel(i + di, j + dj)]

    def get_edge_weight(self, pixel1, pixel2):
        """Calcule le poids de l'arete entre deux pixels.

        Le poids est la valeur absolue de la difference d'intensite
        entre les deux pixels.

        Args:
            pixel1 (tuple[int, int]): Coordonnees (i, j) du premier pixel.
            pixel2 (tuple[int, int]): Coordonnees (i, j) du second pixel.

        Returns:
            int: Poids de l'arete (difference d'intensite, 0-255).
        """
        return abs(self.pixels[pixel1[0]][pixel1[1]] - self.pixels[pixel2[0]][pixel2[1]])

    def get_dimensions(self):
        """Retourne les dimensions de l'image.

        Returns:
            tuple[int, int]: Tuple (hauteur, largeur) en pixels.
        """
        return (self.height, self.width)

    def get_total_vertices(self):
        """Retourne le nombre total de sommets du graphe.

        Correspond au nombre total de pixels de l'image.

        Returns:
            int: Nombre de pixels (hauteur * largeur).
        """
        return self.height * self.width