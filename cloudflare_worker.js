const GEMINI_API_KEY = 'AIzaSyDhnw1xyPaWa6rfi0ZacwTaPt6SEsPZGP4';
// Используем gemini-2.5-flash - новая модель, которую вы используете
// Лимиты бесплатного плана:
// - RPM (Requests per minute): 5 запросов/минуту
// - RPD (Requests per day): 20 запросов/день
// - TPM (Tokens per minute): 250K токенов/минуту
const GEMINI_MODEL = 'gemini-2.5-flash';
// Используем v1beta API для gemini-2.5-flash
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

// CORS заголовки
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request) {
    // Обрабатываем предварительные OPTIONS-запросы (для CORS)
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Обработка endpoint для извлечения концептов
      if (path === '/extract_concepts' && request.method === 'POST') {
        return await handleExtractConcepts(request);
      }

      // Обработка endpoint для анализа резюме
      if (path === '/analyze_resume' && request.method === 'POST') {
        return await handleAnalyzeResume(request);
      }

      // Для всех остальных запросов - проксируем напрямую к Gemini API
      return await proxyToGemini(request, url);
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({ 
        error: error.message,
        details: 'Cloudflare Worker ошибка'
      }), {
        status: 500,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        },
      });
    }
  },
};

// Извлечение концептов из запроса
async function handleExtractConcepts(request) {
  const body = await request.json();
  const query = body.query || '';

  const prompt = `Извлеки ключевые концепты и их синонимы из следующего запроса на русском языке. 
Верни результат в формате JSON массива массивов, где каждый внутренний массив содержит концепт и его синонимы.
Пример: [["python", "питон"], ["разработчик", "developer", "программист"]]

Запрос: ${query}

Верни только JSON, без дополнительного текста:`;

  const response = await callGeminiAPI(prompt);
  
  if (!response || !response.candidates || !response.candidates[0]) {
    throw new Error('Invalid response from Gemini API');
  }

  const text = response.candidates[0].content.parts[0].text;
  
  // Парсим JSON из ответа
  let concepts;
  try {
    // Убираем markdown код блоки если есть
    const jsonMatch = text.match(/\[\[.*?\]\]/s);
    if (jsonMatch) {
      concepts = JSON.parse(jsonMatch[0]);
    } else {
      concepts = JSON.parse(text.trim());
    }
  } catch (e) {
    // Fallback: простой парсинг
    console.warn('Failed to parse concepts, using fallback');
    const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    concepts = words.slice(0, 10).map(w => [w, w]);
  }

  return new Response(JSON.stringify({ concepts }), {
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    },
  });
}

