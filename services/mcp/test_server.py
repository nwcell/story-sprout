"""Tests for the Story Sprout MCP Server."""

from server import StoryRequest, StoryResponse, create_story, get_story_stats


def test_create_story():
    """Test story creation."""
    request = StoryRequest(title="Test Story", content="This is a test story content.", user_id="user123")

    response = create_story(request)

    assert isinstance(response, StoryResponse)
    assert response.title == "Test Story"
    assert response.content == "This is a test story content."
    assert response.status == "draft"
    assert response.id.startswith("story_")


def test_create_story_minimal():
    """Test story creation with minimal data."""
    request = StoryRequest(title="Minimal Story")

    response = create_story(request)

    assert isinstance(response, StoryResponse)
    assert response.title == "Minimal Story"
    assert response.content == ""
    assert response.status == "draft"


def test_get_story_stats():
    """Test getting story statistics."""
    stats = get_story_stats()

    assert isinstance(stats, dict)
    assert "total_stories" in stats
    assert "published_stories" in stats
    assert "draft_stories" in stats
    assert "total_words" in stats
    assert "active_writers" in stats

    # Verify the mock data
    assert stats["total_stories"] == 42
    assert stats["published_stories"] == 15
    assert stats["draft_stories"] == 27
