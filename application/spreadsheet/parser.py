#!/usr/bin/env python3
import pandas

from application.utils import get_logger
from .common import SPREADSHEET_XLSX_PATH

logger = get_logger("Parser")


def normalizeAgilent(sheet):
    return normalize(sheet, ["C1", "C2", "C3", "C4"])


def normalizeMKS(sheet):
    return normalize(sheet, ["A1", "A2", "B1", "B2", "C1", "C2"])


def normalize(sheet, ch_names: list):
    """ Create a dictionary with the beaglebone IP as keys.  Aka: {ip:[devices ...] ... ipn:[devicesn ... ]} """
    ips = {}
    try:
        for n, row in sheet.iterrows():
            ip = row["IP"]
            if ip not in ips:
                ips[ip] = []
            ip_devices = ips[ip]
            data = {}

            ip_devices.append(data)
            data["enable"] = row["ENABLE"] if type(row["ENABLE"]) is bool else False
            data["device"] = row["Dispositivo"]

            info = {}
            info["sector"] = row["Setor"]
            info["serial_id"] = row["RS485 ID"]
            info["rack"] = row["Rack"]
            info["config"] = row["Configuracao"] if "Configuracao" in row else ""

            data["info"] = info

            channels = {}
            num = 0
            for ch_name in ch_names:
                channel = {}
                channel["name"] = ch_name
                channel["prefix"] = row[ch_name]

                config = {}
                config["pressure_hi"] = row["HI " + ch_name]
                config["pressure_hihi"] = row["HIHI " + ch_name]
                channel["config"] = config

                channels[num] = channel
                num += 1

            data["channels"] = channels
    except Exception:
        logger.exception("Failed to update data from spreadsheet.")

    logger.info("Loaded data from sheet with {} different IPs.".format(len(ips)))
    return ips


def loadSheets():

    logger.info('Loading spreadsheet from url "{}".'.format(SPREADSHEET_XLSX_PATH))
    sheets = pandas.read_excel(SPREADSHEET_XLSX_PATH, sheet_name=None,)

    for sheetName in sheets:
        if "PVs" in sheetName:
            sheetNameUpper = sheetName.upper()
            sheet = sheets[sheetName]

            if "AGILENT" in sheetNameUpper:
                Agilent = normalizeAgilent(sheet)
            elif "MKS" in sheetNameUpper:
                MKS = normalizeMKS(sheet)
    return Agilent, MKS
