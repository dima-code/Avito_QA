import random
import string
import time
import uuid

import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"
API_SLOW_THRESHOLD_MS = 2000


def unique_seller_id() -> int:
    return random.randint(111111, 999999)


def unique_name(prefix: str = "qa-item") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}-{suffix}"


def make_payload(
    seller_id=None,
    name=None,
    price=1000,
    likes=1,
    view_count=2,
    contacts=3,
):
    return {
        "sellerID": seller_id if seller_id is not None else unique_seller_id(),
        "name": name if name is not None else unique_name(),
        "price": price,
        "statistics": {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts,
        },
    }


def request_json(method: str, path: str, **kwargs):
    started = time.time()
    response = requests.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
    response.elapsed_ms = (time.time() - started) * 1000
    return response


def parse_json(response):
    try:
        return response.json()
    except Exception as exc:
        pytest.fail(
            f"Ответ сервера не является JSON. "
            f"Статус={response.status_code}, тело={response.text}, ошибка={exc}"
        )


def assert_statistics_shape(statistics):
    assert isinstance(statistics, dict), (
        f"Поле statistics должно быть объектом, получено: {type(statistics)}"
    )
    for field in ("likes", "viewCount", "contacts"):
        assert field in statistics, (
            f"В объекте statistics отсутствует поле {field}: {statistics}"
        )


def assert_item_shape(item):
    assert isinstance(item, dict), (
        f"Объявление должно быть объектом JSON, получено: {type(item)}"
    )
    for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
        assert field in item, (
            f"В объекте объявления отсутствует поле {field}: {item}"
        )
    assert isinstance(item["id"], str) and item["id"].strip(), (
        f"Поле id должно быть непустой строкой: {item['id']}"
    )
    assert isinstance(item["sellerId"], int), (
        f"Поле sellerId должно быть целым числом: {item['sellerId']}"
    )
    assert isinstance(item["name"], str) and item["name"].strip(), (
        f"Поле name должно быть непустой строкой: {item['name']}"
    )
    assert isinstance(item["price"], int), (
        f"Поле price должно быть целым числом: {item['price']}"
    )
    assert isinstance(item["createdAt"], str) and item["createdAt"].strip(), (
        f"Поле createdAt должно быть непустой строкой: {item['createdAt']}"
    )
    assert_statistics_shape(item["statistics"])


def assert_error_shape(body):
    assert isinstance(body, dict), (
        f"Ошибка должна быть объектом JSON, получено: {type(body)}"
    )
    assert "result" in body, f"В ответе ошибки отсутствует поле result: {body}"
    assert "status" in body, f"В ответе ошибки отсутствует поле status: {body}"
    assert isinstance(body["result"], dict), (
        f"Поле result должно быть объектом: {body}"
    )
    assert "message" in body["result"], (
        f"В поле result отсутствует message: {body}"
    )
    assert "messages" in body["result"], (
        f"В поле result отсутствует messages: {body}"
    )


def normalize_item_response(body):
    if isinstance(body, list):
        assert len(body) >= 1, f"Ожидался непустой список, получено: {body}"
        return body[0]
    return body


def create_item(payload=None):
    response = request_json("POST", "/api/1/item", json=payload or make_payload())
    assert response.status_code == 200, (
        f"Ожидался статус 200 при создании объявления, "
        f"получено {response.status_code}, тело={response.text}"
    )

    body = parse_json(response)
    assert_item_shape(body)
    return body


@pytest.mark.parametrize("seller_id", [111111, 999999])
def test_create_item_with_boundary_seller_ids(seller_id):
    payload = make_payload(seller_id=seller_id)
    created = create_item(payload)
    assert created["sellerId"] == seller_id, (
        f"Поле sellerId должно быть равно {seller_id}, "
        f"получено {created['sellerId']}"
    )


