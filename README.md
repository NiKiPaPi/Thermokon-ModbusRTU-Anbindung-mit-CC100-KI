# Thermokon-ModbusRTU Anbindung mit CC100 + KI

Lesbare CODESYS-V3.5-Quellen für die Modbus-RTU-Anbindung eines Thermokon WRF04 P AO2V an einen WAGO CC100 (751-9403). Dieses Paket ermöglicht die lokale Neuerstellung des Geräteprojekts. Es enthält kein Controller-, Betriebssystem- oder Laufzeitdatenbackup.

## Funktion

- Eine serielle WAGO-Masterinstanz bedient RS485 COM1 sequenziell mit 9600 Baud, 8 Datenbits, gerader Parität und einem Stoppbit.
- Automatische Suche der Slave-IDs 1–12; AO2V-Profilprüfung über Gerätekodierung 3 und Typ 0. Andere Geräte werden nicht als AO2V freigegeben.
- 87 dokumentierte Katalogeinträge; 75 Abfragen für das WRF04-AO2V-Profil. Reservierte und reine FTW04-Feuchtefunktionen bleiben ausgeschlossen.
- RO/RW-Kennzeichnung je Datenpunkt; auch RW wird ausschließlich gelesen. Keine Modbus-Schreibfunktion im Anwendercode.
- Messwerte, Betriebszustände, Rohwerte, Skalierungen, Gültigkeit, Zeitstempel und Fehler je Gerät und Datenpunkt. Wiederholungsprüfung ausgefallener Teilnehmer.
- Lokale, nicht persistente Summen der beim Lesen zurückgesetzten Eingangszähler.

Der Gerätescanner ist kein kryptographischer Herstellernachweis. Mehrere Teilnehmer mit derselben Adresse können nicht getrennt erkannt werden. Siehe docs/Inbetriebnahme_RevM.md für Frischezeiten, Sonderwerte und Widersprüche des Handbuchs.

## Voraussetzungen

Die historische Inbetriebnahme verwendete CODESYS 3.5.21.50, WAGO-Gerätebeschreibung 6.4.6.11 für 751-9403/FW31 sowie WagoAppPlcModbus 1.1.5.13, WagoTypesCom 1.6.2.3 und SysTime 3.5.17.0. Die WAGO-/Systemabhängigkeiten müssen separat passend installiert sein. Sie werden aus diesem Paket nicht installiert oder mitgeliefert. Eine andere Firmware-/Engineering-Kombination ist vor Nutzung zu prüfen.

Für Katalogtests und Quellgenerierung genügt Python 3.12 mit Standardbibliothek. Die Projekterstellung läuft dagegen in der installierten CODESYS-ScriptEngine (IronPython), nicht mit normalem Python.

## Tests und Projekterstellung

```powershell
python -m unittest discover -s tests -v
# Optional: Katalog und ST-Quellen aus den dokumentierten Angaben neu erzeugen.
python scripts/make_revm_sources.py
```

Die Hersteller-PDF ist für diese Quellgenerierung nicht erforderlich; ihr dokumentierter SHA-256 steht unter docs/HERSTELLERQUELLEN.md. Der Generator prüft ohne lokale PDF nicht erneut die Herstellerangaben.

In einer frischen Arbeitskopie in CODESYS unter „Tools → Skripting → Skriptdatei ausführen“ scripts/rebuild_project.py auswählen. Alternativ:

```powershell
$env:RBG_PROJECT_ROOT = (Get-Location).Path
& '<CODESYS-INSTALLATION>/CODESYS/Common/CODESYS.exe' '--Profile=CODESYS V3.5 SP21 Patch 5' '--noUI' "--runscript=$env:RBG_PROJECT_ROOT/scripts/rebuild_project.py"
```

Das Skript erzeugt RBG_WAGO_CC100_ModbusRTU.project, importiert alle sieben ST-Objekte, richtet eine zyklische 10-ms-Task ein und erzeugt Code. Ein vorhandenes Projekt wird nicht überschrieben. Das lokale Ergebnis steht unter evidence/offline_rebuild.json. Bei einem Fehler bleibt das Ergebnis ausdrücklich ungeprüft. Es erfolgen keine Geräteverbindung, kein Login, kein Download und kein Start.

## Sichere Inbetriebnahme

IP-Adresse, Benutzer und Passwort ausschließlich lokal konfigurieren. Dieses Paket enthält keine tatsächlichen Zugangsdaten und keine voreingestellte Ziel-IP. Nach Prüfung von Zielidentität, Sicherung und Autorisierung können Download, Start und Boot-Erstellung gezielt in CODESYS erfolgen. Die frühere Freigabe einer konkreten Inbetriebnahme gilt nicht für weitere Geräteänderungen.

Die beiden Eingangszähler und der Tastenspeicher haben Lese-Nebenwirkungen. Nicht als unverändernde passive Messung behandeln. Gültigkeitsfelder und Sonderwertkennzeichen bei der Anzeige immer berücksichtigen.

## Struktur

- source/: sieben ST-Objekte und objects.json für den Import.
- scripts/: offline Projekterstellung und Kataloggenerator.
- docs/: Registerkatalog, Betriebsbeschreibung, Quellen, Wiederherstellung und Prüfgrenzen.
- tests/: fünf Katalogprüfungen; zwölf ST-Selbstprüfungen stehen in source/PRG_ThermokonSelfTest.st.

## Belegter Stand und Grenzen

Die lokalen Aufzeichnungen vom 18.10.2026 beschreiben eine erfolgreiche Inbetriebnahme mit einem realen AO2V-Teilnehmer: 73 gültige Antworten von 75 abgefragten Punkten; die Adressregister 0x4000/0x4001 lieferten Modbus-Ausnahme 2. Download, Boot-Erstellung sowie Warm-Reset mit anschließendem kontrolliertem Start wurden damals geprüft. Es handelt sich um historische Ergebnisse, keine Live-Verifikation vom Tag der GitHub-Vorbereitung.

Kein physischer Stromausfall, vollständiger Betriebssystem-Neustart oder realer Betrieb mit zwölf gleichzeitig vorhandenen Teilnehmern ist nachgewiesen. Das Paket ersetzt keine lokale Geräte- oder Datensicherung. Native Projektdateien und das vollständige Projektarchiv bleiben außerhalb des Uploads, weil proprietäre Binärmetadaten nicht vollständig geprüft und eingebettete Abhängigkeiten nicht mitveröffentlicht werden. Die lesbaren Quellen und das geprüfte Wiederaufbauverfahren bilden den externen Sicherungsumfang.

Für diesen Quellstand wurde keine neue Benutzerabnahme als stabile Version erteilt. Ohne ausdrückliche Klärung der Rechte wird keine Open-Source-Lizenz zugesichert. Herstellerbibliotheken und Handbücher unterliegen ihren jeweiligen Rechten.
