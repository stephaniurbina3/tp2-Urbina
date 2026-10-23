"""Error propio de la aplicacion para consultas que no se pueden resolver."""


class ErrorConsulta(ValueError):
    """Una consulta no se puede resolver (codigo inexistente, categoria sin productos, etc.).

    El mensaje explica el motivo y esta pensado para mostrarse a quien usa el programa.
    """