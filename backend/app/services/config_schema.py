"""Validación de configuración de instalaciones contra el esquema de la EVA.

Subconjunto mínimo de JSON Schema: `properties` (con `type`) y `required`.
Nunca se aceptan claves no declaradas.
"""

_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}


def validate_config(schema: dict | None, config: dict) -> None:
    schema = schema or {}
    if not schema:
        if config:
            raise ValueError("esta EVA no admite configuración")
        return

    properties: dict = schema.get("properties", {})
    required = set(schema.get("required", []))

    extra = set(config) - set(properties)
    if extra:
        raise ValueError(f"claves de configuración no permitidas: {', '.join(sorted(extra))}")

    missing = required - set(config)
    if missing:
        raise ValueError(f"faltan claves de configuración requeridas: {', '.join(sorted(missing))}")

    for key, value in config.items():
        expected = properties.get(key, {}).get("type")
        if expected is None:
            continue
        python_type = _TYPE_MAP.get(expected)
        if python_type is None:
            raise ValueError(f"tipo de esquema desconocido: {expected}")
        if isinstance(value, bool) and expected in {"integer", "number"}:
            raise ValueError(f"tipo inválido para '{key}' (se esperaba {expected})")
        if not isinstance(value, python_type):
            raise ValueError(f"tipo inválido para '{key}' (se esperaba {expected})")
