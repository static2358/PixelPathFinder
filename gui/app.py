import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.graph import Graph
from core.dijkstra import Dijkstra
from core.astar import AStar


class Application:
    COLORS = {
        'bg': '#0f0f0f', 'surface': '#1a1a1a', 'card': '#252525', 'border': '#3d3d3d',
        'primary': '#6366f1', 'primary_hover': '#818cf8', 'success': '#22c55e',
        'danger': '#ef4444', 'warning': '#f59e0b', 'text': '#ffffff',
        'text_muted': '#a3a3a3', 'text_dim': '#525252',
    }
    
    HEURISTIC_MAP = {'Intensite': 'intensity', 'Manhattan': 'manhattan', 
                     'Euclidienne': 'euclidean', 'Chebyshev': 'chebyshev'}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pathfinder")
        self.root.geometry("1200x720")
        self.root.configure(bg=self.COLORS['bg'])
        self.root.minsize(1200, 720)
        self._set_dark_title_bar()
        
        self.image_graph = self.original_image = self.photo_image = None
        self.start_pixel = self.end_pixel = self.last_result = None
        self.current_path = []
        self.zoom_level, self.min_zoom, self.max_zoom = 1.0, 0.1, 20.0
        
        self.algorithm = tk.StringVar(value="dijkstra")
        self.heuristic = tk.StringVar(value="Intensite")
        self.animation_enabled = tk.BooleanVar(value=False)
        self.is_animating = False
        
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        for name, bg in [('Card.TFrame', 'card'), ('Surface.TFrame', 'surface')]:
            style.configure(name, background=self.COLORS[bg])
        
        style.configure('TCombobox', fieldbackground=self.COLORS['bg'], 
            background=self.COLORS['card'], foreground=self.COLORS['text'],
            arrowcolor=self.COLORS['text'], bordercolor=self.COLORS['border'])
        style.map('TCombobox',
            fieldbackground=[('readonly', self.COLORS['bg']), ('disabled', self.COLORS['surface'])],
            foreground=[('disabled', self.COLORS['text_dim'])])

    def _build_ui(self):
        main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg=self.COLORS['surface'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        content = tk.Frame(sidebar, bg=self.COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self._create_button(content, "Charger Image", self._load_image, 
                           self.COLORS['card']).pack(fill=tk.X, pady=(0, 10))
        
        # Algorithme card
        algo_card = self._create_card(content, "Algorithme")
        self._create_radiobutton(algo_card, "Dijkstra", "dijkstra")
        
        astar_frame = tk.Frame(algo_card, bg=self.COLORS['card'])
        astar_frame.pack(fill=tk.X, anchor='w')
        self._create_radiobutton(astar_frame, "A*", "astar", pack=False).pack(side=tk.LEFT)
        
        for opt in ['*TCombobox*Listbox.background', '*TCombobox*Listbox.foreground',
                    '*TCombobox*Listbox.selectBackground', '*TCombobox*Listbox.selectForeground']:
            self.root.option_add(opt, self.COLORS['bg' if 'background' in opt and 'select' not in opt 
                                                   else 'text' if 'Foreground' in opt and 'select' not in opt
                                                   else 'primary' if 'selectBack' in opt else 'text'])
        
        self.heuristic_combo = ttk.Combobox(astar_frame, textvariable=self.heuristic,
            values=list(self.HEURISTIC_MAP.keys()), state='disabled', font=('Segoe UI', 9), width=12)
        self.heuristic_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        anim_frame = tk.Frame(algo_card, bg=self.COLORS['card'])
        anim_frame.pack(fill=tk.X, pady=(10, 0))
        self.anim_checkbox = tk.Checkbutton(anim_frame, text="Animation",
            variable=self.animation_enabled, font=('Segoe UI', 10), 
            bg=self.COLORS['card'], fg=self.COLORS['text'], selectcolor=self.COLORS['bg'],
            activebackground=self.COLORS['card'], activeforeground=self.COLORS['text'])
        self.anim_checkbox.pack(anchor='w')
        tk.Label(anim_frame, text="(Recommande pour petites images)", font=('Segoe UI', 8),
                bg=self.COLORS['card'], fg=self.COLORS['text_dim']).pack(anchor='w')
        
        # Points cards
        start_card = self._create_card(content, "Point de Depart")
        self.start_x_var, self.start_y_var = tk.StringVar(value="0"), tk.StringVar(value="0")
        self._create_coord_inputs(start_card, self.start_x_var, self.start_y_var)
        self._create_button(start_card, "Definir", self._set_start_from_entry, 
                           self.COLORS['success'], small=True).pack(fill=tk.X, pady=(10, 0))
        self.start_label = tk.Label(start_card, text="Non defini", font=('Consolas', 9),
                                    bg=self.COLORS['card'], fg=self.COLORS['text_dim'])
        self.start_label.pack(anchor='w', pady=(5, 0))
        
        end_card = self._create_card(content, "Point d'Arrivee")
        self.end_x_var, self.end_y_var = tk.StringVar(value="0"), tk.StringVar(value="0")
        self._create_coord_inputs(end_card, self.end_x_var, self.end_y_var)
        self._create_button(end_card, "Definir", self._set_end_from_entry,
                           self.COLORS['danger'], small=True).pack(fill=tk.X, pady=(10, 0))
        self.end_label = tk.Label(end_card, text="Non defini", font=('Consolas', 9),
                                  bg=self.COLORS['card'], fg=self.COLORS['text_dim'])
        self.end_label.pack(anchor='w', pady=(5, 0))
        
        # Action buttons
        actions = tk.Frame(content, bg=self.COLORS['surface'])
        actions.pack(fill=tk.X, pady=10)
        
        self.btn_compute = self._create_button(actions, "Calculer Chemin", 
                                               self._compute_path, self.COLORS['primary'])
        self.btn_compute.pack(fill=tk.X, pady=(0, 5))
        self.btn_compute.config(state=tk.DISABLED)
        
        self._create_button(actions, "Reinitialiser", self._reset, 
                           self.COLORS['card']).pack(fill=tk.X, pady=(0, 5))
        
        self.btn_visualize = self._create_button(actions, "Visualiser",
                                                 self._show_matplotlib, self.COLORS['warning'])
        self.btn_visualize.pack(fill=tk.X)
        self.btn_visualize.config(state=tk.DISABLED)
        
        tk.Label(content, text="Clic gauche = Depart | Clic droit = Arrivee\nCtrl+Molette = Zoom",
                font=('Segoe UI', 8), bg=self.COLORS['surface'], 
                fg=self.COLORS['text_dim'], justify=tk.LEFT).pack(anchor='w', pady=(10, 0))
        
        # Canvas
        img_frame = tk.Frame(main_container, bg=self.COLORS['bg'])
        img_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas = tk.Canvas(tk.Frame(img_frame, bg=self.COLORS['surface']),
            bg=self.COLORS['surface'], highlightthickness=0, cursor="crosshair")
        self.canvas.master.pack(fill=tk.BOTH, expand=True)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Configure>", lambda e: self._update_display())
        
        self.cursor_label = tk.Label(img_frame, text="", font=('Consolas', 9),
                                     bg=self.COLORS['bg'], fg=self.COLORS['text_dim'])
        self.cursor_label.pack(pady=(10, 0))
        self._show_placeholder()

    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.COLORS['card'])
        card.pack(fill=tk.X, pady=(0, 8))
        inner = tk.Frame(card, bg=self.COLORS['card'])
        inner.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(inner, text=title, font=('Segoe UI', 10, 'bold'),
                bg=self.COLORS['card'], fg=self.COLORS['text']).pack(anchor='w')
        return inner

    def _create_button(self, parent, text, command, color, small=False):
        btn = tk.Button(parent, text=text, command=command,
            font=('Segoe UI', 9 if small else 10, 'bold'), bg=color, fg='#ffffff',
            activebackground=color, activeforeground='#ffffff', disabledforeground='#ffffff',
            relief=tk.FLAT, cursor='hand2', bd=0, highlightthickness=0,
            padx=10, pady=6 if small else 8)
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten_color(color)) if btn['state'] != tk.DISABLED else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=color) if btn['state'] != tk.DISABLED else None)
        return btn

    def _create_radiobutton(self, parent, text, value, pack=True):
        rb = tk.Radiobutton(parent, text=text, variable=self.algorithm, value=value,
            font=('Segoe UI', 10), bg=self.COLORS['card'], fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg'], activebackground=self.COLORS['card'],
            activeforeground=self.COLORS['text'], command=self._on_algorithm_change)
        if pack:
            rb.pack(anchor='w')
        return rb

    def _create_coord_inputs(self, parent, x_var, y_var):
        frame = tk.Frame(parent, bg=self.COLORS['card'])
        frame.pack(fill=tk.X, pady=(10, 5))
        for label, var, padx in [("X:", x_var, (5, 15)), ("Y:", y_var, 5)]:
            tk.Label(frame, text=label, font=('Segoe UI', 10),
                    bg=self.COLORS['card'], fg=self.COLORS['text_muted']).pack(side=tk.LEFT)
            tk.Entry(frame, textvariable=var, width=8, font=('Consolas', 11),
                bg=self.COLORS['bg'], fg=self.COLORS['text'], insertbackground=self.COLORS['text'],
                relief=tk.FLAT, highlightthickness=1, highlightbackground=self.COLORS['border'],
                highlightcolor=self.COLORS['primary']).pack(side=tk.LEFT, padx=padx)

    def _lighten_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return '#{:02x}{:02x}{:02x}'.format(*[min(255, int(hex_color[i:i+2], 16) + 30) for i in (0, 2, 4)])

    def _set_dark_title_bar(self):
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except: pass

    def _show_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.canvas.winfo_width() // 2 or 400,
            self.canvas.winfo_height() // 2 or 300, text="Chargez une image pour commencer",
            font=('Segoe UI', 16), fill=self.COLORS['text_dim'])

    def _load_image(self):
        path = filedialog.askopenfilename(title="Selectionner une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"), ("Tous", "*.*")])
        if not path:
            return
        try:
            self.original_image = Image.open(path).convert('RGB')
            self.image_graph = Graph(path)
            self.start_pixel = self.end_pixel = self.last_result = None
            self.current_path = []
            self.zoom_level = 1.0
            self.btn_visualize.config(state=tk.DISABLED)
            self._update_display()
            self._update_buttons_state()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")

    def _on_mousewheel(self, event):
        if event.state & 0x4:  # Ctrl
            old_zoom = self.zoom_level
            self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2) if event.delta > 0 else max(self.min_zoom, self.zoom_level / 1.2)
            if old_zoom != self.zoom_level:
                self._zoom_at_point(event)
        elif event.state & 0x1:  # Shift
            self.canvas.xview_scroll(int(-event.delta/120), "units")
        else:
            self.canvas.yview_scroll(int(-event.delta/120), "units")

    def _zoom_at_point(self, event):
        if not self.original_image:
            return
        if event:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self._update_display_animated() if self.is_animating else self._update_display()
            self.canvas.xview_moveto((x * self.zoom_level / self.zoom_level - event.x) / (self.original_image.width * self.zoom_level))
            self.canvas.yview_moveto((y * self.zoom_level / self.zoom_level - event.y) / (self.original_image.height * self.zoom_level))
        else:
            self._update_display_animated() if self.is_animating else self._update_display()

    def _update_display(self):
        if not self.original_image:
            self._show_placeholder()
            return
        img = self.original_image.copy()
        draw = ImageDraw.Draw(img)
        
        if len(self.current_path) > 1:
            color = self._get_path_color()
            draw.line([(j, i) for i, j in self.current_path], fill=color, width=max(1, int(2/self.zoom_level)))
        
        if self.start_pixel:
            draw.point((self.start_pixel[1], self.start_pixel[0]), fill=(34, 197, 94))
        if self.end_pixel:
            draw.point((self.end_pixel[1], self.end_pixel[0]), fill=(239, 68, 68))
        
        w, h = int(img.width * self.zoom_level), int(img.height * self.zoom_level)
        if w > 0 and h > 0:
            img = img.resize((w, h), Image.NEAREST if self.zoom_level > 1 else Image.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.configure(scrollregion=(0, 0, w, h))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)

    def _get_path_color(self):
        if not self.current_path or not self.original_image:
            return (255, 0, 0)
        sample_size = min(50, len(self.current_path))
        step = max(1, len(self.current_path) // sample_size)
        red_count = sum(1 for idx in range(0, len(self.current_path), step)
                       if self._is_red_pixel(self.current_path[idx]))
        return (0, 255, 255) if red_count > sample_size * 0.3 else (255, 0, 0)

    def _is_red_pixel(self, pixel):
        try:
            r, g, b = self.original_image.getpixel((pixel[1], pixel[0]))[:3]
            return r > 150 and r > g * 1.5 and r > b * 1.5
        except: return False

    def _canvas_to_pixel(self, x, y):
        if not self.image_graph:
            return None
        j, i = int(self.canvas.canvasx(x) / self.zoom_level), int(self.canvas.canvasy(y) / self.zoom_level)
        return (i, j) if self.image_graph.is_valid_pixel(i, j) else None

    def _on_left_click(self, event):
        if pixel := self._canvas_to_pixel(event.x, event.y):
            self.start_pixel = pixel
            self.current_path = []
            self.start_x_var.set(str(pixel[1]))
            self.start_y_var.set(str(pixel[0]))
            self.start_label.config(text=f"({pixel[1]}, {pixel[0]})")
            self._update_display()
            self._update_buttons_state()

    def _on_right_click(self, event):
        if pixel := self._canvas_to_pixel(event.x, event.y):
            self.end_pixel = pixel
            self.current_path = []
            self.end_x_var.set(str(pixel[1]))
            self.end_y_var.set(str(pixel[0]))
            self.end_label.config(text=f"({pixel[1]}, {pixel[0]})")
            self._update_display()
            self._update_buttons_state()

    def _on_mouse_move(self, event):
        if pixel := self._canvas_to_pixel(event.x, event.y):
            i, j = pixel
            self.cursor_label.config(text=f"Position: ({j}, {i})  |  Intensite: {self.image_graph.get_pixel_value(i, j)}  |  Zoom: {int(self.zoom_level * 100)}%")
        elif self.original_image:
            self.cursor_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")
        else:
            self.cursor_label.config(text="")

    def _set_point_from_entry(self, x_var, y_var, is_start):
        try:
            x, y = int(x_var.get()), int(y_var.get())
            if self.image_graph and self.image_graph.is_valid_pixel(y, x):
                if is_start:
                    self.start_pixel = (y, x)
                    self.start_label.config(text=f"({x}, {y})")
                else:
                    self.end_pixel = (y, x)
                    self.end_label.config(text=f"({x}, {y})")
                self.current_path = []
                self._update_display()
                self._update_buttons_state()
            else:
                messagebox.showwarning("Attention", "Coordonnees invalides")
        except ValueError:
            messagebox.showwarning("Attention", "Entrez des nombres valides")

    def _set_start_from_entry(self):
        self._set_point_from_entry(self.start_x_var, self.start_y_var, True)

    def _set_end_from_entry(self):
        self._set_point_from_entry(self.end_x_var, self.end_y_var, False)

    def _update_buttons_state(self):
        state = tk.NORMAL if self.start_pixel and self.end_pixel else tk.DISABLED
        self.btn_compute.config(state=state)

    def _on_algorithm_change(self):
        self.heuristic_combo.config(state='readonly' if self.algorithm.get() == "astar" else 'disabled')

    def _compute_path(self):
        if not self.start_pixel or not self.end_pixel or self.is_animating:
            return
        try:
            if self.algorithm.get() == "astar":
                algo = AStar(self.image_graph, heuristic=self.HEURISTIC_MAP.get(self.heuristic.get(), 'intensity'))
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
        self.is_animating = True
        self.btn_compute.config(state=tk.DISABLED)
        self.anim_checkbox.config(state=tk.DISABLED)
        
        result = algo.find_shortest_path(self.start_pixel, self.end_pixel)
        visited_steps = result.get('visited_steps', [])
        
        if not visited_steps:
            self._finish_animation(result)
            return
        
        nodes_per_frame = max(1, len(visited_steps) // 90)
        
        self.animation_visited = set()
        self.animation_trail = []
        self.trail_length = max(20, nodes_per_frame)
        self.animation_steps = visited_steps
        self.animation_result = result
        self.animation_index = 0
        self.nodes_per_frame = nodes_per_frame
        self.animation_img_array = np.array(self.original_image).astype(np.float32)
        self.animation_original_array = self.animation_img_array.copy()
        
        self._animate_step()

    def _animate_step(self):
        if not self.is_animating:
            return
        
        end_idx = min(self.animation_index + self.nodes_per_frame, len(self.animation_steps))
        new_pixels = []
        
        for i in range(self.animation_index, end_idx):
            pixel = self.animation_steps[i]
            new_pixels.append(pixel)
            self.animation_visited.add(pixel)
            pi, pj = pixel
            self.animation_img_array[pi, pj] = self.animation_original_array[pi, pj] * 0.5 + np.array([255, 140, 0]) * 0.5
        
        self.animation_trail = (self.animation_trail + new_pixels)[-self.trail_length:]
        self.animation_index = end_idx
        self._update_display_animated()
        
        if self.animation_index < len(self.animation_steps):
            self.root.after(33, self._animate_step)
        else:
            self._finish_animation(self.animation_result)

    def _update_display_animated(self):
        if not self.original_image:
            return
        
        img_array = self.animation_img_array.copy()
        
        if self.animation_trail:
            trail = np.array(self.animation_trail)
            progress = np.linspace(0, 1, len(trail))
            for idx, (i, j) in enumerate(trail):
                alpha = 0.7 + 0.3 * progress[idx]
                color = np.array([50 * progress[idx], 80 + 120 * progress[idx], 180 + 75 * progress[idx]])
                img_array[i, j] = self.animation_original_array[i, j] * (1 - alpha) + color * alpha
        
        img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8), 'RGB')
        draw = ImageDraw.Draw(img)
        
        if self.start_pixel:
            draw.point((self.start_pixel[1], self.start_pixel[0]), fill=(34, 197, 94))
        if self.end_pixel:
            draw.point((self.end_pixel[1], self.end_pixel[0]), fill=(239, 68, 68))
        
        w, h = int(img.width * self.zoom_level), int(img.height * self.zoom_level)
        if w > 0 and h > 0:
            img = img.resize((w, h), Image.NEAREST)
        
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        
        pct = int(100 * self.animation_index / len(self.animation_steps))
        self.cursor_label.config(text=f"Animation: {pct}% - Noeuds explores: {len(self.animation_visited)}")

    def _finish_animation(self, result):
        self.is_animating = False
        self.current_path = result['path']
        self.last_result = result
        self.btn_compute.config(state=tk.NORMAL)
        self.btn_visualize.config(state=tk.NORMAL)
        self.anim_checkbox.config(state=tk.NORMAL)
        self._update_display()
        self.cursor_label.config(text="Animation terminee")

    def _reset(self):
        self.is_animating = False
        self.start_pixel = self.end_pixel = self.last_result = None
        self.current_path = []
        self.zoom_level = 1.0
        for var in [self.start_x_var, self.start_y_var, self.end_x_var, self.end_y_var]:
            var.set("0")
        self.start_label.config(text="Non defini")
        self.end_label.config(text="Non defini")
        self.btn_visualize.config(state=tk.DISABLED)
        self._update_display()
        self._update_buttons_state()

    def _show_matplotlib(self):
        if not self.last_result or not self.original_image:
            return
        
        plt.rcParams.update({'figure.facecolor': '#0a0a0a', 'axes.facecolor': '#0a0a0a',
            'text.color': '#e0e0e0', 'axes.labelcolor': '#e0e0e0', 'axes.edgecolor': '#404040'})
        
        h, w = self.image_graph.get_dimensions()
        img_array = np.array(self.original_image)
        visited_set = self.last_result.get('visited_set', set())
        
        fig = plt.figure(figsize=(14, 10), dpi=100)
        fig.patch.set_facecolor('#0a0a0a')
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.2, left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        path_x = np.array([p[1] for p in self.current_path]) if self.current_path else None
        path_y = np.array([p[0] for p in self.current_path]) if self.current_path else None
        
        # Image originale
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.imshow(img_array)
        if self.current_path:
            ax1.plot(path_x, path_y, color='#ff4444', linewidth=2, label=f'Chemin ({len(self.current_path)}px)')
        if self.start_pixel:
            ax1.scatter(self.start_pixel[1], self.start_pixel[0], c='#00ff88', s=100, marker='.', 
                       edgecolors='white', linewidths=2, label='Source', zorder=5)
        if self.end_pixel:
            ax1.scatter(self.end_pixel[1], self.end_pixel[0], c='#ff6b6b', s=100, marker='.',
                       edgecolors='white', linewidths=2, label='Destination', zorder=5)
        ax1.legend(loc='upper left', fontsize=8, framealpha=0, labelcolor='#ffffff', bbox_to_anchor=(0, -0.02), ncol=3)
        ax1.axis('off')
        ax1.set_title("Image originale avec chemin optimal", fontsize=12, fontweight='bold', color='#e0e0e0', pad=10)
        
        # Grayscale
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.imshow(np.mean(img_array, axis=2), cmap='gray')
        if self.current_path:
            ax2.plot(path_x, path_y, color='#ff4444', linewidth=2)
        ax2.axis('off')
        ax2.set_title("Image en niveaux de gris", fontsize=12, fontweight='bold', color='#e0e0e0', pad=10)
        
        # Exploration
        ax3 = fig.add_subplot(gs[1, 0])
        exploration_map = np.zeros((h, w), dtype=np.float32)
        for i, j in visited_set:
            exploration_map[i, j] = 1.0
        ax3.imshow(img_array, alpha=0.4)
        ax3.imshow(exploration_map, cmap='YlOrRd', alpha=0.6, interpolation='nearest')
        if self.current_path:
            ax3.plot(path_x, path_y, color='#00ffff', linewidth=2)
        exploration_pct = 100 * len(visited_set) / (w * h)
        ax3.axis('off')
        ax3.set_title(f"Zone d'exploration ({exploration_pct:.1f}%)", fontsize=12, fontweight='bold', color='#e0e0e0', pad=10)
        
        # Stats
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        ax4.add_patch(FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor='#151515', edgecolor='#404040', linewidth=2, transform=ax4.transAxes))
        
        algo_name = self.last_result['algorithm']
        heuristic = self.last_result.get('heuristic', '')
        algo_display = f"A* ({heuristic})" if algo_name == 'A*' and heuristic else algo_name
        
        stats = [
            ("ALGORITHME", algo_display, True), ("", "", False),
            ("Dimensions", f"{w}x{h}", False), ("Total pixels", f"{w*h:,} px", False), ("", "", False),
            ("Longueur chemin", f"{len(self.current_path)} px", False),
            ("Distance ponderee", f"{self.last_result['distance']:,.1f}", False), ("", "", False),
            ("Noeuds explores", f"{self.last_result['nodes_visited']:,}", False),
            ("Couverture", f"{exploration_pct:.2f}%", False), ("", "", False),
            ("Temps", f"{self.last_result['execution_time']*1000:.2f} ms", False),
        ]
        
        y = 0.88
        for label, value, is_title in stats:
            if not label:
                y -= 0.03
                continue
            if is_title:
                ax4.text(0.5, y, f"{label}: {value}", transform=ax4.transAxes, fontsize=14,
                        fontweight='bold', color='#6366f1', ha='center')
                y -= 0.08
            else:
                ax4.text(0.15, y, label, transform=ax4.transAxes, fontsize=10, color='#a0a0a0')
                ax4.text(0.85, y, value, transform=ax4.transAxes, fontsize=10, color='#ffffff',
                        fontfamily='monospace', ha='right')
                y -= 0.055
        
        plt.show()

    def run(self):
        self.root.mainloop()
