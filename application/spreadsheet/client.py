import logging
import os
import pickle
import select
import socket
import threading
import time

from application.utils import get_logger
from .parser import loadSheets
from .common import (
    DevicesList,
    Command,
    Devices,
    SPREADSHEET_SOCKET_PATH,
    SPREADSHEET_XLSX_PATH,
)


CLIENT_SOCKET_TIMEOUT = 10


class SyncService:
    def __init__(self):
        self.logger = get_logger("SyncService")
        self.thread = threading.Thread(target=self.doWork, daemon=True)
        self.update_time = None

    def start(self):
        self.logger.info("Starting sync service.")
        self.thread.start()

    def doWork(self):
        while True:
            if os.path.exists(SPREADSHEET_XLSX_PATH):
                current_update_time = os.path.getmtime(SPREADSHEET_XLSX_PATH)
                if not self.update_time or self.update_time != current_update_time:
                    try:
                        client = BackendClient()
                        res = client.reloadData()
                        if not res:
                            raise Exception('Method "reloadData" returned False.')
                        self.update_time = current_update_time
                        self.logger.info(
                            'Update spreadsheet from "{}" at time "{}"'.format(
                                SPREADSHEET_XLSX_PATH, self.update_time
                            )
                        )
                    except:
                        self.logger.exception("Failed to update the spreadsheet.")
            time.sleep(5)


class BackendClient:
    def __init__(self):
        self.socket_path = SPREADSHEET_SOCKET_PATH
        self.socket_timeout = CLIENT_SOCKET_TIMEOUT

        self.logger = get_logger("Client")
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("BackendClient created")

    def sendCommand(self, payload: dict):
        if "command" not in payload:
            raise Exception('Missing "command"')

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            try:
                self.logger.debug("Connecting to server ...")
                s.connect(self.socket_path)
                payload_bytes = pickle.dumps(payload)
                payload_length = len(payload_bytes).to_bytes(4, "big")
                self.logger.debug(
                    'Sending payload with size {} "{}"'.format(
                        len(payload_bytes), payload_length
                    )
                )
                s.sendall(payload_length)
                s.sendall(payload_bytes)

                ready = select.select([s], [], [], self.socket_timeout)
                if ready[0]:
                    response_len = int.from_bytes(s.recv(4), "big")
                    self.logger.info("Preparing to read {} bytes".format(response_len))
                    response_bytes = s.recv(response_len)
                    response = pickle.loads(response_bytes)
                    return response
            except Exception:
                self.logger.exception("Failed to load reponse from backend server")
        return {}

    def reloadData(self):
        return self.sendCommand({"command": Command.RELOAD_DATA})

    def getDevice(self, ip, deviceType):
        return self.sendCommand(
            {"command": Command.GET_DEVICE, "ip": ip, "deviceType": deviceType}
        )
