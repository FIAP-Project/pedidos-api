import logging

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PEDIDO = {"cliente": "Maria Silva", "descricao": "Notebook 14 polegadas", "valor": 3499.90}


def test_criar_pedido_retorna_201_com_status_criado():
    r = client.post("/pedidos", json=PEDIDO)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["id"]
    assert corpo["status"] == "CRIADO"
    assert corpo["cliente"] == PEDIDO["cliente"]
    assert corpo["valor"] == PEDIDO["valor"]
    assert r.headers["Location"] == f"/pedidos/{corpo['id']}"


def test_consultar_pedido_existente_retorna_200():
    criado = client.post("/pedidos", json=PEDIDO).json()
    r = client.get(f"/pedidos/{criado['id']}")
    assert r.status_code == 200
    assert r.json() == criado


def test_consultar_pedido_inexistente_retorna_404():
    r = client.get("/pedidos/id-que-nao-existe")
    assert r.status_code == 404
    assert r.json()["erro"]["codigo"] == "PEDIDO_NAO_ENCONTRADO"


def test_criar_pedido_com_valor_invalido_retorna_422():
    r = client.post("/pedidos", json={**PEDIDO, "valor": -10})
    assert r.status_code == 422
    assert r.json()["erro"]["codigo"] == "DADOS_INVALIDOS"


def test_request_id_e_propagado_e_aparece_nos_logs(caplog):
    with caplog.at_level(logging.INFO, logger="pedidos"):
        r = client.post("/pedidos", json=PEDIDO, headers={"X-Request-ID": "req-teste-123"})
    assert r.headers["X-Request-ID"] == "req-teste-123"
    log = next(rec for rec in caplog.records if getattr(rec, "operation", "") == "criar_pedido")
    assert log.orderId == r.json()["id"]
