import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
import numpy as np

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.graph import Graph
from core.dijkstra import Dijkstra
from core.astar import AStar


class Application:
    COLORS = {
        'bg': '#0f0f0f',
        'surface': '#1a1a1a',
        'card': '#252525',
        'border': '#3d3d3d',
        'primary': '#6366f1',
        'primary_hover': '#818cf8',
        'success': '#22c55e',
        'danger': '#ef4444',
        'warning': '#f59e0b',
        'text': '#ffffff',
        'text_muted': '#a3a3a3',
        'text_dim': '#525252',
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pathfinder")
        self.root.geometry("1200x720")
        self.root.configure(bg=self.COLORS['bg'])
        self.root.minsize(1200, 720)
        
        self._set_dark_title_bar()
        
        self.image_graph = None
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        
        self.start_pixel = None
        self.end_pixel = None
        self.current_path = []
        self.last_result = None
        
        self.scale_factor = 1.0
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.image_offset = (0, 0)
        
        self.algorithm = tk.StringVar(value="dijkstra")
        self.heuristic = tk.StringVar(value="Intensité")
        self.animation_enabled = tk.BooleanVar(value=False)
        self.is_animating = False
        
        self._setup_styles()
        self._build_ui()
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Card.TFrame', background=self.COLORS['card'])
        style.configure('Surface.TFrame', background=self.COLORS['surface'])
        
        style.configure('Title.TLabel',
            background=self.COLORS['surface'],
            foreground=self.COLORS['text'],
            font=('Segoe UI', 24, 'bold'))
        
        style.configure('CardTitle.TLabel',
            background=self.COLORS['card'],
            foreground=self.COLORS['text'],
            font=('Segoe UI', 12, 'bold'))
        
        style.configure('Muted.TLabel',
            background=self.COLORS['card'],
            foreground=self.COLORS['text_muted'],
            font=('Segoe UI', 10))
        
        style.configure('Stats.TLabel',
            background=self.COLORS['card'],
            foreground=self.COLORS['text'],
            font=('Consolas', 14, 'bold'))

        style.configure('Primary.TButton',
            background=self.COLORS['primary'],
            foreground=self.COLORS['text'],
            font=('Segoe UI', 11, 'bold'),
            padding=(20, 12))
        
        style.map('Primary.TButton',
            background=[('active', self.COLORS['primary_hover'])])
        
        style.configure('Coord.TEntry',
            fieldbackground=self.COLORS['bg'],
            foreground=self.COLORS['text'],
            insertcolor=self.COLORS['text'],
            font=('Consolas', 11))
        
        style.configure('Modern.Vertical.TScrollbar',
            background=self.COLORS['card'],
            troughcolor=self.COLORS['surface'],
            bordercolor=self.COLORS['surface'],
            arrowcolor=self.COLORS['text_muted'],
            width=10)
        style.map('Modern.Vertical.TScrollbar',
            background=[('active', self.COLORS['primary']), ('!active', self.COLORS['border'])])
        
        style.configure('Modern.Horizontal.TScrollbar',
            background=self.COLORS['card'],
            troughcolor=self.COLORS['surface'],
            bordercolor=self.COLORS['surface'],
            arrowcolor=self.COLORS['text_muted'],
            width=10)
        style.map('Modern.Horizontal.TScrollbar',
            background=[('active', self.COLORS['primary']), ('!active', self.COLORS['border'])])
        
        # Style pour Combobox
        style.configure('TCombobox',
            fieldbackground=self.COLORS['bg'],
            background=self.COLORS['card'],
            foreground=self.COLORS['text'],
            arrowcolor=self.COLORS['text'],
            bordercolor=self.COLORS['border'],
            lightcolor=self.COLORS['bg'],
            darkcolor=self.COLORS['bg'])
        style.map('TCombobox',
            fieldbackground=[('readonly', self.COLORS['bg']), ('disabled', self.COLORS['surface'])],
            foreground=[('disabled', self.COLORS['text_dim'])],
            background=[('active', self.COLORS['primary'])])
    
    def _build_ui(self):
        """Construit l'interface utilisateur"""
        
        main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(main_container, bg=self.COLORS['surface'], width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        sidebar_content = tk.Frame(self.sidebar, bg=self.COLORS['surface'])
        sidebar_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.btn_load = self._create_button(sidebar_content, "Charger Image",
            self._load_image, self.COLORS['card'])
        self.btn_load.pack(fill=tk.X, pady=(0, 10))
        
        algo_card = self._create_card(sidebar_content, "Algorithme")
        
        algo_frame = tk.Frame(algo_card, bg=self.COLORS['card'])
        algo_frame.pack(fill=tk.X, pady=(5, 0))
        
        rb_dijkstra = tk.Radiobutton(algo_frame, text="Dijkstra",
            variable=self.algorithm, value="dijkstra",
            font=('Segoe UI', 10), bg=self.COLORS['card'], fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg'], activebackground=self.COLORS['card'],
            activeforeground=self.COLORS['text'],
            command=self._on_algorithm_change)
        rb_dijkstra.pack(anchor='w')
        
        # Frame pour A* + heuristique sur la même ligne
        astar_line = tk.Frame(algo_frame, bg=self.COLORS['card'])
        astar_line.pack(fill=tk.X, anchor='w')
        
        rb_astar = tk.Radiobutton(astar_line, text="A*",
            variable=self.algorithm, value="astar",
            font=('Segoe UI', 10), bg=self.COLORS['card'], fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg'], activebackground=self.COLORS['card'],
            activeforeground=self.COLORS['text'],
            command=self._on_algorithm_change)
        rb_astar.pack(side=tk.LEFT)
        
        # Combobox heuristique à droite de A*
        self.root.option_add('*TCombobox*Listbox.background', self.COLORS['bg'])
        self.root.option_add('*TCombobox*Listbox.foreground', self.COLORS['text'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.COLORS['primary'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.COLORS['text'])
        
        self.heuristic_combo = ttk.Combobox(astar_line,
            textvariable=self.heuristic,
            values=['Intensité', 'Manhattan', 'Euclidienne', 'Chebyshev'],
            state='disabled',
            font=('Segoe UI', 9),
            width=12)
        self.heuristic_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Animation toggle
        anim_frame = tk.Frame(algo_card, bg=self.COLORS['card'])
        anim_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.anim_checkbox = tk.Checkbutton(anim_frame, text="Animation",
            variable=self.animation_enabled,
            font=('Segoe UI', 10), bg=self.COLORS['card'], fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg'], activebackground=self.COLORS['card'],
            activeforeground=self.COLORS['text'])
        self.anim_checkbox.pack(anchor='w')
        
        tk.Label(anim_frame, text="(Recommandé pour petites images)",
            font=('Segoe UI', 8), bg=self.COLORS['card'], fg=self.COLORS['text_dim']).pack(anchor='w')
        
        start_card = self._create_card(sidebar_content, "Point de Depart")
        
        coord_frame1 = tk.Frame(start_card, bg=self.COLORS['card'])
        coord_frame1.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(coord_frame1, text="X:", font=('Segoe UI', 10),
            bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
        
        self.start_x_var = tk.StringVar(value="0")
        self.start_x_entry = tk.Entry(coord_frame1, textvariable=self.start_x_var,
            width=8, font=('Consolas', 11),
            bg=self.COLORS['bg'], fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['primary'])
        self.start_x_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(coord_frame1, text="Y:", font=('Segoe UI', 10),
            bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
        
        self.start_y_var = tk.StringVar(value="0")
        self.start_y_entry = tk.Entry(coord_frame1, textvariable=self.start_y_var,
            width=8, font=('Consolas', 11),
            bg=self.COLORS['bg'], fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['primary'])
        self.start_y_entry.pack(side=tk.LEFT, padx=5)
        
        btn_set_start = self._create_button(start_card, "Définir",
            self._set_start_from_entry, self.COLORS['success'], small=True)
        btn_set_start.pack(fill=tk.X, pady=(10, 0))
        
        self.start_label = tk.Label(start_card, text="Non défini",
            font=('Consolas', 9), bg=self.COLORS['card'], fg=self.COLORS['text_dim'])
        self.start_label.pack(anchor='w', pady=(5, 0))
        
        # === Card Arrivée ===
        end_card = self._create_card(sidebar_content, "Point d'Arrivee")
        
        coord_frame2 = tk.Frame(end_card, bg=self.COLORS['card'])
        coord_frame2.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(coord_frame2, text="X:", font=('Segoe UI', 10),
            bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
        
        self.end_x_var = tk.StringVar(value="0")
        self.end_x_entry = tk.Entry(coord_frame2, textvariable=self.end_x_var,
            width=8, font=('Consolas', 11),
            bg=self.COLORS['bg'], fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['primary'])
        self.end_x_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(coord_frame2, text="Y:", font=('Segoe UI', 10),
            bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
        
        self.end_y_var = tk.StringVar(value="0")
        self.end_y_entry = tk.Entry(coord_frame2, textvariable=self.end_y_var,
            width=8, font=('Consolas', 11),
            bg=self.COLORS['bg'], fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['primary'])
        self.end_y_entry.pack(side=tk.LEFT, padx=5)
        
        btn_set_end = self._create_button(end_card, "Définir",
            self._set_end_from_entry, self.COLORS['danger'], small=True)
        btn_set_end.pack(fill=tk.X, pady=(10, 0))
        
        self.end_label = tk.Label(end_card, text="Non défini",
            font=('Consolas', 9), bg=self.COLORS['card'], fg=self.COLORS['text_dim'])
        self.end_label.pack(anchor='w', pady=(5, 0))
        
        actions_frame = tk.Frame(sidebar_content, bg=self.COLORS['surface'])
        actions_frame.pack(fill=tk.X, pady=10)
        
        self.btn_compute = self._create_button(actions_frame, "Calculer Chemin",
            self._compute_path, self.COLORS['primary'])
        self.btn_compute.pack(fill=tk.X, pady=(0, 5))
        self.btn_compute.config(state=tk.DISABLED)
        
        self.btn_reset = self._create_button(actions_frame, "Reinitialiser",
            self._reset, self.COLORS['card'])
        self.btn_reset.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_visualize = self._create_button(actions_frame, "Visualiser",
            self._show_matplotlib, self.COLORS['warning'])
        self.btn_visualize.pack(fill=tk.X)
        self.btn_visualize.config(state=tk.DISABLED)
        
        instructions = tk.Label(sidebar_content,
            text="Clic gauche = Depart | Clic droit = Arrivee\nCtrl+Molette = Zoom",
            font=('Segoe UI', 8),
            bg=self.COLORS['surface'], fg=self.COLORS['text_dim'],
            justify=tk.LEFT)
        instructions.pack(anchor='w', pady=(10, 0))
        
        self.image_frame = tk.Frame(main_container, bg=self.COLORS['bg'])
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas_container = tk.Frame(self.image_frame, bg=self.COLORS['surface'])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container,
            bg=self.COLORS['surface'],
            highlightthickness=0,
            cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        def on_canvas_mousewheel(event):
            if event.state & 0x4:
                if event.delta > 0:
                    self._zoom_in(event)
                else:
                    self._zoom_out(event)
            elif event.state & 0x1: 
                self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else: 
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", on_canvas_mousewheel)
        
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        self.cursor_label = tk.Label(self.image_frame,
            text="", font=('Consolas', 9),
            bg=self.COLORS['bg'], fg=self.COLORS['text_dim'])
        self.cursor_label.pack(pady=(10, 0))
        
        self._show_placeholder()
    
    def _create_card(self, parent, title):
        """Crée une carte avec titre - flat design"""
        card = tk.Frame(parent, bg=self.COLORS['card'],
            highlightbackground=self.COLORS['border'],
            highlightthickness=0)
        card.pack(fill=tk.X, pady=(0, 8))
        
        inner = tk.Frame(card, bg=self.COLORS['card'])
        inner.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(inner, text=title, font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['card'], fg=self.COLORS['text']).pack(anchor='w')
        
        return inner
    
    def _create_button(self, parent, text, command, color, small=False):
        """Crée un bouton stylisé flat design"""
        btn = tk.Button(parent, text=text, command=command,
            font=('Segoe UI', 9 if small else 10, 'bold'),
            bg=color, fg='#ffffff',
            activebackground=color, activeforeground='#ffffff',
            disabledforeground='#ffffff',
            relief=tk.FLAT, cursor='hand2',
            bd=0, highlightthickness=0,
            padx=10, pady=6 if small else 8)
        
        original_color = color
        
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=self._lighten_color(original_color))
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=original_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _lighten_color(self, hex_color):
        """Éclaircit une couleur hex"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _set_dark_title_bar(self):
        """Configure la barre de titre en noir (Windows 10/11)"""
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except:
            pass 
    
    def _get_path_color(self):
        """Détermine la couleur du chemin selon le fond"""
        if not self.current_path or not self.original_image:
            return (255, 0, 0)  
        
        sample_size = min(50, len(self.current_path))
        step = max(1, len(self.current_path) // sample_size)
        
        red_count = 0
        for idx in range(0, len(self.current_path), step):
            i, j = self.current_path[idx]
            try:
                pixel = self.original_image.getpixel((j, i))
                r, g, b = pixel[:3]
                if r > 150 and r > g * 1.5 and r > b * 1.5:
                    red_count += 1
            except:
                pass
        
        if red_count > sample_size * 0.3:
            return (0, 255, 255) 
        return (255, 0, 0) 
    
    def _show_placeholder(self):
        """Affiche le placeholder sur le canvas"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2 or 400,
            self.canvas.winfo_height() // 2 or 300,
            text="Chargez une image pour commencer",
            font=('Segoe UI', 16),
            fill=self.COLORS['text_dim'])
    
    def _load_image(self):
        """Charge une image"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("Tous les fichiers", "*.*")
            ])
        
        if not file_path:
            return
        
        try:
            self.original_image = Image.open(file_path).convert('RGB')
            self.image_graph = Graph(file_path)
            
            self.start_pixel = None
            self.end_pixel = None
            self.current_path = []
            self.last_result = None
            self.zoom_level = 1.0
            
            self.btn_visualize.config(state=tk.DISABLED)
            
            self._update_display()
            self._update_buttons_state()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")
    
    def _zoom_in(self, event=None):
        """Zoom avant"""
        if not self.original_image:
            return
        
        old_zoom = self.zoom_level
        self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2)
        
        if old_zoom != self.zoom_level:
            self._zoom_at_point(event, old_zoom, animated=self.is_animating)
    
    def _zoom_out(self, event=None):
        """Zoom arrière"""
        if not self.original_image:
            return
        
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
        
        if old_zoom != self.zoom_level:
            self._zoom_at_point(event, old_zoom, animated=self.is_animating)
    
    def _zoom_at_point(self, event, old_zoom, animated=False):
        """Zoom centré sur le point de la souris"""
        if event:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            scale_change = self.zoom_level / old_zoom
            new_x = x * scale_change
            new_y = y * scale_change

            if animated:
                self._update_display_animated()
            else:
                self._update_display()
            
            self.canvas.xview_moveto((new_x - event.x) / (self.original_image.width * self.zoom_level))
            self.canvas.yview_moveto((new_y - event.y) / (self.original_image.height * self.zoom_level))
        else:
            if animated:
                self._update_display_animated()
            else:
                self._update_display()
    
    def _calculate_scale(self):
        """Calcule le facteur d'échelle"""
        if not self.original_image:
            return
        
        canvas_w = self.canvas.winfo_width() - 40
        canvas_h = self.canvas.winfo_height() - 40
        
        if canvas_w < 10 or canvas_h < 10:
            canvas_w, canvas_h = 700, 500
        
        img_w, img_h = self.original_image.size
        
        scale_w = canvas_w / img_w
        scale_h = canvas_h / img_h
        self.scale_factor = min(scale_w, scale_h, 4.0)  
    
    def _update_display(self):
        """Met à jour l'affichage de l'image avec zoom"""
        if not self.original_image:
            self._show_placeholder()
            return
        
        img = self.original_image.copy()
        draw = ImageDraw.Draw(img)
        
        if len(self.current_path) > 1:
            path_color = self._get_path_color()
            path_coords = [(j, i) for (i, j) in self.current_path]
            draw.line(path_coords, fill=path_color, width=max(1, int(2/self.zoom_level)))
        
        # Marqueurs de 1 pixel
        if self.start_pixel:
            i, j = self.start_pixel
            draw.point((j, i), fill=(34, 197, 94))
        
        if self.end_pixel:
            i, j = self.end_pixel
            draw.point((j, i), fill=(239, 68, 68))
        
        new_width = int(img.width * self.zoom_level)
        new_height = int(img.height * self.zoom_level)
        
        if new_width > 0 and new_height > 0:
            img_resized = img.resize((new_width, new_height), Image.NEAREST if self.zoom_level > 1 else Image.LANCZOS)
        else:
            img_resized = img

        self.photo_image = ImageTk.PhotoImage(img_resized)
        
        self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        self.image_offset = (0, 0)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
    
    def _on_canvas_resize(self, event):
        self._update_display()
    
    def _canvas_to_pixel(self, x, y):
        if not self.image_graph:
            return None
        
        canvas_x = self.canvas.canvasx(x)
        canvas_y = self.canvas.canvasy(y)
        
        j, i = int(canvas_x / self.zoom_level), int(canvas_y / self.zoom_level)
        
        if self.image_graph.is_valid_pixel(i, j):
            return (i, j)
        return None
    
    def _on_left_click(self, event):
        pixel = self._canvas_to_pixel(event.x, event.y)
        if pixel:
            self.start_pixel = pixel
            self.current_path = []  
            self.start_x_var.set(str(pixel[1]))
            self.start_y_var.set(str(pixel[0]))
            self.start_label.config(text=f"({pixel[1]}, {pixel[0]})")
            self._update_display()
            self._update_buttons_state()
    
    def _on_right_click(self, event):
        pixel = self._canvas_to_pixel(event.x, event.y)
        if pixel:
            self.end_pixel = pixel
            self.current_path = [] 
            self.end_x_var.set(str(pixel[1]))
            self.end_y_var.set(str(pixel[0]))
            self.end_label.config(text=f"({pixel[1]}, {pixel[0]})")
            self._update_display()
            self._update_buttons_state()
    
    def _on_mouse_move(self, event):
        pixel = self._canvas_to_pixel(event.x, event.y)
        if pixel:
            i, j = pixel
            intensity = self.image_graph.get_pixel_value(i, j)
            zoom_pct = int(self.zoom_level * 100)
            self.cursor_label.config(text=f"Position: ({j}, {i})  |  Intensité: {intensity}  |  Zoom: {zoom_pct}%")
        else:
            if self.original_image:
                zoom_pct = int(self.zoom_level * 100)
                self.cursor_label.config(text=f"Zoom: {zoom_pct}%")
            else:
                self.cursor_label.config(text="")
    
    def _set_start_from_entry(self):
        try:
            x = int(self.start_x_var.get())
            y = int(self.start_y_var.get())
            
            if self.image_graph and self.image_graph.is_valid_pixel(y, x):
                self.start_pixel = (y, x)
                self.current_path = [] 
                self.start_label.config(text=f"({x}, {y})")
                self._update_display()
                self._update_buttons_state()
            else:
                messagebox.showwarning("Attention", "Coordonnées invalides")
        except ValueError:
            messagebox.showwarning("Attention", "Entrez des nombres valides")
    
    def _set_end_from_entry(self):
        try:
            x = int(self.end_x_var.get())
            y = int(self.end_y_var.get())
            
            if self.image_graph and self.image_graph.is_valid_pixel(y, x):
                self.end_pixel = (y, x)
                self.current_path = []  
                self.end_label.config(text=f"({x}, {y})")
                self._update_display()
                self._update_buttons_state()
            else:
                messagebox.showwarning("Attention", "Coordonnées invalides")
        except ValueError:
            messagebox.showwarning("Attention", "Entrez des nombres valides")
    
    def _update_buttons_state(self):
        """Met à jour l'état des boutons"""
        has_points = self.start_pixel is not None and self.end_pixel is not None
        self.btn_compute.config(state=tk.NORMAL if has_points else tk.DISABLED)
    
    def _on_algorithm_change(self):
        """Active/désactive le sélecteur d'heuristique selon l'algorithme"""
        if self.algorithm.get() == "astar":
            self.heuristic_combo.config(state='readonly')
        else:
            self.heuristic_combo.config(state='disabled')
    
    def _compute_path(self):
        """Calcule le plus court chemin"""
        if not self.start_pixel or not self.end_pixel:
            return
        
        if self.is_animating:
            return
        
        try:
            # Mapper les noms français vers les clés anglaises
            heuristic_map = {
                'Intensité': 'intensity',
                'Manhattan': 'manhattan', 
                'Euclidienne': 'euclidean',
                'Chebyshev': 'chebyshev'
            }
            
            if self.algorithm.get() == "astar":
                heuristic_key = heuristic_map.get(self.heuristic.get(), 'intensity')
                algo = AStar(self.image_graph, heuristic=heuristic_key)
            else:
                algo = Dijkstra(self.image_graph)
            
            if self.animation_enabled.get():
                self._compute_path_animated(algo)
            else:
                result = algo.find_shortest_path(self.start_pixel, self.end_pixel)
                
                self.current_path = result['path']
                self.last_result = result
                
                self.btn_visualize.config(state=tk.NORMAL)
                
                self._update_display()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul:\n{e}")
    
    def _compute_path_animated(self, algo):
        """Calcule le chemin avec animation en temps réel"""
        
        self.is_animating = True
        self.btn_compute.config(state=tk.DISABLED)
        self.btn_reset.config(state=tk.DISABLED)
        self.anim_checkbox.config(state=tk.DISABLED)
        
        # Lancer le calcul et récupérer les étapes
        result = algo.find_shortest_path(self.start_pixel, self.end_pixel)
        
        visited_steps = result.get('visited_steps', [])
        total_steps = len(visited_steps)
        
        if total_steps == 0:
            self._finish_animation(result)
            return
        
        # Paramètres d'animation optimisés
        # Animation de 3 secondes max, minimum 30 FPS
        target_duration = 3.0  # secondes
        min_fps = 30
        max_frames = int(target_duration * min_fps)
        
        # Calculer combien de nœuds par frame
        nodes_per_frame = max(1, total_steps // max_frames)
        
        # Délai fixe pour fluidité (33ms = ~30 FPS)
        time_per_frame = 33
        
        self.animation_visited = set()
        self.animation_trail = []  # Liste des derniers pixels pour le gradient
        self.trail_length = max(20, nodes_per_frame * 1)  # Trail proportionnel (2 frames)
        self.animation_steps = visited_steps
        self.animation_result = result
        self.animation_index = 0
        self.nodes_per_frame = nodes_per_frame
        self.animation_delay = time_per_frame
        
        # Pré-calculer l'image numpy pour optimiser (on la modifie directement)
        self.animation_img_array = np.array(self.original_image).astype(np.float32)
        self.animation_original_array = np.array(self.original_image).astype(np.float32)
        
        self._animate_step()
    
    def _animate_step(self):
        """Exécute une étape de l'animation"""
        if not self.is_animating:
            return
        
        # Récupérer les nouveaux pixels pour cette frame
        end_index = min(self.animation_index + self.nodes_per_frame, len(self.animation_steps))
        
        new_pixels = []
        for i in range(self.animation_index, end_index):
            pixel = self.animation_steps[i]
            new_pixels.append(pixel)
            self.animation_visited.add(pixel)
            
            # Colorier en orange directement dans l'image (persistant)
            pi, pj = pixel
            alpha = 0.5
            self.animation_img_array[pi, pj] = (
                self.animation_original_array[pi, pj] * (1 - alpha) + 
                np.array([255, 140, 0]) * alpha
            )
        
        # Ajouter au trail (gradient bleu)
        self.animation_trail.extend(new_pixels)
        # Garder seulement les derniers pixels pour le gradient
        if len(self.animation_trail) > self.trail_length:
            self.animation_trail = self.animation_trail[-self.trail_length:]
        
        self.animation_index = end_index
        
        # Mettre à jour l'affichage
        self._update_display_animated()
        
        # Continuer ou terminer
        if self.animation_index < len(self.animation_steps):
            self.root.after(self.animation_delay, self._animate_step)
        else:
            self._finish_animation(self.animation_result)
    
    def _update_display_animated(self):
        """Met à jour l'affichage pendant l'animation avec gradient bleu"""
        if not self.original_image:
            return
        
        # Copier l'image avec les pixels orange (déjà appliqués)
        img_array = self.animation_img_array.copy()
        
        # Dessiner le gradient bleu (trail des derniers pixels)
        trail_len = len(self.animation_trail)
        if trail_len > 0:
            # Utiliser numpy vectorisé pour le gradient
            trail_array = np.array(self.animation_trail)
            rows = trail_array[:, 0]
            cols = trail_array[:, 1]
            
            # Calculer les couleurs du gradient pour chaque pixel
            progress = np.linspace(0, 1, trail_len)  # 0 = ancien, 1 = récent
            
            # Couleurs: bleu foncé (0, 80, 180) -> bleu vif (50, 200, 255)
            r_vals = (50 * progress).astype(np.float32)
            g_vals = (80 + 120 * progress).astype(np.float32)
            b_vals = (180 + 75 * progress).astype(np.float32)
            alphas = (0.7 + 0.3 * progress).astype(np.float32)  # 70% -> 100%
            
            # Appliquer le gradient
            for idx in range(trail_len):
                i, j = rows[idx], cols[idx]
                alpha = alphas[idx]
                color = np.array([r_vals[idx], g_vals[idx], b_vals[idx]])
                img_array[i, j] = self.animation_original_array[i, j] * (1 - alpha) + color * alpha
        
        # Convertir en image PIL
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        # Marqueurs start/end
        draw = ImageDraw.Draw(img)
        if self.start_pixel:
            i, j = self.start_pixel
            draw.point((j, i), fill=(34, 197, 94))
        
        if self.end_pixel:
            i, j = self.end_pixel
            draw.point((j, i), fill=(239, 68, 68))
        
        # Redimensionner
        new_width = int(img.width * self.zoom_level)
        new_height = int(img.height * self.zoom_level)
        
        if new_width > 0 and new_height > 0:
            img_resized = img.resize((new_width, new_height), Image.NEAREST)
        else:
            img_resized = img
        
        self.photo_image = ImageTk.PhotoImage(img_resized)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        
        # Afficher la progression
        progress_pct = int(100 * self.animation_index / len(self.animation_steps))
        self.cursor_label.config(text=f"Animation: {progress_pct}% - Nœuds explorés: {len(self.animation_visited)}")
    
    def _finish_animation(self, result):
        """Termine l'animation et affiche le résultat final"""
        self.is_animating = False
        self.current_path = result['path']
        self.last_result = result
        
        self.btn_compute.config(state=tk.NORMAL)
        self.btn_reset.config(state=tk.NORMAL)
        self.btn_visualize.config(state=tk.NORMAL)
        self.anim_checkbox.config(state=tk.NORMAL)
        
        self._update_display()
        self.cursor_label.config(text="Animation terminée")
    
    def _reset(self):
        """Réinitialise tout"""
        self.is_animating = False  # Stop any ongoing animation
        self.start_pixel = None
        self.end_pixel = None
        self.current_path = []
        self.last_result = None
        self.zoom_level = 1.0  
        
        self.start_x_var.set("0")
        self.start_y_var.set("0")
        self.end_x_var.set("0")
        self.end_y_var.set("0")
        
        self.start_label.config(text="Non défini")
        self.end_label.config(text="Non défini")
        
        self.btn_visualize.config(state=tk.DISABLED)
        
        self._update_display()
        self._update_buttons_state()
    
    def _show_matplotlib(self):
        """Affiche la visualisation matplotlib simplifiée"""
        if not self.last_result or not self.original_image:
            return
        
        # Style sombre
        plt.rcParams.update({
            'font.family': 'serif',
            'font.size': 10,
            'figure.facecolor': '#0a0a0a',
            'axes.facecolor': '#0a0a0a',
            'text.color': '#e0e0e0',
            'axes.labelcolor': '#e0e0e0',
            'axes.edgecolor': '#404040',
        })
        
        h, w = self.image_graph.get_dimensions()
        img_array = np.array(self.original_image)
        visited_set = self.last_result.get('visited_set', set())
        algo_name = self.last_result['algorithm']
        
        # Figure 2x2
        fig = plt.figure(figsize=(14, 10), dpi=100)
        fig.patch.set_facecolor('#0a0a0a')
        
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.2,
            left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        # (a) Image originale avec chemin
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.imshow(img_array)
        
        if self.current_path:
            path_y = np.array([p[0] for p in self.current_path])
            path_x = np.array([p[1] for p in self.current_path])
            ax1.plot(path_x, path_y, color='#ff4444', linewidth=2, 
                label=f'Chemin ({len(self.current_path)}px)')
        
        if self.start_pixel:
            ax1.scatter(self.start_pixel[1], self.start_pixel[0], 
                c='#00ff88', s=100, marker='.', edgecolors='white', linewidths=2,
                label='Source', zorder=5)
        if self.end_pixel:
            ax1.scatter(self.end_pixel[1], self.end_pixel[0], 
                c='#ff6b6b', s=100, marker='.', edgecolors='white', linewidths=2,
                label='Destination', zorder=5)
        
        ax1.legend(loc='upper left', fontsize=8, fancybox=False, 
            framealpha=0.0, facecolor='none', edgecolor='none',
            labelcolor='#ffffff', bbox_to_anchor=(0, -0.02), ncol=3)
        ax1.axis('off')
        ax1.set_title("Image originale avec chemin optimal", fontsize=12, 
            fontweight='bold', color='#e0e0e0', pad=10)
        
        # (b) Image en niveaux de gris
        ax2 = fig.add_subplot(gs[0, 1])
        gray_img = np.mean(img_array, axis=2)
        ax2.imshow(gray_img, cmap='gray')
        
        if self.current_path:
            ax2.plot(path_x, path_y, color='#ff4444', linewidth=2)
        
        ax2.axis('off')
        ax2.set_title("Image en niveaux de gris", fontsize=12, 
            fontweight='bold', color='#e0e0e0', pad=10)
        
        # (c) Zone d'exploration
        ax3 = fig.add_subplot(gs[1, 0])
        
        exploration_map = np.zeros((h, w), dtype=np.float32)
        for (i, j) in visited_set:
            exploration_map[i, j] = 1.0
        
        ax3.imshow(img_array, alpha=0.4)
        ax3.imshow(exploration_map, cmap='YlOrRd', alpha=0.6, interpolation='nearest')
        
        if self.current_path:
            ax3.plot(path_x, path_y, color='#00ffff', linewidth=2)
        
        exploration_pct = 100 * len(visited_set) / (w * h)
        ax3.axis('off')
        ax3.set_title(f"Zone d'exploration ({exploration_pct:.1f}%)", fontsize=12, 
            fontweight='bold', color='#e0e0e0', pad=10)
        
        # (d) Statistiques
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        
        # Cadre
        from matplotlib.patches import FancyBboxPatch
        bbox = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, 
            boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor='#151515', edgecolor='#404040', linewidth=2,
            transform=ax4.transAxes, zorder=0)
        ax4.add_patch(bbox)
        
        # Métriques
        exec_time = self.last_result['execution_time'] * 1000
        path_len = len(self.current_path)
        distance = self.last_result['distance']
        nodes = self.last_result['nodes_visited']
        heuristic_name = self.last_result.get('heuristic', '')
        
        # Titre algorithme avec heuristique si A*
        algo_display = algo_name
        if algo_name == 'A*' and heuristic_name:
            algo_display = f"A* ({heuristic_name})"
        
        stats_lines = [
            ("ALGORITHME", algo_display, True),
            ("", "", False),
            ("Dimensions", f"{w} × {h} px", False),
            ("Total pixels", f"{w*h:,}", False),
            ("", "", False),
            ("Longueur chemin", f"{path_len} px", False),
            ("Distance pondérée", f"{distance:,.1f}", False),
            ("", "", False),
            ("Nœuds explorés", f"{nodes:,}", False),
            ("Couverture", f"{exploration_pct:.2f}%", False),
            ("", "", False),
            ("Temps", f"{exec_time:.2f} ms", False),
        ]
        
        y = 0.88
        for label, value, is_title in stats_lines:
            if label == "":
                y -= 0.03
                continue
            if is_title:
                ax4.text(0.5, y, f"{label}: {value}", transform=ax4.transAxes,
                    fontsize=14, fontweight='bold', color='#6366f1',
                    ha='center', fontfamily='sans-serif')
                y -= 0.08
            else:
                ax4.text(0.15, y, label, transform=ax4.transAxes,
                    fontsize=10, color='#a0a0a0', fontfamily='sans-serif')
                ax4.text(0.85, y, value, transform=ax4.transAxes,
                    fontsize=10, color='#ffffff', fontfamily='monospace', ha='right')
                y -= 0.055
        
        ax4.set_xlabel("(d) Statistiques", fontsize=11, 
            fontweight='bold', color='#e0e0e0', labelpad=10)
        ax4.xaxis.set_label_position('bottom')
        
        plt.show()
    
    def run(self):
        self.root.mainloop()
