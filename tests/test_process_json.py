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


class TestProcessJSON(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_CanBeAnObject(self):
        self.converter.ProcessJSON("{}")

    def test_CanBeAnArray(self):
        self.converter.ProcessJSON("[]")

    def test_CanBeAnArrayWithOneObject(self):
        self.converter.ProcessJSON("[{}]")

    def test_CanBeAnArrayWithSeveralObjects(self):
        self.converter.ProcessJSON("[{},{},{}]")

    def test_JSONData_IsNotObjectOrArray_RaisesValueError(self):
        json_data_list = ['""', "0", "true", "false", "null"]
        for json_data in json_data_list:
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_JSONData_IsArrayWithNonObject_RaisesValueError(self):
        json_data_list = ['""', "[]", "0", "true", "false", "null"]
        for json_data in json_data_list:
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(f"[{json_data}]")

    def test_ModuleName_NoError(self):
        self.converter.ProcessJSON('{"Section_Prefix": "MODULE"}')

    def test_ModuleName_MustBeString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            with self.assertRaises(ValueError):
                self.converter.ProcessJSON(
                    f'{{"Section_Prefix": {json_value}}}'
                )

    def test_PassInvalidConfig_ValueError(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"Invalid_Config": "CONFIG"}')


class TestStringProcessJSON(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_PassKeyString_VariablePresentInC(self):
        self.converter.ProcessJSON('{"string:NAME": "VALUE"}')
        code = self.converter.GetC()
        lines = ['static char NAME[] = "VALUE";']
        AssertIsInSequence(lines, code, self)

    def test_PassOtherString_VariablePresentInC(self):
        self.converter.ProcessJSON('{"string:NAME": "OTHER_VALUE"}')
        lines = ['static char NAME[] = "OTHER_VALUE";']
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_PassOtherKey_VariablePresentInC(self):
        self.converter.ProcessJSON('{"string:OTHER_NAME": "VALUE"}')
        code = self.converter.GetC()
        lines = ['static char OTHER_NAME[] = "VALUE";']
        AssertIsInSequence(lines, code, self)

    def test_PassKeyString_FunctionPresentInC(self):
        self.converter.ProcessJSON('{"string:NAME": "VALUE"}')
        code = self.converter.GetC()
        self.assertIn("const char *PtrNAME(void) {", code)
        self.assertIn("return &NAME[0];", code)
        self.assertIn("}", code)

    def test_PassOtherString_FunctionPresentInC(self):
        self.converter.ProcessJSON('{"string:NAME": "OTHER_VALUE"}')
        code = self.converter.GetC()
        self.assertIn("const char *PtrNAME(void) {", code)
        self.assertIn("return &NAME[0];", code)
        self.assertIn("}", code)

    def test_PassOtherKey_FunctionPresentInC(self):
        self.converter.ProcessJSON('{"string:OTHER_NAME": "VALUE"}')
        code = self.converter.GetC()
        self.assertIn("const char *PtrOTHERNAME(void) {", code)
        self.assertIn("return &OTHER_NAME[0];", code)
        self.assertIn("}", code)

    def test_PassKeyStringAndModuleName_VariablePresentInC(self):
        self.converter.ProcessJSON(
            """{
                "Section_Prefix": "BUILD",
                "string:NAME": "VALUE"
            }"""
        )
        code = self.converter.GetC()
        lines = ['static char BUILD_NAME[] = "VALUE";']
        AssertIsInSequence(lines, code, self)

    def test_PassKeyStringAndModuleName_FunctionPresentInC(self):
        self.converter.ProcessJSON(
            """{
                "Section_Prefix": "BUILD",
                "string:NAME": "VALUE"
            }"""
        )
        code = self.converter.GetC()
        self.assertIn("const char *BUILD_PtrNAME(void) {", code)
        self.assertIn("return &BUILD_NAME[0];", code)
        self.assertIn("}", code)

    def test_ModuleNameAfterData_IsUsed(self):
        self.converter.ProcessJSON(
            """{
                "string:NAME": "VALUE",
                "Section_Prefix": "BUILD"
            }"""
        )
        code = self.converter.GetC()
        lines = ['static char BUILD_NAME[] = "VALUE";']
        AssertIsInSequence(lines, code, self)

    def test_PassTwoStrings_VariablesPresentInC(self):
        self.converter.ProcessJSON(
            """{
                "string:NAME1": "VALUE1",
                "string:NAME2": "VALUE2"
            }"""
        )
        code = self.converter.GetC()
        lines = [
            'static char NAME1[] = "VALUE1";',
            'static char NAME2[] = "VALUE2";',
        ]
        AssertIsInSequence(lines, code, self)

    def test_PassTwoStrings_FunctionsPresentInC(self):
        self.converter.ProcessJSON(
            """{
                "string:NAME1": "VALUE1",
                "string:NAME2": "VALUE2"
            }"""
        )
        code = self.converter.GetC()
        self.assertIn("const char *PtrNAME1(void) {", code)
        self.assertIn("return &NAME1[0];", code)
        self.assertIn("}", code)
        self.assertIn("const char *PtrNAME2(void) {", code)
        self.assertIn("return &NAME2[0];", code)
        self.assertIn("}", code)

    def test_PassKeyString_FunctionPresentInH(self):
        self.converter.ProcessJSON('{"string:NAME": "VALUE"}')
        self.assertIn("const char *PtrNAME(void);", self.converter.GetH())

    def test_PassOtherString_FunctionPresentInH(self):
        self.converter.ProcessJSON('{"string:NAME": "OTHER_VALUE"}')
        self.assertIn("const char *PtrNAME(void);", self.converter.GetH())

    def test_PassOtherKey_FunctionPresentInH(self):
        self.converter.ProcessJSON('{"string:OTHER_NAME": "VALUE"}')
        self.assertIn("const char *PtrOTHERNAME(void);", self.converter.GetH())

    def test_PassKeyStringAndModuleName_FunctionPresentInH(self):
        self.converter.ProcessJSON(
            """{
                "Section_Prefix": "BUILD",
                "string:NAME": "VALUE"
            }"""
        )
        self.assertIn("const char *BUILD_PtrNAME(void);", self.converter.GetH())

    def test_PassTwoStrings_FunctionsPresentInH(self):
        self.converter.ProcessJSON(
            """{
                "string:NAME1": "VALUE1",
                "string:NAME2": "VALUE2"
            }"""
        )
        code = self.converter.GetH()
        self.assertIn("const char *PtrNAME1(void);", code)
        self.assertIn("const char *PtrNAME2(void);", code)

    def test_TypeStringAndValueNotString_CausesValueError(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"string:OTHER_NAME": {json_value}}}'
            with self.assertRaises(ValueError):
                self.converter.ProcessJSON(json_data)

    def test_InvalidType_CausesValueError(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"Invalid_Type:NAME": "VALUE"}')

    def test_String_HasLengthFunction_InH(self):
        self.converter.ProcessJSON('{"string:NAME": "VALUE"}')
        lines = ["uint16_t LenNAME(void);", "const char *PtrNAME(void);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)

    def test_String_HasLengthFunction_InC(self):
        self.converter.ProcessJSON('{"string:NAME": "VALUE"}')
        lines = [
            "uint16_t LenNAME(void) {",
            "return sizeof(NAME);",
            "}",
            "const char *PtrNAME(void) {",
        ]
        AssertIsInSequence(lines, self.converter.GetC(), self)

    def test_StringWritable_IsNotConst(self):
        self.converter.ProcessJSON('{"string:w:NAME": "VALUE"}')
        lines = ['static char NAME[] = "VALUE"']
        AssertIsInSequence(lines, self.converter.GetC(), self)

    def test_StringWritable_HasSetFunction(self):
        self.converter.ProcessJSON('{"string:w:NAME": "VALUE"}')
        lines = ["bool SetNAME(const char *buff_ptr, uint16_t len);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)
        lines = ["bool SetNAME(const char *buff_ptr, uint16_t len) {", "}"]
        AssertIsInSequence(lines, self.converter.GetC(), self)


class TestGetH(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_HeaderGuard_IsPresent(self):
        self.converter.ProcessJSON("{}")
        code = self.converter.GetH()
        self.assertIn("#ifndef INFO_H_", code)
        self.assertIn("#define INFO_H_", code)
        self.assertIn("#endif /* INFO_H_ */", code)

    def test_HeaderGuard_UsesModuleName(self):
        self.converter.ProcessJSON("""{"Section_Prefix": "BUILD"}""")
        code = self.converter.GetH()
        self.assertIn("#ifndef BUILD_H_", code)
        self.assertIn("#define BUILD_H_", code)
        self.assertIn("#endif /* BUILD_H_ */", code)

    def test_IncludeStdint_IsPresent(self):
        self.converter.ProcessJSON("{}")
        self.assertIn("#include <stdint.h>", self.converter.GetH())


class TestGetC(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_IncludeHeader_IsPresent(self):
        self.converter.ProcessJSON("{}")
        self.assertIn('#include "info.h"', self.converter.GetC())

    def test_IncludeHeader_UsesModuleName(self):
        self.converter.ProcessJSON('{"Section_Prefix": "BUILD"}')
        self.assertIn('#include "build.h"', self.converter.GetC())


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Underscore_KeepOnVariable(self):
        self.converter.ProcessJSON('{"string:Project_Name": "Build Info"}')
        code = self.converter.GetC()
        lines = ['static char Project_Name[] = "Build Info";']
        AssertIsInSequence(lines, code, self)

    def test_Underscore_RemoveOnFunction(self):
        self.converter.ProcessJSON('{"string:Project_Name": "Build Info"}')
        self.assertIn(
            "const char *PtrProjectName(void) {", self.converter.GetC()
        )
        self.assertIn(
            "const char *PtrProjectName(void);", self.converter.GetH()
        )


class TestSignedIntegerProcessJSON(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_SInt_InvalidValue_CausesValueError(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for typ in bi.BuildInfo.INT_TYPES:
            for json_value in json_value_list:
                json_data = f'{{"{typ}:NAME": {json_value}}}'
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_SInt8Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int8:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static int8_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt8Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int8:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static int8_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt8Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"int8:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "int8_t GetNAME(void) {",
            "int8_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_SInt8Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"int8:NAME": 0}')
        self.assertIn("int8_t GetNAME(void);", self.converter.GetH())

    def test_SInt8Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"int8:NAME": -{str(0x80)}}}')
        self.converter.ProcessJSON(f'{{"int8:NAME": {str(0x7F)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int8:NAME": -{str(0x81)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int8:NAME": {str(0x80)}}}')

    def test_SInt16Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int16:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static int16_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt16Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int16:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static int16_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt16Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"int16:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "int16_t GetNAME(void) {",
            "int16_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_SInt16Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"int16:NAME": 0}')
        self.assertIn("int16_t GetNAME(void);", self.converter.GetH())

    def test_SInt16Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"int16:NAME": -{str(0x8000)}}}')
        self.converter.ProcessJSON(f'{{"int16:NAME": {str(0x7FFF)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int16:NAME": -{str(0x8001)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int16:NAME": {str(0x8000)}}}')

    def test_SInt16Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int16:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static int16_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt32Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int32:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static int32_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt32Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"int32:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "int32_t GetNAME(void) {",
            "int32_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_SInt32Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"int32:NAME": 0}')
        self.assertIn("int32_t GetNAME(void);", self.converter.GetH())

    def test_SInt32Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"int32:NAME": -{str(0x80000000)}}}')
        self.converter.ProcessJSON(f'{{"int32:NAME": {str(0x7FFFFFFF)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int32:NAME": -{str(0x80000001)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"int32:NAME": {str(0x80000000)}}}')

    def test_SInt64Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int64:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static int64_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt64Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"int64:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static int64_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_SInt64Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"int64:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "int64_t GetNAME(void) {",
            "int64_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_SInt64Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"int64:NAME": 0}')
        self.assertIn("int64_t GetNAME(void);", self.converter.GetH())

    def test_SInt64Bit_TestLimits(self):
        self.converter.ProcessJSON(
            f'{{"int64:NAME": -{str(0x8000000000000000)}}}'
        )
        self.converter.ProcessJSON(
            f'{{"int64:NAME": {str(0x7FFFFFFFFFFFFFFF)}}}'
        )
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(
                f'{{"int64:NAME": -{str(0x8000000000000001)}}}'
            )
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(
                f'{{"int64:NAME": {str(0x8000000000000000)}}}'
            )

    def test_IntegerWritable_IsNotConst(self):
        self.converter.ProcessJSON('{"int8:w:NAME": 0}')
        lines = ["static int8_t NAME = 0"]
        AssertIsInSequence(lines, self.converter.GetC(), self)

    def test_IntegerWritable_HasSetFunction(self):
        self.converter.ProcessJSON('{"int8:w:NAME": 0}')
        lines = ["void SetNAME(int8_t val);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)
        lines = ["void SetNAME(int8_t val) {", "NAME = val;", "}"]
        AssertIsInSequence(lines, self.converter.GetC(), self)


class TestUnsignedIntegerProcessJSON(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_UInt_InvalidValue_CausesValueError(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for typ in bi.BuildInfo.INT_TYPES:
            for json_value in json_value_list:
                json_data = f'{{"{typ}:NAME": {json_value}}}'
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_UInt8Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint8:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static uint8_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt8Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint8:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static uint8_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt8Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"uint8:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "uint8_t GetNAME(void) {",
            "uint8_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_UInt8Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"uint8:NAME": 0}')
        self.assertIn("uint8_t GetNAME(void);", self.converter.GetH())

    def test_UInt8Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"uint8:NAME": {str(0)}}}')
        self.converter.ProcessJSON(f'{{"uint8:NAME": {str(255)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint8:NAME": -{str(1)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint8:NAME": {str(0x100)}}}')

    def test_UInt16Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint16:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static uint16_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt16Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint16:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static uint16_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt16Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"uint16:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "uint16_t GetNAME(void) {",
            "uint16_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_UInt16Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"uint16:NAME": 0}')
        self.assertIn("uint16_t GetNAME(void);", self.converter.GetH())

    def test_UInt16Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"uint16:NAME": {str(0)}}}')
        self.converter.ProcessJSON(f'{{"uint16:NAME": {str(0xFFFF)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint16:NAME": -{str(1)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint16:NAME": {str(0x10000)}}}')

    def test_UInt16Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint16:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static uint16_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt32Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint32:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static uint32_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt32Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"uint32:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "uint32_t GetNAME(void) {",
            "uint32_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_UInt32Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"uint32:NAME": 0}')
        self.assertIn("uint32_t GetNAME(void);", self.converter.GetH())

    def test_UInt32Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"uint32:NAME": {str(0)}}}')
        self.converter.ProcessJSON(f'{{"uint32:NAME": {str(0xFFFFFFFF)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint32:NAME": -{str(1)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint32:NAME": {str(0x100000000)}}}')

    def test_UInt64Bit_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint64:NAME": 0}')
        code = self.converter.GetC()
        lines = ["static uint64_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt64Bit_OtherValue_VariableIsPresentInC(self):
        self.converter.ProcessJSON('{"uint64:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static uint64_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_UInt64Bit_FunctionIsPresentInC(self):
        self.converter.ProcessJSON('{"uint64:NAME": 0}')
        code = self.converter.GetC()
        lines = [
            "uint64_t GetNAME(void) {",
            "uint64_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_UInt64Bit_FunctionIsPresentInH(self):
        self.converter.ProcessJSON('{"uint64:NAME": 0}')
        self.assertIn("uint64_t GetNAME(void);", self.converter.GetH())

    def test_UInt64Bit_TestLimits(self):
        self.converter.ProcessJSON(f'{{"uint64:NAME": -{str(0)}}}')
        self.converter.ProcessJSON(
            f'{{"uint64:NAME": {str(0xFFFFFFFFFFFFFFFF)}}}'
        )
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"uint64:NAME": -{str(1)}}}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(
                f'{{"uint64:NAME": {str(0x10000000000000000)}}}'
            )


class TestArrayOfObjects(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_ArrayOfObjects_AddAllToCAndH(self):
        self.converter.ProcessJSON(
            """[
                {
                    "string:NAME1": "VALUE1"
                },
                {
                    "Section_Prefix": "BUILD",
                    "string:NAME2": "VALUE2"
                }
            ]"""
        )

        lines = [
            'static char NAME1[] = "VALUE1";',
            'static char BUILD_NAME2[] = "VALUE2";',
            "const char *PtrNAME1(void) {",
            "const char *BUILD_PtrNAME2(void) {",
        ]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

        lines = [
            "const char *PtrNAME1(void);",
            "const char *BUILD_PtrNAME2(void);",
        ]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)

    def test_ArrayOfObjects_DefaultModuleName(self):
        self.converter.ProcessJSON(
            """[
                {
                    "Section_Prefix": "BUILD",
                    "string:NAME1": "VALUE1"
                },
                {
                    "string:NAME2": "VALUE2"
                }
            ]"""
        )

        lines = [
            'static char BUILD_NAME1[] = "VALUE1";',
            'static char NAME2[] = "VALUE2";',
            "const char *BUILD_PtrNAME1(void) {",
            "const char *PtrNAME2(void) {",
        ]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

        lines = [
            "const char *BUILD_PtrNAME1(void);",
            "const char *PtrNAME2(void);",
        ]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)


class TestSetFilename(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_SetFilename_UsedOnInclude(self):
        self.converter.SetFilename("file_name")
        self.converter.ProcessJSON("{}")
        self.assertIn('#include "file_name.h"', self.converter.GetC())

    def test_SetFilename_UsedOnHeaderGuards(self):
        self.converter.SetFilename("file_name")
        self.converter.ProcessJSON("{}")
        code = self.converter.GetH()
        self.assertIn("#ifndef FILE_NAME_H_", code)
        self.assertIn("#define FILE_NAME_H_", code)
        self.assertIn("#endif /* FILE_NAME_H_ */", code)

    def test_SetFilename_OnJSON(self):
        self.converter.ProcessJSON('{"Module_Name": "other_file_name"}')
        code = self.converter.GetC()
        self.assertIn('#include "other_file_name.h"', self.converter.GetC())
        code = self.converter.GetH()
        self.assertIn("#ifndef OTHER_FILE_NAME_H_", code)
        self.assertIn("#define OTHER_FILE_NAME_H_", code)
        self.assertIn("#endif /* OTHER_FILE_NAME_H_ */", code)

    def test_SetFilename_OnJSON_MustBeString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            with self.assertRaises(ValueError):
                self.converter.ProcessJSON(f'{{"Module_Name": {json_value}}}')


class TestStringsWitMaximumSize(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_StringSize_AnySize(self):
        self.converter.ProcessJSON('{"string[]:NAME": "VALUE"}')
        code = self.converter.GetC()
        lines = ['static char NAME[] = "VALUE"']
        AssertIsInSequence(lines, code, self)

    def test_StringSize_AllUsed_AccountNullTerminator(self):
        self.converter.ProcessJSON('{"string[6]:NAME": "VALUE"}')
        code = self.converter.GetC()
        lines = ['static char NAME[6] = "VALUE"']
        AssertIsInSequence(lines, code, self)

    def test_StringSize_OutOfBounds_AccountNullTerminator(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"string[5]:NAME": "VALUE"}')

    def test_StringSize_NotAllUsed_AccountNullTerminator(self):
        self.converter.ProcessJSON('{"string[2]:NAME": ""}')
        code = self.converter.GetC()
        lines = ['static char NAME[2] = ""']
        AssertIsInSequence(lines, code, self)


class TestMacros(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Macro_SimpleMacro(self):
        self.converter.ProcessJSON('{"macro:NAME": "VALUE"}')
        code = self.converter.GetH()
        self.assertIn("#define NAME VALUE", code)

    def test_Macro_MustBeString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"macro:NAME": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_Macro_EmptyModuleName_NoPrefix(self):
        self.converter.ProcessJSON(
            """{
                "Section_Prefix": "",
                "macro:NAME": "VALUE"
            }"""
        )
        code = self.converter.GetH()
        self.assertIn("#define NAME VALUE", code)

    def test_Macro_FunctionMacro(self):
        self.converter.ProcessJSON('{"macro:NAME()": "VALUE"}')
        code = self.converter.GetH()
        self.assertIn("#define NAME() VALUE", code)

    def test_Macro_FunctionMacroWithOneParameter(self):
        self.converter.ProcessJSON('{"macro:ADD_ONE(x)": "((x) + 1)"}')
        code = self.converter.GetH()
        self.assertIn("#define ADD_ONE(x) ((x) + 1)", code)

    def test_Macro_FunctionMacroWithSeveralParameters(self):
        self.converter.ProcessJSON(
            '{"macro:SUM_3(x, y, z)": "((x) + (y) + (z))"}'
        )
        code = self.converter.GetH()
        self.assertIn("#define SUM_3(x, y, z) ((x) + (y) + (z))", code)

    def test_NonMacro_WithMacroFunction_CausesError(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"string:NAME()": "VAL"}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"uint8:NAME()": 1}')
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"bool:NAME()": true}')

    def test_Macro_WithArraySize_CausesError(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"macro[]:NAME(x)": "VAL"}')


class TestFloat(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Float_VariableInC(self):
        self.converter.ProcessJSON('{"float:NAME": 1.0}')
        code = self.converter.GetC()
        lines = ["static float NAME = 1.0;"]
        AssertIsInSequence(lines, code, self)

    def test_Float_FunctionInC(self):
        self.converter.ProcessJSON('{"float:NAME": 1.0}')
        code = self.converter.GetC()
        lines = [
            "float GetNAME(void) {",
            "float val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_Float_FunctionInH(self):
        self.converter.ProcessJSON('{"float:NAME": 1.0}')
        lines = ["float GetNAME(void);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)

    def test_FloatValue_CanBeInteger(self):
        self.converter.ProcessJSON('{"float:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static float NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_FloatValue_MustBeFloatOrInt(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"float:NAME": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_Float_AboveLimit_RaisesValueError(self):
        value_too_big = "1" + str(bi.FLOAT_MAX)
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"float:NAME": {value_too_big}}}')

    def test_Float_BelowLimit_RaisesValueError(self):
        value_too_small = str(bi.FLOAT_MIN)
        value_too_small = "-1" + value_too_small[1:]
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"float:NAME": {value_too_small}}}')


class TestDouble(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Double_VariableInC(self):
        self.converter.ProcessJSON('{"double:NAME": 1.0}')
        lines = ["static double NAME = 1.0;"]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_Double_FunctionInC(self):
        self.converter.ProcessJSON('{"double:NAME": 1.0}')
        code = self.converter.GetC()
        lines = [
            "double GetNAME(void) {",
            "double val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_Double_FunctionInH(self):
        self.converter.ProcessJSON('{"double:NAME": 1.0}')
        lines = ["double GetNAME(void);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)

    def test_DoubleValue_CanBeInteger(self):
        self.converter.ProcessJSON('{"double:NAME": 1}')
        code = self.converter.GetC()
        lines = ["static double NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_DoubleValue_MustBeDoubleOrInt(self):
        json_value_list = ['""', "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"double:NAME": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_Double_AboveLimit_RaisesValueError(self):
        value_too_big = "1" + str(bi.DOUBLE_MAX)
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"double:NAME": {value_too_big}}}')

    def test_Double_BelowLimit_RaisesValueError(self):
        value_too_small = str(bi.DOUBLE_MIN)
        value_too_small = "-1" + value_too_small[1:]
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON(f'{{"double:NAME": {value_too_small}}}')


class TestBool(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()
        self.converter.ProcessJSON('{"bool:NAME": true}')

    def test_Bool_ValueTrue_VariableInC(self):
        lines = ["static bool NAME = true;"]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_Bool_ValueFalse_VariableInC(self):
        self.converter.Reset()
        self.converter.ProcessJSON('{"bool:NAME": false}')
        lines = ["static bool NAME = false;"]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_Bool_FunctionInC(self):
        lines = [
            "bool GetNAME(void) {",
            "bool val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, self.converter.GetC(), self)

    def test_Bool_FunctionInH(self):
        lines = ["bool GetNAME(void);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)

    def test_BoolValue_MustBeBool(self):
        json_value_list = ['""', "0", "{}", "[]", "null"]
        for json_value in json_value_list:
            json_data = f'{{"bool:NAME": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)


class TestBoolAsInteger(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()
        self.converter.ProcessJSON(
            """{
                "Bool_Is_Integer": true,
                "bool:NAME": true
            }"""
        )

    def test_Bool_ValueTrue_VariableInC(self):
        code = self.converter.GetC()
        lines = ["static uint8_t NAME = 1;"]
        AssertIsInSequence(lines, code, self)

    def test_Bool_ValueFalse_VariableInC(self):
        self.converter.Reset()
        self.converter.ProcessJSON(
            """{
                "Bool_Is_Integer": true,
                "bool:NAME": false
            }"""
        )
        code = self.converter.GetC()
        lines = ["static uint8_t NAME = 0;"]
        AssertIsInSequence(lines, code, self)

    def test_Bool_AsIntegerAtTheEnd_StillHasEffect(self):
        self.converter.Reset()
        self.converter.ProcessJSON(
            """{
                "bool:NAME": true,
                "Bool_Is_Integer": true
            }"""
        )
        lines = ["static uint8_t NAME = 1;"]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_Bool_FunctionInC(self):
        lines = [
            "uint8_t GetNAME(void) {",
            "uint8_t val;",
            "val = NAME;",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, self.converter.GetC(), self)

    def test_Bool_FunctionInH(self):
        lines = ["uint8_t GetNAME(void);"]
        AssertIsInSequence(lines, self.converter.GetH(), self)

    def test_BoolValue_MustBeBool(self):
        json_value_list = ['""', "0", "{}", "[]", "null"]
        for json_value in json_value_list:
            json_data = f"""{{
                "Bool_Is_Integer": true,
                "bool:NAME": {json_value}
            }}"""
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_BoolIntegerValue_MustBeBool(self):
        json_value_list = ['""', "0", "{}", "[]", "null"]
        for json_value in json_value_list:
            json_data = f"""{{
                "Bool_Is_Integer": {json_value}
            }}"""
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)


class TestHashFiles(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()
        self.converter.ProcessJSON('{"int8:Var": 0}')

    def test_CommentWithHash_HashMustBeInC(self):
        hash = self.converter.CalcCHash()
        code = self.converter.GetC()
        self.assertIn(hash, code)

    def test_CommentWithHash_HashMustBeInH(self):
        hash = self.converter.CalcHHash()
        code = self.converter.GetH()
        self.assertIn(hash, code)


class TestIncludeHeaders(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_IncludeSource_AddsIncludeToC(self):
        self.converter.ProcessJSON('{"Include_Source": ["mymath.h", "test.h"]}')
        lines = [
            '#include "info.h"',
            '#include "mymath.h"',
            '#include "test.h"',
        ]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_IncludeSource_MustBeArray(self):
        json_value_list = ['""', "0", "{}", "ture", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Include_Source": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_IncludeSource_MustBeArrayOfStrings(self):
        json_value_list = ["0", "{}", "[]", "ture", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Include_Source": [{json_value}]}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_IncludeSource_AllowStandardLibraryIncludes(self):
        self.converter.ProcessJSON('{"Include_Source": ["<stddef.h>"]}')
        lines = ["#include <stddef.h>"]
        code = self.converter.GetC()
        AssertIsInSequence(lines, code, self)

    def test_IncludeHeader_AddsIncludeToC(self):
        self.converter.ProcessJSON('{"Include_Header": ["mymath.h", "test.h"]}')
        lines = [
            "#include <stdint.h>",
            '#include "mymath.h"',
            '#include "test.h"',
        ]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)

    def test_IncludeHeader_MustBeArray(self):
        json_value_list = ['""', "0", "{}", "ture", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Include_Header": {json_value}}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_IncludeHeader_MustBeArrayOfStrings(self):
        json_value_list = ["0", "{}", "[]", "ture", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Include_Header": [{json_value}]}}'
            with self.subTest(json_data=json_data):
                with self.assertRaises(ValueError):
                    self.converter.ProcessJSON(json_data)

    def test_IncludeHeader_AllowStandardLibraryIncludes(self):
        self.converter.ProcessJSON('{"Include_Header": ["<stddef.h>"]}')
        lines = ["#include <stddef.h>"]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)

    def test_IncludeHeader_InAnyObjectOfArray_SameEffect_OnFirst(self):
        self.converter.ProcessJSON('[{"Include_Header": ["<stddef.h>"]},{}]')
        lines = ["#include <stddef.h>"]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)

    def test_IncludeHeader_InAnyObjectOfArray_SameEffect_OnSecond(self):
        self.converter.ProcessJSON('[{},{"Include_Header": ["<stddef.h>"]}]')
        lines = ["#include <stddef.h>"]
        code = self.converter.GetH()
        AssertIsInSequence(lines, code, self)


class TestWritableVariablesCode(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_CriticalBlock_Numbers(self):
        self.converter.ProcessJSON('{"int8:w:Val": 0}')
        code = self.converter.GetC()
        lines = [
            "static int8_t Val = 0;",
            "int8_t GetVal(void) {",
            "int8_t val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
            "void SetVal(int8_t val) {",
            "CRITICAL_BLOCK(",
            "Val = val;",
            ");",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_Bool(self):
        self.converter.ProcessJSON('{"bool:w:Val": false}')
        code = self.converter.GetC()
        lines = [
            "static bool Val = false;",
            "bool GetVal(void) {",
            "bool val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
            "void SetVal(bool val) {",
            "CRITICAL_BLOCK(",
            "Val = val;",
            ");",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_BoolAsInteger(self):
        self.converter.ProcessJSON(
            '{"Bool_Is_Integer": true, "bool:w:Val": false}'
        )
        code = self.converter.GetC()
        lines = [
            "static uint8_t Val = 0;",
            "uint8_t GetVal(void) {",
            "uint8_t val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
            "void SetVal(uint8_t val) {",
            "CRITICAL_BLOCK(",
            "Val = val;",
            ");",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_String(self):
        self.converter.ProcessJSON('{"string:w:Val": "A"}')
        code = self.converter.GetC()
        lines = [
            'static char Val[] = "A";',
            "uint16_t LenVal(void) {",
            "return sizeof(Val);",
            "}",
            "const char *PtrVal(void) {",
            "return &Val[0];",
            "}",
            "bool GetVal(char *buff_ptr, uint16_t len) {",
            "bool success = true;",
            "uint16_t i;",
            "const char *ptr = &Val[0];",
            "char *buff_end_ptr = &buff_ptr[len - 1];",
            "CRITICAL_BLOCK(",
            "for (i = 0; i < sizeof(Val); i++) {",
            "if (i >= len) {",
            "success = false;",
            "break;",
            "}",
            "*buff_ptr++ = *ptr++;",
            "}",
            ");",
            "*buff_end_ptr = 0;",
            "return success;",
            "}",
            "bool SetVal(const char *buff_ptr, uint16_t len) {",
            "bool success = true;",
            "uint16_t i;",
            "char *ptr = &Val[0];",
            "CRITICAL_BLOCK(",
            "for (i = 0; i < len; i++) {",
            "if (i >= sizeof(Val)) {",
            "success = false;",
            "break;",
            "}",
            "*ptr++ = *buff_ptr++;",
            "}",
            ");",
            "Val[sizeof(Val) - 1] = 0;",
            "return success;",
        ]
        AssertIsInSequence(lines, code, self)


class TestReadableVariablesCode(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_CriticalBlock_Numbers(self):
        self.converter.ProcessJSON('{"int8:r:Val": 0}')
        code = self.converter.GetC()
        lines = [
            "static int8_t Val = 0;",
            "int8_t GetVal(void) {",
            "int8_t val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_Bool(self):
        self.converter.ProcessJSON('{"bool:r:Val": false}')
        code = self.converter.GetC()
        lines = [
            "static bool Val = false;",
            "bool GetVal(void) {",
            "bool val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_BoolAsInteger(self):
        self.converter.ProcessJSON(
            '{"Bool_Is_Integer": true, "bool:r:Val": false}'
        )
        code = self.converter.GetC()
        lines = [
            "static uint8_t Val = 0;",
            "uint8_t GetVal(void) {",
            "uint8_t val;",
            "CRITICAL_BLOCK(",
            "val = Val;",
            ");",
            "return val;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)

    def test_CriticalBlock_String(self):
        self.converter.ProcessJSON('{"string:r:Val": "A"}')
        code = self.converter.GetC()
        lines = [
            'static char Val[] = "A";',
            "uint16_t LenVal(void) {",
            "return sizeof(Val);",
            "}",
            "const char *PtrVal(void) {",
            "return &Val[0];",
            "}",
            "bool GetVal(char *buff_ptr, uint16_t len) {",
            "bool success = true;",
            "uint16_t i;",
            "const char *ptr = &Val[0];",
            "char *buff_end_ptr = &buff_ptr[len - 1];",
            "CRITICAL_BLOCK(",
            "for (i = 0; i < sizeof(Val); i++) {",
            "if (i >= len) {",
            "success = false;",
            "break;",
            "}",
            "*buff_ptr++ = *ptr++;",
            "}",
            ");",
            "*buff_end_ptr = 0;",
            "return success;",
            "}",
        ]
        AssertIsInSequence(lines, code, self)


class TestModuleAndFileName(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Module_DefaultsToNoModule_C(self):
        self.converter.ProcessJSON('{"int8:w:Val": 0}')
        code = self.converter.GetC()
        lines = [
            "static int8_t Val = 0;",
            "int8_t GetVal(void) {",
            "void SetVal(int8_t val) {",
        ]
        AssertIsInSequence(lines, code, self)

    def test_Module_WhenModuleNameSet_UseTheModuleName_C(self):
        self.converter.ProcessJSON(
            '{"Section_Prefix": "INFO", "int8:w:Val": 0}'
        )
        code = self.converter.GetC()
        lines = [
            "static int8_t INFO_Val = 0;",
            "int8_t INFO_GetVal(void) {",
            "void INFO_SetVal(int8_t val) {",
        ]
        AssertIsInSequence(lines, code, self)

    def test_Module_DefaultsToNoModule_H(self):
        self.converter.ProcessJSON('{"int8:w:Val": 0}')
        code = self.converter.GetH()
        lines = ["int8_t GetVal(void)", "void SetVal(int8_t val);"]
        AssertIsInSequence(lines, code, self)

    def test_Module_DefaultsToNoModule_H(self):
        self.converter.ProcessJSON(
            '{"Section_Prefix": "INFO", "int8:w:Val": 0}'
        )
        code = self.converter.GetH()
        lines = ["int8_t INFO_GetVal(void)", "void INFO_SetVal(int8_t val);"]
        AssertIsInSequence(lines, code, self)

    def test_FileName_DefaultsToInfo_C(self):
        self.converter.ProcessJSON("{}")
        code = self.converter.GetC()
        lines = ['#include "info.h"']
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenModuleNameSet_UseTheModuleName_C(self):
        self.converter.ProcessJSON('{"Section_Prefix":"BUILD"}')
        code = self.converter.GetC()
        lines = ['#include "build.h"']
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenFileNameSet_UseTheFileName_C(self):
        self.converter.ProcessJSON('{"Module_Name": "build_info"}')
        code = self.converter.GetC()
        lines = ['#include "build_info.h"']
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenFileNameAndModuleNameSet_UseTheFileName_C(self):
        self.converter.ProcessJSON(
            '{"Module_Name": "build_info", "Section_Prefix":"BUILD"}'
        )
        code = self.converter.GetC()
        lines = ['#include "build_info.h"']
        AssertIsInSequence(lines, code, self)

    def test_FileName_DefaultsToInfo_H(self):
        self.converter.ProcessJSON("{}")
        code = self.converter.GetH()
        lines = ["#ifndef INFO_H_", "#define INFO_H_", "#endif /* INFO_H_ */"]
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenModuleNameSet_UseTheModuleName_H(self):
        self.converter.ProcessJSON('{"Section_Prefix":"BUILD"}')
        code = self.converter.GetH()
        lines = [
            "#ifndef BUILD_H_",
            "#define BUILD_H_",
            "#endif /* BUILD_H_ */",
        ]
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenFileNameSet_UseTheFileName_H(self):
        self.converter.ProcessJSON('{"Module_Name": "build_info"}')
        code = self.converter.GetH()
        lines = [
            "#ifndef BUILD_INFO_H_",
            "#define BUILD_INFO_H_",
            "#endif /* BUILD_INFO_H_ */",
        ]
        AssertIsInSequence(lines, code, self)

    def test_FileName_WhenFileNameAndModuleNameSet_UseTheFileName_H(self):
        self.converter.ProcessJSON(
            '{"Module_Name": "build_info", "Section_Prefix":"BUILD"}'
        )
        code = self.converter.GetH()
        lines = [
            "#ifndef BUILD_INFO_H_",
            "#define BUILD_INFO_H_",
            "#endif /* BUILD_INFO_H_ */",
        ]
        AssertIsInSequence(lines, code, self)


class TestQualifiers(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_Qualifier_Default(self):
        self.converter.ProcessJSON('{"int8:Val": 0}')

    def test_Qualifier_Read(self):
        self.converter.ProcessJSON('{"int8:r:Val": 0}')

    def test_Qualifier_Write(self):
        self.converter.ProcessJSON('{"int8:w:Val": 0}')

    def test_Qualifier_BadQualifier(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"int8:X:Val": 0}')


class TestBadKey(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def test_BadKey_RaisesValueError(self):
        with self.assertRaises(ValueError):
            self.converter.ProcessJSON('{"": 0}')


if __name__ == "__main__":
    unittest.main()
