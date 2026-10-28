TYPE ST_Thermokon_Value :
STRUCT
    wRaw : WORD;
    rValue : REAL;
    xValid : BOOL; // Successful response, freshness and supported point
    xNumericValid : BOOL; // FALSE when raw is a special control code
    xSpecial : BOOL;
    xUnsupportedByDevice : BOOL; // Modbus exceptions 1/2/3, retried next cycle
    udiLastGoodMs : UDINT;
    wLastException : WORD;
    udiErrors : UDINT;
END_STRUCT
END_TYPE

