"""Flask config class."""
import os


class Config:
    """Base config vars."""

    DEBUG = True
    TESTING = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    """ This can be an url or a filesystem path.
        If it's a filesystem path, it will automatically be updated when the file changes. """
    SPREADSHEET_XLSX_PATH = os.environ.get(
        "SPREADSHEET_XLSX_PATH",
        "http://10.0.38.42/streamdevice-ioc/Redes%20e%20Beaglebones.xlsx",
    )
    SPREADSHEET_SOCKET_PATH = os.environ.get(
        "SPREADSHEET_SOCKET_PATH", "/var/tmp/devices_socket"
    )
