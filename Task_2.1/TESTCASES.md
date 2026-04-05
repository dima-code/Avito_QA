# TESTCASES.md


Тест-кейсы API.

Источник требований: описание задания и загруженная Postman-коллекция с ручками:
- `POST /api/1/item` — создание объявления
- `GET /api/1/item/{id}` — получение объявления по идентификатору
- `GET /api/1/{sellerID}/item` — получение всех объявлений конкретного продавца
- `GET /api/1/statistic/{id}` — получение статистики по `item id`
- дополнительно в коллекции есть ручки версии `/api/2` и `DELETE /api/2/item/{id}`, но они не входят в обязательный объем текущего задания и в автотестах не используются

## Подход и техники тест-дизайна
При составлении набора тестов использовались:
- классы эквивалентности
- анализ граничных значений
- таблицы решений для обязательных полей
- попарное покрытие основных комбинаций входных данных
- негативные проверки обязательности и типов полей
- corner-cases: повторная отправка одинаковых запросов, повторяемость значений, пустые выборки
- нефункциональные проверки: время отклика, формат ответа, устойчивость структуры

## Правила
1. `sellerId`/`sellerID` должен передаваться как целое число, рекомендуемый диапазон — `111111–999999`.
2. Значения полей `name`, `price`, `sellerId`, `statistics` могут совпадать у разных объявлений.
3. Каждое новое объявление должно получать уникальный `id`.
4. Ручка получения объявления по `id` может возвращать либо объект, либо массив с одним объектом — это уточняется по фактическому поведению сервиса. Автотесты должны учитывать оба варианта.
5. Для воспроизводимости и независимости каждый тест использует собственные тестовые данные.

---

## Позитивные тест-кейсы

### TC-01 Получение статистики по item id
**Цель:** убедиться, что сервис корректно возвращает статистику созданного объявления.

**Пример входных запросов:**

1. Создать объявление:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Статистика для проверки",
  "price": 1500,
  "statistics": {
    "likes": 11,
    "viewCount": 22,
    "contacts": 33
  }
}
```

2. Получить статистику:
```http
GET /api/1/statistic/{id}
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Создать объявление с заранее заданными значениями статистики.
2. Выполнить `GET /api/1/statistic/{id}`.

**Ожидаемый результат:**
- HTTP `200`
- статистика успешно возвращается
- поля `likes`, `viewCount`, `contacts` совпадают с переданными значениями


---

### TC-02 Получение списка объявлений продавца
**Цель:** проверить ручку выборки по `sellerId`.

**Пример входных запросов:**

1. Создать первое объявление:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 456789,
  "name": "same-seller-a",
  "price": 1200,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

2. Создать второе объявление:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 456789,
  "name": "same-seller-b",
  "price": 1300,
  "statistics": {
    "likes": 4,
    "viewCount": 5,
    "contacts": 6
  }
}
```

3. Получить объявления продавца:
```http
GET /api/1/456789/item
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Сгенерировать уникальный `sellerId`.
2. Создать 2 объявления для одного и того же продавца.
3. Выполнить `GET /api/1/{sellerID}/item`.

**Ожидаемый результат:**
- HTTP `200`
- сервис возвращает список объявлений
- в списке есть оба созданных объявления
- у всех найденных элементов `sellerId` соответствует ожидаемому значению


---

### TC-03 Созданное объявление доступно по id
**Цель:** проверить цепочку create → get by id.

**Пример входных запросов:**

1. Создать объявление:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 567890,
  "name": "Получение по id",
  "price": 1700,
  "statistics": {
    "likes": 7,
    "viewCount": 8,
    "contacts": 9
  }
}
```

2. Получить объявление по id:
```http
GET /api/1/item/{id}
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Создать новое объявление.
2. Выполнить `GET /api/1/item/{id}` для созданного ресурса.
3. Сравнить фактические данные с исходными.

**Ожидаемый результат:**
- HTTP `200`
- возвращается именно созданное объявление
- `id` совпадает
- остальные поля сохранены без искажений


---

### TC-04 Проверка уникальности идентификаторов объявлений
**Цель:** убедиться, что каждому новому объявлению назначается уникальный `id`.

**Пример входных запросов:**

1. Первый запрос:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 678901,
  "name": "Уникальность id 1",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 1,
    "contacts": 1
  }
}
```

2. Второй запрос:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 678902,
  "name": "Уникальность id 2",
  "price": 1001,
  "statistics": {
    "likes": 2,
    "viewCount": 2,
    "contacts": 2
  }
}
```

**Шаги:**
1. Создать первое объявление.
2. Создать второе объявление.
3. Сравнить полученные идентификаторы.

**Ожидаемый результат:**
- оба запроса завершаются успешно
- `id` у объявлений различаются


---

### TC-05 Создание объявления с корректными обязательными полями
**Цель:** проверить базовый успешный сценарий создания объявления.

**Предусловия:** отсутствуют.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

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

**Шаги:**
1. Отправить `POST /api/1/item` с валидным телом:
   - `sellerID` — целое число в диапазоне `111111–999999`
   - `name` — непустая строка
   - `price` — целое положительное число
   - `statistics.likes/viewCount/contacts` — целые неотрицательные значения
