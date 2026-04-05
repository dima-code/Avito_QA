# BUGS.md

---
# BUG-001 — Ответ POST /api/1/item не соответствует Postman-коллекции

**Краткое описание:**  
При успешном создании объявления сервис возвращает тело ответа, не соответствующее описанию в Postman-коллекции.

**Шаги воспроизведения:**  
1. Отправить `POST /api/1/item` с валидным телом запроса, например:
```json
{
  "sellerID": 345678,
  "name": "Тестовое объявление",
  "price": 1500,
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```
2. Проверить тело ответа

**Ожидаемый результат по Postman-коллекции:**  
Сервис возвращает JSON-объект объявления:
```json
{
  "id": "<string>",
  "sellerId": "<integer>",
  "name": "<string>",
  "price": "<integer>",
  "statistics": {
    "likes": "<integer>",
    "viewCount": "<integer>",
    "contacts": "<integer>"
  },
  "createdAt": "<string>"
}
```

**Фактический результат**

```json
{
  "status": "Сохранили объявление - <uuid>"
}
```