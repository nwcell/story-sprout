from django.template.loader import get_template


def generate_prompt(template_name: str, context: dict):
    template = get_template(template_name)
    return template.render(context)

def generate_page_content_prompt(story, page_num, generation_type="content"):
    return generate_prompt("page_content.md", {
        "book_title": story.title,
        "age_range": "2-3 years",
        "page_count": story.pages.count(),
        "current_page": page_num,
        "generation_type": generation_type,
        "book_summary": story.description,
        "pages": story.pages.all().order_by("order"),
    })
        