#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

"""Convert JSON to C variables"""


import json
import re
import struct
import hashlib
import collections
import time
import datetime

try:
    import git
except ModuleNotFoundError as e:
    print(f"Warning: {e}")
    print("Warning: Not able to read Git repositories.")
    print("Warning: To install the required module run")
    print("Warning: pip install GitPython")

    # Set to None to allow testing without the module
    git = None

FLOAT_MAX = struct.unpack(">f", b"\x7f\x7f\xff\xff")[0]
FLOAT_MIN = struct.unpack(">f", b"\xff\x7f\xff\xff")[0]
DOUBLE_MAX = struct.unpack(">d", b"\x7f\xef\xff\xff\xff\xff\xff\xff")[0]
DOUBLE_MIN = struct.unpack(">d", b"\xff\xef\xff\xff\xff\xff\xff\xff")[0]

KeyRegex = re.compile(
    # Regex: type[size]:qualif:name(params, a, b)
    #
    #                  brackets_size
    #                  /           \
    #        type     [    size     ]     :
    #        |  \          |  \           |
    r"^(?:\s*(\w*)\s*(\[\s*(\w*)\s*\])?\s*:)?"
    #
    #                           macro_params
    #                           |           \
    #       qualif  :     name  (params, a, b)
    #       |  \    |     |  \  |           \
    r"(?:\s*(\w*)\s*:)?\s*(\w+)(\([\w\s,]*?\))?\s*$"
)

KeyData = collections.namedtuple(
    "KeyRegex",
    "type brackets_size size qualif name macro_params",
    defaults=["", "", None, "", "", ""],
)

CodeData = collections.namedtuple(
    "CodeData", "macro header variable function", defaults=["", "", "", ""]
)


class DefaultFormatter:
    """Formatter for names.

    Write names in Camel_Case and let the format make the conversion.

    Examples:

    Name            | Project_Name
    ------------------------------
    Local variable  | project_name
    Global variable | Project_Name
    Function        | ProjectName
    Macro           | PROJECT_NAME

    Module       | Build_Info
    ----------------------------
    Section_Prefix       | BUILD_INFO_
    Source file  | build_info.c
    Header file  | build_info.h
    Header guard | BUILD_INFO_H_
    """

    def NameToLocalVariable(self, name):
        return name.lower()

    def NameToGlobalVariable(self, name):
        return name

    def NameToFunction(self, name):
        return name.replace("_", "")

    def NameToMacro(self, name):
        return name.upper()

    def NameToPrefix(self, name):
        return name.upper() + "_"

    def NameToSourceFilename(self, name):
        return name.lower() + ".c"

    def NameToHeaderFilename(self, name):
        return name.lower() + ".h"

    def NameToHeaderGuard(self, name):
        return name.upper() + "_H_"


class SecondFormatter:
    """Formatter for names.

    Write names in Camel_Case and let the format make the conversion.

    Examples:

    Name            | Project_Name
    ------------------------------
    Local variable  | projectName
    Global variable | ProjectName
    Function        | project_name
    Macro           | PROJECT_NAME

    Module       | Build_Info
    ----------------------------
    Section_Prefix       | BUILD_INFO_
    Source file  | build_info.c
    Header file  | build_info.h
    Header guard | BUILD_INFO_H_
    """

    def NameToLocalVariable(self, name):
        return (name[0].lower() + name[1:]).replace("_", "")

    def NameToGlobalVariable(self, name):
        return name.replace("_", "")

    def NameToFunction(self, name):
        return name.lower()

    def NameToMacro(self, name):
        return name.upper()

    def NameToPrefix(self, name):
        return name.upper() + "_"

    def NameToSourceFilename(self, name):
        return name.lower() + ".c"

    def NameToHeaderFilename(self, name):
        return name.lower() + ".h"

    def NameToHeaderGuard(self, name):
        return name.upper() + "_H_"


