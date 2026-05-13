from jinja2 import Environment
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import mark_safe
from django.middleware.csrf import get_token

# FUNCIONES CUSTOM PARA USAR EN LAS TEMPLATES
# date_format: Permite formatear fechas en las templates de Jinja2.
from datetime import datetime

def date_format(value, fmt="%d/%m/%Y"):
    if value is None:
        return ""
    return value.strftime(fmt)

# render_field: Permite renderizar un campo de formulario con atributos personalizados.
def render_field(field, **attrs):
    if field is None:
        return ""

    if not hasattr(field, "as_widget"):
        return field

    widget = field.field.widget
    final_attrs = dict(widget.attrs)

    extra_class = attrs.pop("class", None)
    if extra_class:
        final_attrs["class"] = (
            final_attrs.get("class", "") + " " + extra_class
        ).strip()

    # limpiar None
    clean_attrs = {}
    for k, v in attrs.items():
        if v is True:
            clean_attrs[k] = k  # boolean HTML attribute
        elif v not in (None, False):
            clean_attrs[k] = v

    final_attrs.update(clean_attrs)

    return field.as_widget(attrs=final_attrs)

# CONFIGURARION GENERAL DE JINJA2 PARA USAR EN EL PROYECTO
def environment(**options):
    env = Environment(
        **options
        )

    env.globals.update({
        "static": static,
        "url": reverse,
        "render_field": render_field,
        "date_format": date_format,
        "csrf_token_only": lambda request: get_token(request),
    })

    env.globals["render_csrf_token"] = lambda request: (
    f"<input type='hidden' name='csrfmiddlewaretoken' value='{get_token(request)}'>"
    )


    env.filters.update({
        "safe": mark_safe,
    })

    return env