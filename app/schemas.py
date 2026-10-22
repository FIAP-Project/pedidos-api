"""Contratos de entrada e saída da API (camada de apresentação)."""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StatusPedido(str, Enum):
    CRIADO = "CRIADO"


class PedidoCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "cliente": "Maria Silva",
                "descricao": "Notebook 14 polegadas",
                "valor": 3499.90,
            }
        },
    )

    cliente: str = Field(..., min_length=1, max_length=120, description="Nome ou identificação do cliente")
    descricao: str = Field(..., min_length=1, max_length=500, description="Descrição do pedido")
    valor: float = Field(..., gt=0, description="Valor do pedido (maior que zero)")


class PedidoResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "0b8f1c3e-5d7a-4a9e-9c11-7f2a6d4e8b10",
                "cliente": "Maria Silva",
                "descricao": "Notebook 14 polegadas",
                "valor": 3499.90,
                "status": "CRIADO",
            }
        }
    )

    id: str = Field(..., description="Identificador único (UUID)")
    cliente: str
    descricao: str
    valor: float
    status: StatusPedido


class ErroDetalhe(BaseModel):
    campo: str
    mensagem: str


class ErroInfo(BaseModel):
    codigo: str
    mensagem: str
    requestId: Optional[str] = None
    detalhes: Optional[List[ErroDetalhe]] = None


class ErroResponse(BaseModel):
    erro: ErroInfo
