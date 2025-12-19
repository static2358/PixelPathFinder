PixelPathfinder - Documentation
================================

Bienvenue dans la documentation de **PixelPathfinder**, une application de recherche
de chemin dans des images utilisant les algorithmes Dijkstra et A*.

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   modules

Introduction
------------

PixelPathfinder est une application Python qui permet de trouver le plus court chemin
entre deux points dans une image. L'image est convertie en graphe ou chaque pixel
est un sommet et les aretes relient les pixels voisins.

Fonctionnalites
---------------

* **Algorithme Dijkstra**: Trouve le chemin optimal garanti
* **Algorithme A***: Recherche plus rapide avec heuristiques
* **4 heuristiques A***: Intensite, Manhattan, Euclidienne, Chebyshev
* **Interface graphique**: Theme sombre moderne avec Tkinter
* **Visualisation**: Graphiques detailles avec Matplotlib
* **Animation**: Visualisation en temps reel de l'exploration

Installation
------------

.. code-block:: bash

   pip install pillow matplotlib numpy

Utilisation
-----------

.. code-block:: bash

   python main.py

Indices et tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
