"""Regras de negócio (camada de serviço)."""
import logging
import uuid

from .errors import PedidoNaoEncontrado
from .repository import PedidoRepository
from .schemas import PedidoCreate, StatusPedido

logger = logging.getLogger("pedidos")


class PedidoService:
    def __init__(self, repository: PedidoRepository) -> None:
        self._repo = repository

    def criar(self, dados: PedidoCreate) -> dict:
        pedido = {
            "id": str(uuid.uuid4()),
            "cliente": dados.cliente,
            "descricao": dados.descricao,
            "valor": dados.valor,
            "status": StatusPedido.CRIADO.value,  # status inicial definido pelo servidor
        }
        self._repo.salvar(pedido)
        logger.info("Pedido criado", extra={"operation": "criar_pedido", "orderId": pedido["id"]})
        return pedido

    def buscar(self, pedido_id: str) -> dict:
        pedido = self._repo.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNaoEncontrado(pedido_id)
        logger.info("Pedido consultado", extra={"operation": "consultar_pedido", "orderId": pedido_id})
        return pedido
