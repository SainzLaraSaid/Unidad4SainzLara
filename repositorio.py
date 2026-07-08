# =====================================================
# repositorio.py
# Capa de acceso a datos (Repository/DAO) con manejo de excepciones
# SOLID: SRP — esta capa es la única que sabe de MySQL
# =====================================================

import mysql.connector                               # Librería para conectar con MySQL
from mysql.connector import Error                    # Clase de error genérica de mysql-connector
from modelos import Categoria, Proveedor, Usuario, Producto  # Modelos de datos del paso 2
from configuracion import CONFIGURACION_BD            # Datos de conexión del paso 1
from excepciones_repositorio import (                # Excepciones propias del paso 3
    ClaveForaneaInvalidaError, RegistroEnUsoError          # Las 2 que vamos a lanzar nosotros mismos
)


def _conectar():                                       # Abre una conexión nueva a MySQL
    """Abre y devuelve una conexión a la base de datos."""
    return mysql.connector.connect(**CONFIGURACION_BD)  # ** descompone el diccionario en host=, user=, etc.


def _crear_tablas(conexion):                            # Crea las 4 tablas si todavía no existen
    """Crea categorias, proveedores, usuarios y productos (con sus 3 FK)."""
    cursor = conexion.cursor()                        # Cursor para ejecutar las sentencias SQL

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (              -- tabla padre 1
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,      -- ID numérico autoincremental
            nombre VARCHAR(80) NOT NULL                       -- nombre de la categoría
        ) ENGINE=InnoDB                                       -- InnoDB es obligatorio para FOREIGN KEY
    """)                                                  # Ejecuta el CREATE TABLE de categorias

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (             -- tabla padre 2
            id_proveedor INT AUTO_INCREMENT PRIMARY KEY,      -- ID numérico autoincremental
            nombre VARCHAR(80) NOT NULL                       -- nombre del proveedor
        ) ENGINE=InnoDB
    """)                                                  # Ejecuta el CREATE TABLE de proveedores

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (                -- tabla padre 3
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,        -- ID numérico autoincremental
            nombre VARCHAR(80) NOT NULL,                      -- nombre del usuario
            correo VARCHAR(120) NOT NULL                      -- correo del usuario
        ) ENGINE=InnoDB
    """)                                                  # Ejecuta el CREATE TABLE de usuarios

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (               -- tabla hija con 3 FK
            id_producto INT AUTO_INCREMENT PRIMARY KEY,       -- ID numérico autoincremental
            nombre VARCHAR(100) NOT NULL,                     -- nombre del producto
            precio DECIMAL(10,2) NOT NULL,                    -- precio con 2 decimales
            id_categoria INT NOT NULL,                        -- FK 1: quién la registra como categoría
            id_proveedor INT NOT NULL,                        -- FK 2: quién la registra como proveedor
            id_usuario INT NOT NULL,                          -- FK 3: quién registró el producto
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),  -- valida FK 1
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor), -- valida FK 2
            FOREIGN KEY (id_usuario)   REFERENCES usuarios(id_usuario)       -- valida FK 3
        ) ENGINE=InnoDB                                       -- las 3 FK necesitan InnoDB
    """)                                                  # Ejecuta el CREATE TABLE de productos (al final)

    conexion.commit()                                   # Confirma la creación de las 4 tablas
    cursor.close()                                       # Cierra el cursor temporal de este método
class RepositorioCategoriaMySQL:                       # CRUD básico de la tabla categorias
    """Acceso a datos de categorias (tabla padre)."""

    def __init__(self):                                   # Constructor del repositorio
        self._conexion = _conectar()                    # Abre la conexión al crear el repositorio
        _crear_tablas(self._conexion)                    # Asegura que las 4 tablas ya existan

    def crear(self, categoria: Categoria) -> int:        # INSERT de una categoría nueva
        """Inserta una categoría y devuelve su ID autogenerado."""
        cursor = self._conexion.cursor()                # Cursor para ejecutar el INSERT
        cursor.execute(
            "INSERT INTO categorias (nombre) VALUES (%s)",  # %s = placeholder seguro (evita inyección SQL)
            (categoria.nombre,)                          # Tupla de 1 valor (la coma es obligatoria)
        )
        self._conexion.commit()                        # Confirma el INSERT en la base de datos
        return cursor.lastrowid                          # ID que MySQL generó automáticamente

    def leer_todos(self) -> list:                      # SELECT de todas las categorías
        """Devuelve la lista de todas las categorías."""
        cursor = self._conexion.cursor()                # Cursor para ejecutar el SELECT
        cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")  # Consulta ordenada
        filas = cursor.fetchall()                        # Todas las filas devueltas, como lista de tuplas
        return [Categoria(nombre=f[1], id_categoria=f[0]) for f in filas]  # Convierte cada tupla en un objeto Categoria

    def eliminar(self, id_categoria: int) -> bool:        # DELETE de una categoría por ID
        """Elimina una categoría. Lanza RegistroEnUsoError si la usa algún producto."""
        try:                                              # Intenta el DELETE (puede fallar por FK)
            cursor = self._conexion.cursor()            # Cursor para ejecutar el DELETE
            cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id_categoria,))  # Borra por ID
            self._conexion.commit()                    # Confirma el DELETE
            return cursor.rowcount > 0                  # True si de verdad borró 1 fila
        except Error as e:                              # Captura cualquier error de MySQL
            if e.errno == 1451:                          # 1451 = registro padre en uso por una tabla hija
                raise RegistroEnUsoError("categoria", id_categoria)  # Traduce a nuestra excepción propia
            raise                                          # Cualquier otro error: lo deja "subir" sin disfrazarlo


