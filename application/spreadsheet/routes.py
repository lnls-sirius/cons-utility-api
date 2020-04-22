from flask import Blueprint, render_template
from flask import current_app, request

from .common import Devices, DevicesList
from .client import BackendClient

from application.utils import get_logger

# Set up a Blueprint
spreadsheet_bp = Blueprint(
    "spreadsheet_bp", __name__, template_folder="templates", static_folder="static"
)


logger = get_logger("Spreadsheet Routes")


@spreadsheet_bp.route("/reload")
def reload():
    try:
        client = BackendClient()
        client.reloadData()
        return f"Data reloaded succesfully!", 200

    except Exception:
        logger.exceptino("reload entries failed.")
        return (
            f"Unable to update entries from spreadsheet.",
            400,
        )


@spreadsheet_bp.route("/status")
def status():
    # @todo: Return status information.
    return f"Healthy!", 200


@spreadsheet_bp.route("/devices")
def devices():
    deviceType = request.args.get("type", None)
    ip = request.args.get("ip", None)

    try:
        client = BackendClient()
        response = client.getDevice(deviceType=deviceType, ip=ip)
        return response, 200
    except Exception:
        logger.exception("routes")
        return (
            'Invalid response from backend. Available "deviceType" options are "{}".'.format(
                DevicesList
            ),
            422,
        )
