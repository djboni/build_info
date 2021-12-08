#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

import unittest
from unittest.mock import Mock
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


class TestMainBadParameters(unittest.TestCase):
    def setUp(self):
        self.open = OpenMock()
        self.print = Mock()

        self.input_filename = "input.json"
        self.output_basename = "output"
        self.output_h_filename = "output.h"
        self.output_c_filename = "output.c"
        self.parameters = [self.input_filename, self.output_basename]

    def CallMain(self):
        argv = ["biuld_info.py", *self.parameters]
        self.return_value = bi.main(argv, open=self.open, print=self.print)

    def test_Main_NoParameter_ReturnError_AKA_1(self):
        self.parameters = []
        self.CallMain()
        self.assertEqual(1, self.return_value)

    def test_Main_NoParameter_ShowsUsage(self):
        self.parameters = []
        self.CallMain()
        self.print.assert_called_once()
        self.assertIn("Usage:", str(self.print.call_args))

    def test_Main_OneParameter_ReturnError_AKA_1(self):
        self.parameters = ["input.json"]
        self.CallMain()
        self.assertEqual(1, self.return_value)

    def test_Main_OneParameter_ShowsUsage(self):
        self.parameters = ["input.json"]
        self.CallMain()
        self.print.assert_called_once()
        self.assertIn("Usage:", str(self.print.call_args))

    def test_Main_ThreeParameter_ReturnError_AKA_1(self):
        self.parameters = ["input.json", "output", "too_many_parameters"]
        self.CallMain()
        self.assertEqual(1, self.return_value)

    def test_Main_ThreeParameter_ShowsUsage(self):
        self.parameters = ["input.json", "output", "too_many_parameters"]
        self.CallMain()
        self.print.assert_called_once()
        self.assertIn("Usage:", str(self.print.call_args))


class TestMainGoodParameters(TestMainBadParameters):
    def setUp(self):
        super().setUp()

        self.input_data = '{"int8:Var": 0}'

        self.output_h_data = [
            "#ifndef OUTPUT_H_",
            "#define OUTPUT_H_",
            "#include <stdint.h>",
            "int8_t GetVar(void);",
            "#endif /* OUTPUT_H_ */",
        ]

        self.output_c_data = [
            '#include "output.h"',
            "static int8_t Var = 0;",
            "int8_t GetVar(void) {",
            "}",
        ]

    def CallMainWithGoodParameters(self, reset=True):
        if reset:
            self.open.Reset()
        self.open.SetFileData(self.input_filename, self.input_data)
        self.CallMain()

    def test_Main_TwoParameter_ReturnSuccess_AKA_0(self):
        self.CallMainWithGoodParameters()
        self.assertEqual(0, self.return_value)

    def test_Main_TwoParameter_NoPrint(self):
        self.CallMainWithGoodParameters()
        self.print.assert_not_called()

    def test_Main_ReadsInputFile(self):
        self.CallMainWithGoodParameters()
        self.assertTrue(self.open.FileWasRead(self.input_filename))

    def test_Main_WritesCOutputFile(self):
        self.CallMainWithGoodParameters()
        self.assertTrue(self.open.FileWasWritten(self.output_c_filename))

    def test_Main_WritesHOutputFile(self):
        self.CallMainWithGoodParameters()
        self.assertTrue(self.open.FileWasWritten(self.output_h_filename))

    def test_Main_ContentOfHOutputFile(self):
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_h_filename)
        AssertIsInSequence(self.output_h_data, code_written, self)

    def test_Main_ContentOfCOutputFile(self):
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_c_filename)
        AssertIsInSequence(self.output_c_data, code_written, self)

    def test_Main_GiveOutputWithDotH_WriteHFile(self):
        self.parameters = [self.input_filename, self.output_basename + ".h"]
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_h_filename)
        AssertIsInSequence(self.output_h_data, code_written, self)

    def test_Main_GiveOutputWithDotH_WriteCFile(self):
        self.parameters = [self.input_filename, self.output_basename + ".h"]
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_c_filename)
        AssertIsInSequence(self.output_c_data, code_written, self)

    def test_Main_GiveOutputWithDotC_WriteHFile(self):
        self.parameters = [self.input_filename, self.output_basename + ".h"]
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_h_filename)
        AssertIsInSequence(self.output_h_data, code_written, self)

    def test_Main_GiveOutputWithDotC_WriteCFile(self):
        self.parameters = [self.input_filename, self.output_basename + ".h"]
        self.CallMainWithGoodParameters()
        code_written = self.open.GetFileData(self.output_c_filename)
        AssertIsInSequence(self.output_c_data, code_written, self)


