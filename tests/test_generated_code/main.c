/*
 * Build Info - https://github.com/djboni/build_info
 * MIT License - Copyright (c) 2021 Djones A. Boni
 */

#include "info.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

#define INIT_VALUE 0x5A

int main(void) {
    printf("Git_Repository = \"%s\"\n", BUILD_PtrGitCommitStr());
    printf("Time_Str = \"%s\"\n", BUILD_PtrTimeStr());
    printf("Version_Str = \"%s\"\n", BUILD_PtrVersionStr());

    assert(INFO_GetInt8() == 0);
    INFO_SetInt8(1);
    assert(INFO_GetInt8() == 1);

    assert(INFO_GetUint8() == 0);
    INFO_SetUint8(1);
    assert(INFO_GetUint8() == 1);

    assert(INFO_GetInt16() == 0);
    INFO_SetInt16(1);
    assert(INFO_GetInt16() == 1);

    assert(INFO_GetUint16() == 0);
    INFO_SetUint16(1);
    assert(INFO_GetUint16() == 1);

    assert(INFO_GetInt32() == 0);
    INFO_SetInt32(1);
    assert(INFO_GetInt32() == 1);

    assert(INFO_GetUint32() == 0);
    INFO_SetUint32(1);
    assert(INFO_GetUint32() == 1);

    assert(INFO_GetInt64() == 0);
    INFO_SetInt64(1);
    assert(INFO_GetInt64() == 1);

    assert(INFO_GetUint64() == 0);
    INFO_SetUint64(1);
    assert(INFO_GetUint64() == 1);

    assert(INFO_GetFloat() == 0);
    INFO_SetFloat(1);
    assert(INFO_GetFloat() == 1);

    assert(INFO_GetDouble() == 0);
    INFO_SetDouble(1);
    assert(INFO_GetDouble() == 1);

    assert(INFO_GetBool() == 0);
    INFO_SetBool(1);
    assert(INFO_GetBool() == 1);

    {
        /* Guard BUFF[N] Guard */
        char buff_eight[10];
        char buff_seven[9];
        char buff_six[8];
        char buff_five[7];
        char buff_four[6];

        memset(buff_eight, INIT_VALUE, sizeof(buff_eight));
        memset(buff_seven, INIT_VALUE, sizeof(buff_seven));
        memset(buff_six, INIT_VALUE, sizeof(buff_six));
        memset(buff_five, INIT_VALUE, sizeof(buff_five));
        memset(buff_four, INIT_VALUE, sizeof(buff_four));

        assert(INFO_LenString() == 6);
        assert(strcmp(INFO_PtrString(), "Value") == 0);

        assert(INFO_GetString(buff_eight + 1, 8) == TRUE);
        assert(buff_eight[0] == INIT_VALUE);          /* Guard */
        assert(strcmp(buff_eight + 1, "Value") == 0); /* Copied string */
        assert(buff_eight[7] == INIT_VALUE);          /* Unwritten */
        assert(buff_eight[8] == 0);                   /* Forced null */
        assert(buff_eight[9] == INIT_VALUE);          /* Guard */

        assert(INFO_GetString(buff_seven + 1, 7) == TRUE);
        assert(buff_seven[0] == INIT_VALUE);          /* Guard */
        assert(strcmp(buff_seven + 1, "Value") == 0); /* Copied string */
        assert(buff_seven[7] == 0);                   /* Forced null */
        assert(buff_seven[8] == INIT_VALUE);          /* Guard */

        assert(INFO_GetString(buff_six + 1, 6) == TRUE);
        assert(buff_six[0] == INIT_VALUE);          /* Guard */
        assert(strcmp(buff_six + 1, "Value") == 0); /* Copied string */
        assert(buff_six[6] == 0);                   /* Forced null */
        assert(buff_six[7] == INIT_VALUE);          /* Guard */

        assert(INFO_GetString(buff_five + 1, 5) == FALSE);
        assert(buff_six[0] == INIT_VALUE);          /* Guard */
        assert(strcmp(buff_five + 1, "Valu") == 0); /* Copied string. */
        assert(buff_five[5] == 0);                  /* Forced null */
        assert(buff_five[6] == INIT_VALUE);         /* Guard */

        assert(INFO_GetString(buff_four + 1, 4) == FALSE);
        assert(buff_six[0] == INIT_VALUE);         /* Guard */
        assert(strcmp(buff_four + 1, "Val") == 0); /* Copied string. */
        assert(buff_four[4] == 0);                 /* Forced null */
        assert(buff_four[5] == INIT_VALUE);        /* Guard */

        /* Nothing is written. */
        assert(INFO_SetString("", 0) == TRUE);
        assert(strcmp(INFO_PtrString(), "Value") == 0);

        assert(INFO_SetString("", 1) == TRUE);
        assert(strcmp(INFO_PtrString(), "") == 0);

        assert(INFO_SetString("T", 2) == TRUE);
        assert(strcmp(INFO_PtrString(), "T") == 0);

        assert(INFO_SetString("TE", 3) == TRUE);
        assert(strcmp(INFO_PtrString(), "TE") == 0);

        assert(INFO_SetString("TES", 4) == TRUE);
        assert(strcmp(INFO_PtrString(), "TES") == 0);

        assert(INFO_SetString("TEST", 5) == TRUE);
        assert(strcmp(INFO_PtrString(), "TEST") == 0);

        assert(INFO_SetString("TESTA", 6) == TRUE);
        assert(strcmp(INFO_PtrString(), "TESTA") == 0);

        /* If out of bounds, return FALSE and do not write out of bounds. */
        assert(INFO_SetString("TESTAB", 7) == FALSE);
        assert(strcmp(INFO_PtrString(), "TESTA") == 0);
    }

    return 0;
}