class GitData:
    def GetCommitString(self, repository):
        repo = git.Repo(repository, search_parent_directories=True)
        describe_args = ["--always", "--tags", "--dirty=-D", "--broken=-B"]
        commit_string = repo.git.describe(describe_args)
        return commit_string


class BuildInfo:
    INT_TYPES = (
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
    )
    INT_LIMITS = {
        # "type": (MIN, MAX+1)
        "int8": (-0x80, 0x80),
        "int16": (-0x8000, 0x8000),
        "int32": (-0x80000000, 0x80000000),
        "int64": (-0x8000000000000000, 0x8000000000000000),
        "uint8": (0, 0x100),
        "uint16": (0, 0x10000),
        "uint32": (0, 0x100000000),
        "uint64": (0, 0x10000000000000000),
    }

    FLOAT_TYPES = ("float", "double")
    FLOAT_LIMITS = {
        # "type": (MIN, MAX)
        "float": (FLOAT_MIN, FLOAT_MAX),
        "double": (DOUBLE_MIN, DOUBLE_MAX),
    }

    ALLOWED_QUALIFIERS = "rw"

    def __init__(self, filename_base=None, formatter=DefaultFormatter()):
        self.Reset()
        self.SetFilename(filename_base)
        self._formatter = formatter
        self._bool_integer = False

    def Reset(self):
        """Reset on initialization and when user calls."""
        self._SemiReset()

        self._c_code_vars = []
        self._c_code_funcs = []
        self._h_code_macros = []
        self._h_code_funcs = []

        self._h_code_includes = ["<stdint.h>"]
        self._c_code_includes = ["<<FILE_HEADER_NAME>>"]

    def _SemiReset(self):
        """_SemiReset when new object starts."""
        self.SetModuleName()

    def SetModuleName(self, name=None):
        if name == None:
            self._module_name = self._GetDefaultModuleName()
        else:
            self._module_name = name

    def SetFilename(self, filename_base):
        self._filename_base = filename_base

    def _GetDefaultModuleName(self):
        return ""

    def _GetDefaultFilename(self):
        if self._module_name == "":
            return "INFO"
        return self._module_name

    def ProcessJSON(self, json_data):
        data = json.loads(json_data)

        if type(data) is dict:
            self._ProcessJSONObject(data)
        elif type(data) is list:
            self._ProcessJSONArray(data)
        else:
            raise ValueError(
                "json_data must have an object (dict) or an array of objects (list of dict)"
            )

    def _ProcessJSONArray(self, data):
        for obj in data:
            self._ProcessJSONObject(obj)

    def _ProcessJSONObject(self, obj):
        if type(obj) is not dict:
            raise ValueError(
                "json_data must have an object (dict) or an array of objects (list of dict)"
            )

        self._SemiReset()

        for raw_type_data, value in obj.items():
            self._GenAndAddVariable(raw_type_data, value)
            self._AddNewlineSeparators()

        self._RepalceTags()

    def _GenAndAddVariable(self, raw_type_data, value):
        key_data = self._SplitTypeSizeNameMacro(raw_type_data)
        code_data = self._GenCodeFromTypeSizeNameValueMacro(key_data, value)
        self._AddCode(code_data)

    def _SplitTypeSizeNameMacro(self, raw_type_data):
        key_data = KeyRegex.findall(raw_type_data)
        if len(key_data) != 1:
            raise ValueError(
                f"{raw_type_data} had {len(key_data)} matches (!= 1)"
            )
        key_data = KeyData(*key_data[0])

        if key_data.type == "":
            key_data = key_data._replace(type="config")

        if key_data.size != "":
            # [number]
            key_data = key_data._replace(size=int(key_data.size))
        elif key_data.brackets_size != "":
            # [] w/o number
            key_data = key_data._replace(size=True)
        else:
            # No []
            key_data = key_data._replace(size=None)

        if key_data.qualif == "":
            key_data = key_data._replace(qualif="r")

        self._ValidateQualifiers(key_data.qualif)
        self._ValidateKeyDataValue(key_data, raw_type_data)

        return key_data

    def _ValidateQualifiers(self, qualif):
        for ch in qualif:
            if qualif not in self.ALLOWED_QUALIFIERS:
                raise ValueError(f"invalid qualifier {qualif=}")

    def _ValidateKeyDataValue(self, key_data, raw_type_data):
        if key_data.macro_params != "" and key_data.type != "macro":
            raise ValueError(
                f"not a macro to use () on the key_data.name '{raw_type_data}'"
            )
        elif key_data.size is not None and key_data.type == "macro":
            raise ValueError(
                f"a macro cannot use [] in the type '{raw_type_data}'"
            )

    def _GenCodeFromTypeSizeNameValueMacro(self, key_data, value):
        if key_data.type == "config":
            return self._ProcessConfig(key_data, value)
        elif key_data.type == "string":
            return self._GenString(key_data, value)
        elif key_data.type in self.INT_TYPES:
            return self._GenNumberWithUnderscoreT(key_data, value)
        elif key_data.type in self.FLOAT_TYPES:
            return self._GenNumber(key_data, value)
        elif key_data.type == "bool":
            return self._GenBool(key_data, value)
        elif key_data.type == "macro":
            return self._GenMacro(key_data, value)
        else:
            raise ValueError(f"invalid type '{key_data.type}'")

    def _ProcessConfig(self, key_data, value):
        if key_data.name == "Section_Prefix":
            return self._ConfigModuleName(key_data, value)
        elif key_data.name == "Module_Name":
            return self._ConfigFileName(key_data, value)
        elif key_data.name == "Bool_Is_Integer":
            return self._ConfigBoolInteger(key_data, value)
        elif key_data.name == "Include_Source":
            return self._ConfigIncludesOnSource(key_data, value)
        elif key_data.name == "Include_Header":
            return self._ConfigIncludesOnHeader(key_data, value)
        elif key_data.name == "Git_Repository":
            return self._ConfigGitCommitStr(key_data, value)
        elif key_data.name == "Date_Time":
            return self._ConfigTimeData(key_data, value)
        elif key_data.name == "Version":
            return self._ConfigVersion(key_data, value)
        else:
            raise ValueError(f"invalid config '{key_data.name}'")

    def _ConfigModuleName(self, key_data, value):
        if type(value) is not str:
            raise ValueError(
                f"config {key_data.name} must be string, not '{value}'"
            )
        self.SetModuleName(value)
        return CodeData()

    def _ConfigFileName(self, key_data, value):
        if type(value) is not str:
            raise ValueError(
                f"config {key_data.name} must be string, not '{value}'"
            )
        self.SetFilename(value)
        return CodeData()

    def _ConfigBoolInteger(self, key_data, value):
        if type(value) is not bool:
            raise ValueError(f"invalid bool '{value}'")
        self._bool_integer = value
        return CodeData()

    def _ConfigIncludesOnSource(self, key_data, value):
        if type(value) is not list:
            raise ValueError(f"invalid array '{value}'")
        for file in value:
            if type(file) is not str:
                raise ValueError(f"invalid array of strings '{value}'")
            self._c_code_includes.append(file)
        return CodeData()

    def _ConfigIncludesOnHeader(self, key_data, value):
        if type(value) is not list:
            raise ValueError(f"invalid array '{value}'")
        for file in value:
            if type(file) is not str:
                raise ValueError(f"invalid array of strings '{value}'")
            self._h_code_includes.append(file)
        return CodeData()

    def _ConfigGitCommitStr(self, key_data, value):
        if type(value) is not str:
            raise ValueError(f"invalid str '{value}'")
        git_data = GitData()
        commit = git_data.GetCommitString(value)
        self._GenAndAddVariable("string[]:Git_Commit_Str", f"{commit}")
        return CodeData()

    def _ConfigTimeData(self, key_data, value):
        if type(value) is not bool:
            raise ValueError(f"invalid bool '{value}'")
        unix_time = int(time.time())
        time_str = datetime.datetime.fromtimestamp(unix_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if value:
            self._GenAndAddVariable("uint32:Unix_Time", unix_time)
            self._GenAndAddVariable("string:Time_Str", time_str)
        return CodeData()

    def _ConfigVersion(self, key_data, value):
        if type(value) is not list:
            raise ValueError(f"invalid array '{value}'")
        elif len(value) != 5:
            raise ValueError(
                f"invalid version '{value}',"
                + " should be [int, int, int, str, str]"
                + " [major, minor, patch, pre_release, build_metadata]"
            )

        major = value[0]
        minor = value[1]
        patch = value[2]
        pre_release = value[3]
        build_metadata = value[4]

        if type(major) is not int:
            raise ValueError(f"version major must be int '{major}'")
        elif type(minor) is not int:
            raise ValueError(f"version minor must be int '{minor}'")
        elif type(patch) is not int:
            raise ValueError(f"version patch must be int '{patch}'")
        elif type(pre_release) is not str:
            raise ValueError(f"version pre_release must be str '{pre_release}'")
        elif type(build_metadata) is not str:
            raise ValueError(
                f"version build_metadata must be str '{build_metadata}'"
            )

        if major < 0 or minor < 0 or patch < 0:
            raise ValueError(f"version numbers must be >= 0")
        elif major >= 256 or minor >= 256 or patch >= 256:
            raise ValueError(f"version numbers must be < 256")

        version_str = f"{major}.{minor}"
        if patch != 0:
            version_str += f".{patch}"
        if pre_release != "":
            version_str += f"-{pre_release}"
        if build_metadata != "":
            version_str += f"+{build_metadata}"

        version_num = (major << 16) + (minor << 8) + patch

        self._GenAndAddVariable("string:Version_Str", version_str)
        self._GenAndAddVariable("uint32:Version_Num", version_num)

        return CodeData()

    def _GenString(self, key_data, value):
        if type(value) is not str:
            raise ValueError(f"invalid string '{value}'")

        name_var = self._formatter.NameToGlobalVariable(key_data.name)

        if key_data.size in (None, True):
            size = ""
        elif len(value) + 1 <= key_data.size:
            size = str(key_data.size)
        else:
            raise ValueError(
                f"string does not fit size={key_data.size} string='{value}'"
            )

        if "r" in key_data.qualif:
            qualif = ""
        else:
            qualif = ""

        # Variable
        variable = f'static {qualif}char <<MODULE_NAME>>{name_var}[{size}] = "{value}";\n'

        # Length
        func_prefix = "Len"
        name_func = self._formatter.NameToFunction(
            f"{func_prefix}_{key_data.name}"
        )
        prototype1 = f"uint16_t <<MODULE_NAME>>{name_func}(void)"
        header1 = f"{prototype1};\n"
        function1 = f"""
{prototype1} {{
    return sizeof(<<MODULE_NAME>>{name_var});
}}
"""

        # Ptr
        func_prefix = "Ptr"
        name_func = self._formatter.NameToFunction(
            f"{func_prefix}_{key_data.name}"
        )
        prototype2 = f"const char *<<MODULE_NAME>>{name_func}(void)"
        header2 = f"{prototype2};\n"
        function2 = f"""
{prototype2} {{
    return &<<MODULE_NAME>>{name_var}[0];
}}
"""

        # Get
        func_prefix = "Get"
        name_func = self._formatter.NameToFunction(
            f"{func_prefix}_{key_data.name}"
        )
        prototype3 = f"<<BOOL_TYPE>> <<MODULE_NAME>>{name_func}(char *buff_ptr, uint16_t len)"
        header3 = f"{prototype3};\n"
        function3 = f"""
{prototype3} {{
    <<BOOL_TYPE>> success = <<BOOL_TRUE>>;
    uint16_t i;
    const char *ptr = &<<MODULE_NAME>>{name_var}[0];
    char *buff_end_ptr = &buff_ptr[len - 1];

    CRITICAL_BLOCK(
        for (i = 0; i < sizeof(<<MODULE_NAME>>{name_var}); i++) {{
            if (i >= len) {{
                success = <<BOOL_FALSE>>;
                break;
            }}
            *buff_ptr++ = *ptr++;
        }}
    );

    *buff_end_ptr = 0;
    return success;
}}
"""

        # Set
        if "w" in key_data.qualif:
            func_prefix = "Set"
            name_func = self._formatter.NameToFunction(
                f"{func_prefix}_{key_data.name}"
            )
            prototype4 = f"<<BOOL_TYPE>> <<MODULE_NAME>>{name_func}(const char *buff_ptr, uint16_t len)"
            header4 = f"{prototype4};\n"
            function4 = f"""
{prototype4} {{
    <<BOOL_TYPE>> success = <<BOOL_TRUE>>;
    uint16_t i;
    char *ptr = &<<MODULE_NAME>>{name_var}[0];

    CRITICAL_BLOCK(
        for (i = 0; i < len; i++) {{
            if (i >= sizeof(<<MODULE_NAME>>{name_var})) {{
                success = <<BOOL_FALSE>>;
                break;
            }}
            *ptr++ = *buff_ptr++;
        }}
    );

    <<MODULE_NAME>>{name_var}[sizeof(<<MODULE_NAME>>{name_var}) - 1] = 0;
    return success;
}}
"""
        else:
            header4 = ""
            function4 = ""

        header = header1 + header2 + header3 + header4
        function = function1 + function2 + function3 + function4

        return CodeData(header=header, variable=variable, function=function)

    def _GenNumberWithUnderscoreT(self, key_data, value):
        return self._GenNumber(key_data, value, add_undersdore_t=True)

    def _GenNumber(self, key_data, value, add_undersdore_t=False):
        if key_data.type in self.INT_TYPES:
            if type(value) is not int:
                raise ValueError(f"invalid int '{value}'")
            elif value not in range(*self.INT_LIMITS[key_data.type]):
                raise ValueError(
                    f"value '{value}' is outside of range of type {key_data.type}"
                )
        elif key_data.type in self.FLOAT_TYPES:
            if type(value) not in (float, int):
                raise ValueError(f"invalid float '{value}'")
            elif value < FLOAT_MIN or value > FLOAT_MAX:
                raise ValueError(
                    f"value '{value}' is outside of range of type {key_data.type}"
                )
        else:
            raise ValueError(
                f"invalid number type or value type={key_data.type} {value=}"
            )

        name_var = self._formatter.NameToGlobalVariable(key_data.name)

        if add_undersdore_t:
            key_data = key_data._replace(type=key_data.type + "_t")

        if "r" in key_data.qualif:
            qualif = ""
        else:
            qualif = ""

        # Variable
        variable = f"static {qualif}{key_data.type} <<MODULE_NAME>>{name_var} = {value};\n"

        # Get
        func_prefix = "Get"
        name_func = self._formatter.NameToFunction(
            f"{func_prefix}_{key_data.name}"
        )
        prototype1 = f"{key_data.type} <<MODULE_NAME>>{name_func}(void)"
        header1 = f"{prototype1};\n"
        function1 = f"""
{prototype1} {{
    {key_data.type} val;

    CRITICAL_BLOCK(
        val = <<MODULE_NAME>>{name_var};
    );

    return val;
}}
"""

        # Set
        if "w" in key_data.qualif:
            func_prefix = "Set"
            name_func = self._formatter.NameToFunction(
                f"{func_prefix}_{key_data.name}"
            )
            prototype2 = f"void <<MODULE_NAME>>{name_func}({key_data.type} val)"
            header2 = f"{prototype2};\n"
            function2 = f"""
{prototype2} {{
    CRITICAL_BLOCK(
        <<MODULE_NAME>>{name_var} = val;
    );
}}
"""
        else:
            header2 = ""
            function2 = ""

        header = header1 + header2
        function = function1 + function2

        return CodeData(header=header, variable=variable, function=function)

    def _GenBool(self, key_data, value):
        if type(value) is not bool:
            raise ValueError(f"invalid bool '{value}'")

        name_var = self._formatter.NameToGlobalVariable(key_data.name)

        value = "<<BOOL_TRUE>>" if value else "<<BOOL_FALSE>>"

        if "r" in key_data.qualif:
            qualif = ""
        else:
            qualif = ""

        # Variable
        variable = f"static {qualif}<<BOOL_TYPE>> <<MODULE_NAME>>{name_var} = {value};\n"

        # Get
        func_prefix = "Get"
        name_func = self._formatter.NameToFunction(
            f"{func_prefix}_{key_data.name}"
        )
        prototype1 = f"<<BOOL_TYPE>> <<MODULE_NAME>>{name_func}(void)"
        header1 = f"{prototype1};\n"
        function1 = f"""
{prototype1} {{
    <<BOOL_TYPE>> val;

    CRITICAL_BLOCK(
        val = <<MODULE_NAME>>{name_var};
    );

    return val;
}}
"""

        # Set
        if "w" in key_data.qualif:
            func_prefix = "Set"
            name_func = self._formatter.NameToFunction(
                f"{func_prefix}_{key_data.name}"
            )
            prototype2 = f"void <<MODULE_NAME>>{name_func}(<<BOOL_TYPE>> val)"
            header2 = f"{prototype2};\n"
            function2 = f"""
{prototype2} {{
    CRITICAL_BLOCK(
        <<MODULE_NAME>>{name_var} = val;
    );
}}
"""
        else:
            header2 = ""
            function2 = ""

        header = header1 + header2
        function = function1 + function2

        return CodeData(header=header, variable=variable, function=function)

    def _GenMacro(self, key_data, value):
        if type(value) is not str:
            raise ValueError(f"macro must be a string, not '{value}'")

        name_macro = self._formatter.NameToMacro(key_data.name)

        macro = f"#define <<MODULE_NAME>>{name_macro}{key_data.macro_params} {value}\n"

        return CodeData(macro=macro)

    def _AddNewlineSeparators(self):
        self._AddCode(CodeData("\n", "\n", "\n", "\n"))

    def _AddCode(self, code_data):
        self._h_code_macros.append(code_data.macro)
        self._h_code_funcs.append(code_data.header)
        self._c_code_vars.append(code_data.variable)
        self._c_code_funcs.append(code_data.function)

    def _RepalceTags(self):
        for i, line in enumerate(self._c_code_vars):
            self._c_code_vars[i] = self._ReplaceAllTagsInLine(line)
        for i, line in enumerate(self._c_code_funcs):
            self._c_code_funcs[i] = self._ReplaceAllTagsInLine(line)
        for i, line in enumerate(self._h_code_funcs):
            self._h_code_funcs[i] = self._ReplaceAllTagsInLine(line)
        for i, line in enumerate(self._h_code_macros):
            self._h_code_macros[i] = self._ReplaceAllTagsInLine(line)

    def GetH(self, with_hash=True):
        code = "".join(self._h_code_macros + self._h_code_funcs)
        code = self._AddHHeaderGuardsAndIncludes(code)
        code = self._ReplaceAllTagsInLine(code)
        code = self._RemoveExtraNewlines(code)
        if with_hash:
            code = self._AddHeaderWithHash(code)
        return code

    def GetC(self, with_hash=True):
        code = "".join(self._c_code_vars + self._c_code_funcs)
        code = self._AddCIncludes(code)
        code = self._ReplaceAllTagsInLine(code)
        code = self._RemoveExtraNewlines(code)
        if with_hash:
            code = self._AddHeaderWithHash(code)
        return code

    def _AddHHeaderGuardsAndIncludes(self, code):
        code = [
            f"#ifndef <<FILE_HEADER_GUARD>>\n",
            f"#define <<FILE_HEADER_GUARD>>\n",
            f"\n",
            *self._ListOfIncludesH(),
            f"\n",
            code,
            f"\n",
            f"#endif /* <<FILE_HEADER_GUARD>> */\n",
        ]
        return "".join(code)

    def _ListOfIncludesH(self):
        includes = [
            f"#include {self._StandardLibInclude(file)}\n"
            for file in self._h_code_includes
        ]
        return includes

    def _StandardLibInclude(self, file):
        if (
            file.startswith("<")
            and file.endswith(">")
            and file != "<<FILE_HEADER_NAME>>"
        ):
            return file
        else:
            return f'"{file}"'

    def _AddCIncludes(self, code):
        code = self._ListOfIncludesC() + ["\n", code]
        return "".join(code)

    def _ListOfIncludesC(self):
        includes = [
            f"#include {self._StandardLibInclude(file)}\n"
            for file in self._c_code_includes
        ]
        return includes

    def _ReplaceAllTagsInLine(self, code):
        if self._filename_base == None:
            filename_base = self._GetDefaultFilename()
        else:
            filename_base = self._filename_base

        if self._module_name == "":
            module_name = ""
        else:
            module_name = self._formatter.NameToPrefix(self._module_name)

        code = code.replace("<<MODULE_NAME>>", module_name)

        code = code.replace(
            "<<FILE_HEADER_GUARD>>",
            self._formatter.NameToHeaderGuard(filename_base),
        )

        code = code.replace(
            "<<FILE_HEADER_NAME>>",
            self._formatter.NameToHeaderFilename(filename_base),
        )

        if self._bool_integer:
            bool_type = "uint8_t"
            bool_true = "1"
            bool_false = "0"
        else:
            bool_type = "bool"
            bool_true = "true"
            bool_false = "false"

        code = code.replace("<<BOOL_TYPE>>", bool_type)

        code = code.replace("<<BOOL_TRUE>>", bool_true)

        code = code.replace("<<BOOL_FALSE>>", bool_false)

        return code

    def _AddHeaderWithHash(self, code):
        hash = self._CalcHash(code)
        hash_comment = [
            f'/*{78 * "*"}\n',
            " * Code generated automatically.\n",
            " * The hash below is used to detect if this file needs to be updated.\n",
            f" * SHA-256: {hash}\n",
            f' {78 * "*"}/\n\n',
            code,
        ]
        return "".join(hash_comment)

    def _RemoveExtraNewlines(self, code):
        code = re.sub("\n\n+", "\n\n", code)
        return code

    def CalcCHash(self):
        return self._CalcHash(self.GetC(with_hash=False))

    def CalcHHash(self):
        return self._CalcHash(self.GetH(with_hash=False))

    def _CalcHash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()


def main(argv, open=open, print=print):
    import os

    if len(argv) != 3:
        print(f"Usage: {os.path.basename(argv[0])} INPUT.json OUTPUT[.c|.h]")
        return 1

    filein = argv[1]
    fileout = argv[2]

    with open(filein, "r") as fp:
        json_data = fp.read()

    fileout = RemoveFilenameExtension(fileout)
    fileoutc = fileout + ".c"
    fileouth = fileout + ".h"

    bi = BuildInfo(filename_base=fileout)
    bi.ProcessJSON(json_data)
    code_c = bi.GetC()
    hash_c = bi.CalcCHash()
    code_h = bi.GetH()
    hash_h = bi.CalcHHash()

    try:
        with open(fileoutc, "r") as fp:
            current_code_c = fp.read()
    except FileNotFoundError:
        current_code_c = ""

    if hash_c not in current_code_c:
        with open(fileoutc, "w") as fp:
            fp.write(code_c)

    try:
        with open(fileouth, "r") as fp:
            current_code_h = fp.read()
    except FileNotFoundError:
        current_code_h = ""

    if hash_h not in current_code_h:
        with open(fileouth, "w") as fp:
            fp.write(code_h)

    return 0


def RemoveFilenameExtension(filename):
    return re.sub(r"\.[cChH]$", "", filename)


if __name__ == "__main__":
    import sys

    main(sys.argv)
