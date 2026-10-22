"""Aplicação FastAPI: middleware de requestId/logs e tratamento padronizado de erros."""
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .errors import PedidoNaoEncontrado
from .logging_config import configure_logging, request_id_var
from .routes import router

configure_logging()
logger = logging.getLogger("pedidos")


def _erro(status_code: int, codigo: str, mensagem: str, detalhes=None) -> JSONResponse:
    corpo = {"erro": {"codigo": codigo, "mensagem": mensagem, "requestId": request_id_var.get()}}
    if detalhes:
        corpo["erro"]["detalhes"] = detalhes
    return JSONResponse(status_code=status_code, content=corpo)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = (request.headers.get("X-Request-ID") or str(uuid.uuid4()))[:64]
        token = request_id_var.set(request_id)
        inicio = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Erro inesperado", extra={"operation": "erro_interno"})
                response = _erro(500, "ERRO_INTERNO", "Erro interno do servidor")
            duracao = round((time.perf_counter() - inicio) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            nivel = logging.ERROR if response.status_code >= 500 else logging.INFO
            logger.log(
                nivel,
                "Requisição concluída",
                extra={
                    "operation": "http_request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "durationMs": duracao,
                },
            )
            return response
        finally:
            request_id_var.reset(token)


app = FastAPI(
    title="API de Pedidos",
    version="1.0.0",
    description="API REST simples para gerenciamento de pedidos (CP5 - Arquitetura Orientada a Serviço).",
)
app.add_middleware(RequestContextMiddleware)
app.include_router(router)


@app.exception_handler(PedidoNaoEncontrado)
async def pedido_nao_encontrado_handler(request: Request, exc: PedidoNaoEncontrado):
    logger.warning(
        "Pedido não encontrado", extra={"operation": "consultar_pedido", "orderId": exc.pedido_id}
    )
    return _erro(404, "PEDIDO_NAO_ENCONTRADO", str(exc))


@app.exception_handler(RequestValidationError)
async def validacao_handler(request: Request, exc: RequestValidationError):
    detalhes = [
        {"campo": ".".join(str(p) for p in e["loc"] if p != "body") or "body", "mensagem": e["msg"]}
        for e in exc.errors()
    ]
    logger.warning("Dados inválidos", extra={"operation": "validar_requisicao"})
    return _erro(422, "DADOS_INVALIDOS", "Os dados enviados são inválidos", detalhes)
