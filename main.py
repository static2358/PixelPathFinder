"""Point d'entree principal de l'application Pathfinder.

Ce module lance l'interface graphique de l'application de recherche
de chemin dans des images.

Example:
    Pour lancer l'application::

        $ python main.py
"""

from gui import Application


def main():
    """Lance l'interface graphique de Pathfinder.

    Cree une instance de l'application et demarre la boucle principale
    Tkinter.
    """
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
