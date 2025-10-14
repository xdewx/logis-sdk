import websockets


def parse_client_info(connection: websockets.ServerConnection):
    """
    从连接中解析客户端ip、port等信息
    """
    client_ip, client_port = connection.transport.get_extra_info("peername")
    return client_ip, client_port
