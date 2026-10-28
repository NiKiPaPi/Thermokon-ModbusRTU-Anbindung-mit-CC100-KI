TYPE ST_Thermokon_Register :
STRUCT
    xDocumented : BOOL;
    xSupported : BOOL;
    sName : STRING(80);
    sSource : STRING(80);
    sAccess : STRING(2); // RO=read only, RW=read/write per manual; ALL writes disabled
    bReadFunction : BYTE; // FC01 coils; FC03 register reads (manual supports FC03/04)
    uiAddress : UINT; // Exact ZERO-BASED protocol address from Rev M
    xSigned : BOOL; // INT16 versus UINT16, all Rev M values are one word or one bit
    rScale : REAL := 1.0;
    sUnit : STRING(16);
    xReadClears : BOOL;
    usiSpecial : USINT; // 1=FFFF hold last; 2=>1000 automatic
END_STRUCT
END_TYPE

