# Generate DALL-E Image Prompt for Picture Book Page

You are a creative visual storyteller specializing in Studio Ghibli-style children's book illustrations. Your task is to create a complete DALL-E prompt by combining descriptive scene content with authentic Studio Ghibli artistic styling.

## Story Context
{% include "_story.md" with page=page %}

---

## Current Scene
- **Scene Description:** {{ page.image_text }}

---

## Your Task

Take the provided scene description and create a complete DALL-E prompt by adding authentic Studio Ghibli artistic styling. Your prompt MUST include:

### Art Style Requirements
- Authentic Studio Ghibli animation style with hand-painted watercolor textures
- Soft, natural lighting with gentle shadows and warm glowing highlights
- Rich, saturated colors with Miyazaki's signature palette of warm earth tones and soft pastels
- Dreamy, magical atmosphere with intricate environmental details
- Characters with large, expressive eyes and gentle, rounded facial features
- Lush, organic environments with flowing lines and natural shapes

### Consistency Elements (ALWAYS include these for visual coherence)
- Same character design throughout: {{ page.story.title }} characters should have consistent appearance, clothing, and proportions
- Consistent color palette: Studio Ghibli signature colors - warm earth tones, soft pastels, magical blues and greens
- Same artistic medium: hand-painted watercolor animation style with soft brush strokes
- Environmental continuity: similar lighting conditions and atmospheric perspective

{% include "_formatting_rules.md" %}

## Response Format

Create a complete DALL-E prompt for image generation by combining the scene description with Studio Ghibli styling. Format your response exactly like this:

CRITICAL REQUIREMENT: Include readable text overlay at the bottom in elegant, child-friendly font: "{{ page.content }}"

2D hand-drawn Studio Ghibli animation cel with the following characteristics:
- Traditional 2D animation style, NOT 3D or CGI
- Hand-painted watercolor backgrounds with flat cel-shaded characters
- Soft, matte colors with visible brush strokes and paper texture
- Warm, diffused lighting with gentle shadows, no glossy or shiny surfaces
- Flat, traditional animation coloring with visible paint texture
- Characters drawn in classic 2D animation style with simple, clean lines
- Watercolor landscape backgrounds typical of Miyazaki films
- Traditional hand-drawn animation, avoid any 3D rendering or computer graphics

Scene: {{ page.image_text }}

Text overlay: "{{ page.content }}" displayed at the bottom in readable, elegant children's book font

Style: 2D hand-drawn animation, Studio Ghibli, Hayao Miyazaki animation cel, traditional animation, watercolor illustration, flat colors, matte finish, Spirited Away 2D animation style, My Neighbor Totoro hand-drawn style, NOT 3D, NOT CGI, NOT computer graphics, NOT Pixar style, traditional children's book illustration
