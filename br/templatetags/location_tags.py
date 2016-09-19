from django import template

register = template.Library()


@register.filter
def extract_ancestor_name(queryset, type_name):
    ancestor = queryset.get(type__name=type_name)
    if not ancestor:
        return ''
    return ancestor.name
