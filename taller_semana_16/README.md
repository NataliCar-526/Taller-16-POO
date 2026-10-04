# Tarea Semana 16 - Manejo de eventos aplicado a la gestión de usuarios en restaurante_app

**Estudiante:** Natalia Belén Carvajal Díaz

---

## Descripción del sistema

Esta semana *restaurante_app* aplica el **manejo de eventos de Tkinter** a un caso real del sistema: la gestión de usuarios. Se incorpora el atributo `rol` al modelo `Usuario` (Administrador, Empleado, Cliente), de modo que solo un Administrador puede registrar, consultar, actualizar y eliminar usuarios desde la interfaz; los demás roles acceden únicamente a una consulta de solo lectura. La sección combina botones asociados mediante `command=` con eventos asociados mediante `bind()`: selección en una tabla, teclas de atajo y cambio en una lista desplegable.

Se mantiene todo lo desarrollado en semanas anteriores: inicio de sesión, gestión de productos, registro de ventas, diseño con sidebar, paleta de colores y recursos de `assets/`.

---

## Evolución respecto a la Semana 15

| Aspecto | Semana 15 | Semana 16 |
|---------|-----------|-----------|
| Usuario | Sin rol | Con atributo `rol`: Administrador, Empleado o Cliente |
| Sección Usuarios | Consulta de solo lectura para cualquiera | CRUD completo, visible solo para Administrador; solo lectura para los demás roles |
| Interacción | Solo botones con `command=` | Se agregan eventos con `bind()`: `<<TreeviewSelect>>`, `<Return>`, `<Escape>`, `<<ComboboxSelected>>` |
| Eliminar usuario | No existía | Elimina con confirmación previa; impide que la cuenta activa se elimine a sí misma |

---

## Estructura del proyecto

```
restaurante_app/
├── assets/
│ ├── logo/
│ │ ├── logo.png
│ │ └── icono.ico
│ └── icons/
│ ├── home.png, usuarios.png, productos.png, ventas.png, logout.png
│ └── agregar.png, buscar.png, editar.png, eliminar.png, limpiar.png
├── datos/
│ ├── productos.json
│ ├── usuarios.json                    # Ahora incluye el campo "rol" en cada usuario
│ └── ventas.json
├── modelos/
│ ├── init.py
│ ├── producto.py
│ ├── usuario.py                       # Incorpora ROLES_VALIDOS, rol y es_administrador()
│ └── venta.py
├── servicios/
│ ├── init.py
│ ├── archivo_servicio.py
│ └── restaurante_servicio.py          # Incorpora el CRUD de usuarios
├── ui/
│ ├── init.py
│ ├── login_view.py
│ └── main_view.py                     # Sección Usuarios con formulario, Treeview y eventos
└── main.py
```

En la raíz del repositorio se encuentra `README.md`.

---

## Roles de usuario

| Rol | Acceso a la gestión de usuarios |
|-----|----------------------------------|
| Administrador | Formulario completo: registrar, consultar, actualizar y eliminar |
| Empleado | Solo consulta de lectura (tabla sin formulario ni botones) |
| Cliente | Solo consulta de lectura (tabla sin formulario ni botones) |

El control de acceso se resuelve en `MainView`, consultando `self.usuario_actual.es_administrador()` (el usuario activo se obtiene una sola vez al iniciar sesión, mediante `RestauranteServicio.buscar_usuario_por_nombre()`).

---

## Gestión de usuarios (CRUD)

`RestauranteServicio` concentra las reglas:

- **Registrar:** valida que el ID no exista y que los datos sean válidos (reutilizando las validaciones del propio modelo `Usuario`).
- **Actualizar:** construye un `Usuario` temporal con los nuevos datos para validar sin duplicar las reglas, y solo si es válido actualiza el objeto real.
- **Eliminar:** impide que un Administrador elimine su propia cuenta mientras está activa (`ValueError` si el ID coincide con el usuario logueado).

Cada operación guarda automáticamente en `usuarios.json` mediante `ArchivoServicio`.

---

## Manejo de eventos

### Flujo general

```
INTERACCIÓN DEL USUARIO
↓
EVENTO (selección, tecla, cambio de opción)
↓
bind() / command=
↓
CALLBACK
↓
RestauranteServicio (validación y persistencia)
↓
Actualización del Treeview y mensaje de respuesta
```

---

### Eventos implementados

