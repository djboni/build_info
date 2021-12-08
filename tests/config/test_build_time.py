#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

import unittest
from unittest.mock import Mock, patch
import sys

try:
    import build_info as bi
except ModuleNotFoundError:
    sys.path.append("../src")
    sys.path.append("../../src")
    import build_info as bi

try:
    from helper import *
except ModuleNotFoundError:
    sys.path.append("..")
    from helper import *


class TestProcessJSONTimeData(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.bi = bi.BuildInfo()
        self.time_mock = TimeMock()
        self.patch1 = patch("build_info.time", self.time_mock)
        self.patch1_enter = self.patch1.__enter__()
        self.patch2 = patch("build_info.datetime", self.time_mock)
        self.patch2_enter = self.patch2.__enter__()

    def tearDown(self) -> None:
        self.patch2.__exit__(None, None, None)
        self.patch1.__exit__(None, None, None)

        return super().tearDown()

    def test_TimeData_AddsNumberWithUnixTime_InC(self):
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ["static uint32_t Unix_Time = ", "uint32_t GetUnixTime(void) {"]
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_AddsNumberWithUnixTime_InH(self):
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ["uint32_t GetUnixTime(void);"]
        code = self.bi.GetH()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_AddsStringWithTime_InC(self):
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ['static char Time_Str[] = "', "const char *PtrTimeStr(void) {"]
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_AddsStringWithTime_InH(self):
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ["const char *PtrTimeStr(void);"]
        code = self.bi.GetH()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_ValueMustBeBoolean(self):
        json_value_list = ['""', "0", "{}", "[]", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Date_Time": {json_value}}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_TimeData_GetCorrectUnixTime(self):
        self.time_mock.SetUnixTime(1.0)
        self.time_mock.SetTimeStr("1970-01-01 00:00:01")
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ["static uint32_t Unix_Time = 1;"]
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_GetCorrectTimeString(self):
        self.time_mock.SetUnixTime(1.0)
        self.time_mock.SetTimeStr("1970-01-01 00:00:01")
        self.bi.ProcessJSON('{"Date_Time": true}')
        lines = ['static char Time_Str[] = "1970-01-01 00:00:01";']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_TimeData_ValueFalseAddsNothing_InC(self):
        self.bi.ProcessJSON('{"Date_Time": false}')
        code = self.bi.GetC()
        self.assertNotIn("Unix_Time", code)
        self.assertNotIn("GetUnixTime", code)
        self.assertNotIn("Time_Str", code)
        self.assertNotIn("GetTimeStr", code)

    def test_TimeData_ValueFalseAddsNothing_InH(self):
        self.bi.ProcessJSON('{"Date_Time": false}')
        code = self.bi.GetC()
        self.assertNotIn("GetUnixTime", code)
        self.assertNotIn("GetTimeStr", code)


if __name__ == "__main__":
    unittest.main()