class RepositorioProveedorMySQL:                       # CRUD básico de la tabla proveedores
    """Acceso a datos de proveedores (tabla padre)."""

    def __init__(self):
        self._conexion = _conectar()                    # Abre la conexión al crear el repositorio
        _crear_tablas(self._conexion)                    # Asegura que las 4 tablas ya existan

    def crear(self, proveedor: Proveedor) -> int:        # INSERT de un proveedor nuevo
        """Inserta un proveedor y devuelve su ID autogenerado."""
        cursor = self._conexion.cursor()                # Cursor para ejecutar el INSERT
        cursor.execute("INSERT INTO proveedores (nombre) VALUES (%s)", (proveedor.nombre,))  # INSERT seguro
        self._conexion.commit()                        # Confirma el INSERT
        return cursor.lastrowid                          # ID generado por MySQL

    def leer_todos(self) -> list:                      # SELECT de todos los proveedores
        """Devuelve la lista de todos los proveedores."""
        cursor = self._conexion.cursor()
        cursor.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre")  # Consulta ordenada
        filas = cursor.fetchall()                        # Todas las filas devueltas
        return [Proveedor(nombre=f[1], id_proveedor=f[0]) for f in filas]  # Tuplas -> objetos Proveedor

    def eliminar(self, id_proveedor: int) -> bool:        # DELETE de un proveedor por ID
        """Elimina un proveedor. Lanza RegistroEnUsoError si lo usa algún producto."""
        try:
            cursor = self._conexion.cursor()
            cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_proveedor,))  # Borra por ID
            self._conexion.commit()
            return cursor.rowcount > 0
        except Error as e:
            if e.errno == 1451:                          # 1451 = en uso por una tabla hija
                raise RegistroEnUsoError("proveedor", id_proveedor)  # Traduce a nuestra excepción propia
            raise


class RepositorioUsuarioMySQL:                         # CRUD básico de la tabla usuarios
    """Acceso a datos de usuarios (tabla padre, la 3ª FK)."""

    def __init__(self):
        self._conexion = _conectar()                    # Abre la conexión al crear el repositorio
        _crear_tablas(self._conexion)                    # Asegura que las 4 tablas ya existan

    def crear(self, usuario: Usuario) -> int:            # INSERT de un usuario nuevo
        """Inserta un usuario y devuelve su ID autogenerado."""
        cursor = self._conexion.cursor()                # Cursor para ejecutar el INSERT
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)",  # 2 placeholders seguros
            (usuario.nombre, usuario.correo)              # Tupla con nombre y correo
        )
        self._conexion.commit()                        # Confirma el INSERT
        return cursor.lastrowid                          # ID generado por MySQL

    def leer_todos(self) -> list:                      # SELECT de todos los usuarios
        """Devuelve la lista de todos los usuarios."""
        cursor = self._conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios ORDER BY nombre")  # Consulta ordenada
        filas = cursor.fetchall()
        return [Usuario(nombre=f[1], correo=f[2], id_usuario=f[0]) for f in filas]  # Tuplas -> objetos Usuario

    def eliminar(self, id_usuario: int) -> bool:            # DELETE de un usuario por ID
        """Elimina un usuario. Lanza RegistroEnUsoError si lo usa algún producto."""
        try:
            cursor = self._conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))  # Borra por ID
            self._conexion.commit()
            return cursor.rowcount > 0
        except Error as e:
            if e.errno == 1451:                          # 1451 = en uso por una tabla hija (un producto)
                raise RegistroEnUsoError("usuario", id_usuario)  # Traduce a nuestra excepción propia
            raise
