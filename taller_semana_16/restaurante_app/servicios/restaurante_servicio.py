from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio

class RestauranteServicio:
    def __init__(self, archivo_servicio: ArchivoServicio):
        self.archivo_servicio = archivo_servicio
        self.productos: list[Producto] = []
        self.usuarios: list[Usuario] = []
        self.ventas: list[Venta] = []

    # ===== CARGA DE DATOS =====

    def cargar_productos(self, productos: list[Producto]) -> None:
        self.productos = productos

    def cargar_usuarios(self, usuarios: list[Usuario]) -> None:
        self.usuarios = usuarios

    def cargar_ventas(self, ventas: list[Venta]) -> None:
        self.ventas = ventas

    # ===== ACCESO (LOGIN) =====

    def buscar_usuario_por_nombre(self, nombre: str) -> Usuario | None:
        for usuario in self.usuarios:
            if usuario.nombre == nombre:
                return usuario
        return None

    def validar_acceso(self, nombre: str, contrasena: str) -> bool:
        if not nombre or not contrasena:
            return False
        usuario = self.buscar_usuario_por_nombre(nombre)
        if usuario is None:
            return False
        return usuario.verificar_contrasena(contrasena)

    # ===== CONSULTAS =====

    def listar_productos(self) -> list[Producto]:
        return self.productos

    def listar_usuarios(self) -> list[Usuario]:
        return self.usuarios

    def listar_ventas(self) -> list[Venta]:
        return self.ventas

    def buscar_producto(self, id_producto: int) -> Producto | None:
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto
        return None

    def buscar_usuario(self, id_usuario: int) -> Usuario | None:
        for usuario in self.usuarios:
            if usuario.id_usuario == id_usuario:
                return usuario
        return None

    # ===== GESTIÓN DE PRODUCTOS (CRUD) =====

    def agregar_producto(self, id_producto: int, nombre: str, precio: float, categoria: str, stock: int) -> None:
        if self.buscar_producto(id_producto) is not None:
            raise ValueError(f"Ya existe un producto con el ID {id_producto}.")
        nuevo_producto = Producto(id_producto, nombre, precio, categoria, stock)
        self.productos.append(nuevo_producto)
        self._guardar_productos()

    def actualizar_producto(self, id_producto: int, nombre: str, categoria: str, precio: float, stock: int) -> bool:
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
        producto.nombre = nombre
        producto.categoria = categoria
        producto.precio = precio
        producto.stock = stock
        self._guardar_productos()
        return True

    def eliminar_producto(self, id_producto: int) -> bool:
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        self.productos.remove(producto)
        self._guardar_productos()
        return True

    def _guardar_productos(self) -> None:
        self.archivo_servicio.guardar_productos(self.productos)

    # ===== GESTIÓN DE USUARIOS (CRUD) =====

    # Registra un nuevo usuario, validando ID único y los datos del modelo
    def agregar_usuario(self, id_usuario: int, nombre: str, correo: str, contrasena: str, rol: str) -> Usuario:
        if self.buscar_usuario(id_usuario) is not None:
            raise ValueError(f"Ya existe un usuario con el ID {id_usuario}.")
        nuevo_usuario = Usuario(id_usuario, nombre, correo, contrasena, rol)
        self.usuarios.append(nuevo_usuario)
        self._guardar_usuarios()
        return nuevo_usuario

    # Actualiza un usuario existente; valida los datos reconstruyendo un Usuario temporal
    def actualizar_usuario(self, id_usuario: int, nombre: str, correo: str, contrasena: str, rol: str) -> bool:
        usuario = self.buscar_usuario(id_usuario)
        if usuario is None:
            return False
        # Se valida mediante el propio modelo, reutilizando sus reglas (nombre, correo, contraseña, rol)
        Usuario(id_usuario, nombre, correo, contrasena, rol)
        usuario.nombre = nombre
        usuario.correo = correo
        usuario.contrasena = contrasena
        usuario.rol = rol
        self._guardar_usuarios()
        return True

    # Elimina un usuario, impidiendo que la cuenta administrativa activa se elimine a sí misma
    def eliminar_usuario(self, id_usuario: int, id_usuario_actual: int) -> bool:
        if id_usuario == id_usuario_actual:
            raise ValueError("No puede eliminar su propia cuenta mientras está activa.")
        usuario = self.buscar_usuario(id_usuario)
        if usuario is None:
            return False
        self.usuarios.remove(usuario)
        self._guardar_usuarios()
        return True

    def _guardar_usuarios(self) -> None:
        self.archivo_servicio.guardar_usuarios(self.usuarios)

    # ===== GESTIÓN DE VENTAS =====

    def _siguiente_id_venta(self) -> int:
        if not self.ventas:
            return 1
        return max(venta.id_venta for venta in self.ventas) + 1

    def registrar_venta(self, id_usuario: int, id_producto: int) -> Venta:
        usuario = self.buscar_usuario(id_usuario)
        if usuario is None:
            raise ValueError("Debe seleccionar un usuario válido.")
        producto = self.buscar_producto(id_producto)
        if producto is None:
            raise ValueError("Debe seleccionar un producto válido.")
        nueva_venta = Venta(self._siguiente_id_venta(), id_usuario, id_producto)
        self.ventas.append(nueva_venta)
        self.archivo_servicio.guardar_ventas(self.ventas)
        return nueva_venta