"""Tests for search service"""
import pytest
from app.application.services.search_service import search_service
from app.domain.entities.search import Search


@pytest.mark.asyncio
async def test_create_search(test_user):
    """Test search creation"""
    search = await search_service.create_search(
        user=test_user,
        query="Python developer",
        city="Москва"
    )
    
    assert search.query == "Python developer"
    assert search.city == "Москва"
    assert search.status == "pending"
    assert search.user_id == str(test_user.id)


@pytest.mark.asyncio
async def test_preliminary_scoring():
    """Test preliminary scoring"""
    resume_data = {
        "title": "Python Developer",
        "experience": [
            {
                "position": "Senior Python Developer",
                "description": "FastAPI development"
            }
        ],
        "skills": [
            {"name": "Python"},
            {"name": "FastAPI"},
            {"name": "MongoDB"}
        ]
    }
    concepts = [["python", "python developer"], ["fastapi", "fast api"]]
    
    score = await search_service.preliminary_scoring(resume_data, concepts)
    
    assert isinstance(score, float)
    assert 0 <= score <= 10
