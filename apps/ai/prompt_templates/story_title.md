# Sugest a title for a picture book

Suggest a fun picturebook title for the following story:

{% include "_story.md" with story=story %}

{% if story.title %}
**IMPORTANT**: This story already has the title "{{ story.title }}". Please create a NOTICEABLY DIFFERENT title that explores the story from a fresh angle. Avoid similar words, themes, or structure.
{% endif %}

## Instructions

Create a fun, catchy title for this children's picture book. Your task is to:

1. **Make it Kid-Friendly**: Use simple, playful language that appeals to children aged 2-3
2. **Capture the Story**: Reflect the main theme, character, or adventure from the book
3. **Keep it Light**: Make it fun, whimsical, and engaging - avoid scary or serious themes
4. **Make it Memorable**: Use rhythm, rhyme, or alliteration when possible
5. **Stay Concise**: Keep it short and easy to remember
{% if story.title %}6. **Be Creative & Different**: Since there's already a title, focus on a completely different aspect of the story - maybe a secondary character, a different emotion, or an alternate perspective{% endif %}

## Response Format

Provide just the title (2-5 words). No quotation marks, explanations, or additional text.

**BAD EXAMPLE:**
"This is a story about a little train who goes on adventures and learns important lessons"

**GOOD EXAMPLE:**
Chug's Big Adventure
