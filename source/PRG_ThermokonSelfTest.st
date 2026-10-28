PROGRAM PRG_ThermokonSelfTest
VAR
    xDone : BOOL;
    xPassed : BOOL;
    uiChecks : UINT;
    d : FB_Thermokon_Device;
END_VAR

IF NOT xDone THEN
    xPassed:=TRUE;
    d(bSlaveId:=1,xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,wDeviceCode:=3,wFirmware:=16#0012,wDeviceType:=0,udiNowMs:=100,xUpdate:=FALSE);
    xPassed:=xPassed AND d.xThermokonConfirmed AND d.xOnline; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=FALSE,xUpdate:=TRUE,xSuccess:=TRUE,uiRegisterIndex:=43,wRaw:=16#FFE7,udiNowMs:=200);
    xPassed:=xPassed AND d.xTemperatureValid AND (ABS(d.rRoomTemperature-(-2.5))<0.001); uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,xUpdate:=FALSE,wDeviceCode:=3,wDeviceType:=0,udiNowMs:=205);
    xPassed:=xPassed AND d.xTemperatureValid; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=FALSE,xUpdate:=TRUE);
    d(uiRegisterIndex:=49,wRaw:=1023,udiNowMs:=210);
    xPassed:=xPassed AND (ABS(d.rHeatingPercent-100.0)<0.001); uiChecks:=uiChecks+1;
    d(uiRegisterIndex:=52,wRaw:=500,udiNowMs:=220);
    xPassed:=xPassed AND (ABS(d.rAO1Volts-5.0)<0.001); uiChecks:=uiChecks+1;
    d(uiRegisterIndex:=39,wRaw:=16#FFFF,udiNowMs:=230);
    xPassed:=xPassed AND d.aValues[39].xSpecial AND NOT d.aValues[39].xNumericValid; uiChecks:=uiChecks+1;
    d(uiRegisterIndex:=65,wRaw:=1001,udiNowMs:=240);
    xPassed:=xPassed AND d.aValues[65].xSpecial; uiChecks:=uiChecks+1;
    d(uiRegisterIndex:=56,wRaw:=5,udiNowMs:=250);
    d(wRaw:=7,udiNowMs:=260);
    xPassed:=xPassed AND (d.uliDI1CountSinceStart=12); uiChecks:=uiChecks+1;
    d(xSuccess:=FALSE,wException:=2,uiRegisterIndex:=68,udiNowMs:=270);
    xPassed:=xPassed AND d.aValues[68].xUnsupportedByDevice AND d.xOnline; uiChecks:=uiChecks+1;
    d(xUpdate:=FALSE,udiNowMs:=121000);
    xPassed:=xPassed AND NOT d.xOnline AND NOT d.xTemperatureValid; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,wDeviceCode:=7,wDeviceType:=0,udiNowMs:=122000);
    xPassed:=xPassed AND NOT d.xThermokonConfirmed AND d.xOtherDevice; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,wDeviceCode:=3,wDeviceType:=0,udiNowMs:=123000);
    xPassed:=xPassed AND d.xThermokonConfirmed; uiChecks:=uiChecks+1;
    xDone:=TRUE;
END_IF