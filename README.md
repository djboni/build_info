# ARCHIVED

The projects below superseed this project.

- [Info](https://github.com/embtool/info)
- [Toggle](https://github.com/embtool/toggle)

# Build Info

Convert JSON to build information

Generate build information for a C/C++ project using a simple JSON file.

A simple way to add to the software:

* Project information and configuration
* Version of the software
* Commit being build
* Date and time of build

Steps:

1. Create a JSON specifying the desired information
2. Run build_info.py passing the JSON and the output file names
3. See the generated files
4. Add the command to the pre-build steps

## Step 1. Create a JSON

Input file: build.json

```json
{
    "string : Project_Name": "Build Info",
    "Version": [0, 1, 0, "", ""],
    "Git_Repository": "/PATH/TO/GIT/REPOSITORY",
    "Date_Time": true
}
```

## Step 2. Run the Command

Pass the input JSON file (build.json) and pass the basename to the C and
H file (build).

```sh
$ python build_info.py build.json build.h
```

## Step 3. See the generated files

Generated file: build.h

For the sake of brevity a few lines are ommitted.

```c
#ifndef BUILD_H_
#define BUILD_H_

#include <stdint.h>

const char *PtrProjectName(void);

uint32_t GetVersionNum(void);
const char *PtrVersionStr(void);

const char *PtrGitCommitStr(void);

uint32_t GetUnixTime(void);
const char *PtrTimeStr(void);

#endif /* BUILD_H_ */
```

## Step 4. Add Command to Pre-Build Steps

This depends on your IDE or build environment.

Let's see how to do it in Eclipse-CDT:

1. Enter the menu: Project > Properties > C/C++ Build > Settings >
    Build Steps
2. Select the configuration (Debug, Release, etc)
3. In the Pre-build steps box set the command to
    `python build_info.py build.json build.h`
4. Apply and Close
5. Build

You may need fix the paths, since the building is run inside the build
directory. Something like this:

`python ../path/to/build_info.py ../build/build.json ../build/build.h`

## Features

* Several configurations and types available

* Choose between Read-Only or Read-Write data

* Add macros and includes

* Values are held in variables in the C file. This limits the changes to the
header files: less frequent rebuilds of the whole project

* A hash is used to determine if the files need to be updated. This allows
reformatting of the generated code without causint an update of the H file every
time

## Configurations

```json
{
    "Module_Name":    "build",
    "Section_Prefix": "BUILD",
    "Version": [0, 1, 0, "", ""],
    "Git_Repository": "/PATH/TO/GIT/REPOSITORY",
    "Date_Time": true,
    "Bool_Is_Integer": true
}
```

* "Module_Name": "filename" - Used in the header include guards and as header
name in the inclusion

* "Section_Prefix": "BUILD" - Make all variables and functions be prefixed with
the string

* "Version": [MAJOR, MINOR, PATCH, "pre_release", "build_metadata"] - Add
version string and version number

* "Git_Repository": "/PATH/TO/REPO" - Add a string describing the current commit
in the repository

* "Date_Time": true - Add a date-time string and a unix timestamp

* "Bool_Is_Integer": true - By default booleans use type "bool" and values
"true" and "false". Using this configurations allows building with C90 by
changing them to "unit8_t", "1" and "0", respectively

## Types

| Type      | C Type          | Description                             |
| --------- | --------------- | --------------------------------------- |
| string    | char[]          | Null terminated string                  |
| string[N] | char[N]         | Null terminated string with fixed size  |
| int8      | int8_t          | 8 bit signed integer                    |
| int16     | int16_t         | 16 bit signed integer                   |
| int32     | int32_t         | 32 bit signed integer                   |
| int64     | int64_t         | 64 bit signed integer                   |
| uint8     | uint8_t         | 8 bit unsigned integer                  |
| uint16    | uint16_t        | 16 bit unsigned integer                 |
| uint32    | uint32_t        | 32 bit unsigned integer                 |
| uint64    | uint64_t        | 64 bit unsigned integer                 |
| float     | float           | 32 bit floating point                   |
| double    | double          | 64 bit floating point                   |
| bool      | bool or uint8_t | Boolean (can be implemented as uint8_t) |

## Read-Only Data

```json
{
    "Module_Name":    "info",
    "Section_Prefix": "INFO",
    "string : Project_Name": "Build Info",
    "uint32 : Data_Name":    0
}
```

* "type : Name_Of_Data": VALUE - Add data with its related type and value

* "string[16] : Name_Of_Str": "STRING" - Add a string with a fixed size

## Read-Write Data

```json
{
    "Module_Name":    "config",
    "Section_Prefix": "CONFIG",
    "uint32 :w: Serial_Baudrate":   9600,
    "uint32 :w: Serial_Timeout_ms": 1000,
}
```

* To be able to write to the value, just add a ":w" after the type

* "type :w: Name_Of_Data": VALUE - Add data with its related type and initial
value

# Macros and Includes

```json
{
    "macro : MAX(a,b)": "((a)>(b)?(a):(b))",
    "Include_Header": ["my_header.h", "<stdio.h>"],
    "Include_Source": ["my_header.h", "<stdio.h>"]
}
```

* "macro : MAX(a,b)": "((a)>(b)?(a):(b))" - Add a macro to the header

* "Include_Header": ["my_header.h", "<stdio.h>"] Add includes to the H file

* "Include_Source": ["my_header.h", "<stdio.h>"] - Add includes to the C file

# License

MIT License:
[LICENSE.txt](https://github.com/djboni/build_info/blob/master/LICENSE.txt)
