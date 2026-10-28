FUNCTION_BLOCK FB_Thermokon_Device
VAR_INPUT
    bSlaveId : BYTE;
    xIdentityUpdate : BOOL;
    xIdentitySuccess : BOOL;
    wDeviceCode : WORD;
    wFirmware : WORD;
    wDeviceType : WORD;
    xUpdate : BOOL;
    xSuccess : BOOL;
    uiRegisterIndex : UINT;
    wRaw : WORD;
    wException : WORD;
    udiNowMs : UDINT;
    tStaleTime : TIME := T#120s;
END_VAR
VAR_OUTPUT
    xOnline : BOOL;
    xEverSeen : BOOL;
    xThermokonConfirmed : BOOL; // Rev M code=3 and AO2V type=0, not cryptographic identity
    xOtherDevice : BOOL;
    wGeraetekodierung : WORD;
    wFirmwareversion : WORD;
    wGeraetetyp : WORD;
    udiLastGoodMs : UDINT;
    udiGoodReplies : UDINT;
    udiCommunicationErrors : UDINT;
    wLastException : WORD;
    aValues : ARRAY[1..128] OF ST_Thermokon_Value;
    rRoomTemperature : REAL;
    rEffectiveSetpoint : REAL;
    rLocalOffset : REAL;
    rHeatingPercent : REAL;
    rCoolingPercent : REAL;
    rAO1Volts : REAL;
    rAO2Volts : REAL;
    xRoomOccupied : BOOL;
    xDI1 : BOOL;
    xDI2 : BOOL;
    wFanStage : WORD;
    wControllerMode : WORD;
    uliDI1CountSinceStart : ULINT; // Sum of read-to-clear deltas, NOT retained
    uliDI2CountSinceStart : ULINT;
    xTemperatureValid : BOOL;
END_VAR
VAR
    i : UINT;
    v : REAL;
END_VAR

IF xIdentityUpdate THEN
    xOnline := xIdentitySuccess;
    xThermokonConfirmed := FALSE;
    xOtherDevice := FALSE;
    IF xIdentitySuccess THEN
        xEverSeen := TRUE;
        udiLastGoodMs := udiNowMs;
        udiGoodReplies := udiGoodReplies + 1;
        wGeraetekodierung := wDeviceCode;
        wFirmwareversion := wFirmware;
        wGeraetetyp := wDeviceType;
        xThermokonConfirmed := (wDeviceCode = 3) AND (wDeviceType = 0);
        xOtherDevice := NOT xThermokonConfirmed;
    ELSE
        udiCommunicationErrors := udiCommunicationErrors + 1;
    END_IF
    // A successful repeat identification does not invalidate still-fresh measurements.
    IF NOT xIdentitySuccess OR NOT xThermokonConfirmed THEN
        FOR i:=1 TO 128 DO aValues[i].xValid:=FALSE; aValues[i].xNumericValid:=FALSE; END_FOR
    END_IF
END_IF
IF xUpdate AND (uiRegisterIndex >= 1) AND (uiRegisterIndex <= GVL_Thermokon.uiRegisterCount) THEN
    wLastException := wException;
    aValues[uiRegisterIndex].wLastException := wException;
    aValues[uiRegisterIndex].xValid := xSuccess;
    aValues[uiRegisterIndex].xNumericValid := FALSE;
    IF xSuccess THEN
        xOnline := TRUE;
        udiLastGoodMs := udiNowMs;
        udiGoodReplies := udiGoodReplies + 1;
        aValues[uiRegisterIndex].wRaw := wRaw;
        aValues[uiRegisterIndex].xUnsupportedByDevice := FALSE;
        IF GVL_Thermokon.aRegisters[uiRegisterIndex].xSigned THEN
            v := INT_TO_REAL(WORD_TO_INT(wRaw));
        ELSE v := UINT_TO_REAL(WORD_TO_UINT(wRaw)); END_IF
        aValues[uiRegisterIndex].xSpecial :=
            ((GVL_Thermokon.aRegisters[uiRegisterIndex].usiSpecial=1) AND (wRaw=16#FFFF))
            OR ((GVL_Thermokon.aRegisters[uiRegisterIndex].usiSpecial=2) AND (wRaw>1000));
        IF NOT aValues[uiRegisterIndex].xSpecial THEN
            aValues[uiRegisterIndex].rValue := v * GVL_Thermokon.aRegisters[uiRegisterIndex].rScale;
            aValues[uiRegisterIndex].xNumericValid := TRUE;
        END_IF
        aValues[uiRegisterIndex].udiLastGoodMs := udiNowMs;
    ELSE
        aValues[uiRegisterIndex].udiErrors := aValues[uiRegisterIndex].udiErrors + 1;
        aValues[uiRegisterIndex].xUnsupportedByDevice := (wException>=1) AND (wException<=3);
        udiCommunicationErrors := udiCommunicationErrors + 1;
        // A Modbus exception proves presence; a transport timeout invalidates online status.
        IF wException=0 THEN xOnline:=FALSE; END_IF
    END_IF
END_IF
IF (udiNowMs-udiLastGoodMs)>=TIME_TO_UDINT(tStaleTime) THEN xOnline:=FALSE; END_IF
FOR i:=1 TO 128 DO
    IF NOT xOnline OR ((udiNowMs-aValues[i].udiLastGoodMs)>=TIME_TO_UDINT(tStaleTime)) THEN
        aValues[i].xValid:=FALSE;
        aValues[i].xNumericValid:=FALSE;
    END_IF
END_FOR
rRoomTemperature := aValues[43].rValue;
rEffectiveSetpoint := aValues[45].rValue;
rLocalOffset := aValues[44].rValue;
rHeatingPercent := aValues[49].rValue;
rCoolingPercent := aValues[50].rValue;
rAO1Volts := aValues[52].rValue;
rAO2Volts := aValues[53].rValue;
wFanStage := aValues[47].wRaw;
wControllerMode := aValues[58].wRaw;
xTemperatureValid := aValues[43].xValid;
xRoomOccupied := aValues[48].wRaw<>0;
xDI1 := aValues[54].wRaw<>0;
xDI2 := aValues[55].wRaw<>0;
IF xUpdate AND xSuccess THEN
    IF uiRegisterIndex=56 THEN uliDI1CountSinceStart:=uliDI1CountSinceStart+WORD_TO_ULINT(wRaw); END_IF
    IF uiRegisterIndex=57 THEN uliDI2CountSinceStart:=uliDI2CountSinceStart+WORD_TO_ULINT(wRaw); END_IF
END_IF
// Temperature offset depends on the documented Poti-Zuordnung coil.
IF aValues[82].wRaw<>0 THEN
    aValues[44].xNumericValid:=FALSE;
    aValues[10].xNumericValid:=FALSE;
    aValues[11].xNumericValid:=FALSE;
END_IF
