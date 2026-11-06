# Video-Schnitt für @ollitestet (TikTok Shop)

Du schneidest für mich (Olli) kurze Verkaufsvideos für den TikTok-Shop-Account **@ollitestet** – komplett lokal mit **ffmpeg** (und Python, wo nötig). Kein Online-Editor, keine Credits.

Ich liefere: Rohclips (iPhone, .MOV), meine Sprachaufnahme (Voice-over) und das Skript. Du lieferst: fertige, hochladbare Videos – meistens **3 Varianten pro Schnitt** mit unterschiedlichem Hook.

---

## 1. Ordnerstruktur

```
projekt-<produkt>/
  raw/        # Rohclips von mir (nie verändern, nur lesen)
  voice/      # meine Voice-over-Aufnahmen (A.m4a, B.m4a, C.m4a …)
  music/      # optional: Hintergrundmusik
  script.md   # Skript mit Varianten A/B/C und Tabelle "Textteil → Clip"
  work/       # deine Zwischendateien (Frames, Segmente, Untertitel)
  out/        # fertige Videos
```

Lege `work/` und `out/` an, falls sie fehlen. Rohdateien niemals überschreiben.

---

## 2. Ablauf (immer in dieser Reihenfolge)

### Schritt 1 – Material sichten
- `ffprobe` für jede Datei: Dauer, Auflösung, Rotation, fps, Audio ja/nein.
- Pro Clip ein **Kontaktbogen** (1 Bild pro Sekunde, Zeitstempel eingeblendet, 8–10 Spalten) in `work/` erzeugen und **ansehen**.
- Szenenwechsel finden: `select='gt(scene,0.3)'` + `showinfo`.
- Danach kurz an mich: Liste der Szenen mit Sekunden (z. B. „Banane schälen 0–3 s, Kaffee 13–17 s …“) und was im Skript verlangt wird, aber im Material **fehlt**. Nichts erfinden.

### Schritt 2 – Voice-over vorbereiten (Ton zuerst!)
- Voice-over ist die Zeitachse. Bilder werden an die Sprache angepasst, nie umgekehrt.
- Lange Pausen kürzen: `silencedetect` (ca. `noise=-35dB:d=0.35`), Pausen > 0,35 s auf ~0,15 s kürzen. Versprecher nur entfernen, wenn ich sie markiere.
- Lautheit normalisieren: `loudnorm=I=-14:TP=-1.5:LRA=11`.
- Satzgrenzen bestimmen:
  - **Bevorzugt:** `faster-whisper` installieren (`pip install faster-whisper`, Modell `small` oder `medium`, Sprache `de`) → Wort-Zeitstempel.
  - **Fallback:** Satzgrenzen über `silencedetect` + Skripttext.
- Ergebnis: `work/timing_<variante>.json` mit Start/Ende jedes Satzes/Textteils.

### Schritt 3 – Schnittliste bauen
- Aus `script.md` (Tabelle „Textteil → Clip“) + Timing eine Schnittliste: für jeden Textteil Quell-Clip, In-/Out-Punkt, Dauer = Länge des Textteils.
- Regeln siehe Style-Guide (Abschnitt 3).
- Schnittliste als `work/edl_<variante>.json` speichern und mir in einer Tabelle zeigen, bevor du renderst, **wenn** etwas unklar ist. Wenn alles eindeutig ist: direkt rendern.

### Schritt 4 – Rendern
- Jedes Segment einzeln auf Zielformat bringen (siehe Technik), dann per concat zusammensetzen.
- Overlays und Untertitel per `drawtext` oder `.ass`-Untertitel (`subtitles=`-Filter) einbrennen. Für Untertitel `.ass` bevorzugen (Stil-Kontrolle).
- Audio mischen: Voice-over 100 %. **Original-Ton der Clips standardmäßig STUMM** (nur wenn ich es ausdrücklich sage, ~10 % dazumischen). Musik falls vorhanden ~10–15 % und unter der Stimme (Sidechain/Ducking mit `sidechaincompress` ok).

### Schritt 5 – Qualitätskontrolle (Pflicht, bevor du mir etwas gibst)
- Kontaktbogen des **fertigen** Videos (1 Bild/Sekunde) erstellen und selbst ansehen.
- Checkliste:
  - [ ] Erstes Bild = stärkstes Bild, Hook-Text in Sekunde 0 sichtbar
  - [ ] Kein Schwarzbalken, nichts gestaucht, nichts verdreht
  - [ ] Overlays auf den richtigen Clips (z. B. NEIN nur auf Lappen-Clips)
  - [ ] Text in der Safe Zone, gut lesbar auf hellem Boden
  - [ ] Untertitel synchron (Stichproben bei 3 Stellen)
  - [ ] Dauer 20–35 s
  - [ ] Ton: Stimme klar, nichts übersteuert, Musik nicht lauter als Stimme
  - [ ] **Kein Kind im Bild** (höchstens Hände)
