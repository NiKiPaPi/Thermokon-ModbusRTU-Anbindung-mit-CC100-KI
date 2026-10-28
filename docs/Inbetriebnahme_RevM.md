# Inbetriebnahme WRF04 P AO2V, Revision M

## Umfang und Quellen

Eigenstaendiges CODESYS-V3.5-Projekt fuer CC100 751-9403, Ziel <CC100-IP>, Geraetebeschreibung 6.4.6.11 (FW31). Keine Uebernahme einer bisherigen SPS-Applikation. Thermokon-Quelle: `vendor/WRF04_FTW04_RS485-Modbus_RevM_german.pdf`, Revision M, 25.11.2019; Registerseiten gedruckt 11-18, PDF-Seiten 12-19. Dateihash und Katalogumfang stehen in `evidence/manual_revm.json`.

`Registerliste_RevM.csv` und `registers_revm.json` enthalten Adressbasis, FC, Namen, Zugriff RO/RW, Vorzeichen, Skalierung, Einheit, Quellseite, Lese-Nebenwirkungen und Hinweise je Datenpunkt. `GVL_Thermokon.aRegisters` bildet dieselben Metadaten in der SPS ab. Firmware wird bewusst als Rohwort dargestellt: eine eindeutige Versionskodierung ist im Handbuch nicht beschrieben.

## Serielle Kommunikation

- WAGO COM1: RS485 Halbduplex, RTU, 9600 Baud, 8 Datenbits, gerade Paritaet, ein Stoppbit.
- Bibliotheken: WagoAppPlcModbus 1.1.5.13, WagoTypesCom 1.6.2.3, SysTime 3.5.17.0; weitere Systemabhaengigkeiten aus der FW31-Geraetebeschreibung.
- Eine einzige Instanz `FbMbMasterSerial` fuer den gesamten Bus. Zyklische Task 10 ms; Modbus-Anfragen sind nicht blockierend.
- Timeout 4 s, damit die dokumentierte konfigurierbare Antwortverzoegerung bis 3100/3200 ms beruecksichtigt wird. Pause nach jeder Antwort mindestens 20 ms; Herstellerminimum bei 9600 Baud 4 ms.
- Alle IDs 1-12 werden einzeln geprueft. Identitaetsprobe FC03, Adresse 0, drei Woerter: Code 3 und Typ 0 kennzeichnen das dokumentierte AO2V-Profil. Andere Antwortgeraete werden als solche ausgewiesen und nicht als AO2V zyklisch abgefragt. Das ist eine Profilpruefung, kein kryptographischer Herstellernachweis.
- Wortregister werden mit FC03 gelesen. Das Handbuch erlaubt FC03 und FC04 und zeigt FC03 auch fuer die Eingabedaten. Coils werden mit FC01 einzeln gelesen. Maximal drei Register bzw. ein Coil je Telegramm; Herstellergrenzen 20 Register bzw. 16 Coils im RTU-Modus werden eingehalten.
- Komplettabfrage pro erreichbarem AO2V, danach mindestens 5 s bis zur naechsten Abfrage dieses Geraets. Offline/abweichende Geraete werden nach mindestens 60 s neu geprueft. Anfaengliche Timeouts der anderen elf IDs koennen zusammen etwa 44 s benoetigen. Die Zeiten sind keine feste garantierte Abtastrate.

## Daten und Qualitaet

`PLC_PRG.scanner.aDevices[1..12]` enthaelt Identitaet, Online-Status, Fehlerzaehler, Rohdaten und Messwerte. Der Arrayindex entspricht der Slave-ID. `aDetectedIds` speichert bereits bestaetigte IDs auch bei spaeterem Ausfall; der aktuelle Online-Status ist separat zu beachten.

Jeder Datenpunkt unter `aValues[Katalogindex]` hat Rohwort, skalierten REAL-Wert, letzte gute monotone Laufzeit in Millisekunden, Fehlernummer und Gueltigkeit. Bei Kommunikationsausfall werden Werte als ungueltig gekennzeichnet; die letzten Zahlen bleiben zur Diagnose sichtbar. `xValid` und `xNumericValid` sind deshalb gemeinsam mit Zahlen auszuwerten. Nach 120 s ohne aktuelle Daten erfolgt ebenfalls eine Ungueltig-Kennzeichnung. Die Zeitstempel sind keine UTC-Zeit.

