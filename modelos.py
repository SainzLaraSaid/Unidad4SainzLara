# =====================================================
# modelos.py
# Clases que representan los datos (sin lógica de BD ni de GUI)
# SOLID: Responsabilidad Única — cada clase solo modela datos
# =====================================================


class Categoria:                                       # Modela una categoría (tabla padre 1)
    """Representa una fila de la tabla categorias."""

    def __init__(self, nombre: str, id_categoria: int = None):  # Constructor: nombre obligatorio, ID opcional
        self.id_categoria = id_categoria       # None = categoría nueva (aún no guardada en MySQL)
        self.nombre = nombre                   # Nombre de la categoría

    def __repr__(self) -> str:                  # Representación técnica (debugging)
        return f"Categoria(id={self.id_categoria}, nombre='{self.nombre}')"  # Texto con ID y nombre


class Proveedor:                                       # Modela un proveedor (tabla padre 2)
    """Representa una fila de la tabla proveedores."""

    def __init__(self, nombre: str, id_proveedor: int = None):  # Constructor: nombre obligatorio, ID opcional
        self.id_proveedor = id_proveedor       # None = proveedor nuevo (aún no guardado en MySQL)
        self.nombre = nombre                   # Nombre del proveedor

    def __repr__(self) -> str:                  # Representación técnica (debugging)
        return f"Proveedor(id={self.id_proveedor}, nombre='{self.nombre}')"  # Texto con ID y nombre


class Usuario:                                         # Modela un usuario del sistema (tabla padre 3)
    """Representa una fila de la tabla usuarios."""

    def __init__(self, nombre: str, correo: str, id_usuario: int = None):  # Constructor: recibe nombre, correo e ID opcional
        self.id_usuario = id_usuario           # None = usuario nuevo (aún no guardado en MySQL)
        self.nombre = nombre                   # Nombre del usuario
        self.correo = correo                   # Correo del usuario

    def __repr__(self) -> str:                  # Representación técnica (debugging)
        return f"Usuario(id={self.id_usuario}, nombre='{self.nombre}')"  # Texto con ID y nombre


class Producto:                                        # Modela la entidad principal (tabla hija, con 3 FK)
    """
    Representa un producto con sus 3 llaves foráneas:
    id_categoria, id_proveedor e id_usuario.
    """

    def __init__(self, nombre: str, precio: float,            # Datos propios del producto
                 id_categoria: int, id_proveedor: int, id_usuario: int,  # Las 3 llaves foráneas
                 id_producto: int = None,                      # ID opcional (None = aún no guardado)
                 nombre_categoria: str = "",                 # Nombre legible de la categoría (lo llena el JOIN)
                 nombre_proveedor: str = "",                 # Nombre legible del proveedor (lo llena el JOIN)
                 nombre_usuario: str = ""):                  # Nombre legible del usuario (lo llena el JOIN)
        self.id_producto = id_producto           # None = producto nuevo (aún no guardado en MySQL)
        self.nombre = nombre                       # Nombre del producto
        self.precio = precio                       # Precio del producto
        self.id_categoria = id_categoria         # FK 1 -> categorias.id_categoria
        self.id_proveedor = id_proveedor         # FK 2 -> proveedores.id_proveedor
        self.id_usuario = id_usuario             # FK 3 -> usuarios.id_usuario
        self.nombre_categoria = nombre_categoria  # Solo para mostrar en pantalla (no es columna propia)
        self.nombre_proveedor = nombre_proveedor  # Solo para mostrar en pantalla (no es columna propia)
        self.nombre_usuario = nombre_usuario      # Solo para mostrar en pantalla (no es columna propia)

    def __repr__(self) -> str:                  # Representación técnica (debugging)
        return f"Producto(id={self.id_producto}, nombre='{self.nombre}')"  # Texto con ID y nombre