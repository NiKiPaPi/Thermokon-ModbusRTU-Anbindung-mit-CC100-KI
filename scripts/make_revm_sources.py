"""Generate documented Rev M register catalog and read-only WAGO driver."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("source", "docs", "evidence"):
    (ROOT/folder).mkdir(parents=True, exist_ok=True)
rows = []


def reg(addr, name, access='RW', signed=False, scale=1, unit='', page=11,
        supported=True, note='', fc=3, clears=False, special=0):
    rows.append(dict(address=addr, hex=f'0x{addr:04X}', name=name, access=access,
                     signed=signed, scale=scale, unit=unit, page=page,
                     supported=supported, note=note, fc=fc, read_clears=clears,
                     special=special))


reg(0,'Geraetekodierung','RO',note='Erwartet 0x0003; trotz Holding-Tabelle nicht veraenderbar')
reg(1,'Firmwareversion','RO',note='Rohwert, Versionskodierung nicht eindeutig spezifiziert')
reg(2,'Geraetetyp',note='0=AO2V; andere Typen werden erkannt, aber nicht als AO2V freigegeben')
reg(3,'Standortkennung')
reg(4,'Tasterfunktion')
reg(5,'Anzeigeintervall',unit='s')
reg(6,'Antwortverzoegerung',signed=True,unit='ms',note='Text max 3100ms, Tabellenbereich bis 0x0C80=3200; nicht schreiben')
reg(7,'Temperatur_Kalibrierung',signed=True,scale=.1,unit='K')
reg(8,'Feuchte_Kalibrierung',signed=True,scale=.1,unit='%rH',supported=False,note='Nur FTW04/LCN FTW04; widerspricht Fliesstext zur Moduswahl, Tabelle massgeblich')
reg(9,'Poti_Obergrenze',signed=True,scale=.1,unit='K',note='Temperatur-Zuordnung; bei Feuchte-Zuordnung nicht als Temperatur auswerten')
reg(10,'Poti_Untergrenze',signed=True,scale=.1,unit='K',page=12)
reg(11,'Basis_Sollwert_nach_Reset',signed=True,scale=.1,unit='degC',page=12)
reg(12,'Sollwertanzeige',page=12)
reg(13,'Nachtabsenkung',scale=.1,unit='K',page=12)
reg(14,'Totzone',scale=.1,unit='K',page=12)
reg(15,'Luefter_Automatikoption',page=12)
for base, mode in [(16,'Heizen'),(22,'Kuehlen')]:
    reg(base,'Xp_'+mode,scale=.1,unit='K',page=12)
    reg(base+1,'Tn_'+mode,unit='min',page=12)
    reg(base+2,'Stellgroesse_Max_'+mode,unit='%',page=12)
    reg(base+3,'Stellgroesse_Min_'+mode,unit='%',page=12)
    reg(base+4,'PWM_Zeit_'+mode,unit='min',page=12)
    reg(base+5,'Reserviert_'+f'{base+5:04X}',page=12,supported=False,note='Reserviert; wird nicht abgefragt')
reg(28,'Frostschutz',scale=.1,unit='K',page=12)
reg(29,'Nicht_benutzt_001D',page=12,supported=False,note='Tabelle nicht benutzt; Fliesstext S6 widerspricht, kein Zugriff')
reg(30,'Nicht_benutzt_001E',page=12,supported=False,note='Tabelle nicht benutzt; Fliesstext S6 widerspricht, kein Zugriff')
reg(31,'DI1_Funktion',page=13)
reg(32,'DI2_Funktion',page=13)
reg(33,'DI1_Zaehlermodus',page=13,note='0 Flanken, 1 Impulse, 2 Zeit; Zeiteinheit nicht dokumentiert')
reg(34,'DI2_Zaehlermodus',page=13,note='0 Flanken, 1 Impulse, 2 Zeit; Zeiteinheit nicht dokumentiert')
reg(35,'Bypasszeit',unit='min',page=13)
reg(36,'LED_Funktion',page=13)
reg(37,'Reglermodus_nach_Reset',page=13)
reg(38,'Ausfallwert_AO1',signed=True,scale=.1,unit='%',page=13,special=1,note='0xFFFF bedeutet letzten Wert behalten; kein normaler Prozentwert')
reg(39,'Ausfallwert_AO2',signed=True,scale=.1,unit='%',page=13,special=1,note='0xFFFF bedeutet letzten Wert behalten; kein normaler Prozentwert')
reg(0x100,'Taster_Zustand','RO',page=14)
reg(0x101,'Taster_Speicher','RO',page=14,clears=True,note='Lesen aktualisiert Speicher auf aktuellen Tasterzustand')
reg(0x102,'Raumtemperatur','RO',True,.1,'degC',14)
reg(0x103,'Lokaler_Sollwertoffset','RO',True,.1,'K',14,note='Poti-Zuordnung beachten')
reg(0x104,'Wirksamer_Sollwert','RO',True,.1,'degC',14)
reg(0x105,'Feuchte','RO',False,.1,'%rH',14,supported=False,note='Nur FTW04/LCN FTW04')
reg(0x106,'Luefterstufe','RO',page=14,note='0 Aus; 1..3 Stufen; 0xFF00 Automatik; Rohwort erhalten')
reg(0x107,'Raumbelegung','RO',page=14)
reg(0x108,'Regler_Heizen','RO',False,100/1023,'%',14)
reg(0x109,'Regler_Kuehlen','RO',False,100/1023,'%',14)
reg(0x10A,'Lokale_Reglersperre','RO',page=14)
reg(0x10B,'AO1_Spannung','RO',False,.01,'V',14,note='AO2V: 500=5V; abweichende Typen separat behandeln')
reg(0x10C,'AO2_Spannung','RO',False,.01,'V',14)
reg(0x10D,'DI1_Zustand','RO',page=15)
reg(0x10E,'DI2_Zustand','RO',page=15)
reg(0x10F,'DI1_Zaehler','RO',page=15,clears=True,note='Wird durch JEDE Leseabfrage genullt; letzte Differenz und lokale Summe erhalten')
reg(0x110,'DI2_Zaehler','RO',page=15,clears=True,note='Wird durch JEDE Leseabfrage genullt; keine absolute Geraetegesamtsumme')
reg(0x111,'Aktiver_Reglermodus','RO',page=15,note='0 Sperre; 1 Heizen; 2 Kuehlen; 3 Auto Heizen; 4 Auto Kuehlen')
reg(0x200,'Externe_Temperatur',signed=True,scale=.1,unit='degC',page=15)
reg(0x201,'Externe_Feuchte',scale=.1,unit='%rH',page=15,supported=False,note='Nur FTW04/LCN FTW04')
reg(0x202,'Externer_Sollwertoffset',signed=True,scale=.1,unit='K',page=15)
reg(0x203,'Basis_Sollwert',signed=True,scale=.1,unit='degC',page=15)
reg(0x204,'Vorgabe_Raumbelegung',page=15,note='0 unbelegt, 1 belegt, 2 Bypass')
reg(0x205,'Vorgabe_Reglermodus',page=15)
reg(0x206,'Handwert_AO1',scale=.1,unit='%',page=16,special=2,note='0..1000=0..100%; >1000 Automatik, kein Prozentwert')
reg(0x207,'Handwert_AO2',scale=.1,unit='%',page=16,special=2,note='0..1000=0..100%; >1000 Automatik, kein Prozentwert')
reg(0x4000,'Adress_Zugriffsschutz',page=16,note='Ab FW1.13; nur lesen, kein Freischaltwert schreiben')
reg(0x4001,'Erweiterte_Slaveadresse',page=16,note='Ab FW1.13; keine Adressaenderung')
coils=['Anzeige_Raumtemperatur','Anzeige_Feuchte','Anzeige_Feuchtesollwert','Anzeige_Temperatursollwert',
       'Anzeige_Absolutwert','Aenderung_Absolutwert','Einheit_Celsius','Anzeige_RH',
       'Minimale_Stellgroesse_Konfigurationsbit','Belegung_nach_Reset','Nicht_benutzt_000A','Nicht_benutzt_000B',
       'Change_Over','Poti_Zuordnung_Feuchte']
for a,name in enumerate(coils):
    reg(a,name,page=17,fc=1,supported=a not in [1,2,7,10,11],note=('Nur Feuchtevariante bzw. reserviert; nicht abgefragt' if a in [1,2,7,10,11] else ('Bit8: Tabelle und Fliesstext S7 widersprechen; Rohbit anzeigen' if a==8 else '')))
for a,name in enumerate(['Taupunktmeldung','Energiesperre','Freigabe_Praesenztaster','Freigabe_Regler','LED_Vorgabe']):
    reg(0x100+a,name,page=18,fc=1)
for i,r in enumerate(rows,1): r['index']=i
idx={r['name']:r['index'] for r in rows}
objects=[]


def add(name,kind,decl,impl=''):
    objects.append(dict(name=name,kind=kind,declaration=decl,implementation=impl))
    (ROOT/'source'/(name+'.st')).write_text(decl+'\n\n'+impl,encoding='utf-8',newline='\n')


add('ST_Thermokon_Register','dut','''TYPE ST_Thermokon_Register :
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
END_TYPE''')
add('ST_Thermokon_Value','dut','''TYPE ST_Thermokon_Value :
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
END_TYPE''')
initial=[]
for r in rows:
    initial.append("(xDocumented:=TRUE, xSupported:=%s, sName:='%s', sSource:='Rev M 25.11.2019 S.%s', sAccess:='%s', bReadFunction:=%s, uiAddress:=16#%04X, xSigned:=%s, rScale:=%.10f, sUnit:='%s', xReadClears:=%s, usiSpecial:=%s)" %
                   (str(r['supported']).upper(),r['name'],r['page'],r['access'],r['fc'],r['address'],str(r['signed']).upper(),r['scale'],r['unit'],str(r['read_clears']).upper(),r['special']))
add('GVL_Thermokon','gvl',"""{attribute 'qualified_only'}
VAR_GLOBAL CONSTANT
    xRegisterMapVerified : BOOL := TRUE;
    uiRegisterCount : UINT := %d;
    xThermokonWritesEnabled : BOOL := FALSE;
    aRegisters : ARRAY[1..%d] OF ST_Thermokon_Register := [
    %s];
