import sqlite3
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Quad
from kivy.utils import platform

try:
    from plyer import notification
    PLYER_DISPONIBLE = True
except ImportError:
    PLYER_DISPONIBLE = False

DB_PATH = "pape_sistema_minimalista.db"

class PantallaPortada(Screen):
    def on_enter(self, *args):
        self.clear_widgets()
        ruta_img = "/storage/emulated/0/Download/Mi Negocio/logo_carga.png"
        
        if os.path.exists(ruta_img):
            img = Image(source=ruta_img, allow_stretch=True, keep_ratio=True)
            self.add_widget(img)
        else:
            self.add_widget(Label(text=f"No halla la imagen en:\n{ruta_img}\n\n(Cargando menú en 3s...)"))
            
        Clock.schedule_once(self.ir_al_menu, 3)

    def ir_al_menu(self, dt):
        self.manager.current = 'menu'

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        id TEXT, categoria TEXT, nombre TEXT, variante TEXT, precio REAL, stock INTEGER,
                        PRIMARY KEY (id, variante))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, total REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, descripcion TEXT, monto REAL, fecha TEXT)''')
    conn.commit()
    conn.close()

def lanzar_alerta_nativa(nombre_prod, variante_prod, stock_restante):
    from kivy.uix.popup import Popup
    contenido = Label(
        text=f"Quedan solo {stock_restante} piezas de:\n{nombre_prod} ({variante_prod})",
        font_size='16sp',
        halign='center'
    )
    alerta_popup = Popup(
        title="⚠️ ¡STOCK BAJO EN ALMACÉN!",
        content=contenido,
        size_hint=(0.8, 0.3)
    )
    alerta_popup.open()

# Estilos Visuales Learn Up
ICON_VENTAS = "CAJA"
ICON_ALMACEN = "INV"
ICON_REGISTRO = "REG"
ICON_MAS = "[ + ]"
ICON_MENOS = "[ - ]"
ICON_ELIMINAR = "[ X ]"
ICON_VOLVER = "< Volver"
ICON_GUARDAR = "[ OK ]"

COLOR_BG_LIGHT = (0.95, 0.95, 0.96, 1)      
COLOR_CARD_WHITE = (1, 1, 1, 1)             
COLOR_TEXT_DARK = (0.07, 0.07, 0.08, 1)     
COLOR_TEXT_MUTED = (0.45, 0.45, 0.48, 1)    
COLOR_BTN_BLACK = (0.02, 0.02, 0.03, 1)        
COLOR_BORDER_LINE = (0.85, 0.85, 0.88, 1)   

class BotonSolidoNegro(ButtonBehavior, AnchorLayout):
    def __init__(self, radius=[28], **kwargs):
        super().__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        self.radius = radius
        self.bind(pos=self.actualizar_graficos, size=self.actualizar_graficos)

    def actualizar_graficos(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_BTN_BLACK)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

class BotonContornoLimpio(ButtonBehavior, AnchorLayout):
    def __init__(self, radius=[24], **kwargs):
        super().__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        self.radius = radius
        self.bind(pos=self.actualizar_graficos, size=self.actualizar_graficos)

    def actualizar_graficos(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_CARD_WHITE)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            Color(*COLOR_BORDER_LINE)
            Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 
                                     self.radius[0], self.radius[0], self.radius[0], self.radius[0]), width=1.5)

class TarjetaContenedorBlanca(BoxLayout):
    def __init__(self, radius=[24], **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.bind(pos=self.actualizar_graficos, size=self.actualizar_graficos)

    def actualizar_graficos(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_CARD_WHITE)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            Color(*COLOR_BORDER_LINE)
            Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 
                                     self.radius[0], self.radius[0], self.radius[0], self.radius[0]), width=1.2)

class FondoOndaDecorativa(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.actualizar_ondas, size=self.actualizar_ondas)

    def actualizar_ondas(self, *args):
        self.canvas.before.clear()
        x, y = self.pos
        w, h = self.size
        with self.canvas.before:
            Color(*COLOR_BG_LIGHT)
            RoundedRectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BTN_BLACK)
            Quad(points=[x, y + h,  x + w, y + h,  x + w, y + h * 0.74,  x, y + h * 0.84])
            Color(0.02, 0.02, 0.03, 0.15)
            Quad(points=[x, y + h * 0.84,  x + w, y + h * 0.74,  x + w, y + h * 0.70,  x, y + h * 0.78])
            Color(*COLOR_BTN_BLACK)
            Quad(points=[x, y,  x + w, y,  x + w, y + h * 0.08,  x, y + h * 0.04])

class GraficaBarrasVentas(BoxLayout):
    def __init__(self, datos_ventas, **kwargs):
        super().__init__(**kwargs)
        self.datos = datos_ventas[-6:] if datos_ventas else []
        self.bind(pos=self.dibujar_grafica, size=self.dibujar_grafica)

    def dibujar_grafica(self, *args):
        self.canvas.clear()
        if not self.datos: return
        x_start, y_start = self.pos
        ancho_total, alto_total = self.size
        padding_x, padding_y = 30, 20
        ancho_util = ancho_total - (padding_x * 2)
        alto_util = alto_total - (padding_y * 2)
        max_valor = max(self.datos) if max(self.datos) > 0 else 1.0
        num_barras = len(self.datos)
        ancho_barra = (ancho_util / num_barras) * 0.65
        espaciado = (ancho_util / num_barras) * 0.35
        with self.canvas:
            for i, valor in enumerate(self.datos):
                altura_barra = (valor / max_valor) * alto_util
                altura_barra = max(altura_barra, 5)
                bx = x_start + padding_x + (i * (ancho_barra + espaciado)) + (espaciado / 2)
                by = y_start + padding_y
                Color(*COLOR_BTN_BLACK)
                RoundedRectangle(pos=(bx, by), size=(ancho_barra, altura_barra), radius=[6, 6, 0, 0])

class PantallaMenu(Screen):
    def on_enter(self):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        layout_principal = BoxLayout(orientation='vertical', padding=[30, 20, 30, 20], spacing=20)
        
        header = BoxLayout(orientation='vertical', size_hint_y=0.18, spacing=2)
        header.add_widget(Label(text="learn up", font_size='46sp', color=(1, 1, 1, 1), bold=True, halign='center'))
        header.add_widget(Label(text="Mi Papelería  •  Control de Ventas", font_size='14sp', color=(1, 1, 1, 1), halign='center'))
        layout_principal.add_widget(header)
        
        btn_caja = BotonSolidoNegro(size_hint_y=0.15, radius=[24])
        box_caja = BoxLayout(orientation='horizontal', padding=[24, 0, 24, 0], spacing=16)
        box_caja.add_widget(Label(text=ICON_VENTAS, font_size='15sp', bold=True, color=(1,1,1,1), size_hint_x=0.2))
        box_caja.add_widget(Label(text="Punto de Venta", font_size='18sp', bold=True, color=(1,1,1,1), halign='left'))
        btn_caja.add_widget(box_caja)
        btn_caja.bind(on_press=lambda x: setattr(self.manager, 'current', 'caja'))
        layout_principal.add_widget(btn_caja)
        
        fila_cuadrados = BoxLayout(orientation='horizontal', size_hint_y=0.18, spacing=16)
        
        btn_inv = BotonContornoLimpio(radius=[20])
        box_inv = BoxLayout(orientation='vertical', padding=[10, 12, 10, 12], spacing=4)
        box_inv.add_widget(Label(text=ICON_ALMACEN, font_size='15sp', bold=True, color=COLOR_TEXT_DARK))
        box_inv.add_widget(Label(text="Almacén", font_size='15sp', bold=True, color=COLOR_TEXT_DARK))
        btn_inv.add_widget(box_inv)
        btn_inv.bind(on_press=lambda x: setattr(self.manager, 'current', 'inventario'))

        btn_gastos = BotonContornoLimpio(radius=[20])
        box_gastos = BoxLayout(orientation='vertical', padding=[10, 12, 10, 12], spacing=4)
        box_gastos.add_widget(Label(text="💰", font_size='15sp'))
        box_gastos.add_widget(Label(text="Gastos", font_size='15sp', bold=True, color=COLOR_TEXT_DARK))
        btn_gastos.add_widget(box_gastos)
        btn_gastos.bind(on_press=lambda x: setattr(self.manager, 'current', 'gastos'))
        
        btn_corte = BotonContornoLimpio(radius=[20])
        box_corte = BoxLayout(orientation='vertical', padding=[10, 12, 10, 12], spacing=4)
        box_corte.add_widget(Label(text=ICON_REGISTRO, font_size='15sp', bold=True, color=COLOR_TEXT_DARK))
        box_corte.add_widget(Label(text="Registro", font_size='15sp', bold=True, color=COLOR_TEXT_DARK))
        btn_corte.add_widget(box_corte)
        btn_corte.bind(on_press=lambda x: setattr(self.manager, 'current', 'corte'))
        
        fila_cuadrados.add_widget(btn_inv)
        fila_cuadrados.add_widget(btn_gastos)
        fila_cuadrados.add_widget(btn_corte)
        layout_principal.add_widget(fila_cuadrados)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT total FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
        ventas_hoy = cursor.fetchall()
        cursor.execute("SELECT monto FROM gastos WHERE fecha LIKE ?", (f"{hoy}%",))
        gastos_hoy = cursor.fetchall()
        conn.close()
        
        total_ventas = sum(v[0] for v in ventas_hoy)
        total_gastos = sum(g[0] for g in gastos_hoy)
        ganancia_neta = total_ventas - total_gastos
        
        panel_dashboard = BotonSolidoNegro(size_hint_y=0.28, radius=[26])
        panel_dashboard.bind(on_press=lambda x: setattr(self.manager, 'current', 'corte'))
        
        box_dash = BoxLayout(orientation='vertical', padding=[20, 14, 20, 14], spacing=2)
        box_dash.add_widget(Label(text="GANANCIA NETA REAL HOY", font_size='12sp', bold=True, color=(0.6, 0.6, 0.6, 1), halign='center'))
        box_dash.add_widget(Label(text=f"${ganancia_neta:.2f}", font_size='38sp', bold=True, color=(1, 1, 1, 1), halign='center'))
        box_dash.add_widget(Label(text=f"Ventas: ${total_ventas:.2f}  |  Gastos: ${total_gastos:.2f}", font_size='13sp', color=(0.8, 0.8, 0.8, 1), halign='center'))
        
        panel_dashboard.add_widget(box_dash)
        layout_principal.add_widget(panel_dashboard)
        
        contenedor.add_widget(layout_principal)
        self.add_widget(contenedor)

class PantallaCaja(Screen):
    def on_enter(self):
        self.carrito = []
        self.total = 0.0
        self.categoria_actual = ""
        self.clear_widgets()
        
        contenedor = FondoOndaDecorativa()
        layout = BoxLayout(orientation='vertical', padding=24, spacing=16)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=14)
        btn_volver = BotonContornoLimpio(size_hint_x=0.32, radius=[14])
        box_vol = BoxLayout(orientation='horizontal', padding=[6,0,6,0], spacing=4)
        box_vol.add_widget(Label(text=ICON_VOLVER, font_size='13sp', bold=True, color=COLOR_TEXT_DARK))
        btn_volver.add_widget(box_vol)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        header.add_widget(btn_volver)
        header.add_widget(Label(text="PUNTO DE VENTA", font_size='18sp', bold=True, color=(1, 1, 1, 1)))
        layout.add_widget(header)

        scroll_pestanas = ScrollView(size_hint_y=0.08, do_scroll_y=False, do_scroll_x=True)
        self.grid_pestanas = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=10, padding=[2, 2, 2, 2])
        self.grid_pestanas.bind(minimum_width=self.grid_pestanas.setter('width'))
        scroll_pestanas.add_widget(self.grid_pestanas)
        layout.add_widget(scroll_pestanas)

        panel_central = BoxLayout(orientation='horizontal', size_hint_y=0.48, spacing=14)
        izq_box = BoxLayout(orientation='vertical', size_hint_x=0.52)
        self.scroll_catalogo = ScrollView()
        self.grid_catalogo = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=[2, 2, 2, 2])
        self.grid_catalogo.bind(minimum_height=self.grid_catalogo.setter('height'))
        self.scroll_catalogo.add_widget(self.grid_catalogo)
        izq_box.add_widget(self.scroll_catalogo)
        
        der_box = TarjetaContenedorBlanca(orientation='vertical', size_hint_x=0.48, padding=12, spacing=6, radius=[18])
        der_box.add_widget(Label(text="TICKET ACTUAL", size_hint_y=0.10, bold=True, font_size='13sp', color=COLOR_TEXT_MUTED))
        self.scroll_carrito = ScrollView()
        self.grid_carrito = GridLayout(cols=1, size_hint_y=None, spacing=8)
        self.grid_carrito.bind(minimum_height=self.grid_carrito.setter('height'))
        self.scroll_carrito.add_widget(self.grid_carrito)
        der_box.add_widget(self.scroll_carrito)
        
        panel_central.add_widget(izq_box)
        panel_central.add_widget(der_box)
        layout.add_widget(panel_central)

        self.lbl_total = Label(text="$0.00", font_size='44sp', bold=True, size_hint_y=0.10, color=COLOR_TEXT_DARK)
        layout.add_widget(self.lbl_total)

        btn_cot = BotonSolidoNegro(size_hint_y=0.08, radius=[18])
        btn_cot.add_widget(Label(text="Cotizar (10% Desc)", bold=True, color=(1,1,1,1)))
        btn_cot.bind(on_press=self.aplicar_descuento)
        layout.add_widget(btn_cot)

        btn_cobrar = BotonSolidoNegro(size_hint_y=0.10, radius=[20])
        btn_cobrar.add_widget(Label(text="COMPLETAR TRANSACCIÓN", font_size='15sp', bold=True, color=(1,1,1,1)))
        btn_cobrar.bind(on_press=self.procesar_pago)
        layout.add_widget(btn_cobrar)

        contenedor.add_widget(layout)
        self.add_widget(contenedor)
        self.cargar_pestanas_categories()

    def aplicar_descuento(self, *args):
        if self.total > 0:
            total_desc = self.total * 0.90
            from kivy.uix.popup import Popup
            Popup(title="Cotización (10% Desc.)", content=Label(text=f"Total: ${total_desc:.2f}"), size_hint=(0.7, 0.3)).open()

    def cargar_pestanas_categories(self):
        self.grid_pestanas.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT categoria FROM inventario ORDER BY categoria ASC")
        cats = cursor.fetchall()
        conn.close()
        primer_cat = ""
        for i, c in enumerate(cats):
            cat_nombre = c[0]
            if i == 0: primer_cat = cat_nombre
            btn_cat = BotonContornoLimpio(size_hint_x=None, width=135, radius=[12])
            btn_cat.add_widget(Label(text=cat_nombre, font_size='13sp', bold=True, color=COLOR_TEXT_DARK))
            btn_cat.bind(on_press=lambda x, cn=cat_nombre: self.seleccionar_categoria(cn))
            self.grid_pestanas.add_widget(btn_cat)
        if primer_cat: self.seleccionar_categoria(primer_cat)

    def seleccionar_categoria(self, cat_nombre):
        self.grid_catalogo.clear_widgets()
        self.categoria_actual = cat_nombre
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, variante, precio, stock FROM inventario WHERE categoria = ? ORDER BY nombre ASC, variante ASC", (cat_nombre,))
        productos = cursor.fetchall()
        conn.close()
        for p in productos:
            p_id, p_nom, p_var, p_pre, p_stk = p
            if p_stk <= 0:
                texto_boton = f"{p_nom} ({p_var})\n[SIN STOCK]"
                t_color = COLOR_TEXT_MUTED
                es_valido = False
            else:
                texto_boton = f"{p_nom} ({p_var})\n${p_pre:.2f}"
                t_color = COLOR_TEXT_DARK
                es_valido = True
            btn_prod = BotonContornoLimpio(size_hint_y=None, height=68, radius=[14])
            if not es_valido: btn_prod.disabled = True
            btn_prod.add_widget(Label(text=texto_boton, font_size='13sp', bold=True, halign='center', color=t_color))
            btn_prod.bind(on_press=lambda x, prod=p: self.agregar_al_carrito_visual(prod))
            self.grid_catalogo.add_widget(btn_prod)

    def agregar_al_carrito_visual(self, prod):
        p_id, p_nom, p_var, p_pre, p_stk = prod
        for item in self.carrito:
            if item['id'] == p_id and item['var'] == p_var:
                if item['cant'] < p_stk:
                    item['cant'] += 1
                    item['subt'] = item['cant'] * p_pre
                    self.actualizar_vista_carrito()
                return
        self.carrito.append({'id': p_id, 'nom': p_nom, 'var': p_var, 'pre': p_pre, 'cant': 1, 'subt': p_pre, 'max_stk': p_stk})
        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        self.grid_carrito.clear_widgets()
        self.total = 0.0
        for item in self.carrito:
            self.total += item['subt']
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=52, spacing=6)
            lbl = Label(text=f"({item['cant']}) {item['nom']} [{item['var']}]\n${item['subt']:.2f}", size_hint_x=0.70, font_size='11sp', bold=True, color=COLOR_TEXT_DARK)
            btn_del = BotonContornoLimpio(size_hint_x=None, width=44, radius=[8])
            btn_del.add_widget(Label(text=ICON_MENOS, font_size='14sp', color=COLOR_TEXT_DARK))
            btn_del.bind(on_press=lambda x, i=item: self.restar_del_carrito(i))
            row.add_widget(lbl); row.add_widget(btn_del)
            self.grid_carrito.add_widget(row)
        self.lbl_total.text = f"${self.total:.2f}"

    def restar_del_carrito(self, item):
        item['cant'] -= 1
        if item['cant'] <= 0: self.carrito.remove(item)
        else: item['subt'] = item['cant'] * item['pre']
        self.actualizar_vista_carrito()

    def procesar_pago(self, instance):
        if not self.carrito: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?,?)", (fecha, self.total))
        for item in self.carrito:
            nuevo_stock = max(0, item['max_stk'] - item['cant'])
            cursor.execute("UPDATE inventario SET stock = ? WHERE id = ? AND variante = ?", (nuevo_stock, item['id'], item['var']))
            if nuevo_stock < 4: lanzar_alerta_nativa(item['nom'], item['var'], nuevo_stock)
        conn.commit(); conn.close()
        self.carrito = []
        self.actualizar_vista_carrito()
        self.lbl_total.text = "REGISTRADO"
        Clock.schedule_once(lambda dt: self.seleccionar_categoria(self.categoria_actual), 1.0)

class PantallaInventario(Screen):
    def on_enter(self):
        self.datos_nuevo_prod = {}
        self.mostrar_vista_principal()

    def mostrar_vista_principal(self):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        self.layout_base = BoxLayout(orientation='vertical', padding=24, spacing=14)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=12)
        btn_volver = BotonContornoLimpio(size_hint_x=0.32, radius=[14])
        box_vol = BoxLayout(orientation='horizontal', padding=[6,0,6,0], spacing=4)
        box_vol.add_widget(Label(text=ICON_VOLVER, font_size='13sp', bold=True, color=COLOR_TEXT_DARK))
        btn_volver.add_widget(box_vol)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        header.add_widget(btn_volver)
        header.add_widget(Label(text="ALMACÉN E INVENTARIO", font_size='18sp', bold=True, color=(1,1,1,1)))
        self.layout_base.add_widget(header)

        btn_abrir_formulario = BotonSolidoNegro(size_hint_y=0.10, radius=[18])
        box_form = BoxLayout(orientation='horizontal', padding=[20,0,20,0], spacing=8)
        box_form.add_widget(Label(text=ICON_MAS, font_size='14sp', bold=True, color=(1,1,1,1), size_hint_x=0.15))
        box_form.add_widget(Label(text="REGISTRAR ARTÍCULO NUEVO", font_size='14sp', bold=True, color=(1,1,1,1)))
        btn_abrir_formulario.add_widget(box_form)
        btn_abrir_formulario.bind(on_press=self.seleccionar_categoria_registro)
        self.layout_base.add_widget(btn_abrir_formulario)

        self.txt_buscar = TextInput(hint_text="🔍 Buscar por nombre, variante...", multiline=False, size_hint_y=0.08)
        self.txt_buscar.bind(text=self.filtrar_busqueda)
        self.layout_base.add_widget(self.txt_buscar)

        self.scroll = ScrollView(size_hint=(1, 0.67))
        self.grid_productos = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid_productos.bind(minimum_height=self.grid_productos.setter('height'))
        self.cargar_tabla()
        self.scroll.add_widget(self.grid_productos)
        self.layout_base.add_widget(self.scroll)
        contenedor.add_widget(self.layout_base)
        self.add_widget(contenedor)

    def filtrar_busqueda(self, instance, texto_busqueda):
        self.cargar_tabla(filtro=texto_busqueda.strip())

    def cargar_tabla(self, filtro=""):
        self.grid_productos.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT id, categoria, nombre, variante, stock FROM inventario WHERE nombre LIKE ? OR variante LIKE ? ORDER BY nombre ASC", (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT id, categoria, nombre, variante, stock FROM inventario ORDER BY nombre ASC")
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            p_id, p_cat, p_nom, p_var, p_stk = r
            fila = TarjetaContenedorBlanca(orientation='horizontal', size_hint_y=None, height=76, padding=[12, 8, 12, 8], radius=[14])
            box_info = BoxLayout(orientation='vertical', size_hint_x=0.48)
            box_info.add_widget(Label(text=p_nom, font_size='14sp', bold=True, color=COLOR_TEXT_DARK, halign='left'))
            box_info.add_widget(Label(text=f"[ {p_var} ] • {p_cat.lower()}", font_size='11sp', color=COLOR_TEXT_MUTED, halign='left'))
            fila.add_widget(box_info)
            
            color_stock = (0.9, 0.2, 0.2, 1) if p_stk < 4 else COLOR_TEXT_DARK
            fila.add_widget(Label(text=f"{p_stk}", size_hint_x=0.12, font_size='16sp', bold=True, color=color_stock))
            
            btns = BoxLayout(orientation='horizontal', size_hint_x=0.40, spacing=6)
            b_menos = BotonContornoLimpio(radius=[8])
            b_menos.add_widget(Label(text=ICON_MENOS, color=COLOR_TEXT_DARK))
            b_menos.bind(on_press=lambda x, i=p_id, v=p_var: self.modificar_stock(i, v, -1))
            b_mas = BotonContornoLimpio(radius=[8])
            b_mas.add_widget(Label(text=ICON_MAS, color=COLOR_TEXT_DARK))
            b_mas.bind(on_press=lambda x, i=p_id, v=p_var: self.modificar_stock(i, v, 1))
            b_eliminar = BotonContornoLimpio(radius=[8])
            b_eliminar.add_widget(Label(text=ICON_ELIMINAR, color=(0.85, 0.15, 0.15, 1)))
            b_eliminar.bind(on_press=lambda x, i=p_id, v=p_var: self.eliminar_producto_definitivo(i, v))
            
            btns.add_widget(b_menos); btns.add_widget(b_mas); btns.add_widget(b_eliminar)
            fila.add_widget(btns)
            self.grid_productos.add_widget(fila)

    def modificar_stock(self, p_id, p_var, cantidad):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE inventario SET stock = max(0, stock + ?) WHERE id = ? AND variante = ?", (cantidad, p_id, p_var))
        conn.commit(); conn.close()
        self.cargar_tabla(filtro=self.txt_buscar.text.strip())

    def eliminar_producto_definitivo(self, p_id, p_var):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario WHERE id = ? AND variante = ?", (p_id, p_var))
        conn.commit(); conn.close()
        self.cargar_tabla()

    def seleccionar_categoria_registro(self, *args):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        layout_sel = BoxLayout(orientation='vertical', padding=25, spacing=16)
        layout_sel.add_widget(Label(text="SECCIÓN DEL ARTÍCULO", font_size='20sp', bold=True, size_hint_y=0.08, color=(1, 1, 1, 1)))
        scroll_cats = ScrollView(size_hint=(1, 0.58))
        grid_cats = GridLayout(cols=1, size_hint_y=None, spacing=10)
        grid_cats.bind(minimum_height=grid_cats.setter('height'))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT categoria FROM inventario ORDER BY categoria ASC")
        categorias = [c[0] for c in cursor.fetchall()]
        conn.close()
        for cat in categorias:
            btn_cat = BotonContornoLimpio(size_hint_y=None, height=52, radius=[12])
            btn_cat.add_widget(Label(text=cat, font_size='14sp', bold=True, color=COLOR_TEXT_DARK))
            btn_cat.bind(on_press=lambda x, c=cat: self.guardar_categoria_y_continuar(c))
            grid_cats.add_widget(btn_cat)
        scroll_cats.add_widget(grid_cats)
        layout_sel.add_widget(scroll_cats)
        
        btn_nueva_cat = BotonSolidoNegro(size_hint_y=0.10, radius=[18])
        box_ncat = BoxLayout(orientation='horizontal', padding=[20,0,20,0])
        box_ncat.add_widget(Label(text="CREAR NUEVA SECCIÓN", font_size='14sp', bold=True, color=(1,1,1,1)))
        btn_nueva_cat.add_widget(box_ncat)
        btn_nueva_cat.bind(on_press=lambda x: self.mostrar_formulario_secuencial('categoria', "Escribe la nueva categoría:", None))
        layout_sel.add_widget(btn_nueva_cat)
        
        btn_cancelar = BotonContornoLimpio(size_hint_y=0.08, radius=[12])
        btn_cancelar.add_widget(Label(text="Cancelar", color=COLOR_TEXT_DARK))
        btn_cancelar.bind(on_press=lambda x: self.mostrar_vista_principal())
        layout_sel.add_widget(btn_cancelar)
        contenedor.add_widget(layout_sel)
        self.add_widget(contenedor)

    def guardar_categoria_y_continuar(self, categoria_seleccionada):
        self.datos_nuevo_prod['categoria'] = categoria_seleccionada
        self.mostrar_formulario_secuencial('nombre', f"Sección: {categoria_seleccionada}\n\nNombre del Artículo:", 'categoria_seleccionada')

    def mostrar_formulario_secuencial(self, campo_actual, texto_instruccion, campo_anterior):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        layout_form = BoxLayout(orientation='vertical', padding=25, spacing=20)
        layout_form.add_widget(Label(text="NUEVO REGISTRO", font_size='20sp', bold=True, size_hint_y=0.08, color=(1,1,1,1)))
        inst_card = TarjetaContenedorBlanca(size_hint_y=0.18, padding=12, radius=[16])
        inst_card.add_widget(Label(text=texto_instruccion, font_size='14sp', bold=True, color=COLOR_TEXT_DARK))
        layout_form.add_widget(inst_card)
        
        in_txt = TextInput(text=str(self.datos_nuevo_prod.get(campo_actual, "")), multiline=False, size_hint_y=0.12)
        layout_form.add_widget(in_txt)
        
        fila_acciones = BoxLayout(orientation='horizontal', size_hint_y=0.10, spacing=12)
        if campo_anterior is not None:
            btn_atras_paso = BotonContornoLimpio(radius=[18], size_hint_x=0.4)
            btn_atras_paso.add_widget(Label(text="< Volver", color=COLOR_TEXT_DARK))
            def regresar_un_paso(obj):
                if campo_anterior == 'categoria_seleccionada': self.seleccionar_categoria_registro()
                elif campo_anterior == 'categoria': self.mostrar_formulario_secuencial('categoria', "Escribe la nueva categoría:", None)
                elif campo_anterior == 'nombre': self.mostrar_formulario_secuencial('nombre', f"Sección: {self.datos_nuevo_prod['categoria']}\n\nNombre:", 'categoria_seleccionada')
                elif campo_anterior == 'variante': self.mostrar_formulario_secuencial('variante', "Variante / Modelo:", 'nombre')
                elif campo_anterior == 'precio': self.mostrar_formulario_secuencial('precio', "Precio de Venta:", 'variante')
            btn_atras_paso.bind(on_press=regresar_un_paso)
            fila_acciones.add_widget(btn_atras_paso)

        btn_accion = BotonSolidoNegro(radius=[18]) if campo_actual == 'stock' else BotonContornoLimpio(radius=[18])
        btn_accion.add_widget(Label(text="FINALIZAR" if campo_actual == 'stock' else "Siguiente ➡️", color=(1,1,1,1) if campo_actual == 'stock' else COLOR_TEXT_DARK))
        fila_acciones.add_widget(btn_accion)
        layout_form.add_widget(fila_acciones)
        
        btn_cancelar = BotonContornoLimpio(size_hint_y=0.08, radius=[12])
        btn_cancelar.add_widget(Label(text="Cancelar", color=COLOR_TEXT_DARK))
        btn_cancelar.bind(on_press=lambda x: self.mostrar_vista_principal())
        layout_form.add_widget(btn_cancelar)
        layout_form.add_widget(Label(size_hint_y=0.24))
        
        def procesar_paso(obj):
            val = in_txt.text.strip()
            if not val: return
            if campo_actual == 'categoria':
                self.datos_nuevo_prod[campo_actual] = val.upper()
                self.mostrar_formulario_secuencial('nombre', f"Sección: {val.upper()}\n\nNombre del Artículo:", 'categoria')
            elif campo_actual == 'nombre':
                self.datos_nuevo_prod[campo_actual] = val
                self.mostrar_formulario_secuencial('variante', "Define la Variante / Modelo:", 'nombre')
            elif campo_actual == 'variante':
                self.datos_nuevo_prod[campo_actual] = val
                self.mostrar_formulario_secuencial('precio', "Precio de Venta:", 'variante')
            elif campo_actual == 'precio':
                self.datos_nuevo_prod[campo_actual] = val
                self.mostrar_formulario_secuencial('stock', "Cantidad en Almacén:", 'precio')
            elif campo_actual == 'stock':
                try:
                    id_auto = f"{self.datos_nuevo_prod['nombre'].replace(' ','')}".lower()
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?)", (id_auto, self.datos_nuevo_prod['categoria'], self.datos_nuevo_prod['nombre'], self.datos_nuevo_prod['variante'], float(self.datos_nuevo_prod['precio']), int(val)))
                    conn.commit(); conn.close()
                except: pass
                self.mostrar_vista_principal()
        btn_accion.bind(on_press=procesar_paso)
        contenedor.add_widget(layout_form)
        self.add_widget(contenedor)

# --- 🚀 AQUÍ ESTÁ EL TRUCO MAGNO PARA MOSTRAR Y RESTAR LOS GASTOS ---
class PantallaCorte(Screen):
    def on_enter(self):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        layout_principal = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        btn_volver = BotonContornoLimpio(size_hint_y=0.07, radius=[12])
        box_vol = BoxLayout(orientation='horizontal', padding=[14,0,14,0])
        box_vol.add_widget(Label(text=ICON_VOLVER, font_size='14sp', bold=True, color=COLOR_TEXT_DARK))
        btn_volver.add_widget(box_vol)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout_principal.add_widget(btn_volver)

        # Cargar Ventas y Gastos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, total FROM ventas ORDER BY id DESC")
        ventas = cursor.fetchall()
        cursor.execute("SELECT id, descripcion, monto, fecha FROM gastos ORDER BY id DESC")
        gastos = cursor.fetchall()
        conn.close()
        
        sum_ventas = sum(v[2] for v in ventas)
        sum_gastos = sum(g[2] for g in gastos)
        ganancia_neta = sum_ventas - sum_gastos
        lista_totales = [float(v[2]) for v in reversed(ventas)]

        # Tarjeta de finanzas nítida
        caja_card = TarjetaContenedorBlanca(orientation='vertical', size_hint_y=0.22, padding=10, radius=[18])
        caja_card.add_widget(Label(text=" GANANCIA NETA REAL (INGRESOS - GASTOS)", font_size='11sp', bold=True, color=COLOR_TEXT_MUTED))
        caja_card.add_widget(Label(text=f"${ganancia_neta:.2f}", font_size='34sp', bold=True, color=COLOR_TEXT_DARK))
        caja_card.add_widget(Label(text=f"Total Ventas (+): ${sum_ventas:.2f}  |  Total Gastos (-): ${sum_gastos:.2f}", font_size='12sp', color=COLOR_TEXT_MUTED))
        layout_principal.add_widget(caja_card)

        # Gráfica visual de ventas
        grafica_card = TarjetaContenedorBlanca(orientation='vertical', size_hint_y=0.18, padding=[10, 4, 10, 4], radius=[18])
        grafica_card.add_widget(GraficaBarrasVentas(datos_ventas=lista_totales, size_hint_y=1))
        layout_principal.add_widget(grafica_card)

        # Botón para reiniciar caja y gastos
        btn_vaciar = BotonContornoLimpio(size_hint_y=0.06, radius=[10])
        btn_vaciar.add_widget(Label(text="Reiniciar historial total (Caja y Gastos)", font_size='13sp', color=COLOR_TEXT_DARK))
        btn_vaciar.bind(on_press=self.borrar_todo_historial)
        layout_principal.add_widget(btn_vaciar)

        # Paneles de listas deslizables (Ventas y Gastos lado a lado)
        listas_box = BoxLayout(orientation='horizontal', size_hint_y=0.47, spacing=10)
        
        # Lado izquierdo: Ventas
        v_box = TarjetaContenedorBlanca(orientation='vertical', padding=8, radius=[14])
        v_box.add_widget(Label(text="🛒 INGRESOS (VENTAS)", font_size='12sp', bold=True, color=COLOR_TEXT_DARK, size_hint_y=0.12))
        scroll_v = ScrollView()
        grid_v = GridLayout(cols=1, size_hint_y=None, spacing=6)
        grid_v.bind(minimum_height=grid_v.setter('height'))
        for v in ventas:
            grid_v.add_widget(Label(text=f"Venta #{v[0]} -> +${v[2]:.2f}", font_size='12sp', color=(0.1, 0.6, 0.1, 1), size_hint_y=None, height=30))
        scroll_v.add_widget(grid_v)
        v_box.add_widget(scroll_v)
        
        # Lado derecho: Gastos (¡Aquí se ven!)
        g_box = TarjetaContenedorBlanca(orientation='vertical', padding=8, radius=[14])
        g_box.add_widget(Label(text="💸 SALIDAS (GASTOS)", font_size='12sp', bold=True, color=COLOR_TEXT_DARK, size_hint_y=0.12))
        scroll_g = ScrollView()
        grid_g = GridLayout(cols=1, size_hint_y=None, spacing=6)
        grid_g.bind(minimum_height=grid_g.setter('height'))
        for g in gastos:
            grid_g.add_widget(Label(text=f"{g[1]} -> -${g[2]:.2f}", font_size='12sp', color=(0.8, 0.1, 0.1, 1), size_hint_y=None, height=30))
        scroll_g.add_widget(grid_g)
        g_box.add_widget(scroll_g)
        
        listas_box.add_widget(v_box)
        listas_box.add_widget(g_box)
        layout_principal.add_widget(listas_box)

        contenedor.add_widget(layout_principal)
        self.add_widget(contenedor)

    def borrar_todo_historial(self, instance):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ventas")
        cursor.execute("DELETE FROM gastos")
        conn.commit(); conn.close()
        self.on_enter()

class PantallaGastos(Screen):
    def on_enter(self):
        self.clear_widgets()
        contenedor = FondoOndaDecorativa()
        layout = BoxLayout(orientation='vertical', padding=24, spacing=16)
        
        btn_volver = BotonContornoLimpio(size_hint_y=0.08, radius=[12])
        btn_volver.add_widget(Label(text=ICON_VOLVER, color=COLOR_TEXT_DARK, bold=True))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_volver)
        
        layout.add_widget(Label(text="REGISTRO DE GASTOS", font_size='22sp', bold=True, color=(1,1,1,1)))
        
        self.txt_desc = TextInput(hint_text="¿En qué se gastó? (Ej: Luz, Mercancía, Limpieza)", multiline=False, size_hint_y=0.12)
        self.txt_monto = TextInput(hint_text="Monto gastado ($)", multiline=False, input_filter='float', size_hint_y=0.12)
        
        btn_guardar = BotonSolidoNegro(size_hint_y=0.12, radius=[18])
        btn_guardar.add_widget(Label(text="💥 REGISTRAR Y DESCONTAR GASTO", color=(1,1,1,1), bold=True))
        btn_guardar.bind(on_press=self.guardar_gasto)
        
        layout.add_widget(self.txt_desc)
        layout.add_widget(self.txt_monto)
        layout.add_widget(btn_guardar)
        layout.add_widget(Label(size_hint_y=0.3))
        
        contenedor.add_widget(layout)
        self.add_widget(contenedor)

    def guardar_gasto(self, *args):
        if self.txt_desc.text.strip() and self.txt_monto.text.strip():
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO gastos (descripcion, monto, fecha) VALUES (?,?,?)", 
                         (self.txt_desc.text.strip().upper(), float(self.txt_monto.text.strip()), datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            self.manager.current = 'menu'

class PapeleriaApp(App):
    title = "Mi Papeleria"
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (1, 1, 1, 1)
        try: inicializar_db()
        except Exception as e: print(f"Error en DB: {e}")
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PantallaPortada(name='portada'))
        sm.add_widget(PantallaMenu(name='menu'))
        sm.add_widget(PantallaCaja(name='caja'))
        sm.add_widget(PantallaInventario(name='inventario'))
        sm.add_widget(PantallaCorte(name='corte'))
        sm.add_widget(PantallaGastos(name='gastos')) 
        sm.current = 'portada'
        return sm

if __name__ == '__main__':
    PapeleriaApp().run()
