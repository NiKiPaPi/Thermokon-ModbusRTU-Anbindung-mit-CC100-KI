FUNCTION_BLOCK FB_Thermokon_ModbusScanner
VAR_INPUT
    xEnable : BOOL := TRUE;
    udiNowMs : UDINT;
    tPollInterval : TIME := T#5s;
    tOfflineRetry : TIME := T#60s;
    tTimeout : TIME := T#4s; // Covers documented delay up to 3100/3200 ms
END_VAR
VAR_OUTPUT
    xBusConnected : BOOL;
    xBusError : BOOL;
    sBusStatus : STRING;
    bCurrentSlaveId : BYTE := 1;
    uiOnlineCount : UINT;
    uiThermokonCount : UINT;
    uiEverSeenCount : UINT;
    aDetectedIds : ARRAY[1..12] OF BYTE; // Historical confirmed AO2V IDs
    aDevices : ARRAY[1..12] OF FB_Thermokon_Device;
    udiRequests : UDINT;
    udiCompletedSweeps : UDINT;
    uiCurrentRegisterIndex : UINT;
    udiTimeouts : UDINT;
END_VAR
VAR
    master : WagoAppPlcModbus.FbMbMasterSerial;
    query : WagoAppPlcModbus.typMbQuery;
    response : WagoAppPlcModbus.typMbResponse;
    xTrigger : BOOL;
    xWaiting : BOOL;
    xUpdate : BOOL;
    xIdentityUpdate : BOOL;
    xSuccess : BOOL;
    xAdvance : BOOL;
    xProbe : BOOL := TRUE;
    uiIndex : UINT := 1;
    i : UINT;
    wRaw : WORD;
    wException : WORD;
    aLastPollMs : ARRAY[1..12] OF UDINT;
    aPolled : ARRAY[1..12] OF BOOL;
    udiGapStartMs : UDINT;
    udiRequiredIntervalMs : UDINT;
    xHasSent : BOOL;
END_VAR

// One WAGO master; every frame is serialized through its trigger handshake.
master(xConnect := xEnable OR xWaiting,
    I_Port := IoConfig_Globals.COM1,
    udiBaudrate := 9600, usiDataBits := 8,
    eParity := WagoTypesCom.eTTYParity.Even,
    eStopBits := WagoTypesCom.eTTYStopBits.One,
    eHandshake := WagoTypesCom.eTTYHandshake.None,
    ePhysical := WagoTypesCom.eTTYPhysicalLayer.RS485_HalfDuplex,
    eFrameType := WagoAppPlcModbus.eMbFrameType.RTU,
    tTimeOut := tTimeout, utQuery := query, xTrigger := xTrigger, utResponse := response);
xBusConnected := master.xIsConnected;
xBusError := master.xError;
sBusStatus := master.oStatus.GetDescription();
xUpdate:=FALSE; xIdentityUpdate:=FALSE; xAdvance:=FALSE;
IF xWaiting AND NOT xTrigger THEN
    xWaiting:=FALSE;
    xSuccess := NOT master.xError AND (response.wError=0)
        AND (response.bUnitId=bCurrentSlaveId)
        AND (response.bFunctionCode=query.bFunctionCode)
        AND (response.uiQuantity=query.uiReadQuantity);
    wException:=response.wError;
    IF xSuccess THEN wRaw:=response.awData[0]; END_IF
    IF NOT xSuccess AND (wException=0) THEN udiTimeouts:=udiTimeouts+1; END_IF
    udiGapStartMs:=udiNowMs;
    IF xProbe THEN xIdentityUpdate:=TRUE; ELSE xUpdate:=TRUE; END_IF
