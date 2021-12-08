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


class TestProcessJSONVersionData(unittest.TestCase):
    """Based on Semantic Versioning https://semver.org/"""

    def setUp(self):
        self.bi = bi.BuildInfo()

    def test_VersionString_CreateVariablesAndFunctions_InC(self):
        self.bi.ProcessJSON('{"Version": [1, 0, 0, "", ""]}')
        lines = [
            'static char Version_Str[] = "',
            "static uint32_t Version_Num = ",
            "const char *PtrVersionStr(void) {",
            "uint32_t GetVersionNum(void) {",
        ]
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_CreateFunctions_InH(self):
        self.bi.ProcessJSON('{"Version": [1, 0, 0, "", ""]}')
        lines = [
            "const char *PtrVersionStr(void);",
            "uint32_t GetVersionNum(void);",
        ]
        code = self.bi.GetH()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_MajorMinor_v10(self):
        self.bi.ProcessJSON('{"Version": [1, 0, 0, "", ""]}')
        lines = ['static char Version_Str[] = "1.0"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_MajorMinor_v01(self):
        self.bi.ProcessJSON('{"Version": [0, 1, 0, "", ""]}')
        lines = ['static char Version_Str[] = "0.1"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_MajorMinorPatch_v012(self):
        self.bi.ProcessJSON('{"Version": [0, 1, 2, "", ""]}')
        lines = ['static char Version_Str[] = "0.1.2"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_PreRelease(self):
        self.bi.ProcessJSON('{"Version": [0, 1, 2, "alpha", ""]}')
        lines = ['static char Version_Str[] = "0.1.2-alpha"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_PreReleaseAndBuildMetadata(self):
        self.bi.ProcessJSON('{"Version": [0, 1, 2, "alpha", "001"]}')
        lines = ['static char Version_Str[] = "0.1.2-alpha+001"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionString_BuildMetadata(self):
        self.bi.ProcessJSON('{"Version": [0, 1, 2, "", "001"]}')
        lines = ['static char Version_Str[] = "0.1.2+001"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_VersionStr_Value_MustBeAnArray(self):
        json_value_list = ['""', "0", "{}", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": {json_value}}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_FirstElement_MustBeAnInteger(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": [{json_value}, 1, 2, "", ""]}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_SecondElement_MustBeAnInteger(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": [0, {json_value}, 2, "", ""]}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_ThirdElement_MustBeAnInteger(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": [0, 1, {json_value}, "", ""]}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_FourthElement_MustBeAString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": [0, 1, 2, {json_value}, ""]}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_FifthElement_MustBeAString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Version": [0, 1, 2, "", {json_value}]}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_VersionStr_FourOrLessElements_IsTooLittle(self):
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, 1, 2, ""]}')

    def test_VersionStr_SixOrMoreElements_IsTooMuch(self):
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, 1, 2, "", "", ""]}')

    def test_VersionStr_MajorMinorPatch_NonNegative(self):
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [-1, 1, 2, "", ""]}')
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, -1, 2, "", ""]}')
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, 1, -1, "", ""]}')

    def test_VersionStr_MajorMinorPatch_LessThan256(self):
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [256, 1, 2, "", ""]}')
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, 256, 2, "", ""]}')
        with self.assertRaises(ValueError):
            self.bi.ProcessJSON('{"Version": [0, 1, 256, "", ""]}')


if __name__ == "__main__":
    unittest.main()