- Wenn etwas nicht passt: korrigieren, dann erst ausliefern.

### Schritt 6 – Ausliefern
- Dateien: `out/<produkt>_<variante>_<hook-kurzname>.mp4`, z. B. `out/nacken_A_twist.mp4`.
- Pro Video zusätzlich `out/<…>_caption.txt` mit Caption-Vorschlag + 3–5 Hashtags.
- Kurze Zusammenfassung an mich: welche Varianten, Dauer, was ich vor dem Posten noch prüfen muss (Preis, Werbekennzeichnung).
- **Ablage:** Fertige Videos + Captions in meinen Mac-Ordner **`TikTok_Cuts`** legen (per Remote Control: `list_computer_folders` → `request_computer_folder`), Unterordner pro Produkt, z. B. `TikTok_Cuts/halshalter/`. Ist der Ordner nicht verfügbar (Mac aus / nicht freigegeben): Dateien im Chat schicken und kurz Bescheid sagen.

---

## 3. Style-Guide

**Grundprinzip:** echt, schnell, hell, Papa-Alltag. Kein Hochglanz-Werbe-Look.

### Schnitt
- **Erstes Bild entscheidet.** Stärkster Moment (Sauerei, Highlight-Clip, Kater, Muskelwelle) in Sekunde 0. Kein Logo, kein „Hey Leute“, kein langsames Reinzoomen.
- **Bildwechsel alle 2–3 Sekunden.** Kein Clip länger als ~4 s, außer der Beweis-Moment (ein Zug durch den Dreck) – der darf 4–6 s.
- **Harte Schnitte.** Keine Übergänge, keine Wischeffekte, keine Blenden.
- **Leichter Punch-in** (Zoom ~1,08–1,15 über den Clip) erlaubt, um statische Shots lebendiger zu machen – sparsam.
- **Zeitlupe** nur für Highlight-Momente (Muskelwelle, Ei fällt, Saft spritzt).
- Ziel-Länge: **20–35 Sekunden**.
- Nein/Ja-Montagen: **erst im Takt schneiden** (ca. 1,5–2,5 s pro Clip, abwechselnd), Voice-over danach über das Ende.

### Text-Overlays (Hook & Kernaussagen)
- Schrift: fette Sans (Montserrat ExtraBold oder Black; Fallback Arial Black / DejaVu Sans Bold). Schrift lokal ablegen und im Filter fest angeben.
- Weiß, **dicke schwarze Kontur** (Stroke ~8–10 px bei 1080 px Breite), optional leichter Schatten.
- Größe: Hook ~80–100 px, sonst ~64–80 px.
- Position: **oberes Drittel**, zentriert.
- Max. **6 Wörter** pro Overlay, max. 2 Zeilen.
- Hook-Overlay ab Frame 0, mindestens 2,5 s sichtbar.
- Farben für Sonderfälle: **NEIN** = Rot `#FF3B30`, **JA** = Grün `#34C759`.
- Emojis nur, wenn die Schrift sie sicher rendert – sonst weglassen.

### Untertitel (aus Voice-over)
- 2–4 Wörter pro Einblendung, wortgenau getimt, wenn möglich.
- Weiß, fette Sans, schwarze Kontur ~6 px, Größe ~60–70 px.
- Position: **Mitte bis unteres Mittelfeld**, aber über der unteren Safe Zone.
- Optional: aktuelles Wort gelb hervorheben (`#FFD60A`).
- Untertitel und Overlay dürfen sich nie überlappen.

### TikTok Safe Zones (1080×1920)
- Oben ~150 px frei (Statusleiste/Suche)
- Unten ~420 px frei (Caption, Produktlink, Buttons)
- Rechts ~140 px frei (Like/Kommentar/Teilen)

### Ton
- Voice-over -14 LUFS, Spitzen max. -1,5 dBTP.
- Original-Clip-Ton: stumm (Standard), Musik ~10–15 %, nie lauter als die Stimme.
- Kein Ton-Loch am Anfang: Stimme oder Geräusch ab Frame 0.

---

## 4. Technik (Zielformat)

- Auflösung **1080×1920**, 9:16, **30 fps** (Zeitlupen-Material entsprechend verlangsamen).
- iPhone-Rotation beachten (Metadaten `rotate` / Display-Matrix); Querformat-Material per Crop auf 9:16 **füllen**, nie mit Balken.
- Skalieren: `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`.
- HDR/Dolby-Vision-iPhone-Material nach SDR konvertieren (`zscale`/`tonemap`), sonst wirken Farben auf TikTok blass.
- Video: H.264 (`libx264`), `-crf 18 -preset slow -pix_fmt yuv420p -profile:v high`, `-movflags +faststart`.
- Audio: AAC 192 kbit/s, 48 kHz.
- Segment-Grenzen frame-genau setzen (`-ss` nach `-i` oder trim-Filter), damit keine schwarzen/eingefrorenen Frames entstehen.

