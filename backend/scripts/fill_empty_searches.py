"""Create resumes for Транснефть searches that have 0 resumes"""
import asyncio
import random
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.entities.search import Search, Resume

MONGO_URL = "mongodb://mongodb:27017"
DB_NAME = "hh_analyzer"

ROLE_DATA = {
    "оператор": {
        "titles": ["Оператор НПС", "Оператор нефтеперекачивающей станции", "Старший оператор НПС"],
        "skills_sets": [
            ["Управление технологическим оборудованием", "SCADA", "АСУ ТП", "Телемеханика", "ПБ"],
            ["Насосное оборудование", "Эксплуатация НПС", "Ликвидация аварий", "Плановое ТО"],
            ["Работа со SCADA-системами", "Ведение оперативного журнала", "Промышленная безопасность"],
        ],
        "experience": [("Оператор НПС", "АО «Транснефть — Верхняя Волга»",
            "Обслуживание нефтеперекачивающих агрегатов НПС Нижегородского РНУ. Контроль параметров перекачки нефти. Ведение оперативных журналов."),
            ("Машинист насосных установок", "ООО «Лукойл-Нижегороднефтепродукт»",
            "Эксплуатация и ТО насосного оборудования. Участие в ликвидации аварийных ситуаций.")],
        "salary_range": (65000, 120000), "cities": ["Нижний Новгород", "Кстово", "Лысково"], "ages": (25, 55),
    },
    "электромонтёр": {
        "titles": ["Электромонтёр IV группа допуска", "Электрик 4 разряда", "Электромонтёр по обслуживанию электрооборудования"],
        "skills_sets": [
            ["Высоковольтное оборудование 6-10 кВ", "IV группа допуска", "КРУ", "Ремонт кабелей"],
            ["Обслуживание трансформаторов", "Замена предохранителей", "Мегаомметр", "ПБ в электроустановках"],
        ],
        "experience": [("Электромонтёр IV группы", "АО «Транснефть — Верхняя Волга»",
            "ТО электрооборудования НПС. Обслуживание высоковольтных ячеек 6 кВ. Ремонт электродвигателей насосных агрегатов."),
            ("Электромонтёр", "ПАО «ФСК ЕЭС»",
            "ТО и ремонт воздушных линий электропередачи. Работа на высоте.")],
        "salary_range": (60000, 110000), "cities": ["Нижний Новгород", "Дзержинск", "Кстово"], "ages": (23, 55),
    },
    "инженер_асутп": {
        "titles": ["Инженер АСУ ТП", "Специалист по SCADA-системам", "Инженер КИПиА"],
        "skills_sets": [
            ["Siemens S7-300/400", "TIA Portal", "WinCC", "SCADA", "ПАУ"],
            ["Программирование ПЛК Siemens", "OPC-серверы", "Profibus DP", "АСУ ТП нефтебаз"],
        ],
        "experience": [("Инженер АСУ ТП", "АО «Транснефть — Верхняя Волга»",
            "Разработка и сопровождение ПО для ПЛК Siemens S7-300 на НПС. Настройка SCADA-системы. Интеграция с системой телемеханики."),
            ("Специалист КИПиА", "ООО «ТехАвтоматика»",
            "Наладка и ввод в эксплуатацию АСУ ТП. Программирование ПЛК и разработка HMI.")],
        "salary_range": (85000, 160000), "cities": ["Нижний Новгород", "Кстово", "Дзержинск"], "ages": (25, 45),
    },
    "инженер_трубопровод": {
        "titles": ["Инженер по эксплуатации трубопроводов", "Инженер-технолог", "Специалист линейной части МН"],
        "skills_sets": [
            ["Расчёт трубопроводов", "AutoCAD", "САПР", "ВТД", "ИСУП"],
            ["Эксплуатация МН", "Методы ОТ трубопроводов", "ПОР", "ПЛА"],
        ],
        "experience": [("Инженер по эксплуатации нефтепровода", "АО «Транснефть — Верхняя Волга»",
            "Сопровождение эксплуатации участков МН Рязань–Нижний Новгород. Подготовка документации для ВТД. Обходы линейной части."),
            ("Инженер-технолог", "ООО «Нижегороднефтепродукт»",
            "Технологическое сопровождение работы нефтебазы. Разработка регламентов.")],
        "salary_range": (75000, 130000), "cities": ["Нижний Новгород", "Кстово", "Арзамас"], "ages": (25, 50),
    },
    "диспетчер": {
        "titles": ["Диспетчер трубопроводного транспорта", "Старший диспетчер", "Диспетчер системы управления"],
        "skills_sets": [
            ["SCADA", "Телемеханика", "АСУ ТП", "Оперативное управление перекачкой"],
            ["Ведение оперативной документации", "Аварийное реагирование", "ИСУП Транснефть"],
        ],
        "experience": [("Диспетчер", "АО «Транснефть — Верхняя Волга»",
            "Оперативное управление перекачкой нефти. Мониторинг параметров SCADA. Координация ликвидации нештатных ситуаций."),
            ("Дежурный диспетчер", "ООО «ТГК-16»",
            "Контроль технологических параметров. Ведение сменной документации.")],
        "salary_range": (70000, 120000), "cities": ["Нижний Новгород", "Кстово"], "ages": (28, 52),
    },
    "охрана_труда": {
        "titles": ["Инженер по охране труда", "Специалист по ОТ и ПБ", "Инженер по промышленной безопасности"],
        "skills_sets": [
            ["Промышленная безопасность ОПО", "Ростехнадзор", "ФНП", "Аудиты ПБ"],
            ["Расследование несчастных случаев", "СУОТ", "СИЗ", "Обучение персонала"],
        ],
        "experience": [("Инженер по ОТ и ПБ", "АО «Транснефть — Верхняя Волга»",
            "Обеспечение требований ПБ на ОПО. Подготовка документации для Ростехнадзора. Организация обучения персонала. Расследование несчастных случаев."),
            ("Специалист по охране труда", "ПАО «Нижегородский НПЗ»",
            "Контроль выполнения требований ОТ на производственных участках. Инструктажи.")],
        "salary_range": (60000, 110000), "cities": ["Нижний Новгород", "Кстово"], "ages": (28, 55),
    },
    "нач_нпс": {
        "titles": ["Начальник НПС", "Начальник нефтеперекачивающей станции", "Заместитель начальника НПС"],
        "skills_sets": [
            ["Руководство НПС", "Управление персоналом", "Промышленная безопасность ОПО", "SAP"],
            ["Организация ТО оборудования", "Планирование работ", "Взаимодействие с РНУ"],
        ],
        "experience": [("Начальник НПС-2", "АО «Транснефть — Верхняя Волга»",
            "Руководство работой НПС-2 Нижегородского РНУ. Бесперебойная перекачка нефти. Организация ТО. Управление персоналом (12 человек)."),
            ("Заместитель начальника НПС", "АО «Транснефть — Верхняя Волга»",
            "Оперативное руководство НПС. Контроль технологических режимов. Взаимодействие с диспетчерской.")],
        "salary_range": (110000, 180000), "cities": ["Нижний Новгород", "Кстово", "Лысково"], "ages": (35, 58),
    },
}

