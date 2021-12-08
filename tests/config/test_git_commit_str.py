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
    import build_info as bi

try:
    from helper import *
except ModuleNotFoundError:
    sys.path.append("..")
    sys.path.append("../../src")
    from helper import *


class TestProcessJSONGitCommitStr(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.bi = bi.BuildInfo()
        self.git_mock = GitMock()
        self.patch = patch("build_info.git", self.git_mock)
        self.patch_enter = self.patch.__enter__()

    def tearDown(self) -> None:
        self.patch.__exit__(None, None, None)
        return super().tearDown()

    def test_GitCommitStr_AddsStringWithCommit_InC(self):
        self.bi.ProcessJSON('{"Git_Repository": "."}')
        lines = [
            'static char Git_Commit_Str[] = "',
            "const char *PtrGitCommitStr(void) {",
        ]
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)

    def test_GitCommitStr_AddsStringWithCommit_InH(self):
        self.bi.ProcessJSON('{"Git_Repository": "."}')
        lines = ["const char *PtrGitCommitStr(void);"]
        code = self.bi.GetH()
        AssertIsInSequence(lines, code, self)

    def test_GitCommitStr_ValueMustBeString(self):
        json_value_list = ["0", "{}", "[]", "true", "false", "null"]
        for json_value in json_value_list:
            json_data = f'{{"Git_Repository": {json_value}}}'
            with self.assertRaises(ValueError):
                self.bi.ProcessJSON(json_data)

    def test_GitCommitStr_GetCorrectCommitString(self):
        self.git_mock.SetCommitString("MOCKED_COMMIT_STRING")
        self.bi.ProcessJSON('{"Git_Repository": "."}')
        lines = ['static char Git_Commit_Str[] = "MOCKED_COMMIT_STRING"']
        code = self.bi.GetC()
        AssertIsInSequence(lines, code, self)


if __name__ == "__main__":
    unittest.main()