Die wichtigsten Werte sind zusaetzlich benannt: `rRoomTemperature`, `rEffectiveSetpoint`, `rLocalOffset`, `rHeatingPercent`, `rCoolingPercent`, `rAO1Volts`, `rAO2Volts`, `xRoomOccupied`, `xDI1`, `xDI2`, `wFanStage`, `wControllerMode`. Fuer diese Kurzfelder gelten die Gueltigkeiten der zugehoerigen Katalogeintraege. Die Feuchtewerte der FTW04-Varianten werden beim WRF04 nicht abgefragt.

Sonderwerte: Ausfallwert 0xFFFF bedeutet letzten Wert halten; Handwert >1000 bedeutet Automatik. Diese Werte werden mit `xSpecial=TRUE` und `xNumericValid=FALSE` markiert und nicht als normale Prozentzahl interpretiert. Bei Poti-Zuordnung Feuchte ist die Interpretation lokaler Offset-/Poti-Werte als Temperatur ungueltig.

Einzelne Modbus-Ausnahmen 1/2/3 markieren einen Punkt als vom Geraet nicht unterstuetzt. Der Scanner liest danach weitere Punkte; im naechsten Zyklus werden die Punkte erneut versucht. Transportfehler beenden die aktuelle Geraeteabfrage und fuehren zur erneuten Identitaetsprobe. `sBusStatus` zeigt die WAGO-Fehlerbeschreibung; der Zaehler `udiTimeouts` umfasst im aktuellen Stand allgemein fehlgeschlagene Transportantworten ohne Modbus-Ausnahme und ist nicht auf reine Zeitueberschreitungen beschraenkt.

## Besonderheiten des Handbuchs

- Register 0x0000 und 0x0001 sind trotz ihrer Einordnung in der Holding-Tabelle RO.
- 0x0101 aktualisiert beim Lesen den Tastenspeicher. 0x010F und 0x0110 werden bei JEDEM Lesen genullt. Die Anwendung liest sie wie beauftragt zyklisch. Lokale ULINT-Summen addieren empfangene Differenzen seit SPS-Programmstart und sind nicht persistent. Ein verlorenes Antworttelegramm kann zu nicht rekonstruierbaren Zaehlimpulsen fuehren. Bei Zaehlermodus Zeit nennt das Handbuch keine Einheit; daher wird keine Einheit erfunden.
- Fuer Coil 0x0008 widersprechen sich Fliesstext und Tabelle hinsichtlich der Wirkungsrichtung. Es wird nur das Rohbit mit neutralem Namen bereitgestellt.
- 0x001D/0x001E: Fliesstext nennt Startwerte, Registertabelle bezeichnet sie als nicht benutzt. Diese Adressen werden nicht abgefragt. Ebenso bleiben reservierte Register 0x0015/0x001B und Coils 0x000A/0x000B ausgeschlossen.
- Erweiterte Adressregister 0x4000/0x4001 sind ab Firmware 1.13 beschrieben. Es erfolgt nur ein Leseversuch; eine Ausnahme aelterer Firmware bleibt sichtbar. Kein Freischaltwert und keine Adressaenderung werden gesendet.
- Der herstellerspezifische Bereich 0xFF00-0xFFFF besitzt keine dokumentierte Einzelbelegung und wird nicht abgefragt.
- Mehrere physische Geraete mit derselben Slave-ID koennen nicht getrennt erkannt werden.

## Schreibsperre und physische I/O

RO/RW kennzeichnet die Herstellerberechtigung. Auch RW wird ausschliesslich gelesen. Im Projekt existiert kein Pfad fuer FC05, FC06, FC15, FC16, FC22 oder FC23. CC100-Ausgaenge werden von diesem Projekt nicht angesteuert. Die Aufgabe umfasst keine Aenderung der vorhandenen Verdrahtung oder Thermokon-Regelparameter.

## Sicherungsumfang und Wiederherstellung

Die GitHub-Vorbereitung enthält die lesbaren Quellen, Metadaten und eine lokale Projekterstellung. Gerätebackups, Betriebsdaten, Hersteller-PDFs, Bibliotheken, native Projektdateien und Projektarchive bleiben ausschließlich lokal. Die Ausschlüsse gelten auch für ein privates Repository.

Siehe WIEDERHERSTELLUNG.md und VALIDIERUNG.md. Vor einer Geräteübertragung das aktuelle Ziel, eine passende lokale Sicherung und die konkrete Autorisierung prüfen. Frühere Freigaben oder Testberichte sind keine Freigabe für einen neuen Download. Dieser Quellstand ist nicht als neue stabile Version abgenommen.
