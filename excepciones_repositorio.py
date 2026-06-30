# =====================================================
# excepciones_repositorio.py
# Excepciones personalizadas para la capa de acceso a datos (Repository/DAO)
# =====================================================


class ErrorRepositorio(Exception):              # Clase base de todos los errores de esta capa
    """Clase base para todos los errores de la capa de datos."""
    pass                                          # No agrega comportamiento propio, solo agrupa


class ConexionFallidaError(ErrorRepositorio):    # Se lanza si no se puede abrir la conexión
    """Se lanza cuando no se puede conectar a MySQL."""

    def __init__(self, detalle: str):             # Recibe el texto técnico del error original
        super().__init__(f"No se pudo conectar a la base de datos: {detalle}")  # Mensaje final legible


class RegistroNoEncontradoError(ErrorRepositorio):  # Se lanza al buscar un ID que no existe
    """Se lanza al actualizar/eliminar un ID que no existe."""

    def __init__(self, entidad: str, id_buscado: int):  # Recibe el nombre de la tabla y el ID buscado
        super().__init__(f"No existe {entidad} con id {id_buscado}.")  # Mensaje final legible


class ClaveForaneaInvalidaError(ErrorRepositorio):  # Traduce el error MySQL 1452
    """Se lanza al insertar/actualizar con un ID de FK que no existe (error MySQL 1452)."""

    def __init__(self, detalle: str):             # Recibe el texto técnico del error original
        super().__init__(f"Llave foránea inválida: {detalle}")  # Mensaje final legible


class RegistroEnUsoError(ErrorRepositorio):      # Traduce el error MySQL 1451
    """Se lanza al eliminar un registro padre referenciado por otra tabla (error MySQL 1451)."""

    def __init__(self, entidad: str, id_usado: int):  # Recibe el nombre de la tabla y el ID en uso
        super().__init__(f"No se puede eliminar {entidad} (id {id_usado}): está en uso por otra tabla.")  # Mensaje final
        