import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk, ImageDraw

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.graph import Graph
from core.dijkstra import Dijkstra


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
        self.root.minsize(1100, 700)
        
        self._set_dark_title_bar()
        
        self.image_graph = None
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        
        self.start_pixel = None
        self.end_pixel = None
        self.current_path = []
        
        self.scale_factor = 1.0
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.image_offset = (0, 0)
        
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
        self.btn_reset.pack(fill=tk.X)
        
        stats_card = self._create_card(sidebar_content, "Resultats")
        
        self.stats = {}
        for name, label, color in [
            ('dims', 'Dimensions', self.COLORS['text_muted']),
            ('distance', 'Distance', self.COLORS['text_muted']),
            ('time', 'Temps', self.COLORS['text_muted']),
            ('nodes', 'Nœuds', self.COLORS['text_muted']),
            ('path', 'Chemin', self.COLORS['text_muted'])
        ]:
            row = tk.Frame(stats_card, bg=self.COLORS['card'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=label, font=('Segoe UI', 10),
                bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
            
            val = tk.Label(row, text="--", font=('Consolas', 12, 'bold'),
                bg=self.COLORS['card'], fg=color)
            val.pack(side=tk.RIGHT)
            self.stats[name] = val
        
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
        """Crée une carte avec titre"""
        card = tk.Frame(parent, bg=self.COLORS['card'],
            highlightbackground=self.COLORS['border'],
            highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 8))
        
        inner = tk.Frame(card, bg=self.COLORS['card'])
        inner.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(inner, text=title, font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['card'], fg=self.COLORS['text']).pack(anchor='w')
        
        return inner
    
    def _create_button(self, parent, text, command, color, small=False):
        """Crée un bouton stylisé"""
        btn = tk.Button(parent, text=text, command=command,
            font=('Segoe UI', 9 if small else 10, 'bold'),
            bg=color, fg='#ffffff',
            activebackground=color, activeforeground='#ffffff',
            disabledforeground='#ffffff',
            relief=tk.FLAT, cursor='hand2',
            padx=10, pady=6 if small else 8)
        
        def on_enter(e):
            btn.config(bg=self._lighten_color(color))
        def on_leave(e):
            btn.config(bg=color)
        
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
            self.zoom_level = 1.0
            
            h, w = self.image_graph.get_dimensions()
            self.stats['dims'].config(text=f"{w} × {h}")
            self._reset_stats()
            
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
            self._zoom_at_point(event, old_zoom)
    
    def _zoom_out(self, event=None):
        """Zoom arrière"""
        if not self.original_image:
            return
        
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
        
        if old_zoom != self.zoom_level:
            self._zoom_at_point(event, old_zoom)
    
    def _zoom_at_point(self, event, old_zoom):
        """Zoom centré sur le point de la souris"""
        if event:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            scale_change = self.zoom_level / old_zoom
            new_x = x * scale_change
            new_y = y * scale_change

            self._update_display()
            
            self.canvas.xview_moveto((new_x - event.x) / (self.original_image.width * self.zoom_level))
            self.canvas.yview_moveto((new_y - event.y) / (self.original_image.height * self.zoom_level))
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
        
        marker_size = max(2, int(4 / self.zoom_level))
        
        if self.start_pixel:
            i, j = self.start_pixel
            draw.ellipse([j - marker_size, i - marker_size, j + marker_size, i + marker_size],
                fill=(34, 197, 94), outline=(255, 255, 255))
        
        if self.end_pixel:
            i, j = self.end_pixel
            draw.ellipse([j - marker_size, i - marker_size, j + marker_size, i + marker_size],
                fill=(239, 68, 68), outline=(255, 255, 255))
        
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
    
    def _compute_path(self):
        """Calcule le plus court chemin"""
        if not self.start_pixel or not self.end_pixel:
            return
        
        try:
            dijkstra = Dijkstra(self.image_graph)
            result = dijkstra.find_shortest_path(self.start_pixel, self.end_pixel)
            
            self.current_path = result['path']
            
            self.stats['distance'].config(text=f"{result['distance']:.0f}")
            self.stats['time'].config(text=f"{result['execution_time']*1000:.1f} ms")
            self.stats['nodes'].config(text=f"{result['nodes_visited']:,}")
            self.stats['path'].config(text=f"{len(self.current_path)} px")
            
            self._update_display()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul:\n{e}")
    
    def _reset(self):
        """Réinitialise tout"""
        self.start_pixel = None
        self.end_pixel = None
        self.current_path = []
        self.zoom_level = 1.0  
        
        self.start_x_var.set("0")
        self.start_y_var.set("0")
        self.end_x_var.set("0")
        self.end_y_var.set("0")
        
        self.start_label.config(text="Non défini")
        self.end_label.config(text="Non défini")
        
        self._reset_stats()
        self._update_display()
        self._update_buttons_state()
    
    def _reset_stats(self):
        for key in ['distance', 'time', 'nodes', 'path']:
            self.stats[key].config(text="--")
    
    def run(self):
        self.root.mainloop()