END_IF
uiOnlineCount:=0; uiThermokonCount:=0; uiEverSeenCount:=0;
FOR i:=1 TO 12 DO
    aDevices[i](bSlaveId:=UINT_TO_BYTE(i),
        xIdentityUpdate:=xIdentityUpdate AND (i=bCurrentSlaveId),
        xIdentitySuccess:=xSuccess, wDeviceCode:=response.awData[0],
        wFirmware:=response.awData[1], wDeviceType:=response.awData[2],
        xUpdate:=xUpdate AND (i=bCurrentSlaveId), xSuccess:=xSuccess,
        uiRegisterIndex:=uiIndex, wRaw:=wRaw, wException:=wException, udiNowMs:=udiNowMs);
    IF aDevices[i].xOnline THEN uiOnlineCount:=uiOnlineCount+1; END_IF
    IF aDevices[i].xOnline AND aDevices[i].xThermokonConfirmed THEN uiThermokonCount:=uiThermokonCount+1; END_IF
    IF aDevices[i].xEverSeen THEN uiEverSeenCount:=uiEverSeenCount+1; END_IF
    IF aDevices[i].xThermokonConfirmed THEN aDetectedIds[i]:=UINT_TO_BYTE(i); END_IF
END_FOR
IF xIdentityUpdate THEN
    IF xSuccess AND aDevices[bCurrentSlaveId].xThermokonConfirmed THEN
        xProbe:=FALSE; uiIndex:=1;
    ELSE xAdvance:=TRUE; END_IF
END_IF
IF xUpdate THEN
    IF NOT xSuccess AND (wException=0) THEN xAdvance:=TRUE;
    ELSE uiIndex:=uiIndex+1; END_IF
END_IF
IF NOT xProbe THEN
    // Never query unsupported humidity/reserved points. No address gaps read implicitly.
    WHILE uiIndex<=GVL_Thermokon.uiRegisterCount DO
        IF GVL_Thermokon.aRegisters[uiIndex].xSupported THEN EXIT; END_IF
        uiIndex:=uiIndex+1;
    END_WHILE
    IF uiIndex>GVL_Thermokon.uiRegisterCount THEN
        xAdvance:=TRUE; udiCompletedSweeps:=udiCompletedSweeps+1;
    END_IF
END_IF
IF xAdvance THEN
    aLastPollMs[bCurrentSlaveId]:=udiNowMs;
    aPolled[bCurrentSlaveId]:=TRUE;
    bCurrentSlaveId:=bCurrentSlaveId+1;
    IF bCurrentSlaveId>12 THEN bCurrentSlaveId:=1; END_IF
    xProbe:=TRUE; uiIndex:=1;
END_IF
uiCurrentRegisterIndex:=uiIndex;
IF xEnable AND xBusConnected AND NOT xWaiting
    AND (NOT xHasSent OR ((udiNowMs-udiGapStartMs)>=20)) THEN
    udiRequiredIntervalMs:=TIME_TO_UDINT(tOfflineRetry);
    IF aDevices[bCurrentSlaveId].xOnline AND aDevices[bCurrentSlaveId].xThermokonConfirmed THEN
        udiRequiredIntervalMs:=TIME_TO_UDINT(tPollInterval);
    END_IF
    IF NOT xProbe OR NOT aPolled[bCurrentSlaveId]
        OR ((udiNowMs-aLastPollMs[bCurrentSlaveId])>=udiRequiredIntervalMs) THEN
        query.bUnitId:=bCurrentSlaveId;
        IF xProbe THEN
            query.bFunctionCode:=3; query.uiReadAddress:=0; query.uiReadQuantity:=3;
        ELSE
            query.bFunctionCode:=GVL_Thermokon.aRegisters[uiIndex].bReadFunction;
            query.uiReadAddress:=GVL_Thermokon.aRegisters[uiIndex].uiAddress;
            query.uiReadQuantity:=1;
        END_IF
        query.uiWriteQuantity:=0; // ALL RO/RW points only read; no write code paths
        response.wError:=0; response.bUnitId:=0; response.bFunctionCode:=0;
        xTrigger:=TRUE; xWaiting:=TRUE; xHasSent:=TRUE;
        udiRequests:=udiRequests+1;
    ELSE
        bCurrentSlaveId:=bCurrentSlaveId+1;
        IF bCurrentSlaveId>12 THEN bCurrentSlaveId:=1; END_IF
    END_IF
END_IF