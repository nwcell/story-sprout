from django.template.loader import get_template

def generate_prompt(template_name: str, context: dict):
    template = get_template(template_name)
    return template.render(context)
