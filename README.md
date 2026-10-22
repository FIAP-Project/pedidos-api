# API de Pedidos — CP5 Arquitetura Orientada a Serviço

FIAP 3ESPY — Profa. Damiana Costa — 21/10/2026

## Integrantes

| Nome                                    | RM       |
|-----------------------------------------|----------|
| Felipe Cerboncini Cordeiro              | RM554909 |
| Pedro Henrique Martins Alves dos Santos | RM558107 |
| Milena Codinhoto da Silva               | RM554682 |

## Tecnologias

- **Linguagem:** Python 3.10+
- **Framework:** FastAPI (+ Uvicorn)
- **Testes:** pytest + TestClient
- **Persistência:** dicionário em memória (os dados se perdem ao reiniciar)

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# subir a API (http://localhost:8000)
python -m uvicorn app.main:app --port 8000 --no-access-log

# rodar os testes
python -m pytest -v
```

A documentação interativa (Swagger UI) fica em http://localhost:8000/docs. A especificação OpenAPI está versionada em [`openapi.yaml`](openapi.yaml) e pode ser regenerada com `python scripts/export_openapi.py`.

## Arquitetura

```mermaid
flowchart LR
    C[Cliente HTTP] -->|JSON| M[Middleware<br/>requestId + logs]
    M --> R[Rotas / API<br/>routes.py + schemas.py]
    R --> S[Serviço<br/>service.py]
    S --> P[(Repositório em memória<br/>repository.py)]
    M -.-> L[Logs JSON<br/>stdout]
    S -.-> L
```

| Componente | Arquivo | Responsabilidade |
|---|---|---|
| Middleware | `app/main.py` | Gera/propaga o `requestId` (header `X-Request-ID`), registra o log de cada requisição e padroniza respostas de erro. |
| Rotas / API | `app/routes.py`, `app/schemas.py` | Define os endpoints, valida o JSON de entrada, escolhe os códigos HTTP e serializa a resposta. |
| Serviço | `app/service.py` | Regras de negócio: gera o id (UUID), define o status inicial `CRIADO`, lança erro se o pedido não existe. |
| Repositório | `app/repository.py` | Armazenamento em memória (thread-safe), sem conhecer HTTP. |
| Logs | `app/logging_config.py` | Formata cada log como um objeto JSON. |

Fluxo: o cliente envia a requisição → o middleware atribui o `requestId` → a rota valida e chama o serviço → o serviço aplica as regras e usa o repositório → a resposta volta, e o middleware registra o log final.

## Endpoints

| Método | Caminho | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/pedidos` | Cria um pedido | 201 (+ header `Location`) | 422 dados inválidos |
| GET | `/pedidos/{id}` | Consulta pedido por id | 200 | 404 não encontrado |

Escolha de design: `POST /pedidos` cria um novo recurso (o servidor gera o id e o status), retornando `201 Created`; `GET /pedidos/{id}` é idempotente e seguro para leitura.

Regras de validação: `cliente` e `descricao` obrigatórios e não vazios; `valor` obrigatório e maior que zero. O `status` é definido pelo servidor.

## Exemplos de requisição e resposta

**Criar pedido** — `POST /pedidos`

```bash
curl -i -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Maria Silva","descricao":"Notebook 14 polegadas","valor":3499.90}'
```

```
HTTP/1.1 201 Created
location: /pedidos/ec23bda0-3c64-4002-80c7-0f1897e774b8
x-request-id: demo-001

{"id":"ec23bda0-3c64-4002-80c7-0f1897e774b8","cliente":"Maria Silva","descricao":"Notebook 14 polegadas","valor":3499.9,"status":"CRIADO"}
```

**Consultar pedido** — `GET /pedidos/{id}`

```
HTTP/1.1 200 OK

{"id":"ec23bda0-3c64-4002-80c7-0f1897e774b8","cliente":"Maria Silva","descricao":"Notebook 14 polegadas","valor":3499.9,"status":"CRIADO"}
```

**Pedido inexistente** — `GET /pedidos/999`

```
HTTP/1.1 404 Not Found

{"erro":{"codigo":"PEDIDO_NAO_ENCONTRADO","mensagem":"Pedido '999' não encontrado","requestId":"397ba89b-fcc4-4b9f-8aed-8ca806ade720"}}
```

**Dados inválidos** — `POST /pedidos` com `{"cliente":"","descricao":"x","valor":-1}`

```
HTTP/1.1 422 Unprocessable Entity

{"erro":{"codigo":"DADOS_INVALIDOS","mensagem":"Os dados enviados são inválidos","requestId":"5ca7ef2b-e635-4dbb-8ece-1dcb2eab9b26","detalhes":[{"campo":"cliente","mensagem":"String should have at least 1 character"},{"campo":"valor","mensagem":"Input should be greater than 0"}]}}
```

## Testes automatizados

Arquivo: [`tests/test_pedidos.py`](tests/test_pedidos.py) — 5 testes: criação (201), consulta existente (200), consulta inexistente (404), validação (422) e propagação do requestId nos logs. Cada teste usa `assert` sobre status HTTP e corpo da resposta.

Executar: `python -m pytest -v`

**Evidência da execução:**

<img width="1454" height="421" alt="Screenshot 2026-10-21 214342" src="https://github.com/user-attachments/assets/88a72459-51d2-4851-aabb-75e8ef08e968" />


## Logs estruturados

Um objeto JSON por linha em stdout, com `timestamp` (UTC), `level`, `message`, `requestId`, `operation` e, quando aplicável, `orderId`, `method`, `path`, `status` e `durationMs`. O `requestId` vem do header `X-Request-ID` (se enviado) ou é gerado, e é devolvido na resposta.

**Evidência:**

<img width="1454" height="352" alt="Screenshot 2026-10-21 214247" src="https://github.com/user-attachments/assets/3ec5f389-d0d7-43c3-a093-e24949eb0697" />


