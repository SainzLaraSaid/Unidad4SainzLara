# =====================================================
# main.py
# Interfaz gráfica con Flet — CRUD de productos con 3 llaves foráneas
# =====================================================

import flet as ft                                          # Flet como 'ft'
from modelos import Producto                                # Modelo de datos del producto
from repositorio import (                                    # Los 4 repositorios del paso 4
    RepositorioCategoriaMySQL, RepositorioProveedorMySQL,
    RepositorioUsuarioMySQL, RepositorioProductoMySQL
)
from excepciones_repositorio import ClaveForaneaInvalidaError, RegistroEnUsoError  # Excepciones propias


def main(page: ft.Page):                                    # Función que Flet invoca al iniciar la app
    """Función principal de Flet. 'page' es la ventana de la aplicación."""
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "📦 Inventario U4 — 3 Llaves Foráneas"       # Texto de la barra de título
    page.bgcolor = ft.colors.BLUE_GREY_50                     # Color de fondo de la ventana (minúscula en Flet 0.24.1)
    page.padding = 20                                       # Espacio interno de la ventana
    page.window.width = 1100                              # Ancho inicial de la ventana en píxeles
    page.window.height = 750                              # Alto inicial de la ventana en píxeles

    repo_cat  = RepositorioCategoriaMySQL()                   # Repositorio de categorías (también crea las 4 tablas)
    repo_prov = RepositorioProveedorMySQL()                   # Repositorio de proveedores
    repo_usr  = RepositorioUsuarioMySQL()                     # Repositorio de usuarios
    repo_prod = RepositorioProductoMySQL()                    # Repositorio de productos

    producto_editando = [None]                            # Lista de 1 elemento (mutable dentro de closures)

    campo_nombre = ft.TextField(label="Nombre del producto", expand=True)  # Campo de texto: nombre
    campo_precio = ft.TextField(                            # Campo de texto: precio
        label="Precio ($)", expand=True,                  # Etiqueta visible y ancho expandido
        keyboard_type=ft.KeyboardType.NUMBER               # Teclado numérico en móviles
    )

    dd_categoria = ft.Dropdown(label="Categoría", expand=True)     # Dropdown para la FK 1
    dd_proveedor = ft.Dropdown(label="Proveedor", expand=True)     # Dropdown para la FK 2
    dd_usuario   = ft.Dropdown(label="Usuario",   expand=True)     # Dropdown para la FK 3

    lbl_estado = ft.Text("", size=14, color=ft.colors.GREEN_700)     # Mensaje de estado (vacío al inicio)

    tabla = ft.DataTable(                                  # Tabla donde se listan los productos
        columns=[                                          # Abre la lista de columnas
            ft.DataColumn(ft.Text("ID")),                     # Columna del ID
            ft.DataColumn(ft.Text("Nombre")),                 # Columna del nombre
            ft.DataColumn(ft.Text("Precio")),                 # Columna del precio
            ft.DataColumn(ft.Text("Categoría")),              # Columna del nombre de categoría (vía JOIN)
            ft.DataColumn(ft.Text("Proveedor")),              # Columna del nombre de proveedor (vía JOIN)
            ft.DataColumn(ft.Text("Usuario")),                # Columna del nombre de usuario (vía JOIN)
            ft.DataColumn(ft.Text("Acciones")),               # Columna de botones editar/eliminar
        ],                                                  # Cierra la lista de columnas
        rows=[],                                          # Empieza sin filas; se llenan al cargar los datos
    )                                                       # Cierra la creación de la tabla
    def cargar_dropdowns():                              # Llena los 3 Dropdown con un SELECT real de cada tabla
        """Llena los 3 Dropdown con las opciones actuales de la base de datos."""
        dd_categoria.options = [                       # Lista de opciones del Dropdown de categoría
            ft.dropdown.Option(key=str(c.id_categoria), text=c.nombre)  # 1 opción por categoría
            for c in repo_cat.leer_todos()                   # SELECT real a la tabla categorias
        ]
        dd_proveedor.options = [                       # Lista de opciones del Dropdown de proveedor
            ft.dropdown.Option(key=str(p.id_proveedor), text=p.nombre)  # 1 opción por proveedor
            for p in repo_prov.leer_todos()                  # SELECT real a la tabla proveedores
        ]
        dd_usuario.options = [                         # Lista de opciones del Dropdown de usuario
            ft.dropdown.Option(key=str(u.id_usuario), text=u.nombre)  # 1 opción por usuario
            for u in repo_usr.leer_todos()                    # SELECT real a la tabla usuarios
        ]
        page.update()                                  # Redibuja la página con las opciones cargadas

    def limpiar_formulario():                            # Deja el formulario listo para un producto nuevo
        """Vacía todos los campos del formulario."""
        campo_nombre.value = ""                          # Borra el nombre escrito
        campo_precio.value = ""                          # Borra el precio escrito
        dd_categoria.value = None                        # Quita la selección de categoría
        dd_proveedor.value = None                        # Quita la selección de proveedor
        dd_usuario.value = None                          # Quita la selección de usuario
        producto_editando[0] = None                     # Ya no hay producto en edición
        lbl_estado.value = ""                           # Borra el mensaje de estado
        page.update()                                  # Redibuja la página con los campos vacíos

    def actualizar_tabla():                              # Refresca la tabla con los datos actuales
        """Recarga y muestra todos los productos (con JOIN) en la tabla."""
        productos = repo_prod.leer_todos()                # Lee los productos con sus 3 FK ya resueltas
        tabla.rows = []                                # Limpia las filas actuales antes de reconstruirlas

        for p in productos:                            # Recorre cada producto para crear su fila
            def editar(e, prod=p):                       # Manejador del botón editar (prod=p fija el valor)
                cargar_para_editar(prod)                  # Llena el formulario con los datos de prod

            def borrar(e, prod=p):                        # Manejador del botón eliminar
                try:                                      # productos no tiene FK apuntándole, pero por si acaso
                    repo_prod.eliminar(prod.id_producto)      # Pide al repositorio borrar este producto
                    lbl_estado.value = f"🗑️ '{prod.nombre}' eliminado."  # Mensaje de éxito
                    lbl_estado.color = ft.colors.ORANGE_700  # Color naranja para "eliminado"
                except RegistroEnUsoError as ex:           # Si algo más llegara a depender de él
                    lbl_estado.value = f"❌ {ex}"          # Muestra el mensaje claro de la excepción
                    lbl_estado.color = ft.colors.RED_700    # Color rojo para el error
                actualizar_tabla()                          # Refresca la tabla sin el producto borrado

            tabla.rows.append(ft.DataRow(cells=[              # Crea la fila de la tabla para este producto
                ft.DataCell(ft.Text(str(p.id_producto))),       # Celda con el ID
                ft.DataCell(ft.Text(p.nombre)),                # Celda con el nombre
                ft.DataCell(ft.Text(f"${p.precio:,.2f}")),         # Celda con el precio formateado
                ft.DataCell(ft.Text(p.nombre_categoria)),       # Celda con el NOMBRE de categoría (JOIN)
                ft.DataCell(ft.Text(p.nombre_proveedor)),       # Celda con el NOMBRE de proveedor (JOIN)
                ft.DataCell(ft.Text(p.nombre_usuario)),         # Celda con el NOMBRE de usuario (JOIN)
                ft.DataCell(ft.Row([                          # Celda con los botones de acción
                    ft.IconButton(icon=ft.icons.EDIT, icon_color=ft.colors.BLUE, on_click=editar),  # Botón editar
                    ft.IconButton(icon=ft.icons.DELETE, icon_color=ft.colors.RED, on_click=borrar),  # Botón eliminar
                ])),                                          # Cierra la fila de botones y la celda de acciones
            ]))                                               # Cierra la creación de la fila y la agrega a tabla.rows
        page.update()                                  # Redibuja la página con la tabla actualizada

    def cargar_para_editar(producto: Producto):             # Pasa los datos de un producto al formulario
        """Llena el formulario con los datos del producto a editar."""
        producto_editando[0] = producto                  # Guarda referencia al producto en edición
        campo_nombre.value = producto.nombre             # Llena el campo nombre
        campo_precio.value = str(producto.precio)        # Llena el campo precio (convertido a texto)
        dd_categoria.value = str(producto.id_categoria)  # Selecciona la categoría actual en el Dropdown
        dd_proveedor.value = str(producto.id_proveedor)  # Selecciona el proveedor actual en el Dropdown
        dd_usuario.value = str(producto.id_usuario)      # Selecciona el usuario actual en el Dropdown
        lbl_estado.value = f"✏️ Editando: {producto.nombre}"  # Mensaje indicando que se está editando
        lbl_estado.color = ft.colors.BLUE_700           # Color azul para el mensaje de edición
        page.update()                                  # Redibuja la página con el formulario lleno

    def guardar(e):                                      # Manejador del botón Guardar (crea o actualiza)
        """Valida, y luego crea o actualiza el producto del formulario."""
        if (not campo_nombre.value or not campo_precio.value or  # Campos de texto vacíos
                not dd_categoria.value or not dd_proveedor.value or not dd_usuario.value):  # o FK sin elegir
            lbl_estado.value = "❌ Todos los campos son obligatorios."  # Mensaje de validación
            lbl_estado.color = ft.colors.RED_700           # Color rojo para el error
            page.update()                                  # Redibuja mostrando el error
            return                                          # Sale de la función sin guardar nada

        try:                                              # Intenta convertir el precio a número
            precio = float(campo_precio.value)            # Convierte el texto a número decimal
        except ValueError:                               # Si el texto no es un número válido
            lbl_estado.value = "❌ El precio debe ser un número."  # Mensaje de error de formato
            lbl_estado.color = ft.colors.RED_700
            page.update()
            return

        try:                                              # Intenta crear/actualizar (puede fallar por FK)
            if producto_editando[0] is None:                # Si no hay producto en edición -> modo CREAR
                nuevo = Producto(                          # Construye el objeto Producto nuevo
                    campo_nombre.value, precio,
                    int(dd_categoria.value), int(dd_proveedor.value), int(dd_usuario.value)
                )
                repo_prod.crear(nuevo)                       # Inserta el producto (puede lanzar ClaveForaneaInvalidaError)
                lbl_estado.value = f"✅ '{nuevo.nombre}' guardado."  # Mensaje de éxito al crear
            else:                                          # Si hay un producto siendo editado -> modo ACTUALIZAR
                p = producto_editando[0]                  # Recupera el producto en edición
                p.nombre = campo_nombre.value              # Actualiza el nombre
                p.precio = precio                          # Actualiza el precio
                p.id_categoria = int(dd_categoria.value)    # Actualiza la FK de categoría
                p.id_proveedor = int(dd_proveedor.value)    # Actualiza la FK de proveedor
                p.id_usuario = int(dd_usuario.value)        # Actualiza la FK de usuario
                repo_prod.actualizar(p)                    # Guarda los cambios (puede lanzar ClaveForaneaInvalidaError)
                lbl_estado.value = f"✅ '{p.nombre}' actualizado."  # Mensaje de éxito al actualizar
            lbl_estado.color = ft.colors.GREEN_700         # Color verde para el mensaje de éxito
        except ClaveForaneaInvalidaError as ex:           # Si alguna de las 3 FK no existe
            lbl_estado.value = f"❌ {ex}"                  # Muestra el mensaje claro de la excepción
            lbl_estado.color = ft.colors.RED_700           # Color rojo para el error
            page.update()                                  # Redibuja mostrando el error
            return                                          # Sale sin limpiar el formulario (para que el usuario corrija)

        limpiar_formulario()                              # Vacía el formulario para el siguiente registro
        actualizar_tabla()                                # Refresca la tabla con los datos más recientes

    page.add(                                          # Agrega los controles a la ventana, en orden
        ft.Text("📦 Inventario — 3 Llaves Foráneas", size=24, weight=ft.FontWeight.BOLD),  # Título
        ft.Container(                                      # Caja visual que agrupa el formulario
            content=ft.Column([                          # Organiza el formulario en columna
                ft.Row([campo_nombre, campo_precio]),         # Fila: nombre y precio
                ft.Row([dd_categoria, dd_proveedor, dd_usuario]),  # Fila: los 3 Dropdown de las FK
                ft.Row([                                  # Fila de botones de acción
                    ft.ElevatedButton("💾 Guardar", on_click=guardar),  # Botón Guardar
                    ft.OutlinedButton("🔄 Limpiar", on_click=lambda e: limpiar_formulario()),  # Botón Limpiar
                ]),
                lbl_estado,                                  # Mensaje de estado al final del formulario
            ]),
            padding=20, bgcolor=ft.colors.WHITE, border_radius=12,  # Estilo visual del contenedor
            margin=ft.margin.only(bottom=16),               # Margen inferior (ft.Margin exige los 4 lados; only() rellena con 0)
        ),
        ft.Container(                                      # Caja visual que envuelve la tabla
            content=ft.Column([tabla], scroll=ft.ScrollMode.AUTO),  # Columna con scroll que contiene la tabla
            bgcolor=ft.colors.WHITE, border_radius=12, padding=10,  # Estilo visual del contenedor
        ),
    )                                                       # Cierra page.add()

    cargar_dropdowns()                                  # Llena los 3 Dropdown al abrir la app
    actualizar_tabla()                                  # Llena la tabla con los productos existentes al abrir


ft.app(target=main)                                    # Punto de entrada: Flet lanza la app ejecutando main()
