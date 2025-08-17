from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Hidden, Layout
from django import forms

from .models import Page, Story


class StoryTitleForm(forms.ModelForm):
    """Form for editing a story's title"""

    class Meta:
        model = Story
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "text-2xl font-medium text-black uppercase tracking-wide w-full p-2",
                    "placeholder": "Enter story title...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = Layout(Field("title", css_class="form-input-base"))


class StoryDescriptionForm(forms.ModelForm):
    """Form for editing a story's description"""

    class Meta:
        model = Story
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4, "class": "w-full p-3", "placeholder": "Enter story description..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = Layout(Field("description", css_class="form-textarea"))


class PageContentForm(forms.ModelForm):
    """Form for editing a page's content"""

    class Meta:
        model = Page
        fields = ["content", "content_generating"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 6, "class": "form-textarea w-full p-3", "placeholder": "Enter page content..."}
            ),
            "content_generating": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False

        # Disable the textarea if content generation is active
        instance = kwargs.get("instance")
        if instance and instance.content_generating:
            self.fields["content"].widget.attrs["disabled"] = True
            self.fields["content"].widget.attrs["class"] += " disabled-blur disabled"

        self.helper.layout = Layout(Field("content", css_class="form-textarea"), Hidden("content_generating"))