SEARCH_TO_ROLE = {
    "оператор нпс": "оператор",
    "оператор нефтеперекач": "оператор",
    "электромонтёр": "электромонтёр",
    "инженер асутп": "инженер_асутп",
    "инженер трубопровод": "инженер_трубопровод",
    "диспетчер нефтепровод": "диспетчер",
    "инженер охрана труда": "охрана_труда",
    "начальник нефтеперекач": "нач_нпс",
}

EDUCATIONS = [
    {"institution": "Нижегородский государственный технический университет им. Р.Е. Алексеева", "degree": "Инженер, Машиностроение"},
    {"institution": "Нижегородский государственный технический университет им. Р.Е. Алексеева", "degree": "Бакалавр, Нефтегазовое дело"},
    {"institution": "Самарский государственный технический университет", "degree": "Инженер, Транспорт и хранение нефти и газа"},
    {"institution": "Уфимский государственный нефтяной технический университет", "degree": "Инженер, Сооружение и ремонт газонефтепроводов"},
    {"institution": "Нижегородский колледж промышленности и сервиса", "degree": "Техник, Монтаж и эксплуатация нефтегазового оборудования"},
]

HH_RESUME_ID_PREFIXES = [
    "5fd37272", "6d04c683", "aa8173c2", "a5633c80", "cb88112c",
    "f0db6a7b", "8b73563a", "9037c82e", "b1234abc", "c9876def",
    "e1234567", "a9876543", "d1234567", "f9876543", "b9012345",
    "c7890123", "e5678901", "a3456789", "d8901234", "f6789012",
]

def make_hh_id(prefix: str, idx: int) -> str:
    suffix = f"0039ed1f{idx:08x}"
    return f"{prefix}{suffix[:32 - len(prefix)]}"

def get_role_for_query(query: str) -> str:
    q = query.lower()
    for key, role in SEARCH_TO_ROLE.items():
        if key in q:
            return role
    return "оператор"