class RepositorioProductoMySQL:                       # CRUD completo de productos, con las 3 FK
    """Acceso a datos de productos (tabla hija con 3 llaves foráneas)."""

    def __init__(self):                                   # Constructor del repositorio
        self._conexion = _conectar()                    # Abre la conexión al crear el repositorio
        _crear_tablas(self._conexion)                    # Asegura que las 4 tablas ya existan

    def crear(self, producto: Producto) -> int:          # INSERT de un producto nuevo
        """Inserta un producto. Lanza ClaveForaneaInvalidaError si alguna FK no existe."""
        sql = """
            INSERT INTO productos (nombre, precio, id_categoria, id_proveedor, id_usuario)
            VALUES (%s, %s, %s, %s, %s)
        """                                              # 5 placeholders seguros, en el mismo orden que abajo
        valores = (producto.nombre, producto.precio,    # Tupla con nombre y precio
                   producto.id_categoria, producto.id_proveedor, producto.id_usuario)  # + las 3 FK
        try:                                              # Intenta el INSERT (puede fallar si alguna FK no existe)
            cursor = self._conexion.cursor()            # Cursor para ejecutar el INSERT
            cursor.execute(sql, valores)                  # Ejecuta el INSERT sustituyendo los %s
            self._conexion.commit()                    # Confirma el INSERT en la base de datos
            return cursor.lastrowid                      # ID generado por MySQL
        except Error as e:                              # Captura cualquier error de MySQL
            if e.errno == 1452:                          # 1452 = alguna de las 3 FK no existe en su tabla padre
                raise ClaveForaneaInvalidaError(f"categoría, proveedor o usuario no existen ({e})")  # Traduce
            raise                                          # Cualquier otro error: lo deja "subir" sin disfrazarlo

    def leer_todos(self) -> list:                      # SELECT con JOIN de las 3 tablas padre
        """Devuelve productos con los NOMBRES de sus 3 FK, no solo los IDs."""
        sql = """
            SELECT p.id_producto, p.nombre, p.precio,
                   p.id_categoria, c.nombre, p.id_proveedor, pr.nombre,
                   p.id_usuario, u.nombre
            FROM productos p
            JOIN categorias  c  ON p.id_categoria = c.id_categoria
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            JOIN usuarios    u  ON p.id_usuario   = u.id_usuario
            ORDER BY p.nombre
        """                                              # 3 JOIN: uno por cada llave foránea
        cursor = self._conexion.cursor()                # Cursor para ejecutar el SELECT
        cursor.execute(sql)                              # Ejecuta la consulta con los 3 JOIN
        filas = cursor.fetchall()                        # Todas las filas devueltas
        productos = []                                 # Lista donde acumulamos los objetos Producto
        for f in filas:                                   # Recorre cada fila (tupla) devuelta por MySQL
            productos.append(Producto(                  # Crea un Producto a partir de la fila
                id_producto=f[0], nombre=f[1], precio=float(f[2]),  # Columnas propias
                id_categoria=f[3], nombre_categoria=f[4],     # FK 1 + nombre vía JOIN
                id_proveedor=f[5], nombre_proveedor=f[6],     # FK 2 + nombre vía JOIN
                id_usuario=f[7], nombre_usuario=f[8],         # FK 3 + nombre vía JOIN
            ))
        return productos                                 # Devuelve la lista completa de productos

    def actualizar(self, producto: Producto) -> bool:      # UPDATE de un producto existente
        """Actualiza un producto. Lanza ClaveForaneaInvalidaError si alguna FK no existe."""
        sql = """
            UPDATE productos
            SET nombre = %s, precio = %s, id_categoria = %s, id_proveedor = %s, id_usuario = %s
            WHERE id_producto = %s
        """                                              # 6 placeholders: 5 valores nuevos + el ID a filtrar
        valores = (producto.nombre, producto.precio, producto.id_categoria,  # Valores nuevos...
                   producto.id_proveedor, producto.id_usuario, producto.id_producto)  # ...+ el ID al final
        try:                                              # Intenta el UPDATE (puede fallar si alguna FK no existe)
            cursor = self._conexion.cursor()            # Cursor para ejecutar el UPDATE
            cursor.execute(sql, valores)                  # Ejecuta el UPDATE sustituyendo los %s
            self._conexion.commit()                    # Confirma el UPDATE
            return cursor.rowcount > 0                  # True si de verdad modificó 1 fila
        except Error as e:                              # Captura cualquier error de MySQL
            if e.errno == 1452:                          # 1452 = alguna de las 3 FK nuevas no existe
                raise ClaveForaneaInvalidaError(f"categoría, proveedor o usuario no existen ({e})")  # Traduce
            raise                                          # Cualquier otro error: lo deja "subir" sin disfrazarlo

    def eliminar(self, id_producto: int) -> bool:          # DELETE de un producto por ID
        """Elimina un producto. productos es la tabla hija: nada más depende de ella."""
        cursor = self._conexion.cursor()                # Cursor para ejecutar el DELETE
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))  # Borra por ID
        self._conexion.commit()                        # Confirma el DELETE
        return cursor.rowcount > 0                      # True si de verdad borró 1 fila