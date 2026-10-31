#!/usr/bin/env python3
"""Rendert eine Variante: python3 work/render.py A|B|C"""
import json, subprocess, sys, os

V = sys.argv[1]
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
FONT = "Montserrat"
T1, T2 = "raw/teil1.mov", "raw/teil2.mov"

# Mittelteil (für alle Varianten gleich): (timeline_start, timeline_end, quelle, in, zoom)
MIDDLE = [
    (5.12, 7.30, T1, 7.06, False),   # Abwaschen
    (7.30, 8.54, T1, 10.25, False),  # Kaffeemaschine Tasten
    (8.54, 10.20, T1, 12.95, False), # Kaffee läuft
    (10.20, 12.40, T2, 12.65, False),# Lego 1
    (12.40, 13.88, T2, 16.90, False),# Lego 2
    (13.88, 17.40, T2, 0.20, True),  # Kaffee mit Milch (Kater fehlt)
    (17.40, 19.38, T1, 5.02, False), # Banane Ende
    (19.38, 20.64, T1, 11.50, False),# Tasten
    (20.64, 22.74, T2, 18.30, False),# Lego Ende
    (22.74, 24.30, T2, 3.66, False), # Tasse nehmen
    (24.30, 27.12, T2, 6.45, False), # Handy drauf
    (27.12, 29.70, T2, 9.27, "top"),  # Produkt (Preis)
    (29.70, 31.75, T2, 14.85, False),# Lego Mitte
    (31.75, 32.42, T2, 11.85, "top"),# Produkt Schluss
]
PROD = (T2, 9.95, "top")    # Produkt mit Handy, sauber
BANANA = (T1, 2.46, False) # Banane POV
LEGO = (T2, 12.65, False)

VARIANTS = {
    "A": {"open": [PROD, BANANA], "hook": "Braucht kein Mensch?", "hookname": "keinmensch"},
    "B": {"open": [BANANA, PROD], "hook": "Beide Hände frei.\\NDas Handy filmt.", "hookname": "haendefrei"},
    "C": {"open": [LEGO, (T1, 0.0, False)], "hook": "Handy nie\\Nangefasst.", "hookname": "nieangefasst"},
}
cfg = VARIANTS[V]
o1, o2 = cfg["open"]
EDL = [(0.00, 2.56, *o1), (2.56, 5.12, *o2)] + MIDDLE
if V == "B":  # Mittel-Clip leicht anders getrimmt (Duplikat-Schutz)
    EDL[2 + 5] = (13.88, 17.40, T2, 0.45, True)
if V == "C":
    EDL[2 + 12] = (29.70, 31.75, T2, 10.45, "top")  # Schluss auf Produkt
    EDL[2 + 3] = (10.20, 12.40, T2, 15.30, False)  # Lego weiter hinten (Anfang ist schon Hook)

OVERLAYS = [
    (0.00, 2.70, cfg["hook"], "Hook"),
    (17.40, 20.60, "Komplett freihändig\\Ngefilmt", "Ov"),
    (27.12, 32.42, "Nur 12,99 €", "Ov"),
]

os.makedirs("work/seg", exist_ok=True)
json.dump([dict(start=a, end=b, src=s, inp=i, zoom=z) for a, b, s, i, z in EDL],
          open(f"work/edl_{V}.json", "w"), indent=1)

def run(cmd):
    subprocess.run(cmd, check=True)

# 1) Segmente frame-genau rendern
segs = []
for n, (a, b, src, inp, zoom) in enumerate(EDL):
    dur = round(b - a, 3)
    frames = round(dur * 30)
    out = f"work/seg/{V}_{n:02d}.mp4"
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
    if zoom == "top":  # Bodenstreifen unten wegschneiden (Kamera hat sich bewegt), Zoom 1.2 nach oben verankert
        vf += ",crop=900:1600:90:0,scale=1080:1920,setsar=1"
    if zoom:  # leichter Punch-in 1.0 -> 1.10 (hochskaliert gegen Ruckeln)
        vf += (f",scale=2160:3840,zoompan=z='1+0.10*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
               f":d=1:s=1080x1920:fps=30,setsar=1")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(inp), "-i", src, "-t", str(dur),
         "-vf", vf, "-frames:v", str(frames),
         "-af", f"volume=0.10,aresample=48000,apad,atrim=0:{dur}", "-ac", "2",
         "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", out.replace(".mp4", ".mov")])
    segs.append(out.replace(".mp4", ".mov"))

with open(f"work/concat_{V}.txt", "w") as f:
    f.writelines(f"file '{os.path.abspath(s)}'\n" for s in segs)
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"work/concat_{V}.txt",
     "-c", "copy", f"work/seg/{V}_all.mov"])

# 2) Untertitel (.ass): 2-4 Wörter, aktuelles Wort gelb
FIX = {"Kader": "Kater", "-Bauen": "bauen", "dich": "nicht", "die Link": "den Link"}
words = []
for s in json.load(open("work/whisper_A.json")):
    words += [dict(w=w["w"], s=w["s"], e=w["e"]) for w in s["words"]]
# Korrekturen
out = []
i = 0
while i < len(words):
    w = dict(words[i])
    if w["w"] == "12" and i + 2 < len(words) and words[i+1]["w"] == ",99":
        w["w"] = "12,99"; w["e"] = words[i+1]["e"]; out.append(w)
        e = dict(words[i+2]); e["w"] = "€," if e["w"].startswith("Euro") else e["w"]; out.append(e); i += 3; continue
    if w["w"] == "die" and i + 1 < len(words) and words[i+1]["w"] == "Link":
        w["w"] = "den"
    w["w"] = FIX.get(w["w"], w["w"])
    out.append(w); i += 1
words = out

chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w["w"][-1] in ",.?!":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

YEL = "&H000AD6FF&"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       f"Style: Sub,{FONT} ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,70,150,640,1",
       f"Style: Hook,{FONT} Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,10,3,8,70,150,300,1",
       f"Style: Ov,{FONT} Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,9,3,8,70,150,300,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a, b, txt, st in OVERLAYS:
    ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{txt}")
for ci, ch in enumerate(chunks):
    nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
    for wi, w in enumerate(ch):
        start = w["s"]
        end = ch[wi + 1]["s"] if wi + 1 < len(ch) else min(nxt, w["e"] + 0.6)
        if end <= start: continue
        txt = " ".join((f"{{\\c{YEL}}}{x['w']}{{\\c&HFFFFFF&}}" if k == wi else x["w"]) for k, x in enumerate(ch))
        ass.append(f"Dialogue: 0,{ts(start)},{ts(end)},Sub,,0,0,0,,{txt}")
open(f"work/subs_{V}.ass", "w").write("\n".join(ass) + "\n")

# 3) Finale: Untertitel einbrennen, Ton mischen
name = f"out/halshalter_{V}_{cfg['hookname']}.mp4"
run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"work/seg/{V}_all.mov", "-i", "voice/A.wav",
     "-filter_complex",
     f"[0:v]subtitles=work/subs_{V}.ass:fontsdir=/usr/local/share/fonts/montserrat[v];"
     "[0:a]aresample=48000[o];[1:a]aresample=48000,aformat=channel_layouts=stereo[vo];"
     "[vo][o]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=false[a]",
     "-map", "[v]", "-map", "[a]", "-t", "32.42",
     "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", "30",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", name])
print("fertig:", name)
