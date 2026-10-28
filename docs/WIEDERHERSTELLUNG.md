# Wiederherstellung aus dem Quellpaket

1. Repository in einen neuen lokalen Ordner klonen. Vorhandene Projektarbeit nicht überschreiben.
2. Passende CODESYS-/WAGO-Versionen und benötigte Bibliotheken nach README separat installieren. Das Paket enthält keine Installer und erteilt keine Lizenzrechte.
3. Fünf Katalogtests ausführen; optional den Generator starten. Sieben ST-Objekte und Registermetadaten sind bereits enthalten.
4. Das Offline-Skript scripts/rebuild_project.py in der CODESYS-ScriptEngine ausführen. Es erzeugt das native Geräteprojekt neu; bei bereits vorhandener Projektdatei verweigert es ein Überschreiben.
5. Das erzeugte Projekt lokal öffnen und den vollständigen Compilerbericht prüfen. Task: 10 ms, COM1, 9600/8E1. Das Anwenderprogramm steuert keine CC100-DO/AO an und schreibt keine Thermokon-Register.
6. Vor jeder realen Übertragung separat die Zielidentität und Kompatibilität prüfen sowie Wiederherstellungspunkt und Autorisierung sicherstellen. Lokale IP-/Zugangsparameter eingeben. Kein automatischer Download oder Start erfolgt durch dieses Paket.
7. Nach einem freigegebenen Download Start, Boot-Erstellung, Datenfrische, Kommunikation, Fehlerstatus und Neustartverhalten am tatsächlichen Gerät prüfen.

Die GitHub-Sicherung enthält weder die ursprüngliche native Projektdatei noch Boot-/Gerätebackups oder Laufzeitdaten. Das lokal vorhandene vollständige Projektarchiv wird nicht extern übertragen. Mit der Neuerstellung wird kein Betriebssystem, keine Firmware und kein vorheriger Betrieb der Steuerung wiederhergestellt.

Es wird eine neue, bereinigte Git-Historie vorbereitet, keine bestehende Versionsgeschichte übernommen. Lokale Zwischenstände und frühere Vorbereitungspakete bleiben unverändert erhalten und werden nicht Teil dieser Historie.
