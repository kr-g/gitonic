import sys
import os
import socket
import select

from .tile.core import log, print_t, print_e
from .tile import TkCmd


def create_socket(port=0):

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        serversocket.bind(("", port))
    except socket.error as err:
        print_e(err)
        return

    port = serversocket.getsockname()

    # become a server socket
    serversocket.listen()

    return serversocket


def create_client_socket(port=0):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("", port))
    try:
        rc = sock.send("helo\n".encode())
        print_t("send helo", rc)
    except Exception as ex:
        print_t("create_client_socket", ex)

    return sock


def bring_to_front(wndw):
    wndw.deiconify()
    wndw.lift()


def check_and_bring_to_front(sock, wndw, accept_and_close=True):
    active, _, _ = select.select([sock], [], [], 0)
    if len(active) == 0:
        return

    (clientsocket, address) = sock.accept()

    if accept_and_close:
        bring_to_front(wndw)
        clientsocket.close()
        return 0

    return sok


def check_instance(pnam):

    port = 0
    try:
        print_t("reading last known socket", pnam)
        with open(pnam) as f:
            port = f.read()
            port = port.strip()
            port = int(port)
            print_t("last known port", port)
    except Exception as ex:
        print_e("app-socket read", ex)

    print_t("try port", port)
    sock = create_socket(port)

    if sock == None:
        print_t("port in use !!!")
        return None, port
    else:
        print_t("port not in use")

    sock.close()

    sock = create_socket()

    _, port = sock.getsockname()
    print_t("new free port", port)

    try:
        print_t("writing last known socket", pnam)
        with open(pnam, "w") as f:
            f.write(str(port))
    except Exception as ex:
        print_e("app-socket write", ex)

    return sock, port
