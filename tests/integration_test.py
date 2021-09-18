import os
import json
import subprocess
import socket

TIMEOUT = 5

import pytest

class TCPServer:
    def __init__(self, bind_interface="0.0.0.0", bind_port=0):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((bind_interface, bind_port))
        self.port = self._sock.getsockname()[1]
        self._sock.listen(1)

    def accept_connection(self, timeout):
        '''Returns connected socket'''
        self._sock.settimeout(timeout)
        return self._sock.accept()[0]

@pytest.mark.integration
def test_integration():
    with open(os.path.join("output", "manifest.json"), "r") as file_:
        manifest = json.load(file_)

    plugin_path = os.path.join("output", manifest["script"])

    request = {
        "id": "3",
        "jsonrpc": "2.0",
        "method": "get_capabilities"
    }
    token = "token"
    server = TCPServer()
    result = subprocess.Popen(
        ["python", plugin_path, token, str(server.port), "plugin.log"]
    )

    plugin_socket = server.accept_connection(TIMEOUT)
    plugin_socket.settimeout(TIMEOUT)
    plugin_socket.sendall((json.dumps(request)+"\n").encode("utf-8"))
    response = json.loads(plugin_socket.recv(4096))
    print(response)
    assert response["result"]["platform_name"] == "psn"
    assert set(response["result"]["features"]) == set([
                'ImportOwnedGames',
                'ImportSubscriptions',
                'ImportSubscriptionGames',
            ])
    assert response["result"]["token"] == token

    plugin_socket.close()
    result.wait(TIMEOUT)
    assert result.returncode == 0