| Evento | Widget | Callback | Qué hace |
|--------|--------|----------|----------|
| `<<TreeviewSelect>>` | Tabla de usuarios | `_callback_seleccionar_usuario` | Toma el ID de la fila seleccionada y consulta el objeto completo mediante `RestauranteServicio.buscar_usuario()`, cargando sus datos en el formulario. La tabla nunca almacena la contraseña. |
| `<Return>` | Campos del formulario | `_callback_return_usuario` | Reutiliza `_registrar_usuario()`, el mismo método que usa el botón "Registrar" — no duplica lógica. |
| `<Escape>` | Campos del formulario y tabla | `_callback_escape_usuario` | Limpia el formulario y quita la selección activa de la tabla, devolviendo la interfaz a su estado inicial. |
| `<<ComboboxSelected>>` | Combobox de rol | `_callback_cambio_rol` | Muestra una indicación cuando se selecciona el rol Administrador. |

### Botones (`command=`)

Los botones Registrar, Actualizar, Eliminar y Limpiar siguen usando `command=`, igual que en semanas anteriores. "Eliminar" además solicita confirmación con `messagebox.askyesno()` antes de ejecutar la operación.

Esta combinación evidencia la diferencia entre `command=` (una acción directa del usuario sobre un botón) y `bind()` (una respuesta a un evento que ocurre sobre otro tipo de interacción: selección, tecla o cambio de valor).

---

## Persistencia

`RestauranteServicio` guarda automáticamente en `usuarios.json` después de registrar, actualizar o eliminar un usuario, mediante `ArchivoServicio`. La vista no lee ni escribe el archivo en ningún momento.

---

## Excepciones controladas

| Excepción | ¿Cuándo ocurre? | ¿Cómo se maneja? |
|-----------|-----------------|------------------|
| FileNotFoundError | El archivo JSON no existe | Se inicia esa colección vacía |
| JSONDecodeError | El archivo JSON tiene contenido inválido | Se inicia esa colección vacía |
| PermissionError | No hay permisos de lectura o escritura | Se muestra un mensaje de error |
| KeyError | Un registro no tiene una clave esperada (por ejemplo, un usuario sin `rol`) | Se omite el registro dañado |
| ValueError | ID duplicado, datos inválidos, rol no reconocido, o intento de eliminar la propia cuenta activa | Se muestra el mensaje correspondiente en la interfaz, sin interrumpir la aplicación |

---

## Pruebas realizadas

1. Se ejecutó `main.py` y la aplicación inició sin errores.
2. Se confirmó que el inicio de sesión, Productos y Ventas continúan funcionando.
3. Se ingresó con un usuario de rol Administrador y se accedió a la gestión completa de Usuarios.
4. Se registró un nuevo usuario (Cliente/Empleado) y apareció correctamente en la tabla.
5. Se seleccionó una fila y se confirmó que `<<TreeviewSelect>>` cargó sus datos en el formulario.
6. Se registró un usuario presionando `<Return>` en lugar del botón.
7. Se presionó `<Escape>` con el foco en el formulario y en la tabla, confirmando que limpia los campos y quita la selección en ambos casos.
8. Se cambió el Combobox de rol a "Administrador" y se confirmó la respuesta de `<<ComboboxSelected>>`.
9. Se actualizó un usuario existente y se confirmó que el cambio se conservó.
10. Se intentó eliminar la propia cuenta administrativa activa y se confirmó que la operación fue rechazada.
11. Se eliminó un usuario distinto, confirmando el cuadro de confirmación previo.
12. Se cerró sesión y se ingresó con un usuario Cliente/Empleado, confirmando que solo se muestra la tabla de solo lectura.
13. Se cerró y volvió a ejecutar la aplicación, confirmando que los usuarios se recuperaron correctamente desde `usuarios.json`.

---

## Instrucciones de ejecución

1. Instalar la dependencia necesaria: `pip install -r requirements.txt`
2. Ubicarse dentro de la carpeta `restaurante_app/`.
3. Ejecutar: `python main.py`
4. Ingresar con un usuario registrado en `datos/usuarios.json`. Para probar la gestión completa de usuarios, usar uno con `"rol": "Administrador"`.
5. En la sección **Usuarios**:
   - Seleccionar una fila para cargarla en el formulario.
   - Presionar `Enter` dentro de cualquier campo para registrar.
   - Presionar `Escape` para limpiar el formulario y la selección.
   - Usar los botones para Actualizar, Eliminar o Limpiar manualmente.

---

## Reflexión

Esta semana permitió distinguir con claridad cuándo usar `command=` y cuándo usar `bind()`: el primero responde a una acción directa sobre un botón, mientras que el segundo responde a eventos que ocurren sobre otros widgets, como seleccionar una fila, presionar una tecla específica o cambiar el valor de una lista desplegable. Reutilizar `_registrar_usuario()` dentro del callback de `<Return>`, en lugar de repetir su lógica, reforzó la importancia de mantener cada operación en un único lugar. Incorporar roles y restringir la gestión de usuarios según el rol activo también mostró cómo una regla de negocio (quién puede administrar qué) se resuelve consultando al servicio, sin que la interfaz decida por su cuenta más que mostrar u ocultar componentes.