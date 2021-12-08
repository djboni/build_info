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


class TestCreateCFile(unittest.TestCase):
    def setUp(self):
        self.converter = bi.BuildInfo()

    def ProcessAndCheckResults(self):
        self.converter.ProcessJSON(self.json_data)
        header_code = self.converter.GetH()
        source_code = self.converter.GetC()
        AssertIsInSequence(self.expected_header_lines, header_code, self)
        AssertIsInSequence(self.expected_source_lines, source_code, self)

    def test_JSONStringInput_CreateCAndHFiles(self):
        self.json_data = """{
    "string:Project_Name" : "Build Info",
    "Section_Prefix": "BUILD_INFO"
}"""

        self.expected_source_lines = [
            '#include "build_info.h"',
            'static char BUILD_INFO_Project_Name[] = "Build Info";',
            "const char *BUILD_INFO_PtrProjectName(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef BUILD_INFO_H_",
            "#define BUILD_INFO_H_",
            "#include <stdint.h>",
            "const char *BUILD_INFO_PtrProjectName(void);",
            "#endif /* BUILD_INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_JSONSignedIntegerInput_CreateCAndHFiles(self):
        self.json_data = """{
    "string:Project_Name": "Build Info",
    "string:Version": "v0.1",
    "int8:Version_Major": 0,
    "int8:Version_Minor": 1,
    "int8:Version_Fix": 0,
    "int32:Version_Number": 256,
    "int16:Var16": 0,
    "int64:Var64": 0,
    "Section_Prefix": "BUILD"
}"""

        self.expected_source_lines = [
            '#include "build.h"',
            'static char BUILD_Project_Name[] = "Build Info";',
            'static char BUILD_Version[] = "v0.1";',
            "static int8_t BUILD_Version_Major = 0;",
            "static int8_t BUILD_Version_Minor = 1;",
            "static int8_t BUILD_Version_Fix = 0;",
            "static int32_t BUILD_Version_Number = 256;",
            "static int16_t BUILD_Var16 = 0;",
            "static int64_t BUILD_Var64 = 0;",
            "const char *BUILD_PtrProjectName(void) {",
            "}",
            "const char *BUILD_PtrVersion(void) {",
            "}",
            "int8_t BUILD_GetVersionMajor(void) {",
            "}",
            "int8_t BUILD_GetVersionMinor(void) {",
            "}",
            "int8_t BUILD_GetVersionFix(void) {",
            "}",
            "int32_t BUILD_GetVersionNumber(void) {",
            "}",
            "int16_t BUILD_GetVar16(void) {",
            "}",
            "int64_t BUILD_GetVar64(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef BUILD_H_",
            "#define BUILD_H_",
            "#include <stdint.h>",
            "const char *BUILD_PtrProjectName(void);",
            "const char *BUILD_PtrVersion(void);",
            "int8_t BUILD_GetVersionMajor(void);",
            "int8_t BUILD_GetVersionMinor(void);",
            "int8_t BUILD_GetVersionFix(void);",
            "int32_t BUILD_GetVersionNumber(void);",
            "int16_t BUILD_GetVar16(void);",
            "int64_t BUILD_GetVar64(void);",
            "#endif /* BUILD_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_JSONUnsignedIntegerInput_CreateCAndHFiles(self):
        self.json_data = """{
    "string:Project_Name": "Build Info",
    "string:Version": "v0.1",
    "uint8:Version_Major": 0,
    "uint8:Version_Minor": 1,
    "uint8:Version_Fix": 0,
    "uint32:Version_Number": 256,
    "uint16:Var16": 0,
    "uint64:Var64": 0,
    "Section_Prefix": "BUILD"
}"""

        self.expected_source_lines = [
            '#include "build.h"',
            'static char BUILD_Project_Name[] = "Build Info";',
            'static char BUILD_Version[] = "v0.1";',
            "static uint8_t BUILD_Version_Major = 0;",
            "static uint8_t BUILD_Version_Minor = 1;",
            "static uint8_t BUILD_Version_Fix = 0;",
            "static uint32_t BUILD_Version_Number = 256;",
            "static uint16_t BUILD_Var16 = 0;",
            "static uint64_t BUILD_Var64 = 0;",
            "const char *BUILD_PtrProjectName(void) {",
            "}",
            "const char *BUILD_PtrVersion(void) {",
            "}",
            "uint8_t BUILD_GetVersionMajor(void) {",
            "}",
            "uint8_t BUILD_GetVersionMinor(void) {",
            "}",
            "uint8_t BUILD_GetVersionFix(void) {",
            "}",
            "uint32_t BUILD_GetVersionNumber(void) {",
            "}",
            "uint16_t BUILD_GetVar16(void) {",
            "}",
            "uint64_t BUILD_GetVar64(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef BUILD_H_",
            "#define BUILD_H_",
            "#include <stdint.h>",
            "const char *BUILD_PtrProjectName(void);",
            "const char *BUILD_PtrVersion(void);",
            "uint8_t BUILD_GetVersionMajor(void);",
            "uint8_t BUILD_GetVersionMinor(void);",
            "uint8_t BUILD_GetVersionFix(void);",
            "uint32_t BUILD_GetVersionNumber(void);",
            "uint16_t BUILD_GetVar16(void);",
            "uint64_t BUILD_GetVar64(void);",
            "#endif /* BUILD_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_ArrayOfObjects_AppendSeveralModules(self):
        self.json_data = """[
            {
                "string:Project_Name": "Build Info"
            },
            {
                "Section_Prefix": "BUILD",
                "uint32:Timestamp": 1638628121
            }
        ]"""

        self.expected_source_lines = [
            '#include "build.h"',
            'static char Project_Name[] = "Build Info";',
            "static uint32_t BUILD_Timestamp = 1638628121;",
            "const char *PtrProjectName(void) {",
            "}",
            "uint32_t BUILD_GetTimestamp(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef BUILD_H_",
            "#define BUILD_H_",
            "#include <stdint.h>",
            "const char *PtrProjectName(void);",
            "uint32_t BUILD_GetTimestamp(void);",
            "#endif /* BUILD_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_PassFileName_UsedOnIncludeAndGuards(self):
        self.converter.SetFilename("project_info")

        self.json_data = "{}"

        self.expected_source_lines = ['#include "project_info.h"']

        self.expected_header_lines = [
            "#ifndef PROJECT_INFO_H_",
            "#define PROJECT_INFO_H_",
            "#endif /* PROJECT_INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_PassFileName_AsConfiguration(self):
        self.json_data = """[
            {
                "Module_Name": "project_info",
                "Section_Prefix": "BUILD",
                "string:Project_Name": "Build Info"
            }
        ]"""

        self.expected_source_lines = [
            '#include "project_info.h"',
            'static char BUILD_Project_Name[] = "Build Info";',
            "const char *BUILD_PtrProjectName(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef PROJECT_INFO_H_",
            "#define PROJECT_INFO_H_",
            "#include <stdint.h>",
            "const char *BUILD_PtrProjectName(void);",
            "#endif /* PROJECT_INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_Strings_WithMaximumSize(self):
        self.json_data = """[
            {
                "Module_Name": "project_info",
                "Section_Prefix": "BUILD",
                "string[]:Project_Name": "Build Info",
                "string[41]:Commit_Hash": "0000000000000000000000000000000000000000"
            }
        ]"""

        self.expected_source_lines = [
            '#include "project_info.h"',
            'static char BUILD_Project_Name[] = "Build Info";',
            'static char BUILD_Commit_Hash[41] = "0000000000000000000000000000000000000000";',
            "const char *BUILD_PtrProjectName(void) {",
            "}",
            "const char *BUILD_PtrCommitHash(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef PROJECT_INFO_H_",
            "#define PROJECT_INFO_H_",
            "#include <stdint.h>",
            "const char *BUILD_PtrProjectName(void);",
            "const char *BUILD_PtrCommitHash(void);",
            "#endif /* PROJECT_INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_Macros(self):
        self.json_data = """[
            {
                "Module_Name": "project_info",
                "Section_Prefix": "BUILD",
                "string[]:Project_Name": "Build Info",
                "string[41]:Commit_Hash": "0000000000000000000000000000000000000000",
                "macro:VERSION_STR": "\\"v0.1\\""
            },
            {
                "Section_Prefix": "",
                "macro:INVALID_PTR": "NULL",
                "macro:MAX(x, y)": "((x) >= (y) ? (x) : (y))"
            }
        ]"""

        self.expected_source_lines = [
            '#include "project_info.h"',
            'static char BUILD_Project_Name[] = "Build Info";',
            'static char BUILD_Commit_Hash[41] = "0000000000000000000000000000000000000000";',
            "const char *BUILD_PtrProjectName(void) {",
            "}",
            "const char *BUILD_PtrCommitHash(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef PROJECT_INFO_H_",
            "#define PROJECT_INFO_H_",
            "#include <stdint.h>",
            '#define BUILD_VERSION_STR "v0.1"',
            "#define INVALID_PTR NULL",
            "#define MAX(x, y) ((x) >= (y) ? (x) : (y))",
            "const char *BUILD_PtrProjectName(void);",
            "const char *BUILD_PtrCommitHash(void);",
            "#endif /* PROJECT_INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_Float(self):
        self.json_data = """{
            "Module_Name": "Control_Parameters",
            "Section_Prefix": "CONTROL",
            "float:P": 1.0,
            "float:I": 0.05,
            "float:D": 0.2
        }"""

        self.expected_source_lines = [
            '#include "control_parameters.h"',
            "static float CONTROL_P = 1.0;",
            "static float CONTROL_I = 0.05;",
            "static float CONTROL_D = 0.2;",
            "float CONTROL_GetP(void) {",
            "}",
            "float CONTROL_GetI(void) {",
            "}",
            "float CONTROL_GetD(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef CONTROL_PARAMETERS_H_",
            "#define CONTROL_PARAMETERS_H_",
            "#include <stdint.h>",
            "float CONTROL_GetP(void);",
            "float CONTROL_GetI(void);",
            "float CONTROL_GetD(void);",
            "#endif /* CONTROL_PARAMETERS_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_Double(self):
        self.json_data = """{
            "Module_Name": "Control_Parameters",
            "Section_Prefix": "CONTROL",
            "double:P": 1.0,
            "double:I": 0.05,
            "double:D": 0.2
        }"""

        self.expected_source_lines = [
            '#include "control_parameters.h"',
            "static double CONTROL_P = 1.0;",
            "static double CONTROL_I = 0.05;",
            "static double CONTROL_D = 0.2;",
            "double CONTROL_GetP(void) {",
            "}",
            "double CONTROL_GetI(void) {",
            "}",
            "double CONTROL_GetD(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef CONTROL_PARAMETERS_H_",
            "#define CONTROL_PARAMETERS_H_",
            "#include <stdint.h>",
            "double CONTROL_GetP(void);",
            "double CONTROL_GetI(void);",
            "double CONTROL_GetD(void);",
            "#endif /* CONTROL_PARAMETERS_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_Bool(self):
        self.json_data = """{
            "Section_Prefix": "Debug",
            "bool:Display_Enabled": true,
            "bool:Keypad_Enabled": false
        }"""

        self.expected_source_lines = [
            '#include "debug.h"',
            "static bool DEBUG_Display_Enabled = true;",
            "static bool DEBUG_Keypad_Enabled = false;",
            "bool DEBUG_GetDisplayEnabled(void) {",
            "}",
            "bool DEBUG_GetKeypadEnabled(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef DEBUG_H_",
            "#define DEBUG_H_",
            "#include <stdint.h>",
            "bool DEBUG_GetDisplayEnabled(void);",
            "bool DEBUG_GetKeypadEnabled(void);",
            "#endif /* DEBUG_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_BoolAsInteger(self):
        self.json_data = """{
            "Section_Prefix": "Debug",
            "Bool_Is_Integer": true,
            "bool:Display_Enabled": true,
            "bool:Keypad_Enabled": false
        }"""

        self.expected_source_lines = [
            '#include "debug.h"',
            "static uint8_t DEBUG_Display_Enabled = 1;",
            "static uint8_t DEBUG_Keypad_Enabled = 0;",
            "uint8_t DEBUG_GetDisplayEnabled(void) {",
            "}",
            "uint8_t DEBUG_GetKeypadEnabled(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef DEBUG_H_",
            "#define DEBUG_H_",
            "#include <stdint.h>",
            "uint8_t DEBUG_GetDisplayEnabled(void);",
            "uint8_t DEBUG_GetKeypadEnabled(void);",
            "#endif /* DEBUG_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_ReadOnlyData(self):
        self.json_data = """{
            "Section_Prefix": "TEST",
            "string:r:String": "TEST1",
            "int8:r:Int8_t": -1,
            "int16:r:Int16_t": -2,
            "int32:r:Int32_t": -4,
            "int64:r:Int64_t": -8,
            "uint8:r:Uint8_t": 1,
            "uint16:r:Uint16_t": 2,
            "uint32:r:Uint32_t": 4,
            "uint64:r:Uint64_t": 8,
            "float:r:Float": 1e6,
            "double:r:Double": 1e12,
            "bool:r:Bool": true
        }"""

        self.expected_source_lines = [
            '#include "test.h"',
            'static char TEST_String[] = "TEST1";',
            "static int8_t TEST_Int8_t = -1;",
            "static int16_t TEST_Int16_t = -2;",
            "static int32_t TEST_Int32_t = -4;",
            "static int64_t TEST_Int64_t = -8;",
            "static uint8_t TEST_Uint8_t = 1;",
            "static uint16_t TEST_Uint16_t = 2;",
            "static uint32_t TEST_Uint32_t = 4;",
            "static uint64_t TEST_Uint64_t = 8;",
            "static float TEST_Float = 1000000.0;",
            "static double TEST_Double = 1000000000000.0;",
            "static bool TEST_Bool = true;",
            "uint16_t TEST_LenString(void) {",
            "}",
            "const char *TEST_PtrString(void) {",
            "}",
            "int8_t TEST_GetInt8t(void) {",
            "}",
            "int16_t TEST_GetInt16t(void) {",
            "}",
            "int32_t TEST_GetInt32t(void) {",
            "}",
            "int64_t TEST_GetInt64t(void) {",
            "}",
            "uint8_t TEST_GetUint8t(void) {",
            "}",
            "uint16_t TEST_GetUint16t(void) {",
            "}",
            "uint32_t TEST_GetUint32t(void) {",
            "}",
            "uint64_t TEST_GetUint64t(void) {",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef TEST_H_",
            "#define TEST_H_",
            "#include <stdint.h>",
            "uint16_t TEST_LenString(void);",
            "const char *TEST_PtrString(void);",
            "int8_t TEST_GetInt8t(void);",
            "int16_t TEST_GetInt16t(void);",
            "int32_t TEST_GetInt32t(void);",
            "int64_t TEST_GetInt64t(void);",
            "uint8_t TEST_GetUint8t(void);",
            "uint16_t TEST_GetUint16t(void);",
            "uint32_t TEST_GetUint32t(void);",
            "uint64_t TEST_GetUint64t(void);",
            "float TEST_GetFloat(void);",
            "double TEST_GetDouble(void);",
            "bool TEST_GetBool(void);",
            "#endif /* TEST_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_WritableData(self):
        self.json_data = """{
            "Section_Prefix": "TEST",
            "string:w:String": "TEST1",
            "int8:w:Int8_t": -1,
            "int16:w:Int16_t": -2,
            "int32:w:Int32_t": -4,
            "int64:w:Int64_t": -8,
            "uint8:w:Uint8_t": 1,
            "uint16:w:Uint16_t": 2,
            "uint32:w:Uint32_t": 4,
            "uint64:w:Uint64_t": 8,
            "float:w:Float": 1e6,
            "double:w:Double": 1e12,
            "bool:w:Bool": true
        }"""

        self.expected_source_lines = [
            '#include "test.h"',
            'static char TEST_String[] = "TEST1";',
            "static int8_t TEST_Int8_t = -1;",
            "static int16_t TEST_Int16_t = -2;",
            "static int32_t TEST_Int32_t = -4;",
            "static int64_t TEST_Int64_t = -8;",
            "static uint8_t TEST_Uint8_t = 1;",
            "static uint16_t TEST_Uint16_t = 2;",
            "static uint32_t TEST_Uint32_t = 4;",
            "static uint64_t TEST_Uint64_t = 8;",
            "static float TEST_Float = 1000000.0;",
            "static double TEST_Double = 1000000000000.0;",
            "static bool TEST_Bool = true;",
            "uint16_t TEST_LenString(void) {",
            "}",
            "char *TEST_PtrString(void) {",
            "}",
            "bool TEST_SetString(const char *buff_ptr, uint16_t len) {",
            "}",
            "int8_t TEST_GetInt8t(void) {",
            "}",
            "void TEST_SetInt8t(int8_t val) {",
            "}",
            "int16_t TEST_GetInt16t(void) {",
            "}",
            "void TEST_SetInt16t(int16_t val) {",
            "}",
            "int32_t TEST_GetInt32t(void) {",
            "}",
            "void TEST_SetInt32t(int32_t val) {",
            "}",
            "int64_t TEST_GetInt64t(void) {",
            "}",
            "void TEST_SetInt64t(int64_t val) {",
            "}",
            "uint8_t TEST_GetUint8t(void) {",
            "}",
            "void TEST_SetUint8t(uint8_t val) {",
            "}",
            "uint16_t TEST_GetUint16t(void) {",
            "}",
            "void TEST_SetUint16t(uint16_t val) {",
            "}",
            "uint32_t TEST_GetUint32t(void) {",
            "}",
            "void TEST_SetUint32t(uint32_t val) {",
            "}",
            "uint64_t TEST_GetUint64t(void) {",
            "}",
            "void TEST_SetUint64t(uint64_t val) {",
            "}",
            "float TEST_GetFloat(void) {",
            "}",
            "void TEST_SetFloat(float val) {",
            "}",
            "double TEST_GetDouble(void) {",
            "}",
            "void TEST_SetDouble(double val) {",
            "}",
            "bool TEST_GetBool(void) {",
            "}",
            "void TEST_SetBool(bool val) {",
            "TEST_Bool = val;",
            "}",
        ]

        self.expected_header_lines = [
            "#ifndef TEST_H_",
            "#define TEST_H_",
            "#include <stdint.h>",
            "uint16_t TEST_LenString(void);",
            "const char *TEST_PtrString(void);",
            "bool TEST_SetString(const char *buff_ptr, uint16_t len);",
            "int8_t TEST_GetInt8t(void);",
            "void TEST_SetInt8t(int8_t val);",
            "int16_t TEST_GetInt16t(void);",
            "void TEST_SetInt16t(int16_t val);",
            "int32_t TEST_GetInt32t(void);",
            "void TEST_SetInt32t(int32_t val);",
            "int64_t TEST_GetInt64t(void);",
            "void TEST_SetInt64t(int64_t val);",
            "uint8_t TEST_GetUint8t(void);",
            "void TEST_SetUint8t(uint8_t val);",
            "uint16_t TEST_GetUint16t(void);",
            "void TEST_SetUint16t(uint16_t val);",
            "uint32_t TEST_GetUint32t(void);",
            "void TEST_SetUint32t(uint32_t val);",
            "uint64_t TEST_GetUint64t(void);",
            "void TEST_SetUint64t(uint64_t val);",
            "float TEST_GetFloat(void);",
            "void TEST_SetFloat(float val);",
            "double TEST_GetDouble(void);",
            "void TEST_SetDouble(double val);",
            "bool TEST_GetBool(void);",
            "void TEST_SetBool(bool val);",
            "#endif /* TEST_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_IncludeHeaders(self):
        self.json_data = """{
    "Module_Name": "info",
    "Section_Prefix": "INFO",
    "Include_Source": ["<stddef.h>", "<stdlib.h>", "mydefs.h"],
    "Include_Header": ["projdefs.h", "<math.h>", "mymath.h"]
}"""

        self.expected_source_lines = [
            '#include "info.h"',
            "#include <stddef.h>",
            "#include <stdlib.h>",
            '#include "mydefs.h"',
        ]

        self.expected_header_lines = [
            "#ifndef INFO_H_",
            "#define INFO_H_",
            "#include <stdint.h>",
            '#include "projdefs.h"',
            "#include <math.h>",
            '#include "mymath.h"',
            "#endif /* INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_OneShouldBeAbleTo_AlignKeysWithWhitespace(self):
        self.json_data = """{
    " uint8            : Var_U8       ": 0,
    " uint16       :   : Var_U16      ": 0,
    " uint32       : r : Var_U32      ": 0,
    " uint64       : w : Var_U64      ": 0,
    " string       :   : Str_A        ": "",
    " string [ 4 ]     : Str_B        ": "",
    " macro            : FIRST(a, b)  ": "(a)"
}"""

        self.expected_source_lines = [
            '#include "info.h"',
            "static uint8_t Var_U8 = 0;",
            "static uint16_t Var_U16 = 0;",
            "static uint32_t Var_U32 = 0;",
            "static uint64_t Var_U64 = 0;",
            'static char Str_A[] = "";',
            'static char Str_B[4] = "";',
        ]

        self.expected_header_lines = [
            "#ifndef INFO_H_",
            "#define INFO_H_",
            "#define FIRST(a, b) (a)",
            "#endif /* INFO_H_ */",
        ]

        self.ProcessAndCheckResults()

    def test_CreateByteArrayWitHexString(self):
        self.skipTest("not implemented")
        self.json_data = """{
            "hex8[]:Array1": "00112233",
            "hex8[4]:Array2": "00112233",
            "hex8[]:Array3": "00 11 22 33"
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_CreateArraysOfNumbers(self):
        self.skipTest("not implemented")
        self.json_data = """{
            "uint8[]:Array1": [0, 1],
            "uint8[2]:Array2": [0, 1],
            "bool[]:Array3": [false, true],
            "string[][]:Array4": ["A", "B"]
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_CreateConstantVariablesWithConstantQualifier(self):
        self.skipTest("not implemented")
        self.json_data = """{
            "uint8:c:Constant1": 0,
            "uint8:c:Constant2": 0,
            "bool:c:Constant3": false,
            "string:c:Constant4": "A"
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_MakeInternalStaticWriterFunctionForReadableVariables(self):
        self.skipTest("not implemented")
        self.json_data = """{
            "uint8:Readable1": 0,
            "uint8:r:Readable2": 0
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_GitRepository_ConfigurableCommitStringName(self):
        self.skipTest("not implemented")
        self.json_data = """{
            "Git_Repository": "/path/to/repo",
            "Git_Repository": {
                "Commit_Str_Name": "Git_Commit_Str",
                "Directory": "/path/to/repo"
            }
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_JSON_Comments(self):
        self.skipTest("not implemented")
        self.json_data = """{
            // This is a one line comment.
            "uint8:Val": 0
            /* This is a comment that can
             * span several lines. */
        }"""
        self.expected_source_lines = []
        self.expected_header_lines = []
        self.ProcessAndCheckResults()

    def test_SimplerAndBetterJSONErrors(self):
        self.skipTest("not implemented")
        self.ProcessAndCheckResults()


if __name__ == "__main__":
    unittest.main()
