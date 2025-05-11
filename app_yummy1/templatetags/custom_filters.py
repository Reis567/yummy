from django import template

register = template.Library()

@register.filter(name='abs')
def absolute(value):
    """Retorna o valor absoluto de um número"""
    return abs(value)

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adiciona uma classe CSS a um campo de formulário
    Uso: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='attr')
def set_attr(field, attr_args):
    """
    Adiciona um atributo a um campo de formulário
    Uso: {{ form.field|attr:"placeholder:Digite seu texto" }}
    """
    args = attr_args.split(':')
    if len(args) != 2:
        return field
    
    attr_name = args[0]
    attr_value = args[1]
    
    attrs = {}
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and hasattr(field.field.widget, 'attrs'):
        attrs = field.field.widget.attrs.copy()
    
    attrs[attr_name] = attr_value
    return field.as_widget(attrs=attrs)

@register.filter(name='field_type')
def field_type(field):
    """
    Retorna o tipo do campo de formulário
    Uso: {% if form.field|field_type == "CheckboxInput" %}...{% endif %}
    """
    return field.field.widget.__class__.__name__