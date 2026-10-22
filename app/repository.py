"""Armazenamento em memória (camada de dados)."""
import threading
from typing import Dict, Optional


class PedidoRepository:
    def __init__(self) -> None:
        self._dados: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def salvar(self, pedido: dict) -> dict:
        with self._lock:
            self._dados[pedido["id"]] = pedido
        return pedido

    def buscar_por_id(self, pedido_id: str) -> Optional[dict]:
        with self._lock:
            return self._dados.get(pedido_id)
