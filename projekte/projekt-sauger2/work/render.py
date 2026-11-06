#!/usr/bin/env python3
"""3-in-1-Waschsauger (Shark HydroVac) Teil 2 – rendert eine Variante: python3 work/render.py A|B|C
Clip-Ton stumm, nur Voice-over. Dreifach-Hook: erstes Bild + erster Satz + Text-Overlay ab Frame 0."""
import json, subprocess, sys, os

V = sys.argv[1]
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
FONT = "Montserrat"
A_, T1, T2, KLO = "raw/clip_a.mov", "raw/teil1.mov", "raw/teil2.mov", "raw/img3791.mov"
HDR = {T1, T2, KLO}
RED, GREEN, YEL = "&H00303BFF", "&H0059C734", "&H000AD6FF"

# (start, ende, quelle, in, zoom)
if V == "A":
    VOICE, WHISPER, DUR = "voice/A.wav", "work/whisper_A.json", 28.32
    EDL = [
        (0.00, 3.00, T1, 6.40, False),    # Hook: Krümel + saubere Spur ("Darum schick ich ihn zurück")
        (3.00, 4.70, T2, 1.50, False),    # NEIN: fährt mit Licht in die Krümel
        (4.70, 6.70, T2, 3.50, False),    # NEIN: ... mit einem Wisch weg
        (6.70, 10.50, A_, 35.20, False),  # NEIN: in die Station, reinigt sich selbst
        (10.50, 12.50, T2, 10.60, False), # NEIN: Licht vorne (Nahaufnahme)
        (12.50, 14.20, T1, 10.50, True),  # NEIN: Licht vorne 2
        (14.20, 16.80, A_, 1.90, False),  # "sondern weil ich ihn für 199 € gekauft hab" – Auspacken
        (16.80, 19.20, A_, 6.00, False),  # Station aus dem Karton
        (19.20, 21.00, T1, 12.60, False), # "... jetzt gibt's ihn für 119,99"
        (21.00, 23.40, KLO, 2.60, False), # Dreckwasser ins Klo
        (23.40, 25.60, T1, 1.00, False),  # sauberer Boden, Licht
        (25.60, 28.32, T2, 6.00, True),   # Schluss
    ]
    OV = [(0.00, 3.00, "Warte aufs Ende …", "Hook"),
          (3.00, 6.70, "NEIN", "No"), (6.70, 10.50, "NEIN", "No"), (10.50, 14.20, "NEIN", "No"),
          (15.70, 26.00, "{\\c" + RED + "&\\s1}199 €{\\s0\\c&HFFFFFF&}\\N{\\c" + GREEN + "&\\fs130}119,99 €", "Deal")]
    HOOKNAME = "zurueck"
else:
    raise SystemExit("B/C: Aufnahmen fehlen noch")

# --- Prüfungen
assert all(abs(EDL[n][1] - EDL[n + 1][0]) < 1e-6 for n in range(len(EDL) - 1))
assert abs(EDL[-1][1] - DUR) < 0.01
rng = sorted((s, i, i + (b - a)) for a, b, s, i, z in EDL)
for (s1, x1, y1), (s2, x2, y2) in zip(rng, rng[1:]):
    assert not (s1 == s2 and x2 < y1 - 0.01), f"Doppelt: {s1} {x1:.2f}-{y1:.2f} / {x2:.2f}-{y2:.2f}"
print(f"EDL {V} ok: {len(EDL)} Schnitte, keine Dopplungen")
os.makedirs("work/seg", exist_ok=True)
json.dump([dict(start=a, end=b, src=s, inp=i, zoom=z) for a, b, s, i, z in EDL], open(f"work/edl_{V}.json", "w"), indent=1)

def run(cmd):
    subprocess.run(cmd, check=True)

# 1) Segmente
segs = []
for n, (a, b, src, inp, zoom) in enumerate(EDL):
    dur = round(b - a, 3); frames = round(dur * 30)
    vf = ""
    if src in HDR:
        vf = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
    vf += "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    if zoom:
        vf += (f",scale=2160:3840,zoompan=z='1+0.10*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
               f":d=1:s=1080x1920:fps=30,setsar=1")
    out = f"work/seg/{V}_{n:02d}.mov"
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(inp), "-i", src, "-t", str(dur), "-an",
         "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", out])
    segs.append(out)
with open(f"work/concat_{V}.txt", "w") as f:
    f.writelines(f"file '{os.path.abspath(s)}'\n" for s in segs)
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"work/concat_{V}.txt",
     "-c", "copy", f"work/seg/{V}_all.mov"])

# 2) Untertitel + Overlays (.ass)
FIX = {"Wischbeck": "Wisch weg", "schicke": "schick", "199": "199 €", "Euro": "", "119": "119,99 €", ",99": "",
       "Button": "Button", "sondern,": "sondern"}
words = []
for s in json.load(open(WHISPER)):
    words += [dict(w=w["w"], s=w["s"], e=w["e"]) for w in s["words"]]
for i, w in enumerate(words):
    w["w"] = FIX.get(w["w"], w["w"])
words = [w for w in words if w["w"]]
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w["w"][-1] in ",.?!":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def ts(t):
    t = max(t, 0); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

def style(name, font, size, col, outline, align, mv):
    return f"Style: {name},{FONT} {font},{size},{col},&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{outline},3,{align},70,150,{mv},1"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0",
       "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       style("Sub", "ExtraBold", 70, "&H00FFFFFF", 6, 2, 640),
       style("Hook", "Black", 100, "&H00FFFFFF", 10, 8, 300),
       style("No", "Black", 150, RED, 11, 8, 280),
       style("Deal", "Black", 110, "&H00FFFFFF", 11, 8, 330),
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a, b, txt, s in OV:
    pop = "{\\fscx60\\fscy60\\t(0,120,\\fscx108\\fscy108)\\t(120,200,\\fscx100\\fscy100)}" if s in ("No", "Deal") else ""
    ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},{s},,0,0,0,,{pop}{txt}")
for ci, ch in enumerate(chunks):
    nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
    for wi, w in enumerate(ch):
        start = w["s"]; end = ch[wi + 1]["s"] if wi + 1 < len(ch) else min(nxt, w["e"] + 0.6)
        if end <= start: continue
        txt = " ".join((f"{{\\c{YEL}&}}{x['w']}{{\\c&HFFFFFF&}}" if k == wi else x["w"]) for k, x in enumerate(ch))
        ass.append(f"Dialogue: 0,{ts(start)},{ts(end)},Sub,,0,0,0,,{txt}")
open(f"work/subs_{V}.ass", "w").write("\n".join(ass) + "\n")

# 3) Finale
os.makedirs("out", exist_ok=True)
name = f"out/waschsauger_{V}_{HOOKNAME}.mp4"
run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"work/seg/{V}_all.mov", "-i", VOICE,
     "-filter_complex", f"[0:v]subtitles=work/subs_{V}.ass:fontsdir=/usr/local/share/fonts/montserrat[v];"
     "[1:a]aresample=48000,aformat=channel_layouts=stereo[a]",
     "-map", "[v]", "-map", "[a]", "-t", str(DUR),
     "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", "30",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", name])
print("fertig:", name)
