# PixelPathfinder
> Projet d'Algorithmique Avancée S5 2025

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pillow](https://img.shields.io/badge/Pillow-9.0+-green?style=for-the-badge)](https://pillow.readthedocs.io/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.5+-11557c?style=for-the-badge)](https://matplotlib.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)

---

## Sommaire

1. [Informations Projet](#informations-projet)
2. [Prérequis et Dépendances](#prérequis-et-dépendances)
3. [Installation et Exécution](#installation-et-exécution)

---

## Informations Projet

### Arborescence

```
Algo_projet/
│
├── main.py                    # Point d'entrée
│
├── core/                      # Cœur algorithmique
│   ├── __init__.py
│   ├── graph.py               # Structure du graphe-image
│   ├── dijkstra.py            # Algorithme de Dijkstra
│   └── astar.py               # Algorithme A*
│
├── gui/                       # Interface graphique
│   ├── __init__.py
│   └── app.py                 # Application Tkinter
│
├── images/                    # Images de test
│
├── docs/                      # Documentation Sphinx
│   ├── build/
│   └── source/
│
└── README.md                  # Ce fichier
```

### Point d'entrée

```
main.py
```

---

## Prérequis et Dépendances

### Python

- **Python 3.8** ou supérieur
- Vérifier l'installation : `python --version`

### Bibliothèques requises

| Bibliothèque | Version | Description |
|--------------|---------|-------------|
| **Pillow** | >= 9.0 | Chargement et manipulation d'images |
| **Matplotlib** | >= 3.5 | Visualisation graphique |
| **Tkinter** | (standard) | Interface graphique (inclus avec Python) |

---

## Installation et Exécution

### Windows (PowerShell)

```powershell
# 1. Installer les dépendances
pip install pillow matplotlib

# 2. Lancer l'application
python main.py
```

### macOS / Linux (Terminal)

```bash
# 1. Installer les dépendances
pip install pillow matplotlib

# 2. Lancer l'application
python main.py
```

