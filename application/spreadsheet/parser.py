#!/usr/bin/env python3
from typing import Tuple

import pandas
import numpy

from application.utils import get_logger

logger = get_logger("Parser")

MKS_CONFIG_CC = "ColdCathode"
MKS_CONFIG_PIRANI = "Pirani"
MKS_CONFIG_NOT_USED = "NotUsed"


def normalizeAgilent(sheet) -> dict:
    return normalize(sheet, ["C1", "C2", "C3", "C4"])


def normalizeMKS(sheet) -> dict:
    return normalize(sheet, ["A1", "A2", "B1", "B2", "C1", "C2"])


def normalize(sheet, ch_names: list) -> dict:
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
            data["prefix"] = row["Dispositivo"]

            info = {}
            info["sector"] = row["Setor"]
            info["serial_id"] = row["RS485 ID"]
            info["rack"] = row["Rack"]
            data["info"] = info

            channels = {}
            num = 0
            for ch_name in ch_names:
                channel = {}
                channel["num"] = num
                channel["prefix"] = row[ch_name]
                channel["enable"] = row[ch_name] != "" or row[ch_name] is None

                info = {}
                info["pressure_hi"] = row["HI " + ch_name]
                info["pressure_hihi"] = row["HIHI " + ch_name]
                if "Sensor " + ch_name in row:
                    info["sensor"] = row["Sensor " + ch_name]
                channel["info"] = info

                channels[ch_name] = channel
                num += 1

            data["channels"] = channels
    except Exception:
        logger.exception("Failed to update data from spreadsheet.")

    logger.info("Loaded data from sheet with {} different IPs.".format(len(ips)))
    return ips


def loadSheets(spreadsheet_xlsx_path: str) -> Tuple[dict, dict]:
    """ Tuple of dictionaries. (Agilent, MKS) """

    logger.info('Loading spreadsheet from url "{}".'.format(spreadsheet_xlsx_path))
    sheets = pandas.read_excel(spreadsheet_xlsx_path, sheet_name=None,)
    for sheetName in sheets:
        if "PVs" in sheetName:
            sheetNameUpper = sheetName.upper()
            sheet = sheets[sheetName].replace(numpy.nan, "", regex=True)

            if "AGILENT" in sheetNameUpper:
                Agilent = normalizeAgilent(sheet)
            elif "MKS" in sheetNameUpper:
                MKS = normalizeMKS(sheet)
    return Agilent, MKS