class TestMainUpdateIfNecessary(TestMainGoodParameters):
    def setUp(self):
        super().setUp()

        self.other_input_data = '{"int8:OtherVar": 0}'

        self.other_output_h_data = [
            "#ifndef OUTPUT_H_",
            "#define OUTPUT_H_",
            "#include <stdint.h>",
            "int8_t GetVar(void);",
            "#endif /* OUTPUT_H_ */",
        ]

        self.other_output_c_data = [
            '#include "output.h"',
            "static int8_t Var = 1;",
            "int8_t GetVar(void) {",
            "}",
        ]

    def CallMainWithOtherInput(self):
        self.open.SetFileData(self.input_filename, self.other_input_data)
        self.CallMain()

    def test_Main_ReadsOutputHFile(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithGoodParameters(reset=False)
        self.assertTrue(self.open.FileWasRead(self.output_h_filename))

    def test_Main_ReadsOutputCFile(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithGoodParameters(reset=False)
        self.assertTrue(self.open.FileWasRead(self.output_c_filename))

    def test_Main_IfNoChange_MustNotUpdateH(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithGoodParameters(reset=False)
        self.assertEqual(self.open.GetFileWriteCount(self.output_h_filename), 1)

    def test_Main_IfNoChange_MustNotUpdateC(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithGoodParameters(reset=False)
        self.assertEqual(self.open.GetFileWriteCount(self.output_c_filename), 1)

    def test_Main_IfNoChange_MustUpdateH(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithOtherInput()
        self.assertEqual(self.open.GetFileWriteCount(self.output_h_filename), 2)

    def test_Main_IfNoChange_MustUpdateC(self):
        self.CallMainWithGoodParameters()
        self.CallMainWithOtherInput()
        self.assertEqual(self.open.GetFileWriteCount(self.output_c_filename), 2)

    def test_Main_TestChange_UseHFileHash_InsteadOfContent(self):
        self.CallMainWithGoodParameters()
        filename = self.output_h_filename
        file_data = self.open.GetFileData(filename)
        file_data += " /* Append a comment. */\n"
        self.open.SetFileData(filename, file_data)
        self.CallMainWithGoodParameters(reset=False)
        self.assertEqual(self.open.GetFileWriteCount(filename), 1)

    def test_Main_TestChange_UseCFileHash_InsteadOfContent(self):
        self.CallMainWithGoodParameters()
        filename = self.output_c_filename
        file_data = self.open.GetFileData(filename)
        file_data += " /* Append a comment. */\n"
        self.open.SetFileData(filename, file_data)
        self.CallMainWithGoodParameters(reset=False)
        self.assertEqual(self.open.GetFileWriteCount(filename), 1)


class TestMainUserDefinedCode(TestMainGoodParameters):
    def test_SectionsOfUserDefinedCode_AreKeptOnFileUpdate(self):
        self.skipTest("not implemented")
        code = """
/* Automatically generated includes begin */
#include "info.h"
/* Automatically generated includes end */

/* User defined includes begin */
/* User defined includes end */

/* Automatically generated variables begin */
uint8_t INFO_Val = 0;
/* Automatically generated variables end */

/* User defined variables begin */
uint32_t USER_Get_Val_Count = 0
/* User defined variables end */

/* Automatically generated code 1 INFO_GetVal begin */
uint8_t INFO_GetVal(void) {
    uint8_t val;
    /* Automatically generated code 1 INFO_GetVal end */

    /* User defined code 2 INFO_GetVal begin */
    USER_Get_Val_Count++;
    /* User defined code 2 INFO_GetVal end */

    /* Automatically generated code 3 INFO_GetVal begin */
    CRITICAL_BLOCK(
        val = INFO_Val;
    );
    /* Automatically generated code 3 INFO_GetVal end */

    /* User defined code 4 INFO_GetVal begin */
    USER_Get_Val_Count++;
    /* User defined code 4 INFO_GetVal end */

    /* Automatically generated code 5 INFO_GetVal begin */
    return val;
}
/* Automatically generated code 5 INFO_GetVal end */

/* User defined functions begin */

uint32_t USER_GetValCount(void) {
    uint8_t val;

    CRITICAL_BLOCK(
        val = USER_Get_Val_Count;
    );

    return val;
}

/* User defined functions end */

"""
        self.fail(
            "what to do with the code if a variable goes missing in the json?"
        )


if __name__ == "__main__":
    unittest.main()
