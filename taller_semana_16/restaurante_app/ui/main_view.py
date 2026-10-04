import os
import tkinter as tk
from tkinter import ttk, messagebox          # se agrega messagebox para confirmar eliminación
from PIL import Image, ImageTk
from servicios.restaurante_servicio import RestauranteServicio
from modelos.usuario import ROLES_VALIDOS    # se agrega

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ASSETS = os.path.join(BASE_DIR, "assets")

# Paleta basada en el logo
COLOR_FONDO = "#FDF8F2"
COLOR_CAFE = "#33160F"
COLOR_CAFE_BOTON = "#45261C"
COLOR_NARANJA = "#F37901"
COLOR_NARANJA_HOVER = "#D96A00"
COLOR_ROJO = "#C0392B"
COLOR_ROJO_HOVER = "#992D22"
COLOR_DORADO = "#B9770E"
COLOR_DORADO_HOVER = "#96600B"
COLOR_CAFE_CLARO = "#6D4C41"
COLOR_CAFE_CLARO_HOVER = "#54382F"
COLOR_BARRA_ESTADO = "#F5E6D3"
COLOR_SIDEBAR = "#7B4A36"
COLOR_SIDEBAR_BOTON = "#65392A"
COLOR_CREMA = "#F5EFE5"

# Vista principal del sistema, visible tras un acceso correcto
class MainView(ttk.Frame):
    def __init__(self, contenedor: tk.Tk, servicio: RestauranteServicio, nombre_usuario: str, al_cerrar_sesion):
        super().__init__(contenedor)
        self.servicio = servicio
        self.nombre_usuario = nombre_usuario
        self.usuario_actual = servicio.buscar_usuario_por_nombre(nombre_usuario)  # NUEVO
        self.al_cerrar_sesion = al_cerrar_sesion

        self.panel_contenido: ttk.Frame | None = None
        self._iconos: dict[str, ImageTk.PhotoImage] = {}  # referencias vivas de las imágenes
        self._botones_nav: dict[str, tk.Button] = {}
        self._imagen_logo_sidebar = None
        self._imagen_logo_inicio = None

        self._construir_estructura()
        self._mostrar_seccion_inicio()

    # ===== RECURSOS (assets) =====

    # Carga un ícono de assets/icons y conserva la referencia para que Tkinter no lo elimine
    def _cargar_icono(self, nombre: str) -> ImageTk.PhotoImage | None:
        ruta = os.path.join(RUTA_ASSETS, "icons", f"{nombre}.png")
        if not os.path.exists(ruta):
            return None
        if nombre not in self._iconos:
            self._iconos[nombre] = ImageTk.PhotoImage(Image.open(ruta))
        return self._iconos[nombre]

    # Carga el logo redimensionado al tamaño máximo indicado
    def _cargar_logo(self, tamano: int) -> ImageTk.PhotoImage | None:
        ruta = os.path.join(RUTA_ASSETS, "logo", "logo.png")
        if not os.path.exists(ruta):
            return None
        imagen = Image.open(ruta)
        imagen.thumbnail((tamano, tamano))
        return ImageTk.PhotoImage(imagen)

    # ===== ESTRUCTURA GENERAL: SIDEBAR + CONTENIDO + BARRA DE ESTADO =====

    def _construir_estructura(self) -> None:
        self.pack(fill="both", expand=True)

        # La barra de estado se empaqueta primero para que siempre quede visible abajo
        self._construir_barra_estado()

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)

        self._construir_sidebar(cuerpo)

        self.contenedor_contenido = ttk.Frame(cuerpo, padding=20)
        self.contenedor_contenido.pack(side="left", fill="both", expand=True)

    def _construir_sidebar(self, cuerpo: ttk.Frame) -> None:
        sidebar = tk.Frame(cuerpo, bg=COLOR_SIDEBAR, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo sobre un recuadro crema para que sus contornos oscuros resalten
        self._imagen_logo_sidebar = self._cargar_logo(80)
        if self._imagen_logo_sidebar:
            recuadro_logo = tk.Frame(sidebar, bg=COLOR_CREMA)
            recuadro_logo.pack(pady=(20, 8), padx=15, fill="x")
            tk.Label(recuadro_logo, image=self._imagen_logo_sidebar, bg=COLOR_CREMA).pack(pady=8)

        tk.Label(sidebar, text="RESTAURANTE", bg=COLOR_SIDEBAR, fg="white",
                 font=("Segoe UI", 12, "bold")).pack()
        tk.Label(sidebar, text=self.nombre_usuario, bg=COLOR_SIDEBAR, fg="#F5E6D3",
                 font=("Segoe UI", 9)).pack(pady=(0, 20))

        self._boton_sidebar(sidebar, "Inicio", "home", self._mostrar_seccion_inicio)
        self._boton_sidebar(sidebar, "Usuarios", "usuarios", self._mostrar_seccion_usuarios)
        self._boton_sidebar(sidebar, "Productos", "productos", self._mostrar_seccion_productos)
        self._boton_sidebar(sidebar, "Ventas", "ventas", self._mostrar_seccion_ventas)

        # Espaciador para empujar "Cerrar sesión" al fondo
        tk.Frame(sidebar, bg=COLOR_SIDEBAR).pack(fill="both", expand=True)

        tk.Button(
            sidebar, text=" Cerrar sesión", image=self._cargar_icono("logout"), compound="left",
            command=self.al_cerrar_sesion, bg=COLOR_ROJO, fg="white",
            activebackground=COLOR_ROJO_HOVER, activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2"
        ).pack(fill="x", padx=15, pady=20, ipady=6)

    # Crea un botón de navegación con ícono y estilo consistente
    def _boton_sidebar(self, sidebar: tk.Frame, texto: str, icono: str, comando) -> None:
        boton = tk.Button(
            sidebar, text=f"  {texto}", image=self._cargar_icono(icono), compound="left",
            command=comando, bg=COLOR_SIDEBAR_BOTON, fg="white",      # antes COLOR_CAFE_BOTON
            activebackground=COLOR_NARANJA, activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", anchor="w", padx=12, cursor="hand2"
        )
        boton.pack(fill="x", padx=15, pady=4, ipady=8)
        self._botones_nav[texto] = boton

    def _marcar_activo(self, seccion: str) -> None:
        for nombre, boton in self._botones_nav.items():
            boton.config(bg=COLOR_NARANJA if nombre == seccion else COLOR_SIDEBAR_BOTON)

    def _construir_barra_estado(self) -> None:
        self.barra_estado = tk.Label(
            self, text="", bg=COLOR_BARRA_ESTADO, fg=COLOR_CAFE,
            font=("Segoe UI", 9), anchor="w", padx=10
        )
        self.barra_estado.pack(fill="x", side="bottom", ipady=4)
        self._actualizar_barra_estado()

    def _actualizar_barra_estado(self) -> None:
        self.barra_estado.config(
            text=(f"Productos: {len(self.servicio.listar_productos())}  |  "
                  f"Usuarios: {len(self.servicio.listar_usuarios())}  |  "
                  f"Ventas: {len(self.servicio.listar_ventas())}  |  Datos JSON locales")
        )

    # Prepara el panel central para mostrar una nueva sección
    def _preparar_seccion(self, nombre_nav: str, titulo: str) -> ttk.Frame:
        if self.panel_contenido is not None:
            self.panel_contenido.destroy()
        self.panel_contenido = ttk.Frame(self.contenedor_contenido)
        self.panel_contenido.pack(fill="both", expand=True)
        self._marcar_activo(nombre_nav)
        ttk.Label(self.panel_contenido, text=titulo, style="Titulo.TLabel").pack(anchor="w", pady=(0, 10))
        self._actualizar_barra_estado()
        return self.panel_contenido

    # Crea un botón de acción de color, con ícono y texto
    def _boton_accion(self, padre, texto: str, icono: str, color: str, color_hover: str, comando) -> None:
        tk.Button(
            padre, text=f"  {texto}", image=self._cargar_icono(icono), compound="left",
            command=comando, bg=color, fg="white",
            activebackground=color_hover, activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2"
        ).pack(fill="x", pady=3, ipady=5)

    # ===== SECCIÓN INICIO =====

    def _mostrar_seccion_inicio(self) -> None:
        panel = self._preparar_seccion("Inicio", "Inicio")

        centro = ttk.Frame(panel)
        centro.pack(expand=True)

        self._imagen_logo_inicio = self._cargar_logo(220)
        if self._imagen_logo_inicio:
            ttk.Label(centro, image=self._imagen_logo_inicio).pack(pady=(0, 15))

        ttk.Label(centro, text=f"Bienvenido, {self.nombre_usuario}", style="Titulo.TLabel").pack()
        ttk.Label(centro, text="Utilice el menú lateral para consultar usuarios, gestionar productos y registrar ventas."
                  ).pack(pady=(8, 0))

    # ===== SECCIÓN USUARIOS =====

    def _mostrar_seccion_usuarios(self) -> None:
        panel = self._preparar_seccion("Usuarios", "Gestión de usuarios")

        if self.usuario_actual is not None and self.usuario_actual.es_administrador():
            self._mostrar_usuarios_administrador(panel)
        else:
            self._mostrar_usuarios_solo_lectura(panel)

    # Vista de solo lectura para roles Empleado y Cliente
    def _mostrar_usuarios_solo_lectura(self, panel: ttk.Frame) -> None:
        ttk.Label(panel, text="Solo un Administrador puede gestionar usuarios.",
                  foreground="#8a5a44").pack(anchor="w", pady=(0, 10))

        marco = ttk.LabelFrame(panel, text="Usuarios registrados", padding=8)
        marco.pack(fill="both", expand=True)

        tabla = ttk.Treeview(marco, columns=("id", "nombre", "correo", "rol"), show="headings")
        for col, texto, ancho in [("id", "ID", 50), ("nombre", "Nombre", 160),
                                   ("correo", "Correo", 220), ("rol", "Rol", 110)]:
            tabla.heading(col, text=texto)
            tabla.column(col, width=ancho, anchor="center" if col in ("id", "rol") else "w")
        tabla.pack(fill="both", expand=True)

        for usuario in self.servicio.listar_usuarios():
            tabla.insert("", tk.END, values=(usuario.id_usuario, usuario.nombre, usuario.correo, usuario.rol))

    # Vista completa de gestión (CRUD + eventos), solo para Administrador
    def _mostrar_usuarios_administrador(self, panel: ttk.Frame) -> None:
        cuerpo = ttk.Frame(panel)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        self._construir_formulario_usuario(cuerpo)
        self._construir_tabla_usuarios(cuerpo)
        self._cargar_tabla_usuarios()

    # Construye el formulario de usuario, con sus botones (command=) y atajos de teclado (bind)
    def _construir_formulario_usuario(self, cuerpo: ttk.Frame) -> None:
        formulario = ttk.LabelFrame(cuerpo, text="Datos del usuario", padding=10)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        campos = ttk.Frame(formulario)
        campos.pack(fill="x", pady=(0, 10))

        ttk.Label(campos, text="ID").grid(row=0, column=0, sticky="w", pady=5)
        self.entrada_id_usuario = ttk.Entry(campos, width=18)
        self.entrada_id_usuario.grid(row=0, column=1, pady=5)

        ttk.Label(campos, text="Nombre").grid(row=1, column=0, sticky="w", pady=5)
        self.entrada_nombre_usuario = ttk.Entry(campos, width=18)
        self.entrada_nombre_usuario.grid(row=1, column=1, pady=5)

        ttk.Label(campos, text="Correo").grid(row=2, column=0, sticky="w", pady=5)
        self.entrada_correo_usuario = ttk.Entry(campos, width=18)
        self.entrada_correo_usuario.grid(row=2, column=1, pady=5)

        ttk.Label(campos, text="Contraseña").grid(row=3, column=0, sticky="w", pady=5)
        self.entrada_contrasena_usuario = ttk.Entry(campos, width=18)
        self.entrada_contrasena_usuario.grid(row=3, column=1, pady=5)

        ttk.Label(campos, text="Rol").grid(row=4, column=0, sticky="w", pady=5)
        self.combo_rol_usuario = ttk.Combobox(campos, values=ROLES_VALIDOS, state="readonly", width=16)
        self.combo_rol_usuario.grid(row=4, column=1, pady=5)

        self._boton_accion(formulario, "Registrar", "agregar", COLOR_NARANJA, COLOR_NARANJA_HOVER, self._registrar_usuario)
        self._boton_accion(formulario, "Actualizar", "editar", COLOR_DORADO, COLOR_DORADO_HOVER, self._actualizar_usuario)
        self._boton_accion(formulario, "Eliminar", "eliminar", COLOR_ROJO, COLOR_ROJO_HOVER, self._eliminar_usuario)
        self._boton_accion(formulario, "Limpiar", "limpiar", COLOR_CAFE_CLARO, COLOR_CAFE_CLARO_HOVER, self._limpiar_formulario_usuario)

        self.etiqueta_mensaje_usuario = ttk.Label(formulario, text="", foreground=COLOR_ROJO, wraplength=220)
        self.etiqueta_mensaje_usuario.pack(anchor="w", pady=(8, 0))

        # ----- EVENTOS (bind): <Return> confirma el registro, <Escape> limpia el formulario -----
        for widget in (self.entrada_id_usuario, self.entrada_nombre_usuario, self.entrada_correo_usuario,
                       self.entrada_contrasena_usuario, self.combo_rol_usuario):
            widget.bind("<Return>", self._callback_return_usuario)
            widget.bind("<Escape>", self._callback_escape_usuario)

        # ----- EVENTO (bind): <<ComboboxSelected>> responde al cambio de rol -----
        self.combo_rol_usuario.bind("<<ComboboxSelected>>", self._callback_cambio_rol)

    # Construye la tabla de usuarios y asocia el evento de selección
    def _construir_tabla_usuarios(self, cuerpo: ttk.Frame) -> None:
        marco = ttk.LabelFrame(cuerpo, text="Usuarios registrados", padding=8)
        marco.grid(row=0, column=1, sticky="nsew")

        self.tabla_usuarios = ttk.Treeview(marco, columns=("id", "nombre", "correo", "rol"), show="headings")
        for col, texto, ancho in [("id", "ID", 50), ("nombre", "Nombre", 140),
                                   ("correo", "Correo", 190), ("rol", "Rol", 100)]:
            self.tabla_usuarios.heading(col, text=texto)
            self.tabla_usuarios.column(col, width=ancho, anchor="center" if col in ("id", "rol") else "w")
        self.tabla_usuarios.pack(fill="both", expand=True)

        # ----- EVENTO (bind): <<TreeviewSelect>> carga la fila seleccionada en el formulario -----
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self._callback_seleccionar_usuario)
        # ----- EVENTO (bind): <Escape> también funciona con el foco en la tabla -----
        self.tabla_usuarios.bind("<Escape>", self._callback_escape_usuario)

    def _cargar_tabla_usuarios(self) -> None:
        self.tabla_usuarios.delete(*self.tabla_usuarios.get_children())
        for usuario in sorted(self.servicio.listar_usuarios(), key=lambda u: u.id_usuario):
            self.tabla_usuarios.insert("", tk.END, values=(
                usuario.id_usuario, usuario.nombre, usuario.correo, usuario.rol
            ))

    def _limpiar_formulario_usuario(self) -> None:
        for entrada in (self.entrada_id_usuario, self.entrada_nombre_usuario,
                        self.entrada_correo_usuario, self.entrada_contrasena_usuario):
            entrada.delete(0, tk.END)
        self.combo_rol_usuario.set("")
        self.etiqueta_mensaje_usuario.config(text="", foreground=COLOR_ROJO)

    def _leer_id_usuario(self) -> int | None:
        try:
            return int(self.entrada_id_usuario.get().strip())
        except ValueError:
            self.etiqueta_mensaje_usuario.config(text="El ID debe ser un número entero.", foreground=COLOR_ROJO)
            return None

    # CALLBACK (command=): registra un nuevo usuario
    def _registrar_usuario(self) -> None:
        id_usuario = self._leer_id_usuario()
        if id_usuario is None:
            return
        try:
            nombre = self.entrada_nombre_usuario.get().strip()
            correo = self.entrada_correo_usuario.get().strip()
            contrasena = self.entrada_contrasena_usuario.get().strip()
            rol = self.combo_rol_usuario.get().strip()

            self.servicio.agregar_usuario(id_usuario, nombre, correo, contrasena, rol)
            self._cargar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            self._actualizar_barra_estado()
            self.etiqueta_mensaje_usuario.config(text=f"Usuario '{nombre}' registrado correctamente.", foreground="#27ae60")
        except ValueError as e:
            self.etiqueta_mensaje_usuario.config(text=str(e), foreground=COLOR_ROJO)

    # CALLBACK (command=): actualiza el usuario cargado en el formulario
    def _actualizar_usuario(self) -> None:
        id_usuario = self._leer_id_usuario()
        if id_usuario is None:
            return
        try:
            nombre = self.entrada_nombre_usuario.get().strip()
            correo = self.entrada_correo_usuario.get().strip()
            contrasena = self.entrada_contrasena_usuario.get().strip()
            rol = self.combo_rol_usuario.get().strip()

            if self.servicio.actualizar_usuario(id_usuario, nombre, correo, contrasena, rol):
                self._cargar_tabla_usuarios()
                self._actualizar_barra_estado()
                self.etiqueta_mensaje_usuario.config(text=f"Usuario {id_usuario} actualizado correctamente.", foreground="#27ae60")
            else:
                self.etiqueta_mensaje_usuario.config(text=f"No existe un usuario con el ID {id_usuario}.", foreground=COLOR_ROJO)
        except ValueError as e:
            self.etiqueta_mensaje_usuario.config(text=str(e), foreground=COLOR_ROJO)

    # CALLBACK (command=): elimina el usuario indicado, con confirmación previa
    def _eliminar_usuario(self) -> None:
        id_usuario = self._leer_id_usuario()
        if id_usuario is None:
            return

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Eliminar al usuario con ID {id_usuario}?")
        if not confirmar:
            return

        try:
            if self.servicio.eliminar_usuario(id_usuario, self.usuario_actual.id_usuario):
                self._cargar_tabla_usuarios()
                self._limpiar_formulario_usuario()
                self._actualizar_barra_estado()
                self.etiqueta_mensaje_usuario.config(text=f"Usuario {id_usuario} eliminado correctamente.", foreground="#27ae60")
            else:
                self.etiqueta_mensaje_usuario.config(text=f"No existe un usuario con el ID {id_usuario}.", foreground=COLOR_ROJO)
        except ValueError as e:
            self.etiqueta_mensaje_usuario.config(text=str(e), foreground=COLOR_ROJO)

    # CALLBACK (bind <<TreeviewSelect>>): carga en el formulario la fila seleccionada,
    # consultando el objeto completo mediante RestauranteServicio (la tabla solo guarda el ID visible).
    def _callback_seleccionar_usuario(self, event) -> None:
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            return
        valores = self.tabla_usuarios.item(seleccion[0], "values")
        id_usuario = int(valores[0])

        usuario = self.servicio.buscar_usuario(id_usuario)
        if usuario is None:
            return

        self.entrada_id_usuario.delete(0, tk.END)
        self.entrada_id_usuario.insert(0, usuario.id_usuario)
        self.entrada_nombre_usuario.delete(0, tk.END)
        self.entrada_nombre_usuario.insert(0, usuario.nombre)
        self.entrada_correo_usuario.delete(0, tk.END)
        self.entrada_correo_usuario.insert(0, usuario.correo)
        self.entrada_contrasena_usuario.delete(0, tk.END)
        self.entrada_contrasena_usuario.insert(0, usuario.contrasena)
        self.combo_rol_usuario.set(usuario.rol)
        self.etiqueta_mensaje_usuario.config(text="Usuario cargado. Puede actualizar o eliminar.", foreground="#2980b9")

    # CALLBACK (bind <Return>): reutiliza el método de registro, sin duplicar su lógica
    def _callback_return_usuario(self, event) -> None:
        self._registrar_usuario()

    # CALLBACK (bind <Escape>): limpia el formulario y cancela la selección actual de la tabla
    def _callback_escape_usuario(self, event) -> None:
        self._limpiar_formulario_usuario()
        self.tabla_usuarios.selection_remove(self.tabla_usuarios.selection())

    # CALLBACK (bind <<ComboboxSelected>>): responde al cambio de rol mostrando una indicación
    def _callback_cambio_rol(self, event) -> None:
        rol = self.combo_rol_usuario.get()
        if rol == "Administrador":
            self.etiqueta_mensaje_usuario.config(
                text="Este rol tendrá acceso completo a la gestión de usuarios.", foreground="#2980b9"
            )
        else:
            self.etiqueta_mensaje_usuario.config(text="", foreground=COLOR_ROJO)

    # ===== SECCIÓN PRODUCTOS =====

    def _mostrar_seccion_productos(self) -> None:
        panel = self._preparar_seccion("Productos", "Gestión de productos")

        cuerpo = ttk.Frame(panel)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        self._construir_formulario_producto(cuerpo)
        self._construir_tabla_productos(cuerpo)
        self._cargar_tabla_productos()

    def _construir_formulario_producto(self, cuerpo: ttk.Frame) -> None:
        formulario = ttk.LabelFrame(cuerpo, text="Datos del producto", padding=10)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        campos = ttk.Frame(formulario)
        campos.pack(fill="x", pady=(0, 10))

        etiquetas = ["ID", "Nombre", "Categoría", "Precio", "Stock"]
        entradas = []
        for fila, texto in enumerate(etiquetas):
            ttk.Label(campos, text=texto).grid(row=fila, column=0, sticky="w", padx=(0, 8), pady=5)
            entrada = ttk.Entry(campos, width=18)
            entrada.grid(row=fila, column=1, pady=5)
            entradas.append(entrada)
        (self.entrada_id, self.entrada_nombre, self.entrada_categoria,
         self.entrada_precio, self.entrada_stock) = entradas

        self._boton_accion(formulario, "Registrar", "agregar", COLOR_NARANJA, COLOR_NARANJA_HOVER, self._registrar_producto)
        self._boton_accion(formulario, "Cargar por ID", "buscar", COLOR_CAFE, COLOR_CAFE_BOTON, self._cargar_producto_en_formulario)
        self._boton_accion(formulario, "Actualizar", "editar", COLOR_DORADO, COLOR_DORADO_HOVER, self._actualizar_producto)
        self._boton_accion(formulario, "Eliminar", "eliminar", COLOR_ROJO, COLOR_ROJO_HOVER, self._eliminar_producto)
        self._boton_accion(formulario, "Limpiar", "limpiar", COLOR_CAFE_CLARO, COLOR_CAFE_CLARO_HOVER, self._limpiar_formulario)

        self.etiqueta_mensaje_producto = ttk.Label(formulario, text="", foreground=COLOR_ROJO, wraplength=220)
        self.etiqueta_mensaje_producto.pack(anchor="w", pady=(8, 0))

    def _construir_tabla_productos(self, cuerpo: ttk.Frame) -> None:
        marco = ttk.LabelFrame(cuerpo, text="Productos registrados", padding=8)
        marco.grid(row=0, column=1, sticky="nsew")

        self.tabla_productos = ttk.Treeview(
            marco, columns=("id", "nombre", "categoria", "precio", "stock"), show="headings"
        )
        for col, texto, ancho, ancla in [
            ("id", "ID", 40, "center"), ("nombre", "Nombre", 130, "w"),
            ("categoria", "Categoría", 90, "w"), ("precio", "Precio", 65, "e"), ("stock", "Stock", 50, "center")
        ]:
            self.tabla_productos.heading(col, text=texto)
            self.tabla_productos.column(col, width=ancho, anchor=ancla)
        self.tabla_productos.pack(fill="both", expand=True)

    def _cargar_tabla_productos(self) -> None:
        self.tabla_productos.delete(*self.tabla_productos.get_children())
        for producto in sorted(self.servicio.listar_productos(), key=lambda p: p.id_producto):
            self.tabla_productos.insert("", tk.END, values=(
                producto.id_producto, producto.nombre, producto.categoria,
                f"{producto.precio:.2f}", producto.stock
            ))

    def _limpiar_formulario(self) -> None:
        for entrada in (self.entrada_id, self.entrada_nombre, self.entrada_categoria,
                        self.entrada_precio, self.entrada_stock):
            entrada.delete(0, tk.END)
        self.etiqueta_mensaje_producto.config(text="", foreground=COLOR_ROJO)

    def _leer_id_producto(self) -> int | None:
        try:
            return int(self.entrada_id.get().strip())
        except ValueError:
            self.etiqueta_mensaje_producto.config(text="El ID debe ser un número entero.", foreground=COLOR_ROJO)
            return None

    def _registrar_producto(self) -> None:
        id_producto = self._leer_id_producto()
        if id_producto is None:
            return
        try:
            nombre = self.entrada_nombre.get().strip()
            categoria = self.entrada_categoria.get().strip()
            precio = float(self.entrada_precio.get().strip())
            stock = int(self.entrada_stock.get().strip())

            self.servicio.agregar_producto(id_producto, nombre, precio, categoria, stock)
            self._cargar_tabla_productos()
            self._limpiar_formulario()
            self._actualizar_barra_estado()
            self.etiqueta_mensaje_producto.config(text=f"Producto '{nombre}' registrado correctamente.", foreground="#27ae60")
        except ValueError as e:
            self.etiqueta_mensaje_producto.config(text=str(e), foreground=COLOR_ROJO)

    def _cargar_producto_en_formulario(self) -> None:
        id_producto = self._leer_id_producto()
        if id_producto is None:
            return
        producto = self.servicio.buscar_producto(id_producto)
        if producto is None:
            self.etiqueta_mensaje_producto.config(text=f"No existe un producto con el ID {id_producto}.", foreground=COLOR_ROJO)
            return

        for entrada, valor in ((self.entrada_nombre, producto.nombre), (self.entrada_categoria, producto.categoria),
                               (self.entrada_precio, str(producto.precio)), (self.entrada_stock, str(producto.stock))):
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)
        self.etiqueta_mensaje_producto.config(text="Producto cargado. Puede actualizar o eliminar.", foreground="#2980b9")

    def _actualizar_producto(self) -> None:
        id_producto = self._leer_id_producto()
        if id_producto is None:
            return
        try:
            nombre = self.entrada_nombre.get().strip()
            categoria = self.entrada_categoria.get().strip()
            precio = float(self.entrada_precio.get().strip())
            stock = int(self.entrada_stock.get().strip())

            if self.servicio.actualizar_producto(id_producto, nombre, categoria, precio, stock):
                self._cargar_tabla_productos()
                self.etiqueta_mensaje_producto.config(text=f"Producto {id_producto} actualizado correctamente.", foreground="#27ae60")
            else:
                self.etiqueta_mensaje_producto.config(text=f"No existe un producto con el ID {id_producto}.", foreground=COLOR_ROJO)
        except ValueError as e:
            self.etiqueta_mensaje_producto.config(text=str(e), foreground=COLOR_ROJO)

    def _eliminar_producto(self) -> None:
        id_producto = self._leer_id_producto()
        if id_producto is None:
            return
        if self.servicio.eliminar_producto(id_producto):
            self._cargar_tabla_productos()
            self._limpiar_formulario()
            self._actualizar_barra_estado()
            self.etiqueta_mensaje_producto.config(text=f"Producto {id_producto} eliminado correctamente.", foreground="#27ae60")
        else:
            self.etiqueta_mensaje_producto.config(text=f"No existe un producto con el ID {id_producto}.", foreground=COLOR_ROJO)
    
    # ===== SECCIÓN VENTAS =====

    def _mostrar_seccion_ventas(self) -> None:
        panel = self._preparar_seccion("Ventas", "Ventas")

        cuerpo = ttk.Frame(panel)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        self._construir_formulario_venta(cuerpo)
        self._construir_tabla_ventas(cuerpo)
        self._cargar_tabla_ventas()

    def _construir_formulario_venta(self, cuerpo: ttk.Frame) -> None:
        formulario = ttk.LabelFrame(cuerpo, text="Registrar venta", padding=10)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Mapas nombre -> id para traducir la selección visible al identificador real
        self._mapa_usuarios = {u.nombre: u.id_usuario for u in self.servicio.listar_usuarios()}
        self._mapa_productos = {p.nombre: p.id_producto for p in self.servicio.listar_productos()}

        ttk.Label(formulario, text="Usuario").pack(anchor="w")
        self.combo_usuario = ttk.Combobox(formulario, values=list(self._mapa_usuarios.keys()),
                                          state="readonly", width=22)
        self.combo_usuario.pack(pady=(2, 12))

        ttk.Label(formulario, text="Producto").pack(anchor="w")
        self.combo_producto = ttk.Combobox(formulario, values=list(self._mapa_productos.keys()),
                                           state="readonly", width=22)
        self.combo_producto.pack(pady=(2, 15))

        # Botón asociado mediante command= al callback de venta (sin paréntesis)
        self._boton_accion(formulario, "Registrar venta", "ventas", COLOR_NARANJA, COLOR_NARANJA_HOVER,
                           self._callback_registrar_venta)

        self.etiqueta_mensaje_venta = ttk.Label(formulario, text="", foreground=COLOR_ROJO, wraplength=200)
        self.etiqueta_mensaje_venta.pack(anchor="w", pady=(8, 0))

    def _construir_tabla_ventas(self, cuerpo: ttk.Frame) -> None:
        marco = ttk.LabelFrame(cuerpo, text="Ventas registradas", padding=8)
        marco.grid(row=0, column=1, sticky="nsew")

        self.tabla_ventas = ttk.Treeview(
            marco, columns=("id_venta", "usuario", "producto", "fecha"), show="headings"
        )
        for col, texto, ancho, ancla in [
            ("id_venta", "Venta", 55, "center"), ("usuario", "Usuario", 140, "w"),
            ("producto", "Producto", 140, "w"), ("fecha", "Fecha", 90, "center")
        ]:
            self.tabla_ventas.heading(col, text=texto)
            self.tabla_ventas.column(col, width=ancho, anchor=ancla)
        self.tabla_ventas.pack(fill="both", expand=True)

    def _cargar_tabla_ventas(self) -> None:
        self.tabla_ventas.delete(*self.tabla_ventas.get_children())
        for venta in sorted(self.servicio.listar_ventas(), key=lambda v: v.id_venta):
            usuario = next((u for u in self.servicio.listar_usuarios() if u.id_usuario == venta.id_usuario), None)
            producto = self.servicio.buscar_producto(venta.id_producto)
            self.tabla_ventas.insert("", tk.END, values=(
                venta.id_venta,
                usuario.nombre if usuario else f"ID {venta.id_usuario}",
                producto.nombre if producto else f"ID {venta.id_producto}",
                venta.fecha
            ))

    # CALLBACK: se ejecuta al presionar "Registrar venta".
    # Flujo: botón -> command= -> callback -> servicio -> persistencia -> respuesta visual.
    def _callback_registrar_venta(self) -> None:
        nombre_usuario = self.combo_usuario.get()
        nombre_producto = self.combo_producto.get()

        if not nombre_usuario or not nombre_producto:
            self.etiqueta_mensaje_venta.config(text="Debe seleccionar un usuario y un producto.", foreground=COLOR_ROJO)
            return

        id_usuario = self._mapa_usuarios[nombre_usuario]
        id_producto = self._mapa_productos[nombre_producto]

        try:
            venta = self.servicio.registrar_venta(id_usuario, id_producto)
            self._cargar_tabla_ventas()
            self._actualizar_barra_estado()
            self.etiqueta_mensaje_venta.config(text=f"Venta {venta.id_venta} registrada correctamente.", foreground="#27ae60")
        except ValueError as e:
            self.etiqueta_mensaje_venta.config(text=str(e), foreground=COLOR_ROJO)