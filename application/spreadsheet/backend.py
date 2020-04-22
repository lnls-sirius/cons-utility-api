import socket
import select
import os
import pickle
import threading
import logging

from application.utils import get_logger
from .parser import loadSheets
from .common import BasicComm, DevicesList, Command, Devices, SPREADSHEET_SOCKET_PATH


SERVER_SOCKET_TIMEOUT = 5


class InvalidParameter(Exception):
    pass


class BackendServer(BasicComm):
    def __init__(self):
        self.logger = get_logger("Backend")
        self.logger.setLevel(logging.DEBUG)
        self.run = True
        self.socket_path = SPREADSHEET_SOCKET_PATH
        self.socket_timeout = SERVER_SOCKET_TIMEOUT
        self.thread = threading.Thread(target=self.listen, daemon=True)

        self.Agilent = None
        self.MKS = None

    def start(self):
        self.logger.info("Starting backend server thread.")
        self.thread.start()

    def fromClient(self, conn):
        payload_bytes = b""
        payload_length = int.from_bytes(self.recvBytes(conn, 4), "big")
        payload_bytes = self.recvBytes(conn, payload_length)

        return payload_bytes

    def toClient(self, conn, response):
        response_length = len(response)

        self.sendBytes(conn, response_length.to_bytes(4, "big"))
        self.sendBytes(conn, response)

    def listen(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            self.logger.warning('Removing socket at "{}"'.format(self.socket_path))

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:

            s.bind(self.socket_path)
            s.listen()

            while self.run:
                self.logger.info(
                    'Waiting for a connection at "{}" ...'.format(self.socket_path)
                )
                conn, addr = s.accept()
                self.logger.info("Client connected ...")
                with conn:
                    try:
                        conn.setblocking(False)
                        payload_bytes = self.fromClient(conn)
                        if payload_bytes != b"":
                            payload = pickle.loads(payload_bytes)
                            response = pickle.dumps(self.handle(payload))
                            self.toClient(conn, response)

                    except InvalidParameter as e:
                        self.logger.error('Invalid paylad content. "{}"'.format(e))
                        self.toClient(conn, pickle.dumps({}))

                    except Exception:
                        self.logger.exception(
                            "The connection with the unix socket {} has been closed."
                        )
                    self.logger.info("Connection with client closed.")
        self.logger.info("Shutting down gracefully.")

    def handle(self, payload: dict):
        command = payload["command"]
        self.logger.info("Handle: {}".format(command))

        if command == Command.GET_DEVICE:
            return self.getDevice(**payload)
        elif command == Command.RELOAD_DATA:
            self.Agilent, self.MKS = loadSheets()
            return True

        return None

    def getDevice(self, deviceType=None, ip=None, **kwargs):

        if deviceType not in DevicesList:
            raise InvalidParameter('Invalid "deviceType".')

        if deviceType == Devices.AGILENT.value:
            return self.getAgilent(ip)

        elif deviceType == Devices.MKS.value:
            return self.getMKS(ip)

        self.logger.warning('No handler for device type "{}"'.format(deviceType))
        return {}

    def getAgilent(self, ip=None):
        if not self.Agilent:
            self.logger.warning("Agilent data not loaded")
            return {}

        if not ip:
            return self.Agilent
        else:
            return {} if ip not in self.Agilent else {ip: self.Agilent[ip]}

    def getMKS(self, ip=None):
        if not self.MKS:
            self.logger.warning("MKS data not loaded")
            return {}

        if not ip:
            return self.MKS
        else:
            return {} if ip not in self.MKS else {ip: self.MKS[ip]}