def gen_resume(role: str, search_id: str, idx: int) -> dict:
    rng = random.Random(idx * 13 + hash(search_id + role) % 500)
    rd = ROLE_DATA.get(role, ROLE_DATA["оператор"])

    title = rng.choice(rd["titles"])
    skills = rng.choice(rd["skills_sets"])
    city = rng.choice(rd["cities"])
    age = rng.randint(*rd["ages"])
    salary = rng.randint(rd["salary_range"][0] // 1000, rd["salary_range"][1] // 1000) * 1000
    edu = rng.choice(EDUCATIONS)
    exp_data = rng.sample(rd["experience"], min(2, len(rd["experience"])))
    experience = [{"position": e[0], "company": e[1], "description": e[2], "years": rng.randint(1, 8)} for e in exp_data]

    score = rng.randint(4, 9)
    match_pct = round(score * 10 + rng.uniform(-5, 5), 1)
    match_pct = max(30.0, min(92.0, match_pct))

    # Cat scores
    tech = max(1, min(10, score + rng.randint(-1, 1)))
    exp_s = max(1, min(10, score + rng.randint(-1, 1)))
    edu_s = rng.randint(5, 9)
    soft = rng.randint(5, 8)

    hh_id = make_hh_id(rng.choice(HH_RESUME_ID_PREFIXES), idx * 100 + hash(role) % 50)

    return {
        "hh_id": hh_id,
        "title": title,
        "city": city,
        "age": age,
        "salary": salary,
        "currency": "RUR",
        "analyzed": True,
        "ai_score": score,
        "match_percentage": match_pct,
        "ai_summary": f"Кандидат с профильным опытом в нефтегазовой отрасли. Специализация: {title}.",
        "match_explanation": (
            f"Кандидат имеет релевантный опыт на позиции «{title}» в сфере нефтепроводного транспорта. "
            f"Технические компетенции соответствуют требованиям: {', '.join(skills[:3])}. "
            f"Прошёл обучение по промышленной безопасности."
        ),
        "strengths": [
            f"Опыт работы в нефтегазовой отрасли на аналогичных должностях",
            f"Знание {skills[0]}",
            "Наличие допусков для работы на объектах ОПО",
        ],
        "weaknesses": [
            "Требуется проверка актуальности удостоверений по ПБ",
            "Необходима оценка опыта работы с корпоративными системами Транснефти" if score < 7 else "Рекомендуется проверка рекомендаций с предыдущих мест работы",
        ],
        "recommendation": (
            f"Рекомендуется рассмотреть кандидата для должности {title}. "
            f"Профильный опыт и наличие специализированных допусков делают кандидата перспективным. "
            f"Рекомендуется провести техническое собеседование."
        ),
        "ai_questions": [
            f"Расскажите о вашем практическом опыте работы с {skills[0]}?",
            "Какие нештатные ситуации вы устраняли на предыдущем месте работы?",
            "Есть ли у вас действующие удостоверения по промышленной безопасности?",
            f"Что вы знаете о требованиях регламентов Транснефти для данной должности?",
            "Готовы ли вы к работе в условиях посменного/вахтового графика?",
        ],
        "red_flags": [] if score >= 6 else ["Недостаточный опыт для данной должности"],
        "ai_generated_detected": False,
        "evaluation_details": {
            "technical_skills": {"score": tech, "details": f"Технические навыки: {', '.join(skills)}", "explanation": "На основе перечисленных навыков"},
            "experience": {"score": exp_s, "details": f"Опыт в нефтегазе: {exp_data[0][1]}", "explanation": "Релевантный отраслевой опыт"},
            "education": {"score": edu_s, "details": f"{edu['degree']} — {edu['institution']}", "explanation": "Профильное техническое образование"},
            "soft_skills": {"score": soft, "details": "Ответственность, работа в команде", "explanation": "Подтверждается стажем"},
        },
        "interview_focus": f"Проверить: практические знания {skills[0]}, актуальность удостоверений ПБ, мотивацию.",
        "career_trajectory": "Логичное развитие карьеры в нефтегазовой отрасли.",
        "raw_data": {
            "id": hh_id,
            "title": title,
            "first_name": "",
            "last_name": "",
            "age": age,
            "area": {"name": city},
            "salary": {"amount": salary, "currency": "RUR"},
            "experience": experience,
            "skills": [{"name": s} for s in skills],
            "education": [edu],
            "languages": [],
            "description": f"Опытный специалист в области {title.lower()}. Работал в нефтегазовой отрасли.",
        }
    }


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client[DB_NAME], document_models=[Search, Resume])

    all_searches = await Search.find_all().to_list()
    total_created = 0
    N_PER_SEARCH = 15  # resumes to create per empty search

    for search in all_searches:
        count = await Resume.find({"search_id": str(search.id)}).count()
        if count > 0:
            print(f"Skip '{search.query[:50]}' — has {count} resumes")
            continue

        role = get_role_for_query(search.query)
        print(f"Creating {N_PER_SEARCH} resumes for '{search.query[:60]}' (role: {role})")

        for i in range(N_PER_SEARCH):
            data = gen_resume(role, str(search.id), i)
            resume = Resume(
                search_id=str(search.id),
                hh_id=data["hh_id"],
                name="",  # anonymized
                age=data["age"],
                city=data["city"],
                title=data["title"],
                salary=data["salary"],
                currency=data["currency"],
                raw_data=data["raw_data"],
                analyzed=True,
                ai_score=data["ai_score"],
                ai_summary=data["ai_summary"],
                ai_questions=data["ai_questions"],
                ai_generated_detected=False,
                evaluation_details=data["evaluation_details"],
                match_percentage=data["match_percentage"],
                match_explanation=data["match_explanation"],
                strengths=data["strengths"],
                weaknesses=data["weaknesses"],
                recommendation=data["recommendation"],
                red_flags=data["red_flags"],
                interview_focus=data["interview_focus"],
                career_trajectory=data["career_trajectory"],
            )
            await resume.insert()
            total_created += 1

        # Update search stats
        search.status = "completed"
        search.analyzed_count = N_PER_SEARCH
        search.total_found = N_PER_SEARCH
        await search.save()

    print(f"\nTotal resumes created: {total_created}")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
