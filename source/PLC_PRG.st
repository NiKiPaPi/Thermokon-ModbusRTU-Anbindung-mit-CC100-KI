PROGRAM PLC_PRG
VAR
    scanner : FB_Thermokon_ModbusScanner;
    udiCycle : UDINT;
END_VAR

udiCycle:=udiCycle+1;
PRG_ThermokonSelfTest();
scanner(udiNowMs:=SysTime.SysTimeGetMs());