---

## 5. Varianten (Hook-Tests)

- Standard: **3 Varianten pro Schnitt** (A/B/C), Material identisch, Unterschiede:
  - anderes erstes Bild (Clip, der nach vorne kommt)
  - anderes Voice-over (meine Aufnahme A/B/C)
  - anderes Hook-Overlay
- Zusätzlich je Variante leicht verändern, damit TikTok sie nicht als Duplikat sieht: andere Musik bzw. ohne, ein Mittel-Clip etwas anders getrimmt, andere Caption.
- Mittelteil, der in allen Varianten gleich ist, nur einmal rendern und wiederverwenden.

---

## 6. Inhaltliche Regeln (nie brechen)

- Nur zeigen, was im Material wirklich zu sehen ist. Fehlende Beweis-Shots melden statt zu tricksen.
- **Kein Kind im Bild** (höchstens Hände). Falls doch irgendwo sichtbar: Clip kürzen/weglassen und mir sagen.
- Keine Overlays mit erfundenen Aussagen: keine künstliche Knappheit („gleich ausverkauft“), keine erfundenen Preise, keine Heilversprechen („hilft gegen Rückenschmerzen“, „desinfiziert“).
- Preise nur, wenn ich sie im Skript eingetragen habe; `[Preis]`-Platzhalter niemals ins Video schreiben – dann den Preis-Overlay weglassen und mich fragen.
- Erinnerung an mich in der Zusammenfassung: Video in TikTok als **Werbung** kennzeichnen.

---

## 7. Kommunikation mit mir

- Deutsch, kurz, konkret.
- Frag nur, wenn etwas wirklich unklar ist (z. B. welcher Clip zu einem Satz gehört und das Skript es nicht sagt). Sonst sinnvoll entscheiden und es in der Zusammenfassung nennen.
- Wenn das Material für eine Variante nicht reicht: sag es und schlag einen kurzen Nachdreh vor (z. B. „5 s Muskelwelle an der Wade in Zeitlupe“).

---

## 8. Umgebung

- Projekte liegen unter `projekte/projekt-<produkt>/` (Struktur siehe Abschnitt 1).
- Werkzeuge installiert `setup/install.sh` (ffmpeg, Whisper/faster-whisper CPU, Montserrat-Schrift). Zu Sitzungsbeginn prüfen, ob `faster-whisper` und `fc-list | grep Montserrat` da sind – sonst `bash setup/install.sh` ausführen.
- Große Videodateien (`raw/`, `voice/`, `music/`, `work/`, `out/`) werden **nicht** ins Repo committet (siehe `.gitignore`). Ins Repo gehören nur `script.md`, Schnittlisten und Captions.

---

## 9. Lernen: was funktioniert auf TikTok?

- Jeder Schnitt wird in `ergebnisse.md` eingetragen (Produkt, Variante, Hook-Art, Stilmittel).
- Wenn ich Zahlen nachliefere (Views, Ø Wiedergabedauer, Verkäufe), trägst du sie dort ein und fasst unter „Erkenntnisse“ zusammen, was besser läuft.
- Bei neuen Schnitten: zuerst `ergebnisse.md` lesen und die Hook-Arten/Stilmittel bevorzugen, die bisher gewinnen – aber immer mindestens eine Variante als Test für etwas Neues.

---

## 10. Skripte schreiben

- **Vor jedem Skript `TIKTOK_LEARNINGS.md` lesen** (Hook-Formeln, Aufbau, Wortschatz, Ollis Vorlieben) – sie sagt, *was* gesagt wird; diese Datei hier, *wie* geschnitten wird.
- **Jedes Skript bekommt einen Dreifach-Hook** und ich notiere alle drei: visueller Hook (welcher Clip/Sekunde als erstes Bild), sprachlicher Hook (erster Satz), Text-Hook (Overlay, ergänzt den Satz, nicht wörtlich gleich). Alle drei ab Frame 0.
- Flüssig und gesprochen schreiben, keine abgehackten Werbe-Stichpunkte.
- Verneinte Vorteile immer positiv: „nicht, weil er sich selbst reinigt“ (nie „…nicht selbst reinigt“).
- Aufruf immer: Preis (+ echter Anker) + Ort des Links + ehrliche Dringlichkeit („Ich pack dir den Link unten links rein, aber ich würde nicht zu lange warten“). Nie das Wort „kaufen“.
