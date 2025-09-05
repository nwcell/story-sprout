# Generate a story description for a picture book

Create an engaging story description (outline) for the following children's picture book:

{% include "_story.md" with story=story %}

{% if story.description %}
**IMPORTANT**: This story already has a description. Please create a SIGNIFICANTLY DIFFERENT description that takes the story in a fresh direction. Explore different themes, emotions, or plot elements while keeping the core concept.
{% endif %}

## Instructions

Create a compelling story description for this children's picture book. Your task is to:

1. **Age-Appropriate Content**: Design for children aged 2-3 with simple concepts and gentle themes
2. **Clear Story Arc**: Include a beginning, middle, and end with a satisfying resolution
3. **Engaging Characters**: Focus on relatable characters that children can connect with
4. **Learning Elements**: Incorporate subtle educational themes (sharing, kindness, problem-solving, etc.)
5. **Visual Storytelling**: Consider how the story will work with illustrations and visual elements
6. **Emotional Journey**: Include gentle conflicts and positive resolutions that build confidence
{% if story.description %}7. **Fresh Perspective**: Since there's already a description, explore a completely different angle - new characters, settings, or themes{% endif %}

## Response Format

Provide a concise story description (2-4 sentences) that outlines the main plot, characters, and theme. Focus on:
- What happens in the story
- Who the main character(s) are
- What problem they solve or adventure they have
- What children will learn or feel

**BAD EXAMPLE:**
"This is a complex narrative about a protagonist who encounters various obstacles and overcomes them through determination and wit, ultimately achieving their goals and learning valuable life lessons about perseverance."

**GOOD EXAMPLE:**
Little Bunny wants to help Mama make carrot soup, but everything goes wrong! The carrots roll away, the water spills, and Bunny feels sad. With Mama's gentle help, Bunny learns that mistakes are okay and that trying your best is what matters most.
