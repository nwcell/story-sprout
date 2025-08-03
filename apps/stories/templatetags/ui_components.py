from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('components/editable_field.html')
def editable_field(instance, field_name, update_url_name, display_url_name=None, **kwargs):
    """
    Renders an editable field with HTMX integration
    
    Parameters:
    - instance: The model instance
    - field_name: Name of the field to edit
    - update_url_name: URL name for the update view
    - display_url_name: URL name for the display view (to cancel edit)
    
    Optional kwargs:
    - editing: Whether the field is in edit mode (default: False)
    - field_type: Type of field ('text_input' or 'textarea', default based on length)
    - label: Label for the field (default: field_name.title())
    - show_label: Whether to show the label (default: True for textarea)
    - placeholder: Placeholder text
    - rows: Number of rows for textarea (default: 4)
    - size: Text size for text_input (default: '2xl')
    - weight: Font weight for text_input (default: 'medium')
    - text_transform: Text transform for text_input (default: 'uppercase' for title)
    - disabled: Whether the field is disabled
    - show_magic: Whether to show magic button
    - is_generating: Whether content is being generated
    - container_class: Additional classes for container
    - form_class: Additional classes for form
    - text_class: Additional classes for text
    - input_classes: Additional classes for input
    """
    # Get the instance UUID or ID for URL generation
    instance_id = getattr(instance, 'uuid', None) or instance.id
    
    # Determine field type based on content length if not specified
    field_type = kwargs.get('field_type')
    if not field_type:
        value = getattr(instance, field_name, '')
        if isinstance(value, str) and len(value) > 100:
            field_type = 'textarea'
        else:
            field_type = 'text_input'
    
    # Generate URLs
    # Determine if we should use story_uuid or pk based on model type
    is_story = instance.__class__.__name__ == 'Story'
    param_name = 'story_uuid' if is_story else 'pk'
    
    # Generate the URLs with the appropriate parameter name
    update_url = reverse(update_url_name, kwargs={param_name: instance_id})
    display_url = None
    if display_url_name:
        display_url = reverse(display_url_name, kwargs={param_name: instance_id})
    
    # Magic URL for content generation (if applicable)
    magic_url = kwargs.get('magic_url')
    if kwargs.get('show_magic') and not magic_url and hasattr(instance, 'toggle_content_generating_url'):
        magic_url = instance.toggle_content_generating_url()
    
    # Get label from kwargs or create from field_name
    label = kwargs.get('label', field_name.replace('_', ' ').title())
    
    # Determine if label should be shown
    show_label = kwargs.get('show_label', field_type == 'textarea')
    
    # Get placeholder text or generate based on field_name
    placeholder = kwargs.get('placeholder', f"Click to add {field_name.replace('_', ' ')}...")
    
    # Field ID for targeting
    field_id = kwargs.get('field_id', f"{instance.__class__.__name__.lower()}-{field_name}-{instance_id}")
    
    # Form ID
    form_id = kwargs.get('form_id', f"{field_id}-form")
    
    return {
        'editing': kwargs.get('editing', False),
        'field_type': field_type,
        'field_name': field_name,
        'value': getattr(instance, field_name, ''),
        'update_url': update_url,
        'edit_url': update_url,  # For display mode, edit_url points to update view
        'display_url': display_url,
        'field_id': field_id,
        'form_id': form_id,
        'label': label,
        'show_label': show_label,
        'placeholder': placeholder,
        'rows': kwargs.get('rows', 4),
        'size': kwargs.get('size', '2xl'),
        'weight': kwargs.get('weight', 'medium'),
        'text_transform': kwargs.get('text_transform', 'uppercase' if field_name == 'title' else ''),
        'disabled': kwargs.get('disabled', False),
        'show_magic': kwargs.get('show_magic', False),
        'is_generating': kwargs.get('is_generating', False),
        'magic_url': magic_url,
        'magic_target': kwargs.get('magic_target', 'closest form'),
        'container_class': kwargs.get('container_class', 'group'),
        'form_class': kwargs.get('form_class', ''),
        'text_class': kwargs.get('text_class', ''),
        'input_classes': kwargs.get('input_classes', ''),
        'button_layout': kwargs.get('button_layout', 'flex-col'),
    }

@register.inclusion_tag('components/form_buttons/button_group.html')
def form_button_group(update_url=None, display_url=None, show_magic=False, is_generating=False, disabled=False, **kwargs):
    """Renders a standard form button group"""
    return {
        'update_url': update_url,
        'get_url': display_url, 
        'show_magic': show_magic,
        'is_generating': is_generating,
        'disabled': disabled,
        'magic_url': kwargs.get('magic_url'),
        'magic_target': kwargs.get('magic_target', 'closest form'),
        'layout': kwargs.get('layout', 'flex-col'),
    }
