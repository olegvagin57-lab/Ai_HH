"""Tests for AI service"""
import pytest
from app.application.services.ai_service import ai_service


@pytest.mark.asyncio
async def test_extract_concepts():
    """Test concept extraction"""
    query = "Python developer with FastAPI experience"
    concepts = await ai_service.extract_concepts(query)
    
    assert isinstance(concepts, list)
    assert len(concepts) > 0
    assert all(isinstance(c, list) for c in concepts)


@pytest.mark.asyncio
async def test_analyze_resume():
    """Test resume analysis"""
    resume_text = """
    Senior Python Developer
    Experience: 5 years
    Skills: Python, FastAPI, MongoDB
    """
    concepts = [["python", "python developer"], ["fastapi", "fast api"]]
    
    result = await ai_service.analyze_resume(resume_text, concepts)
    
    assert "score" in result
    assert "summary" in result
    assert "questions" in result
    assert "ai_generated_detected" in result
    assert 1 <= result["score"] <= 10
    assert isinstance(result["questions"], list)
