## Context
{% if page %}
- Title: {{page.story.title}}
- Target Age Range: 2-3 years
- Page Count: {{page.story.page_count}}
- Current Page: {{page.page_number}} of {{page.story.page_count}}
- Generation Type: text (text content or image description)

## Book Summary
{{page.story.description}}

## Pages

{% for p in page.story.pages.all %}
### Page {{p.page_number}}{% if p.page_number == page.page_number %} (CURRENT){% endif %}
#### Content
{{p.content}}
{% if p.page_number == page.page_number %}
#### Draft Content
{{p.content_draft}}
{% endif %}
#### Image Description
{{p.image_text}}
{% endfor %}

{% else %}
- Title: {{story.title}}
- Target Age Range: 2-3 years
- Page Count: {{story.page_count}}

## Book Summary
{{story.description}}

## Pages

{% for p in story.pages.all %}
### Page {{p.page_number}}
#### Content
{{p.content}}
#### Image Description
{{p.image_text}}
{% endfor %}
{% endif %}
