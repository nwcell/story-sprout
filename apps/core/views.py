from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views import View


class HtmxEditableFieldView(View):
    """Base view for handling editable fields via HTMX

    This is a generic base class for HTMX-powered editable fields.
    Subclasses should implement check_permissions() according to their specific model requirements.

    Attributes:
        model: The Django model class to be edited
        form_class: The form class for editing
        template_name: Single template for both display and edit modes
        field_name: Name of the field being edited
        field_label: Human-readable label for the field (defaults to capitalized field_name)
        placeholder: Placeholder text for empty fields
        permission_denied_message: Message to display when permission is denied
    """

    model = None
    form_class = None
    template_name = None  # Use this as a single template for both display and edit modes
    field_name = None
    field_label = None  # Defaults to capitalized field_name if not set
    placeholder = "Click to edit"
    permission_denied_message = "You don't have permission to edit this item."

    def check_permissions(self, obj):
        """Check if the current user has permission to edit the object

        This method MUST be implemented by subclasses with appropriate permission logic.
        The base implementation always returns False for safety.

        Args:
            obj: The model instance being edited

        Returns:
            bool: True if the user has permission, False otherwise
        """
        return False  # Secure by default - subclasses must override

    def get_object(self, request, *args, **kwargs):
        """Get the object being edited"""
        # The default implementation assumes there's a uuid or pk in the URL pattern
        lookup_field = "uuid" if "uuid" in kwargs else "pk"
        lookup_value = kwargs.get(lookup_field) or kwargs.get("pk")
        return get_object_or_404(self.model, **{lookup_field: lookup_value})

    def get_context_data(self, obj, form=None, mode="display"):
        """Get the context data for the template"""
        field_value = getattr(obj, self.field_name) if self.field_name else None

        # Get label - use field_label if set, otherwise capitalize field_name
        label = self.field_label if self.field_label else self.field_name.capitalize() if self.field_name else ""

        context = {
            "mode": mode,
            self.model.__name__.lower(): obj,
            "value": field_value,
            "url": self.request.path,  # Add the current request URL to the context
            "field_name": self.field_name,  # Ensure field_name is always in context
            "label": label,  # Add field label
            "placeholder": self.placeholder,  # Add placeholder text
            "slot": field_value,  # Add value as slot for Cotton compatibility
        }

        if form:
            context["form"] = form

        return context

    def get(self, request, *args, **kwargs):
        # Only proceed if it's an HTMX request
        if not request.htmx:
            return HttpResponseForbidden("HTMX requests only")

        # Get object
        obj = self.get_object(request, *args, **kwargs)

        # Check permissions
        if not self.check_permissions(obj):
            return HttpResponseForbidden("You don't have permission to edit this item")

        # Determine mode: edit or display
        mode = request.GET.get("mode", "display")

        if mode == "edit" and self.form_class:
            # Edit mode: include the form in context
            form = self.form_class(instance=obj)
            context = self.get_context_data(obj, form=form, mode="edit")
        else:
            # Display mode: just include the value
            context = self.get_context_data(obj, mode="display")

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Only proceed if it's an HTMX request
        if not request.htmx:
            return HttpResponseForbidden("HTMX requests only")

        # Get object
        obj = self.get_object(request, *args, **kwargs)

        # Check permissions
        if not self.check_permissions(obj):
            return HttpResponseForbidden("You don't have permission to edit this item")

        # Process form
        form = self.form_class(request.POST, instance=obj)

        if form.is_valid():
            form.save()
            # After successful save, return the display view
            context = self.get_context_data(obj, mode="display")
            return render(request, self.template_name, context)
        else:
            # If form is invalid, stay in edit mode
            context = self.get_context_data(obj, form=form, mode="edit")
            return render(request, self.template_name, context)


class HtmxToggleView(View):
    """Base view for handling toggle fields via HTMX

    This is a generic base class for HTMX-powered boolean toggle fields.
    Subclasses should implement check_permissions() according to their specific model requirements.

    Attributes:
        model: The Django model class to be edited
        template_name: Template for rendering the updated state
        field_name: Name of the boolean field being toggled
        permission_denied_message: Message to display when permission is denied
    """

    model = None
    template_name = None
    field_name = None
    permission_denied_message = "You don't have permission to edit this item."

    def check_permissions(self, obj):
        """Check if the current user has permission to toggle this object

        This method MUST be implemented by subclasses with appropriate permission logic.
        The base implementation always returns False for safety.

        Args:
            obj: The model instance being edited

        Returns:
            bool: True if the user has permission, False otherwise
        """
        return False  # Secure by default - subclasses must override

    def get_object(self, request, *args, **kwargs):
        """Get the object being toggled

        Args:
            request: The current request
            *args, **kwargs: Positional and keyword arguments from URL

        Returns:
            The model instance to toggle
        """
        if "pk" in kwargs:
            return get_object_or_404(self.model, pk=kwargs["pk"])
        elif "uuid" in kwargs:
            return get_object_or_404(self.model, uuid=kwargs["uuid"])
        else:
            raise ValueError("No ID provided to toggle view")

    def post(self, request, *args, **kwargs):
        """Toggle a boolean field value"""
        if not request.htmx:
            return HttpResponseForbidden("HTMX requests only")

        # Get object
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        # Check permissions
        if not self.check_permissions(obj):
            return HttpResponseForbidden(self.permission_denied_message)

        # Toggle the field value
        current_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, not current_value)
        obj.save()

        # Return the template with the updated object
        context = {self.model.__name__.lower(): obj}
        return render(request, self.template_name, context)
