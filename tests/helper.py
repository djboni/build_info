#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni


class IOWrapperMock:
    def __init__(self, filename, mode, file_manager):
        self.filename = filename
        self.mode = mode
        self.file_manager = file_manager

        self.read_count = 0
        self.write_count = 0

    def close(self):
        self.is_open = False

    def read(self):
        self.read_count += 1
        return self.file_manager.GetFileData(self.filename)

    def write(self, data):
        self.write_count += 1

        if self.file_manager.FileExists(self.filename):
            new_data = self.file_manager.GetFileData(self.filename) + data
        else:
            new_data = data

        self.file_manager.SetFileData(self.filename, new_data)

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.close()

    def SetFileData(self, data):
        self.data = data

    def GetFileData(self):
        return self.data


class OpenMock:
    def __init__(self):
        self.Reset()

    def Reset(self):
        self.open_files = {
            # "file.c": {
            #     "filename": "file.c",
            #     "mode": "r",
            #     "io_wrapper": IOWrapperMock()
            # }
        }
        self.file_system = {
            # "file.c": "data"
        }

    def __call__(self, filename, mode):
        if mode == "r" and filename not in self.file_system:
            raise FileNotFoundError()
        elif mode == "w":
            self.SetFileData(filename, "")

        if filename in self.open_files:
            io_wrapper = self.open_files[filename]["io_wrapper"]
        else:
            # New file
            io_wrapper = IOWrapperMock(filename, mode, file_manager=self)

            self.open_files[filename] = {
                "filename": filename,
                "mode": mode,
                "io_wrapper": io_wrapper,
            }

        return io_wrapper

    def FileExists(self, filename):
        return filename in self.file_system

    def SetFileData(self, filename, data):
        self.file_system[filename] = data

    def GetFileData(self, filename):
        return self.file_system[filename]

    def GetFileReadCount(self, filename):
        return self.open_files[filename]["io_wrapper"].read_count

    def FileWasRead(self, filename):
        return self.GetFileReadCount(filename) != 0

    def GetFileWriteCount(self, filename):
        return self.open_files[filename]["io_wrapper"].write_count

    def FileWasWritten(self, filename):
        return self.GetFileWriteCount(filename) != 0


class GitMock:
    """Used to mock git module (import git)."""

    def __init__(self):
        self.commit_string = "DEFAULT_COMMIT_STRING"

        """Allow call git.Repo(#).git"""
        self.git = self

    def Repo(self, repository, search_parent_directories):
        """Allow call git.Repo(#)"""
        return self

    def describe(self, *args):
        """Allow call git.Repo(#).git.describe"""
        return self.commit_string

    def SetCommitString(self, commit_string):
        self.commit_string = commit_string


class TimeMock:
    """Used to mock time module (import time)."""

    def __init__(self):
        self.unix_time = 0.0
        self.time_str = "1970-01-01 00:00:00"

        """Allow call datetime.datetime"""
        self.datetime = self

    def time(self):
        """Allow call time.time()."""
        return self.unix_time

    def SetUnixTime(self, unix_time):
        self.unix_time = unix_time

    def fromtimestamp(self, unix_time):
        """Allow call datetime.datetime.fromtimestamp(#)"""
        return self

    def strftime(self, format):
        """Allow call datetime.datetime.fromtimestamp(#).strftime(#)"""
        return self.time_str

    def SetTimeStr(self, time_str):
        self.time_str = time_str


def AssertIsInSequence(list_of_lines, code, test):
    next_idx = 0
    for line in list_of_lines:
        idx = code.find(line, next_idx)
        test.assertIn(line, code)
        test.assertNotEqual(-1, idx, f"out of sequence {line=}")
        next_idx = idx + len(line)
