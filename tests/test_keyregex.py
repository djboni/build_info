#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

import unittest
import sys

try:
    import build_info as bi
except ModuleNotFoundError:
    sys.path.append("../src")
    import build_info as bi

from build_info import KeyRegex, KeyData


class TestKeyRegex(unittest.TestCase):
    def RegexFindallOnString(self, string):
        matches = KeyRegex.findall(string)
        if len(matches) != 1:
            raise ValueError(
                f"Number of matches should be one for {string=} {matches=}"
            )
        return KeyData(*matches[0])

    def test_Regex_ObtainName(self):
        kd = self.RegexFindallOnString("name")
        self.assertEqual("name", kd.name)

    def test_Regex_ObtainName_WithType(self):
        kd = self.RegexFindallOnString("type:name")
        self.assertEqual("name", kd.name)

    def test_Regex_ObtainType(self):
        kd = self.RegexFindallOnString("type:name")
        self.assertEqual("type", kd.type)

    def test_Regex_ObtainQualifier(self):
        kd = self.RegexFindallOnString("type:qualif:name")
        self.assertEqual("qualif", kd.qualif)

    def test_Regex_ObtainBraces(self):
        kd = self.RegexFindallOnString("type[]:qualif:name")
        self.assertEqual("[]", kd.brackets_size)

    def test_Regex_ObtainBraces_WithSize(self):
        kd = self.RegexFindallOnString("type[size]:qualif:name")
        self.assertEqual("[size]", kd.brackets_size)

    def test_Regex_ObtainSize(self):
        kd = self.RegexFindallOnString("type[size]:qualif:name")
        self.assertEqual("size", kd.size)

    def test_Regex_ObtainMacro_Parenthesis(self):
        kd = self.RegexFindallOnString("type:qualif:name()")
        self.assertEqual("()", kd.macro_params)

    def test_Regex_ObtainMacro_WithOneParameter(self):
        kd = self.RegexFindallOnString("type:qualif:name(param)")
        self.assertEqual("(param)", kd.macro_params)

    def test_Regex_ObtainMacro_WithTwoParameters(self):
        kd = self.RegexFindallOnString("type:qualif:name(param1,param2)")
        self.assertEqual("(param1,param2)", kd.macro_params)

    def test_Regex_ObtainMacro_WithWhiteSpace(self):
        kd = self.RegexFindallOnString("type:qualif:name( )")
        self.assertEqual("( )", kd.macro_params)

    def test_Regex_ObtainAll(self):
        kd = self.RegexFindallOnString("type[size]:qualif:name(param1,param2)")
        self.assertEqual("type", kd.type)
        self.assertEqual("size", kd.size)
        self.assertEqual("qualif", kd.qualif)
        self.assertEqual("name", kd.name)
        self.assertEqual("(param1,param2)", kd.macro_params)

    def RegexFindallOnString(self, string):
        matches = KeyRegex.findall(string)
        if len(matches) != 1:
            raise ValueError(
                f"Number of matches should be one for {string=} {matches=}"
            )
        return KeyData(*matches[0])

    def test_Whitespace_OnName(self):
        kd = self.RegexFindallOnString(" name ")
        self.assertEqual("name", kd.name, str(kd))

    def test_Whitespace_OnType(self):
        kd = self.RegexFindallOnString(" type :name")
        self.assertEqual("type", kd.type, str(kd))

    def test_Whitespace_OnQualifier(self):
        kd = self.RegexFindallOnString("type: qualif :name")
        self.assertEqual("qualif", kd.qualif, str(kd))

    def test_Whitespace_OnBraces(self):
        kd = self.RegexFindallOnString("type [] :qualif:name")
        self.assertEqual("[]", kd.brackets_size, str(kd))

    def test_Whitespace_OnSize(self):
        kd = self.RegexFindallOnString("type[ size ]:qualif:name")
        self.assertEqual("size", kd.size, str(kd))

    def test_Whitespace_OnMacro_Parenthesis(self):
        kd = self.RegexFindallOnString("type:qualif: name() ")
        self.assertEqual("()", kd.macro_params, str(kd))

    def test_Whitespace_OnAll(self):
        kd = self.RegexFindallOnString(
            " type [ size ] : qualif : name( param1 , param2 ) "
        )
        self.assertEqual("type", kd.type)
        self.assertEqual("size", kd.size)
        self.assertEqual("qualif", kd.qualif)
        self.assertEqual("name", kd.name)
        self.assertEqual("( param1 , param2 )", kd.macro_params, str(kd))


if __name__ == "__main__":
    unittest.main()
