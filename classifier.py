
import json
import urllib.request
import urllib.error

MODEL = "qwen2.5:1.5b"
USE_AI = False  # Поменяй на True, когда модель заработает


def classify_with_rules(message):
    text = message.lower()

    if any(word in text for word in [
        "компьютер", "пароль", "почт", "интернет",
        "принтер", "мышк", "клавиатур"
    ]):
        department = "IT"
    elif any(word in text for word in ["зарплат", "отпуск", "больничн"]):
        department = "HR"
    else:
        department = "Не определён"

    if any(word in text for word in [
        "остановил", "срочно", "весь отдел", "не работает производство"
    ]):
        priority = "high"
    else:
        priority = "normal"

    return {
        "department": department,
        "priority": priority,
        "reason": "Классификация по ключевым словам",
        "method": "rules"
    }


def classify_with_ai(message):
    prompt = f"""
Ты помощник для обработки заявок сотрудников компании.

Определи:
1. Отдел: IT, HR, Production или Other.
2. Приоритет: high или normal.
3. Краткую причину решения.

Высокий приоритет ставь, если проблема останавливает
работу отдела, производство или критичный бизнес-процесс.

Верни только JSON без пояснений и Markdown:
{{
    "department": "IT",
    "priority": "normal",
    "reason": "Краткое объяснение"
}}

Заявка сотрудника: {json.dumps(message, ensure_ascii=False)}
"""

    data = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }).encode("utf-8")

    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)

    analysis = json.loads(result["response"])

    allowed_departments = {"IT", "HR", "Production", "Other"}
    allowed_priorities = {"high", "normal"}

    if analysis.get("department") not in allowed_departments:
        raise ValueError("Нейросеть вернула неизвестный отдел")

    if analysis.get("priority") not in allowed_priorities:
        raise ValueError("Нейросеть вернула неизвестный приоритет")

    return {
        "department": analysis["department"],
        "priority": analysis["priority"],
        "reason": str(analysis.get("reason", "")),
        "method": "ai"
    }


def classify_ticket(message):
    if USE_AI:
        try:
            return classify_with_ai(message)
        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            KeyError,
            ValueError
        ) as error:
            print("Ошибка нейросети:", error)
            print("Используем резервную классификацию.")

    return classify_with_rules(message)