def test_create_item_success_and_response_time():
    payload = make_payload()
    response = request_json("POST", "/api/1/item", json=payload)
    assert response.status_code == 200, (
        f"Ожидался статус 200, получено {response.status_code}, тело={response.text}"
    )
    assert response.elapsed_ms <= API_SLOW_THRESHOLD_MS, (
        f"POST-запрос выполнялся слишком долго: "
        f"{response.elapsed_ms:.2f} мс > {API_SLOW_THRESHOLD_MS} мс"
    )

    body = parse_json(response)
    assert_item_shape(body)
    assert body["sellerId"] == payload["sellerID"]
    assert body["name"] == payload["name"]
    assert body["price"] == payload["price"]


def test_get_item_by_id_returns_created_item():
    payload = make_payload()
    created = create_item(payload)

    response = request_json("GET", f"/api/1/item/{created['id']}")
    assert response.status_code == 200, (
        f"Ожидался статус 200, получено {response.status_code}, тело={response.text}"
    )

    item = normalize_item_response(parse_json(response))
    assert_item_shape(item)
    assert item["id"] == created["id"]
    assert item["sellerId"] == payload["sellerID"]
    assert item["name"] == payload["name"]
    assert item["price"] == payload["price"]


def test_get_items_by_seller_id_returns_all_created_items():
    seller_id = unique_seller_id()
    first_payload = make_payload(seller_id=seller_id, name=unique_name("same-seller-a"))
    second_payload = make_payload(
        seller_id=seller_id, name=unique_name("same-seller-b")
    )

    first = create_item(first_payload)
    second = create_item(second_payload)

    response = request_json("GET", f"/api/1/{seller_id}/item")
    assert response.status_code == 200, (
        f"Ожидался статус 200, получено {response.status_code}, тело={response.text}"
    )

    items = parse_json(response)
    assert isinstance(items, list), (
        f"Ожидался список объявлений, получено: {type(items)}"
    )
    assert len(items) >= 2, (
        "Список объявлений продавца не содержит ожидаемое количество элементов"
    )

    ids = {item["id"] for item in items}
    assert first["id"] in ids
    assert second["id"] in ids

    for item in items:
        assert_item_shape(item)
        assert item["sellerId"] == seller_id, (
            f"Найдено объявление с sellerId={item['sellerId']}, ожидалось {seller_id}"
        )


def test_get_statistics_by_item_id_returns_expected_values():
    payload = make_payload(likes=11, view_count=22, contacts=33)
    created = create_item(payload)

    response = request_json("GET", f"/api/1/statistic/{created['id']}")
    assert response.status_code == 200, (
        f"Ожидался статус 200, получено {response.status_code}, тело={response.text}"
    )

    body = parse_json(response)
    assert isinstance(body, list), (
        f"Ожидался список статистики, получено: {type(body)}"
    )
    assert len(body) >= 1, f"Ожидался непустой список статистики, получено: {body}"

    stat = body[0]
    assert_statistics_shape(stat)
    assert stat["likes"] == 11
    assert stat["viewCount"] == 22
    assert stat["contacts"] == 33


def test_same_payload_twice_creates_two_different_items():
    seller_id = unique_seller_id()
    payload = make_payload(
        seller_id=seller_id, name=unique_name("duplicate-payload"), price=777
    )

    first = create_item(payload)
    second = create_item(payload)

    assert first["id"] != second["id"], (
        "При двух одинаковых POST-запросах были получены одинаковые id"
    )
    assert first["sellerId"] == second["sellerId"] == seller_id
    assert first["name"] == second["name"] == payload["name"]
    assert first["price"] == second["price"] == payload["price"]


def test_create_item_with_missing_required_fields():
    base = make_payload()

    for missing_field in ["sellerID", "name", "price", "statistics"]:
        payload = dict(base)
        payload.pop(missing_field, None)

        response = request_json("POST", "/api/1/item", json=payload)
        assert response.status_code == 400, (
            f"Ожидался статус 400 при отсутствии поля {missing_field}, "
            f"получено {response.status_code}, тело={response.text}"
        )
        assert_error_shape(parse_json(response))


