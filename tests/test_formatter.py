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

try:
    from helper import *
except ModuleNotFoundError:
    sys.path.append("..")
    from helper import *


class TestProcessJSONDefaultFormatter(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_FormatGlobalVariable(self):
        self.converter.ProcessJSON('{"int8:r:Int_Val": 0}')
        code = self.converter.GetC()
        lines = ["static int8_t Int_Val = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_FormatFunction(self):
        self.converter.ProcessJSON('{"int8:r:Int_Val": 0}')
        code = self.converter.GetC()
        lines = ["int8_t GetIntVal(void) {"]
        AssertIsInSequence(lines, code, self)

    def test_FormatMacro(self):
        self.converter.ProcessJSON('{"macro:Int_Val": "1"}')
        code = self.converter.GetH()
        lines = ["#define INT_VAL 1"]
        AssertIsInSequence(lines, code, self)

    def test_FormatPrefix(self):
        self.converter.ProcessJSON(
            '{"Section_Prefix": "MDL_NAM", "int8:r:Int_Val": 0}'
        )
        code = self.converter.GetC()
        lines = ["static int8_t MDL_NAM_Int_Val = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_FormatHeaderFilename(self):
        self.converter.ProcessJSON('{"Module_Name": "Int_Val"}')
        code = self.converter.GetC()
        lines = ['#include "int_val.h"']
        AssertIsInSequence(lines, code, self)

    def test_FormatHeaderGuard(self):
        self.converter.ProcessJSON('{"Module_Name": "Int_Val"}')
        code = self.converter.GetH()
        lines = ["#define INT_VAL_H_"]
        AssertIsInSequence(lines, code, self)


class TestProcessJSONSecondFormatter(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo(formatter=bi.SecondFormatter())

    def test_FormatGlobalVariable(self):
        self.converter.ProcessJSON('{"int8:r:Int_Val": 0}')
        code = self.converter.GetC()
        lines = ["static int8_t IntVal = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_FormatFunction(self):
        self.converter.ProcessJSON('{"int8:r:Int_Val": 0}')
        code = self.converter.GetC()
        lines = ["int8_t get_int_val(void) {"]
        AssertIsInSequence(lines, code, self)

    def test_FormatMacro(self):
        self.converter.ProcessJSON('{"macro:Int_Val": "1"}')
        code = self.converter.GetH()
        lines = ["#define INT_VAL 1"]
        AssertIsInSequence(lines, code, self)

    def test_FormatPrefix(self):
        self.converter.ProcessJSON(
            '{"Section_Prefix": "MDL_NAM", "int8:r:Int_Val": 0}'
        )
        code = self.converter.GetC()
        lines = ["static int8_t MDL_NAM_IntVal = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_FormatHeaderFilename(self):
        self.converter.ProcessJSON('{"Module_Name": "Int_Val"}')
        code = self.converter.GetC()
        lines = ['#include "int_val.h"']
        AssertIsInSequence(lines, code, self)

    def test_FormatHeaderGuard(self):
        self.converter.ProcessJSON('{"Module_Name": "Int_Val"}')
        code = self.converter.GetH()
        lines = ["#define INT_VAL_H_"]
        AssertIsInSequence(lines, code, self)


class TestDefaultFormatter(unittest.TestCase):
    def test_FormaLocalVariable(self):
        self.assertEqual(
            "val_int", bi.DefaultFormatter().NameToLocalVariable("Val_Int")
        )

    def test_FormatGlobalVariable(self):
        self.assertEqual(
            "Val_Int", bi.DefaultFormatter().NameToGlobalVariable("Val_Int")
        )

    def test_FormatFunction(self):
        self.assertEqual(
            "ValInt", bi.DefaultFormatter().NameToFunction("Val_Int")
        )

    def test_FormatMacro(self):
        self.assertEqual(
            "VAL_INT", bi.DefaultFormatter().NameToMacro("Val_Int")
        )

    def test_FormatPrefix(self):
        self.assertEqual(
            "VAL_INT_", bi.DefaultFormatter().NameToPrefix("Val_Int")
        )

    def test_FormatSourceFilename(self):
        self.assertEqual(
            "val_int.c", bi.DefaultFormatter().NameToSourceFilename("Val_Int")
        )

    def test_FormatHeaderFilename(self):
        self.assertEqual(
            "val_int.h", bi.DefaultFormatter().NameToHeaderFilename("Val_Int")
        )

    def test_FormatHeaderGuard(self):
        self.assertEqual(
            "VAL_INT_H_", bi.DefaultFormatter().NameToHeaderGuard("Val_Int")
        )


class TestSecondFormatter(unittest.TestCase):
    def test_FormaLocalVariable(self):
        self.assertEqual(
            "valInt", bi.SecondFormatter().NameToLocalVariable("Val_Int")
        )

    def test_FormatGlobalVariable(self):
        self.assertEqual(
            "ValInt", bi.SecondFormatter().NameToGlobalVariable("Val_Int")
        )

    def test_FormatFunction(self):
        self.assertEqual(
            "val_int", bi.SecondFormatter().NameToFunction("Val_Int")
        )

    def test_FormatMacro(self):
        self.assertEqual("VAL_INT", bi.SecondFormatter().NameToMacro("Val_Int"))

    def test_FormatPrefix(self):
        self.assertEqual(
            "VAL_INT_", bi.SecondFormatter().NameToPrefix("Val_Int")
        )

    def test_FormatSourceFilename(self):
        self.assertEqual(
            "val_int.c", bi.SecondFormatter().NameToSourceFilename("Val_Int")
        )

    def test_FormatHeaderFilename(self):
        self.assertEqual(
            "val_int.h", bi.SecondFormatter().NameToHeaderFilename("Val_Int")
        )

    def test_FormatHeaderGuard(self):
        self.assertEqual(
            "VAL_INT_H_", bi.SecondFormatter().NameToHeaderGuard("Val_Int")
        )


if __name__ == "__main__":
    unittest.main()
