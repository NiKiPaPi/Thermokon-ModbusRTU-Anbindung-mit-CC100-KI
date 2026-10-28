# Validierung und Aussagegrenzen

## Historisch dokumentiert, 18.10.2026

- Codegenerierung ohne Fehler und Warnungen.
- Fünf Katalogtests und zwölf ST-Selbsttests bestanden.
- Ein reales WRF04-AO2V-Gerät erkannt; 73 gültige Datenpunkte und Ausnahmen 2 für die erweiterten Adressregister 0x4000/0x4001.
- Download, Boot-Erstellung und Warm-Reset mit anschließendem Start geprüft.
- Bearbeitbare ST-Objekte des damaligen nativen Projekts und lokalen Archivs gegen die Quellen verglichen.

Diese Aussagen stammen aus lokalen historischen Nachweisen. Rohprotokolle, Geräte-/Bootdateien, Betriebswerte, Adressen und Benutzerpfade werden nicht veröffentlicht. Bei der GitHub-Vorbereitung wurde keine SPS kontaktiert oder geändert.

## Vorbereitung am 28.10.2026

Die aktuellen lesbaren Quelldateien wurden kopiert; nur Paketdokumentation und Offline-Wiederaufbau wurden angepasst. Fünf Katalogtests sind bestanden. Der Generator erzeugte alle sieben ST-Objekte, objects.json und beide Registerkatalogdateien bytegleich neu. Eine separate frische Prüfkopie wurde ausschließlich offline mit CODESYS 3.5.21.50 aufgebaut: sieben ST-Objekte importiert, Codegenerierung mit 0 Fehlern und 0 Warnungen. Diese Prüfung verbindet sich mit keiner Steuerung. Die lokalen Detailberichte bleiben außerhalb des Uploads.

Die Prüfung ist keine Garantie auf Fehler- oder Geheimnisfreiheit. Kein physischer Stromausfall, vollständiger Controller-Neustart, zwölf reale Teilnehmer oder reale Leitungsunterbrechung ist geprüft. Der neue Stand ist nicht als stabile Version vom Benutzer abgenommen.
