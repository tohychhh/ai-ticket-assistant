
import json
import os
from datetime import datetime
from classifier import classify_ticket

FILE_NAME = "tickets.json"


def load_tickets():
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r", encoding="utf-8") as file:
        return json.load(file)


def save_tickets(tickets):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(tickets, file, ensure_ascii=False, indent=2)


def main():
    print("=== AI Ticket Assistant ===")

    message = input("Опишите вашу проблему: ").strip()

    if not message:
        print("Ошибка: заявка не может быть пустой.")
        return

    tickets = load_tickets()

    # Добавляем ID старым заявкам, если их ещё нет
    next_id = max(
        (ticket.get("id", 0) for ticket in tickets),
        default=0
    ) + 1

    for old_ticket in tickets:
        if "id" not in old_ticket:
            old_ticket["id"] = next_id
            next_id += 1

    result = classify_ticket(message)

    ticket = {
        "id": next_id,
        "message": message,
        "department": result["department"],
        "priority": result["priority"],
        "reason": result["reason"],
        "method": result["method"],
        "status": "new",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    tickets.append(ticket)
    save_tickets(tickets)

    print("\n=== Результат обработки ===")
    print(json.dumps(ticket, ensure_ascii=False, indent=2))
    print("\nЗаявка успешно сохранена!")


if __name__ == "__main__":
    main()
