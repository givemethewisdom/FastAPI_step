def test_calculate_sum_valid(client):
    """Тест валидных данных"""
    response = client.get("/sum/", params={"a": 5, "b": 10})
    assert response.status_code == 200
    assert response.json() == {"result": 15}


def test_calculate_sum_negative(client):
    """Тест отрицательных чисел"""
    response = client.get("/sum/", params={"a": -8, "b": -3})
    assert response.status_code == 200
    assert response.json() == {"result": -11}


def test_calculate_sum_zero(client):
    """Тест с нулем"""
    response = client.get("/sum/", params={"a": 0, "b": 7})
    assert response.status_code == 200
    assert response.json() == {"result": 7}


def test_calculate_sum_missing_param(client):
    """Тест пропущенного параметра"""
    response = client.get("/sum/", params={"a": 3})
    assert response.status_code == 422

    # Упрощенная проверка
    error = response.json()
    assert "detail" in error
    assert len(error["detail"]) == 1
    assert "b" in str(error["detail"][0].get("loc", []))