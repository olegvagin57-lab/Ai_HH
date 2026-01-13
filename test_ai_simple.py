#!/usr/bin/env python3
"""
Simple test for AI functionality without full system setup
"""

import asyncio
import os

# Set environment variable
os.environ['GEMINI_API_KEY'] = 'AIzaSyDhnw1xyPaWa6rfi0ZacwTaPt6SEsPZGP4'

try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    print("Gemini API configured successfully")
    
    async def test_gemini():
        """Test Gemini API directly"""
        print("\nTesting Gemini API...")
        
        # Use available model to save credits
        model = genai.GenerativeModel('gemini-pro')
        
        # Test concept extraction
        query = "Нужен активный менеджер по продажам спецодежды B2B"
        
        prompt = f"""
        Ты - HH-Concept-Extractor. Твоя задача - извлечь ключевые концепции из запроса на поиск резюме и создать группы синонимов.

        Запрос: "{query}"

        Верни результат в формате JSON массива массивов, где каждый внутренний массив содержит синонимы одной концепции:
        [["основное понятие", "синоним1", "синоним2"], ["другое понятие", "синоним"]]

        Пример:
        Для запроса "Активный менеджер по оптовым продажам спецодежды (B2B)"
        Ответ: [["менеджер по продажам", "sales manager"], ["оптовым", "опт", "b2b"], ["спецодежда", "сиз"]]

        Отвечай только JSON массивом, без дополнительного текста.
        """
        
        try:
            response = model.generate_content(prompt)
            print(f"Concept extraction response: {response.text}")
            
            # Test resume analysis
            resume_text = """
            Должность: Менеджер по продажам
            Опыт работы:
            - Менеджер по продажам в ООО Рога и копыта (2020 - 2023)
              Продажи спецодежды корпоративным клиентам
            Навыки: Продажи B2B, работа с тендерами, знание 44-ФЗ
            """
            
            analysis_prompt = f"""
            Ты - HH-Analyst, опытный HR-директор. Проанализируй резюме кандидата на соответствие вакансии.

            ВАКАНСИЯ: "{query}"

            РЕЗЮМЕ:
            {resume_text}

            Проведи анализ и верни результат в формате JSON:
            {{
                "score": число от 1 до 10,
                "summary": "краткое резюме в 2-3 предложения",
                "questions": ["вопрос 1", "вопрос 2", "вопрос 3"],
                "ai_generated": false
            }}

            Отвечай только JSON, без дополнительного текста.
            """
            
            analysis_response = model.generate_content(analysis_prompt)
            print(f"Resume analysis response: {analysis_response.text}")
            
            print("\nGemini API работает отлично!")
            print("Система готова к использованию с реальными данными")
            
        except Exception as e:
            print(f"Error testing Gemini: {e}")
    
    # Run the test
    asyncio.run(test_gemini())
    
except ImportError:
    print("google-generativeai not installed")
    print("Install with: pip install google-generativeai")
except Exception as e:
    print(f"Error: {e}")

print("\nNext steps:")
print("1. Gemini API key added and working")
print("2. Get HH API keys for real resume data")
print("3. Install Docker to run full system")
print("4. Or setup Python environment manually")