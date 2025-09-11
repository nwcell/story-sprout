```json
{
  "story": {
    "title": "{{ page.story.title }}",
    "description": "{{ page.story.description }}",
    "target_age": "2-3 years",
    "total_pages": {{ page.story.page_count }},
    "current_page": {{ page.page_number }}
  },
  "pages": [
    {% for p in page.story.pages.all %}
    {
      "page_number": {{ p.page_number }},
      "is_current_page": {% if p.page_number == page.page_number %}true{% else %}false{% endif %},
      "content": "{{ p.content|escapejs }}",
      {% if p.page_number == page.page_number and p.content_draft %}
      "content_draft": "{{ p.content_draft|escapejs }}",
      {% endif %}
      "image_description": "{{ p.image_text|escapejs }}"
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
  ]
}
```
