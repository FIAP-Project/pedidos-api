class PedidoNaoEncontrado(Exception):
    def __init__(self, pedido_id: str):
        self.pedido_id = pedido_id
        super().__init__(f"Pedido '{pedido_id}' não encontrado")
