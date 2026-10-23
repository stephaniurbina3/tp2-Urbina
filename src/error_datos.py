"""Error propio de la aplicacion para datos que no cumplen las reglas."""


class ErrorDatos(ValueError):
    """Un dato no cumple las reglas del catalogo; el mensaje explica el motivo.

    tipo: identifica la regla incumplida (por ejemplo "codigo_invalido").
    detalle: explicacion legible del problema concreto (es tambien el mensaje del error).
    """

    def __init__(self, tipo, detalle):
        super().__init__(detalle)
        self.tipo = tipo
        self.detalle = detalle