// Анализ резюме
async function handleAnalyzeResume(request) {
  const body = await request.json();
  const resumeText = body.resume_text || '';
  const concepts = body.concepts || [];
  const vacancyRequirements = body.vacancy_requirements || {};

  // Формируем prompt для анализа
  const conceptsText = concepts.map(c => c.join(', ')).join('; ');
  
  // Build vacancy requirements text if available
  let vacancyText = '';
  if (vacancyRequirements && Object.keys(vacancyRequirements).length > 0) {
    vacancyText = '\n\nТребования к вакансии:\n';
    if (vacancyRequirements.technical_skills) {
      vacancyText += `Технические навыки: ${vacancyRequirements.technical_skills}\n`;
    }
    if (vacancyRequirements.experience) {
      vacancyText += `Опыт работы: ${vacancyRequirements.experience}\n`;
    }
    if (vacancyRequirements.education) {
      vacancyText += `Образование: ${vacancyRequirements.education}\n`;
    }
  }

  let prompt = `Ты - опытный HR-аналитик и рекрутер. Проведи ГЛУБОКИЙ анализ резюме кандидата и дай детальную оценку его соответствия требованиям.

Резюме кандидата:
${resumeText}

Ключевые требования для поиска: ${conceptsText}${vacancyText}

Проведи детальный анализ по следующим аспектам:

1. **ОПЫТ РАБОТЫ**: 
   - Оцени релевантность опыта работы требованиям
   - Проанализируй карьерный рост и стабильность
   - Оцени длительность работы в каждой компании
   - Выяви пробелы в опыте или частые смены работы

2. **ТЕХНИЧЕСКИЕ НАВЫКИ**:
   - Оцени соответствие технических навыков требованиям
   - Определи уровень владения каждым навыком
   - Выяви недостающие критичные навыки
   - Оцени актуальность технологий

3. **ОБРАЗОВАНИЕ**:
   - Оцени релевантность образования
   - Учти дополнительное образование и сертификаты
   - Оцени престижность учебных заведений

4. **СОФТ-СКИЛЛЫ**:
   - Оцени коммуникативные навыки
   - Оцени способность к работе в команде
   - Оцени лидерские качества (если релевантно)

5. **ПОДХОДИТ ЛИ КАНДИДАТ**:
   - Детально объясни, ПОЧЕМУ кандидат подходит или не подходит
   - Укажи конкретные факты из резюме
   - Оцени потенциал роста

6. **НА ЧТО ОБРАТИТЬ ВНИМАНИЕ**:
   - Выяви подозрительные моменты
   - Укажи на несоответствия
   - Отметь красные флаги

7. **ЧТО СПРОСИТЬ НА СОБЕСЕДОВАНИИ**:
   - Подготовь конкретные вопросы для проверки опыта
   - Вопросы для уточнения пробелов
   - Вопросы для оценки мотивации

Верни результат ТОЛЬКО в формате JSON со следующими полями:
{
  "score": число от 1 до 10 (общая оценка соответствия),
  "summary": "краткое резюме анализа на русском языке (2-3 предложения)",
  "match_explanation": "ПОДРОБНОЕ объяснение на русском языке (5-7 предложений): почему кандидат подходит или не подходит, какие конкретные факты из резюме это подтверждают, какие есть сильные и слабые стороны",
  "strengths": ["конкретная сильная сторона 1 с фактами", "конкретная сильная сторона 2 с фактами", "конкретная сильная сторона 3"],
  "weaknesses": ["конкретная слабая сторона 1 с фактами", "конкретная слабая сторона 2 с фактами"],
  "questions": ["конкретный вопрос для собеседования 1 (для проверки опыта/навыков)", "конкретный вопрос 2 (для уточнения пробелов)", "конкретный вопрос 3 (для оценки мотивации)", "конкретный вопрос 4", "конкретный вопрос 5"],
  "ai_generated_detected": true/false (определи, написано ли резюме с помощью AI),
  "evaluation_details": {
    "technical_skills": {
      "score": число от 1 до 10,
      "details": "детальный анализ технических навыков: какие навыки есть, каких не хватает, уровень владения",
      "explanation": "объяснение оценки: почему именно такая оценка, на основе каких фактов"
    },
    "experience": {
      "score": число от 1 до 10,
      "details": "детальный анализ опыта работы: релевантность опыта, карьерный рост, стабильность, длительность работы",
      "explanation": "объяснение оценки: почему именно такая оценка, какие проекты/компании наиболее релевантны"
    },
    "education": {
      "score": число от 1 до 10,
      "details": "детальный анализ образования: релевантность, престижность, дополнительное образование",
      "explanation": "объяснение оценки: почему именно такая оценка"
    },
    "soft_skills": {
      "score": число от 1 до 10,
      "details": "детальный анализ софт-скиллов: что видно из резюме, что можно предположить",
      "explanation": "объяснение оценки: почему именно такая оценка"
    }
  },
  "match_percentage": число от 0 до 100 (процент соответствия требованиям),
  "red_flags": ["конкретный красный флаг 1 с объяснением", "конкретный красный флаг 2 с объяснением"],
  "recommendation": "ДЕТАЛЬНАЯ рекомендация на русском языке (3-5 предложений): стоит ли приглашать на собеседование, почему, на что обратить внимание при собеседовании, какие вопросы задать, какой потенциал у кандидата",
  "interview_focus": "На чем сосредоточиться на собеседовании: конкретные темы и вопросы для обсуждения",
  "career_trajectory": "Анализ карьерной траектории: рост, стабильность, логичность переходов"
}

ВАЖНО:
- Будь конкретным и ссылайся на факты из резюме
- Давай развернутые объяснения, а не краткие ответы
- Вопросы должны быть конкретными и релевантными
- Рекомендация должна быть детальной и обоснованной

Верни только JSON, без дополнительного текста:`;

  if (Object.keys(vacancyRequirements).length > 0) {
    prompt += `\n\nДополнительные требования к вакансии: ${JSON.stringify(vacancyRequirements)}`;
  }

  const response = await callGeminiAPI(prompt);
  
  if (!response || !response.candidates || !response.candidates[0]) {
    throw new Error('Invalid response from Gemini API');
  }

  const text = response.candidates[0].content.parts[0].text;
  
  // Парсим JSON из ответа
  let result;
  try {
    // Убираем markdown код блоки если есть
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      result = JSON.parse(jsonMatch[0]);
    } else {
      result = JSON.parse(text.trim());
    }
  } catch (e) {
    console.error('Failed to parse Gemini response:', e);
    throw new Error('Failed to parse Gemini API response');
  }

  // Убеждаемся, что все обязательные поля присутствуют
  if (!result.score) result.score = 5;
  if (!result.summary) result.summary = 'Анализ выполнен';
  if (!result.questions) result.questions = [];
  if (result.ai_generated_detected === undefined) result.ai_generated_detected = false;
  if (!result.red_flags) result.red_flags = [];
  if (!result.strengths) result.strengths = [];
  if (!result.weaknesses) result.weaknesses = [];
  if (!result.interview_focus) result.interview_focus = 'Требуется дополнительная оценка на собеседовании';
  if (!result.career_trajectory) result.career_trajectory = 'Требуется анализ карьерной траектории';
  if (!result.match_explanation) result.match_explanation = result.summary || '';
  if (!result.recommendation) result.recommendation = result.summary || '';

  return new Response(JSON.stringify(result), {
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    },
  });
}

// Вызов Gemini API
async function callGeminiAPI(prompt) {
  const requestBody = {
    contents: [{
      parts: [{
        text: prompt
      }]
    }]
  };

  const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Gemini API error: ${response.status} - ${errorText}`);
  }

  return await response.json();
}

// Проксирование напрямую к Gemini API (для обратной совместимости)
async function proxyToGemini(request, url) {
  const externalUrl = "https://generativelanguage.googleapis.com";
  const proxiedUrl = new URL(externalUrl + url.pathname + url.search);
  
  proxiedUrl.searchParams.delete('key');
  proxiedUrl.searchParams.set('key', GEMINI_API_KEY);
  
  const proxiedRequest = new Request(proxiedUrl, {
    method: request.method,
    headers: {
      'Content-Type': request.headers.get('Content-Type') || 'application/json',
    },
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
  });

  const response = await fetch(proxiedRequest);
  const responseHeaders = new Headers(response.headers);
  responseHeaders.set('Access-Control-Allow-Origin', '*');
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}