2. Проверить ответ сервиса.

**Ожидаемый результат:**
- HTTP `200`
- согласно Postman-коллекции в ответе присутствуют `id`, `sellerId`, `name`, `price`, `statistics`, `createdAt`


---

### TC-06 Повторяющиеся значения полей допустимы у разных объявлений
**Цель:** проверить бизнес-правило о возможности дублирования значений полей.

**Пример входных запросов:**

1. Первый запрос:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 789012,
  "name": "Повторяемое объявление",
  "price": 5000,
  "statistics": {
    "likes": 5,
    "viewCount": 6,
    "contacts": 7
  }
}
```

2. Второй запрос:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 789012,
  "name": "Повторяемое объявление",
  "price": 5000,
  "statistics": {
    "likes": 5,
    "viewCount": 6,
    "contacts": 7
  }
}
```

**Шаги:**
1. Создать два объявления с одинаковыми `name`, `price`, `sellerID`, `statistics`.
2. Сравнить полученные результаты.

**Ожидаемый результат:**
- оба запроса обрабатываются успешно
- `id` у объявлений разные
- остальные переданные значения совпадают


---

## Негативные тест-кейсы

### TC-07 Получение объявлений по невалидному sellerId
**Данные:** строковое значение вместо целого числа.

**Пример входного запроса:**
```http
GET /api/1/not-a-number/item
Host: qa-internship.avito.com
Accept: application/json
```

**Ожидаемый результат:**
- HTTP `400`


---

### TC-08 Создание объявления с отрицательной ценой
**Данные:** `price = -1`.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Отрицательная цена",
  "price": -1,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

**Ожидаемый результат:**
- HTTP `400` или другой контролируемый код ошибки валидации


---

### TC-09 Создание объявления с некорректным типом price
**Данные:** `price = "1000"` либо `1.5`.

**Пример входных запросов:**

1. Цена строкой:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Цена строкой",
  "price": "1000",
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

2. Цена дробным числом:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Цена float",
  "price": 1.5,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

**Ожидаемый результат:**
- HTTP `400`


---

### TC-10 Получение объявления по несуществующему id
**Пример входного запроса:**
```http
GET /api/1/item/550e8400-e29b-41d4-a716-446655440000
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Выполнить `GET /api/1/item/{random_non_existing_id}`.

**Ожидаемый результат:**
- HTTP `404`
- понятное сообщение об ошибке

**Автоматизация:** да

---

### TC-11 Создание объявления без statistics
**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Без statistics",
  "price": 1500
}
```

**Шаги:**
1. Отправить `POST /api/1/item` без поля `statistics`.

**Ожидаемый результат:**
- HTTP `400`


---

### TC-12 Создание объявления без sellerID
**Цель:** проверить обязательность поля `sellerID`.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "name": "Без sellerID",
  "price": 1500,
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```

**Шаги:**
1. Отправить `POST /api/1/item` без поля `sellerID`.

**Ожидаемый результат:**
- HTTP `400`
- сообщение валидации указывает на отсутствие обязательного поля


---

### TC-13 Создание объявления с пустым телом
**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{}
```

**Шаги:**
1. Отправить `POST /api/1/item` с пустым телом.

**Ожидаемый результат:**
- HTTP `400`


---

### TC-14 Создание объявления с malformed JSON
**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 123456,
  "name": "broken",
  "price": 1000,
```

**Шаги:**
1. Отправить `POST /api/1/item` с некорректным JSON.

**Ожидаемый результат:**
- HTTP `400`


---

### TC-15 Создание объявления с отрицательными значениями статистики
**Данные:** одно из полей `likes`, `viewCount`, `contacts` меньше `0`.

**Пример входных запросов:**

1. Отрицательный likes:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Отрицательный likes",
  "price": 1000,
  "statistics": {
    "likes": -1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

2. Отрицательный viewCount:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Отрицательный viewCount",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": -1,
    "contacts": 3
  }
}
```

3. Отрицательный contacts:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Отрицательный contacts",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": -1
  }
}
```

**Ожидаемый результат:**
- HTTP `400`


---

### TC-16 Создание объявления без name
**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "price": 1500,
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```

**Шаги:**
1. Отправить `POST /api/1/item` без поля `name`.

**Ожидаемый результат:**
- HTTP `400`


---

### TC-17 Создание объявления без price
**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Без price",
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```

**Шаги:**
1. Отправить `POST /api/1/item` без поля `price`.

**Ожидаемый результат:**
- HTTP `400`


---

### TC-18 Получение статистики по несуществующему id
**Пример входного запроса:**
```http
GET /api/1/statistic/550e8400-e29b-41d4-a716-446655440000
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Выполнить `GET /api/1/statistic/{random_non_existing_id}`.

**Ожидаемый результат:**
- HTTP `404`


---

