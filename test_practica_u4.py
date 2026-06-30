# =====================================================
# test_practica_u4.py
# Evalúa el CRUD de productos con sus 3 llaves foráneas
# =====================================================

import unittest                                       # Framework de pruebas de la librería estándar
from repositorio import (RepositorioCategoriaMySQL, RepositorioProveedorMySQL,  # Repositorios padre
                          RepositorioUsuarioMySQL, RepositorioProductoMySQL)   # Repositorio hijo
from modelos import Categoria, Proveedor, Usuario, Producto   # Modelos del paso 2
from excepciones_repositorio import ClaveForaneaInvalidaError, RegistroEnUsoError  # Excepciones a probar


class TestPracticaU4(unittest.TestCase):                # Hereda de TestCase: cada método test_* es una prueba
    """
    Suite de pruebas que verifica el CRUD completo
    y las 3 llaves foráneas del proyecto de esta práctica.
    """

    def setUp(self):                                    # Se ejecuta automáticamente ANTES de cada test
        """Crea una categoría, un proveedor y un usuario de prueba."""
        self.repo_cat  = RepositorioCategoriaMySQL()          # Repositorio de categorías para este test
        self.repo_prov = RepositorioProveedorMySQL()          # Repositorio de proveedores para este test
        self.repo_usr  = RepositorioUsuarioMySQL()            # Repositorio de usuarios para este test
        self.repo_prod = RepositorioProductoMySQL()           # Repositorio de productos para este test

        self.id_categoria = self.repo_cat.crear(Categoria("TEST-Categoria"))  # Inserta categoría de prueba
        self.id_proveedor = self.repo_prov.crear(Proveedor("TEST-Proveedor"))  # Inserta proveedor de prueba
        self.id_usuario = self.repo_usr.crear(Usuario("TEST-Usuario", "test@uth.edu"))  # Inserta usuario de prueba
        self.ids_productos_creados = []               # Lista para poder limpiar en tearDown

    def tearDown(self):                                 # Se ejecuta automáticamente DESPUÉS de cada test
        """Borra TODO lo creado por la prueba, hijos antes que padres."""
        for id_prod in self.ids_productos_creados:           # Primero borra los productos (tabla hija)
            try:                                          # Por si el test ya lo borró él mismo
                self.repo_prod.eliminar(id_prod)              # Borra el producto de prueba
            except Exception:                            # Ignora si ya no existía
                pass
        self.repo_cat.eliminar(self.id_categoria)         # Ahora sí se puede borrar la categoría (sin hijos)
        self.repo_prov.eliminar(self.id_proveedor)         # Borra el proveedor de prueba
        self.repo_usr.eliminar(self.id_usuario)             # Borra el usuario de prueba

    # ────── CRUD BÁSICO ──────

    def test_crear_producto_valido(self):                 # Prueba 1: crear con las 3 FK válidas
        """Crear un producto con las 3 FK válidas debe funcionar y devolver un id."""
        producto = Producto("Laptop de prueba", 999.99,      # Nombre y precio
                            self.id_categoria, self.id_proveedor, self.id_usuario)  # Las 3 FK válidas del setUp
        id_creado = self.repo_prod.crear(producto)         # Inserta y guarda el ID devuelto
        self.ids_productos_creados.append(id_creado)     # Lo registra para limpiarlo en tearDown
        self.assertIsNotNone(id_creado)                  # Verifica que sí devolvió un ID

    def test_leer_incluye_join_de_las_3_fk(self):           # Prueba 2: el JOIN trae los 3 nombres
        """leer_todos() debe devolver los NOMBRES (vía JOIN), no solo los IDs."""
        producto = Producto("Mouse de prueba", 19.99,
                            self.id_categoria, self.id_proveedor, self.id_usuario)
        id_creado = self.repo_prod.crear(producto)         # Inserta el producto de prueba
        self.ids_productos_creados.append(id_creado)     # Lo registra para limpiarlo

        productos = self.repo_prod.leer_todos()           # Lee todos los productos (con JOIN)
        encontrado = next(p for p in productos if p.id_producto == id_creado)  # Busca el recién creado
        self.assertEqual(encontrado.nombre_categoria, "TEST-Categoria")  # El JOIN trajo el nombre
        self.assertEqual(encontrado.nombre_proveedor, "TEST-Proveedor")  # de cada una de las
        self.assertEqual(encontrado.nombre_usuario, "TEST-Usuario")      # 3 tablas padre

    def test_actualizar_producto(self):                  # Prueba 3: actualizar persiste el cambio
        """Actualizar un producto debe persistir el nuevo valor."""
        producto = Producto("Teclado", 49.99, self.id_categoria, self.id_proveedor, self.id_usuario)
        id_creado = self.repo_prod.crear(producto)         # Crea el producto original
        self.ids_productos_creados.append(id_creado)     # Lo registra para limpiarlo

        producto.id_producto = id_creado                # Asigna el ID real antes de actualizar
        producto.precio = 59.99                          # Cambia el precio
        self.repo_prod.actualizar(producto)               # Guarda el cambio en MySQL

        actualizado = next(p for p in self.repo_prod.leer_todos() if p.id_producto == id_creado)  # Relee
        self.assertEqual(actualizado.precio, 59.99)        # El precio nuevo debe persistir

    def test_eliminar_producto(self):                     # Prueba 4: eliminar lo quita de la lista
        """Eliminar un producto debe quitarlo de leer_todos()."""
        producto = Producto("Monitor", 150.0, self.id_categoria, self.id_proveedor, self.id_usuario)
        id_creado = self.repo_prod.crear(producto)         # Crea el producto (no se registra: se borra aquí mismo)

        self.repo_prod.eliminar(id_creado)                # Lo elimina de inmediato
        ids_restantes = [p.id_producto for p in self.repo_prod.leer_todos()]  # Relee todos los IDs
        self.assertNotIn(id_creado, ids_restantes)         # Ya no debe aparecer

    # ────── LAS 3 LLAVES FORÁNEAS ──────

    def test_crear_con_categoria_inexistente_lanza_error(self):  # Prueba 5: FK 1 inválida
        """Crear con id_categoria que NO existe debe lanzar ClaveForaneaInvalidaError."""
        producto = Producto("Producto inválido", 10.0, 999999, self.id_proveedor, self.id_usuario)  # id_categoria inexistente
        with self.assertRaises(ClaveForaneaInvalidaError):    # Espera que se lance esta excepción
            self.repo_prod.crear(producto)                  # Intenta crear (debe fallar)

    def test_crear_con_usuario_inexistente_lanza_error(self):    # Prueba 6: FK 3 inválida
        """Crear con id_usuario que NO existe debe lanzar ClaveForaneaInvalidaError."""
        producto = Producto("Producto inválido", 10.0, self.id_categoria, self.id_proveedor, 999999)  # id_usuario inexistente
        with self.assertRaises(ClaveForaneaInvalidaError):
            self.repo_prod.crear(producto)

    def test_eliminar_usuario_en_uso_lanza_error(self):       # Prueba 7: integridad referencial al eliminar
        """No se debe poder eliminar un usuario referenciado por un producto."""
        producto = Producto("Producto con dueño", 10.0, self.id_categoria, self.id_proveedor, self.id_usuario)
        id_creado = self.repo_prod.crear(producto)         # Crea un producto que SÍ usa este usuario
        self.ids_productos_creados.append(id_creado)     # Lo registra para limpiarlo

        with self.assertRaises(RegistroEnUsoError):         # Espera que se lance esta excepción
            self.repo_usr.eliminar(self.id_usuario)          # Intenta eliminar el usuario en uso (debe fallar)


if __name__ == "__main__":                              # Solo si se ejecuta este archivo directamente
    unittest.main(verbosity=2)                         # Corre las pruebas mostrando el detalle de cada una

    