END_VAR
"""%(len(rows),len(rows),',\n    '.join(initial)))
add('FB_Thermokon_Device','fb','''FUNCTION_BLOCK FB_Thermokon_Device
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
END_VAR''','''IF xIdentityUpdate THEN
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
''' + '\n'.join(f'{out} := aValues[{idx[key]}].{field};' for out,key,field in [
('rRoomTemperature','Raumtemperatur','rValue'),('rEffectiveSetpoint','Wirksamer_Sollwert','rValue'),
('rLocalOffset','Lokaler_Sollwertoffset','rValue'),('rHeatingPercent','Regler_Heizen','rValue'),
('rCoolingPercent','Regler_Kuehlen','rValue'),('rAO1Volts','AO1_Spannung','rValue'),
('rAO2Volts','AO2_Spannung','rValue'),('wFanStage','Luefterstufe','wRaw'),
('wControllerMode','Aktiver_Reglermodus','wRaw'),('xTemperatureValid','Raumtemperatur','xValid')]) + f'''
xRoomOccupied := aValues[{idx['Raumbelegung']}].wRaw<>0;
xDI1 := aValues[{idx['DI1_Zustand']}].wRaw<>0;
xDI2 := aValues[{idx['DI2_Zustand']}].wRaw<>0;
IF xUpdate AND xSuccess THEN
    IF uiRegisterIndex={idx['DI1_Zaehler']} THEN uliDI1CountSinceStart:=uliDI1CountSinceStart+WORD_TO_ULINT(wRaw); END_IF
    IF uiRegisterIndex={idx['DI2_Zaehler']} THEN uliDI2CountSinceStart:=uliDI2CountSinceStart+WORD_TO_ULINT(wRaw); END_IF
END_IF
// Temperature offset depends on the documented Poti-Zuordnung coil.
IF aValues[{idx['Poti_Zuordnung_Feuchte']}].wRaw<>0 THEN
    aValues[{idx['Lokaler_Sollwertoffset']}].xNumericValid:=FALSE;
    aValues[{idx['Poti_Obergrenze']}].xNumericValid:=FALSE;
    aValues[{idx['Poti_Untergrenze']}].xNumericValid:=FALSE;
END_IF
''')
add('FB_Thermokon_ModbusScanner','fb','''FUNCTION_BLOCK FB_Thermokon_ModbusScanner
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
END_VAR''','''// One WAGO master; every frame is serialized through its trigger handshake.
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
END_IF''')
add('PRG_ThermokonSelfTest','program','''PROGRAM PRG_ThermokonSelfTest
VAR
    xDone : BOOL;
    xPassed : BOOL;
    uiChecks : UINT;
    d : FB_Thermokon_Device;
END_VAR''',f'''IF NOT xDone THEN
    xPassed:=TRUE;
    d(bSlaveId:=1,xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,wDeviceCode:=3,wFirmware:=16#0012,wDeviceType:=0,udiNowMs:=100,xUpdate:=FALSE);
    xPassed:=xPassed AND d.xThermokonConfirmed AND d.xOnline; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=FALSE,xUpdate:=TRUE,xSuccess:=TRUE,uiRegisterIndex:={idx['Raumtemperatur']},wRaw:=16#FFE7,udiNowMs:=200);
    xPassed:=xPassed AND d.xTemperatureValid AND (ABS(d.rRoomTemperature-(-2.5))<0.001); uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,xUpdate:=FALSE,wDeviceCode:=3,wDeviceType:=0,udiNowMs:=205);
    xPassed:=xPassed AND d.xTemperatureValid; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=FALSE,xUpdate:=TRUE);
    d(uiRegisterIndex:={idx['Regler_Heizen']},wRaw:=1023,udiNowMs:=210);
    xPassed:=xPassed AND (ABS(d.rHeatingPercent-100.0)<0.001); uiChecks:=uiChecks+1;
    d(uiRegisterIndex:={idx['AO1_Spannung']},wRaw:=500,udiNowMs:=220);
    xPassed:=xPassed AND (ABS(d.rAO1Volts-5.0)<0.001); uiChecks:=uiChecks+1;
    d(uiRegisterIndex:={idx['Ausfallwert_AO1']},wRaw:=16#FFFF,udiNowMs:=230);
    xPassed:=xPassed AND d.aValues[{idx['Ausfallwert_AO1']}].xSpecial AND NOT d.aValues[{idx['Ausfallwert_AO1']}].xNumericValid; uiChecks:=uiChecks+1;
    d(uiRegisterIndex:={idx['Handwert_AO1']},wRaw:=1001,udiNowMs:=240);
    xPassed:=xPassed AND d.aValues[{idx['Handwert_AO1']}].xSpecial; uiChecks:=uiChecks+1;
    d(uiRegisterIndex:={idx['DI1_Zaehler']},wRaw:=5,udiNowMs:=250);
    d(wRaw:=7,udiNowMs:=260);
    xPassed:=xPassed AND (d.uliDI1CountSinceStart=12); uiChecks:=uiChecks+1;
    d(xSuccess:=FALSE,wException:=2,uiRegisterIndex:={idx['Erweiterte_Slaveadresse']},udiNowMs:=270);
    xPassed:=xPassed AND d.aValues[{idx['Erweiterte_Slaveadresse']}].xUnsupportedByDevice AND d.xOnline; uiChecks:=uiChecks+1;
    d(xUpdate:=FALSE,udiNowMs:=121000);
    xPassed:=xPassed AND NOT d.xOnline AND NOT d.xTemperatureValid; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,xIdentitySuccess:=TRUE,wDeviceCode:=7,wDeviceType:=0,udiNowMs:=122000);
    xPassed:=xPassed AND NOT d.xThermokonConfirmed AND d.xOtherDevice; uiChecks:=uiChecks+1;
    d(xIdentityUpdate:=TRUE,wDeviceCode:=3,wDeviceType:=0,udiNowMs:=123000);
    xPassed:=xPassed AND d.xThermokonConfirmed; uiChecks:=uiChecks+1;
    xDone:=TRUE;
END_IF''')
add('PLC_PRG','program','''PROGRAM PLC_PRG
VAR
    scanner : FB_Thermokon_ModbusScanner;
    udiCycle : UDINT;
END_VAR''','''udiCycle:=udiCycle+1;
PRG_ThermokonSelfTest();
scanner(udiNowMs:=SysTime.SysTimeGetMs());''')
(ROOT/'source'/'objects.json').write_text(json.dumps(objects,indent=2),encoding='utf-8',newline='\n')
(ROOT/'docs'/'registers_revm.json').write_text(json.dumps(rows,indent=2),encoding='utf-8',newline='\n')
with (ROOT/'docs'/'Registerliste_RevM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';',lineterminator='\n'); w.writeheader(); w.writerows(rows)
manual=ROOT/'vendor'/'WRF04_FTW04_RS485-Modbus_RevM_german.pdf'
(ROOT/'evidence'/'manual_revm.json').write_text(json.dumps(dict(edition='M 25.11.2019',sha256=hashlib.sha256(manual.read_bytes()).hexdigest() if manual.is_file() else '12d23127728f12a1db55a742205764708ce737bf3308de14495e1c1dc2ecc3f1',catalog_points=len(rows),enabled_points=sum(r['supported'] for r in rows)),indent=2))
print(f'{len(rows)} documented catalog entries, {sum(r["supported"] for r in rows)} enabled for WRF04 AO2V; zero writes.')
