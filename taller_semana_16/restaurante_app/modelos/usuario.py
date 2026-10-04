# Roles válidos que puede tener un usuario del sistema
ROLES_VALIDOS = ("Administrador", "Empleado", "Cliente")

# Clase que representa un usuario del restaurante
class Usuario:
    def __init__(self, id_usuario: int, nombre: str, correo: str, contrasena: str, rol: str):
        self._validar_datos(nombre, correo, contrasena, rol)
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.contrasena = contrasena
        self.rol = rol

    # Valida que los datos del usuario sean correctos
    def _validar_datos(self, nombre: str, correo: str, contrasena: str, rol: str) -> None:
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        if not correo or "@" not in correo:
            raise ValueError("El correo del usuario no es válido.")
        if not contrasena or not str(contrasena).strip():
            raise ValueError("La contraseña del usuario no puede estar vacía.")
        if rol not in ROLES_VALIDOS:
            raise ValueError(f"El rol debe ser uno de: {', '.join(ROLES_VALIDOS)}.")

    # Verifica si la contraseña ingresada coincide con la del usuario
    def verificar_contrasena(self, contrasena: str) -> bool:
        return self.contrasena == contrasena

    # Indica si el usuario tiene permisos administrativos
    def es_administrador(self) -> bool:
        return self.rol == "Administrador"

    # Muestra la información del usuario (sin incluir la contraseña)
    def mostrar_informacion(self) -> str:
        return f"Usuario: {self.id_usuario} | {self.nombre} | {self.correo} | {self.rol}"

    # Representación en texto del usuario
    def __str__(self) -> str:
        return f"[{self.id_usuario}] {self.nombre} ({self.rol})"

    # Convierte el objeto a diccionario para JSON
    def to_dict(self) -> dict:
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "correo": self.correo,
            "contraseña": self.contrasena,
            "rol": self.rol
        }

    # Crea un objeto Usuario desde un diccionario
    @classmethod
    def from_dict(cls, datos: dict):
        return cls(
            id_usuario=datos["id_usuario"],
            nombre=datos["nombre"],
            correo=datos["correo"],
            contrasena=datos["contraseña"],
            rol=datos["rol"]
        )