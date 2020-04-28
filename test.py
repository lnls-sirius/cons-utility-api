#!/usr/bin/env python3

import unittest

import siriushlacommon.data_model
import application.spreadsheet.parser as parser


class TestParser(unittest.TestCase):
    def setUp(self):
        data = parser.loadSheets("Redes e Beaglebones.xlsx")
        self.data_agilent: dict = data[0]
        self.data_mks: dict = data[1]

    def test_data(self):
        self.assertGreater(self.data_agilent.__len__(), 0)
        self.assertGreater(self.data_mks.__len__(), 0)

    def checkTypes(self, data: dict):
        for device in siriushlacommon.data_model.getDevicesFromBeagles(
            siriushlacommon.data_model.getBeaglesFromList(data)
        ):
            self.assertEqual(type(device.prefix), str)
            for channel in device.channels:
                self.assertEqual(type(channel.prefix), str)

    def test_agilent(self):
        self.checkTypes(self.data_agilent)

    def test_mks(self):
        self.checkTypes(self.data_mks)


if __name__ == "__main__":
    unittest.main()
