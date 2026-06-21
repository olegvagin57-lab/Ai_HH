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


def test_preliminary_scoring():
    """Test _smart_preliminary_score from search tasks"""
    import re
    from celery_app.tasks.search_tasks import _smart_preliminary_score

    exact = _smart_preliminary_score(
        {"title": "Оператор нефтеперекачивающей станции",
         "experience": [{"description": "17 лет 6 месяцев"}],
         "salary": {"amount": 200000}, "age": 49},
        "оператор нефтеперекачивающей станции",
        [["оператор", "операторщик"], ["нефтепровод", "трубопровод"], ["НПС", "станция"]]
    )
    unrelated = _smart_preliminary_score(
        {"title": "Бухгалтер", "experience": [{"description": "15 лет"}],
         "salary": {"amount": 60000}, "age": 45},
        "оператор нефтеперекачивающей станции",
        [["оператор", "операторщик"], ["нефтепровод", "трубопровод"], ["НПС", "станция"]]
    )

    assert isinstance(exact, float)
    assert 0 <= exact <= 10
    assert isinstance(unrelated, float)
    # Relevant candidate must score significantly higher than unrelated one
    assert exact > unrelated + 3