### TC-19 Создание объявления с некорректным типом sellerID
**Данные:** `sellerID = "abc"`.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": "abc",
  "name": "Невалидный sellerID",
  "price": 1500,
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```

**Ожидаемый результат:**
- HTTP `400`
- ошибка валидации типа данных


---

## Корнер-кейсы

### TC-20 Запросы с одинаковым телом не являются идемпотентными
**Цель:** проверить, что два одинаковых `POST` создают два отдельных ресурса.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 456789,
  "name": "Одинаковый payload",
  "price": 777,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

**Шаги:**
1. Дважды отправить один и тот же payload.
2. Сопоставить ответы.

**Ожидаемый результат:**
- оба запроса завершаются успешно
- создаются два разных объявления
- `id` различаются


---

### TC-21 Обработка длинного значения в поле name
**Цель:** проверить работу сервиса с очень длинной строкой.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "ОченьОченьОченьОченьОченьОченьОченьОченьОченьОченьДлинноеИмяОбъявленияДляПроверкиГраничныхУсловийОченьОченьОченьОченьОченьОченьОченьОченьОченьОченьДлинноеИмяОбъявленияДляПроверкиГраничныхУсловий",
  "price": 1500,
  "statistics": {
    "likes": 10,
    "viewCount": 25,
    "contacts": 3
  }
}
```

**Шаги:**
1. Отправить `POST /api/1/item` с длинным значением `name`.

**Ожидаемый результат:**
- либо объявление создается успешно
- либо сервис возвращает контролируемую ошибку валидации
- ответ не должен быть `500`


---

### TC-22 Обработка нулевых значений статистики
**Данные:** `likes = 0`, `viewCount = 0`, `contacts = 0`.

**Пример входного запроса:**
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 345678,
  "name": "Нулевая статистика",
  "price": 1500,
  "statistics": {
    "likes": 0,
    "viewCount": 0,
    "contacts": 0
  }
}
```

**Ожидаемый результат:**
- объявление создается успешно
- статистика сохраняется без искажений


---

### TC-23 Проверка границ рекомендованного диапазона sellerId
**Данные:** `111111` и `999999`.

**Пример входных запросов:**

1. Нижняя граница:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 111111,
  "name": "Граница sellerID min",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

2. Верхняя граница:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 999999,
  "name": "Граница sellerID max",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

**Ожидаемый результат:**
- создание выполняется успешно
- созданные объявления доступны для последующего чтения


---

### TC-24 Пустая выборка объявлений продавца
**Пример входного запроса:**
```http
GET /api/1/987654/item
Host: qa-internship.avito.com
Accept: application/json
```

**Шаги:**
1. Выполнить `GET /api/1/{sellerID}/item` для нового уникального `sellerId`, для которого ранее не создавались объявления.

**Ожидаемый результат:**
- корректный код ответа
- возвращается пустой массив или `404` в соответствии с контрактом
- отсутствует `500`


---

### TC-25 sellerId за пределами рекомендованного диапазона
**Данные:** `111110` и `1000000`.

**Пример входных запросов:**

1. Ниже диапазона:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 111110,
  "name": "SellerID ниже диапазона",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

2. Выше диапазона:
```http
POST /api/1/item
Host: qa-internship.avito.com
Content-Type: application/json
Accept: application/json

{
  "sellerID": 1000000,
  "name": "SellerID выше диапазона",
  "price": 1000,
  "statistics": {
    "likes": 1,
    "viewCount": 2,
    "contacts": 3
  }
}
```

**Ожидаемый результат:**
- либо сервис отклоняет запрос как невалидный
- либо принимает его, если диапазон является рекомендованным, а не обязательным


---

## Нефункциональные проверки

### TC-26 Проверка времени ответа для create/get
**Порог:** базово `<= 2 сек` на один запрос в тестовом окружении.

**Пример входных запросов:**
- `POST /api/1/item` с валидным телом
- `GET /api/1/item/{id}`
- `GET /api/1/{sellerID}/item`
- `GET /api/1/statistic/{id}`

**Ожидаемый результат:**
- ответы укладываются в установленный порог


---

### TC-27 Проверка стабильности структуры ответа
**Пример входных запросов:**
- успешный `POST /api/1/item`
- успешный `GET /api/1/item/{id}`
- негативный `POST /api/1/item` с невалидным телом

**Ожидаемый результат:**
- успешные ответы содержат ожидаемый набор полей согласно Postman-коллекции
- ответы с ошибками имеют понятную и предсказуемую структуру
- отсутствуют неожиданные `500`

**Автоматизация:** да

---

### TC-28 Проверка Content-Type ответа
**Пример входных запросов:**
- `POST /api/1/item`
- `GET /api/1/item/{id}`
- `GET /api/1/{sellerID}/item`
- `GET /api/1/statistic/{id}`

**Ожидаемый результат:**
- для успешных и валидационных ответов заголовок содержит `application/json`, если тело ответа возвращается в формате JSON


---

## Что покрыто автотестами
Автотесты охватывают основные позитивные, негативные, corner- и нефункциональные сценарии:
- успешное создание объявления
- получение объявления по id
- получение списка объявлений продавца
- получение статистики
- уникальность идентификаторов
- отсутствие идемпотентности у POST
- валидацию обязательных полей
- проверки типов входных данных
- обработку несуществующих id
- пустые выборки
- граничные значения sellerId
- время ответа и базовую проверку схемы ответа