@pytest.mark.parametrize(
    "field, value",
    [
        ("sellerID", "abc"),
        ("sellerID", 1.5),
        ("price", "1000"),
        ("price", 1.5),
    ],
)
def test_create_item_with_invalid_scalar_types(field, value):
    payload = make_payload()
    payload[field] = value

    response = request_json("POST", "/api/1/item", json=payload)
    assert response.status_code == 400, (
        f"Ожидался статус 400 для невалидного значения {field}={value}, "
        f"получено {response.status_code}, тело={response.text}"
    )
    assert_error_shape(parse_json(response))


def test_create_item_with_empty_body():
    response = request_json("POST", "/api/1/item", json={})
    assert response.status_code == 400, (
        f"Ожидался статус 400 для пустого тела запроса, "
        f"получено {response.status_code}, тело={response.text}"
    )
    assert_error_shape(parse_json(response))


def test_create_item_with_malformed_json():
    response = request_json(
        "POST",
        "/api/1/item",
        data='{"sellerID": 123456, "name": "broken", "price": 1000,',
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    assert response.status_code == 400, (
        f"Ожидался статус 400 для некорректного JSON, "
        f"получено {response.status_code}, тело={response.text}"
    )
    assert_error_shape(parse_json(response))


def test_get_item_by_non_existing_id_returns_not_found():
    non_existing_id = str(uuid.uuid4())
    response = request_json("GET", f"/api/1/item/{non_existing_id}")
    assert response.status_code == 404, (
        f"Ожидался статус 404 для несуществующего id, "
        f"получено {response.status_code}, тело={response.text}"
    )
    body = parse_json(response)
    assert isinstance(body, dict), (
        f"Ожидался объект JSON, получено: {type(body)}"
    )
    assert "result" in body and "status" in body, (
        f"Ответ 404 не соответствует структуре коллекции: {body}"
    )


def test_get_statistics_by_non_existing_id_returns_not_found():
    non_existing_id = str(uuid.uuid4())
    response = request_json("GET", f"/api/1/statistic/{non_existing_id}")
    assert response.status_code == 404, (
        f"Ожидался статус 404 для несуществующего id статистики, "
        f"получено {response.status_code}, тело={response.text}"
    )
    body = parse_json(response)
    assert isinstance(body, dict), (
        f"Ожидался объект JSON, получено: {type(body)}"
    )
    assert "result" in body and "status" in body, (
        f"Ответ 404 не соответствует структуре коллекции: {body}"
    )


def test_get_items_by_invalid_seller_id_returns_bad_request():
    response = request_json("GET", "/api/1/not-a-number/item")
    assert response.status_code == 400, (
        f"Ожидался статус 400 для невалидного sellerId, "
        f"получено {response.status_code}, тело={response.text}"
    )
    assert_error_shape(parse_json(response))


def test_get_items_for_seller_without_ads_returns_empty_list():
    seller_id = unique_seller_id()
    response = request_json("GET", f"/api/1/{seller_id}/item")
    assert response.status_code == 200, (
        f"Согласно коллекции для корректного sellerId ожидался статус 200, "
        f"получено {response.status_code}, тело={response.text}"
    )
    body = parse_json(response)
    assert isinstance(body, list), (
        f"Ожидался список объявлений, получено: {type(body)}"
    )


def test_create_item_with_long_name_returns_controlled_response():
    payload = make_payload(name="x" * 2048)
    response = request_json("POST", "/api/1/item", json=payload)
    assert response.status_code in (200, 400), (
        f"Ожидался контролируемый ответ 200 или 400 для длинного name, "
        f"получено {response.status_code}, тело={response.text}"
    )
    body = parse_json(response)
    if response.status_code == 200:
        assert_item_shape(body)
    else:
        assert_error_shape(body)


def test_response_content_type_is_json_for_create():
    response = request_json("POST", "/api/1/item", json=make_payload())
    assert response.status_code == 200, (
        f"Ожидался статус 200 при создании объявления, "
        f"получено {response.status_code}, тело={response.text}"
    )
    assert "application/json" in response.headers.get("Content-Type", ""), (
        f"Ожидался Content-Type с application/json, "
        f"получено {response.headers.get('Content-Type', '')}"
    )

