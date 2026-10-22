"""Entrada HTTP (camada de API): rotas, validação e códigos de status."""
from fastapi import APIRouter, Depends, Response, status

from .repository import PedidoRepository
from .schemas import ErroResponse, PedidoCreate, PedidoResponse
from .service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

_repository = PedidoRepository()  # instância única, em memória


def get_service() -> PedidoService:
    return PedidoService(_repository)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PedidoResponse,
    summary="Cria um pedido",
    description="Cria um novo pedido com status inicial CRIADO e retorna o recurso criado.",
    responses={
        201: {"description": "Pedido criado", "headers": {"Location": {"description": "URL do novo pedido", "schema": {"type": "string"}}}},
        422: {
            "model": ErroResponse,
            "description": "Dados inválidos (campo ausente, vazio ou valor <= 0)",
            "content": {"application/json": {"example": {"erro": {
                "codigo": "DADOS_INVALIDOS",
                "mensagem": "Os dados enviados são inválidos",
                "requestId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "detalhes": [{"campo": "valor", "mensagem": "Input should be greater than 0"}],
            }}}},
        },
        500: {"model": ErroResponse, "description": "Erro interno inesperado"},
    },
)
def criar_pedido(dados: PedidoCreate, response: Response, service: PedidoService = Depends(get_service)):
    pedido = service.criar(dados)
    response.headers["Location"] = f"/pedidos/{pedido['id']}"
    return pedido


@router.get(
    "/{pedido_id}",
    response_model=PedidoResponse,
    summary="Consulta um pedido pelo identificador",
    responses={
        200: {"description": "Pedido encontrado"},
        404: {
            "model": ErroResponse,
            "description": "Pedido inexistente",
            "content": {"application/json": {"example": {"erro": {
                "codigo": "PEDIDO_NAO_ENCONTRADO",
                "mensagem": "Pedido '123' não encontrado",
                "requestId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            }}}},
        },
        500: {"model": ErroResponse, "description": "Erro interno inesperado"},
    },
)
def consultar_pedido(pedido_id: str, service: PedidoService = Depends(get_service)):
    return service.buscar(pedido_id)
