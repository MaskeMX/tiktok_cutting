#!/usr/bin/env python3
"""Shark HydroVac – rendert eine Variante: python3 work/render.py A|B|C
Clip-Ton stumm (Wunsch Olli), nur Voice-over."""
import json, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFilter

V = sys.argv[1]
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
FONT = "Montserrat"
C2, C3, C4, C5, KLO = "raw/clip2.mov", "raw/clip3.mov", "raw/clip4.mov", "raw/clip5.mov", "raw/img3791.mov"
HDR = {KLO}

RED, GREEN = "&H00303BFF&", "&H0059C734&"   # ASS: &HBBGGRR  (#FF3B30 / #34C759)

# (start, ende, quelle, in, zoom)
if V == "A":
    VOICE, WHISPER, DUR = "voice/A.wav", "work/whisper_A.json", 29.75
    EDL = [
        (0.00, 1.05, C5, 3.00, False),   # NEIN Lappen Ei
        (1.05, 2.13, C5, 8.20, False),   # JA   Shark Ei
        (2.13, 2.87, C3, 7.10, False),   # NEIN Lappen Milch
        (2.87, 3.83, C3, 11.00, False),  # JA   Shark Milch
        (3.83, 4.77, C4, 0.00, False),   # NEIN Lappen Frischkäse
        (4.77, 5.67, C4, 3.00, False),   # JA   Shark Frischkäse
        (5.67, 8.85, C3, 0.00, False),   # Milch wird gekippt ("Kleinkind ... Endgegner")
        (8.85, 9.73, C3, 4.30, True),    # Pfütze ("Milch")
        (9.73, 10.47, C4, 1.00, True),   # Frischkäse verschmiert ("Essensreste")
        (10.47, 11.41, C5, 0.00, True),  # rohes Ei
        (11.41, 13.57, C5, 9.30, False), # Shark über Ei ("einmal drüber, zack, weg")
        (13.57, 15.60, C3, 13.00, False),# Shark Milch ("kein Lappen, kein Eimer")
        (15.60, 18.80, C2, 8.00, False), # Station Selbstreinigung
        (18.80, 20.85, KLO, 2.20, False),# Schmutzwasser ins Klo
        (20.85, 24.30, C2, 2.30, False), # Shark in der Station (Preis)
        (24.30, 26.95, C4, 9.50, False), # Shark Bahn ("Link")
        (26.95, 29.75, C5, 16.75, True), # Tank mit Ei, Schluss
    ]
    OV = [(0.00, 1.05, "NEIN", "No"), (1.05, 2.13, "JA", "Ja"), (2.13, 2.87, "NEIN", "No"),
          (2.87, 3.83, "JA", "Ja"), (3.83, 4.77, "NEIN", "No"), (4.77, 5.67, "JA", "Ja"),
          (5.67, 8.85, "Kleinkind-Eltern,\\Naufgepasst!", "Ov"),
          (11.41, 13.57, "Einmal drüber.\\NWeg.", "Ov")]
    PRICE = (20.85, 24.30)
    SUB_FROM = 5.60          # vorher stehen NEIN/JA groß im Bild
    HOOK = "neinja"
else:
    VOICE, WHISPER, DUR = "voice/B.wav", "work/whisper_B.json", 29.03
    EDL = [
        (0.00, 2.10, C3, 1.50, False),   # Hook: Milch platscht auf den Boden
        (2.10, 3.65, C3, 18.45, True),   # Runde 1: Frischkäse liegt, Lappen kommt
        (3.65, 5.65, C4, 0.00, False),   # Lappen schiebt hin und her
        (5.65, 7.45, C4, 2.00, True),    # ... schmiert alles voll (Punch-in = sichtbarer Schnitt)
        (7.45, 9.30, C4, 3.80, False),   # Shark nimmt alles in einem Zug
        (9.30, 10.55, C3, 4.20, True),   # Runde 2: Milch-Pfütze
        (10.55, 11.60, C3, 7.10, False), # Lappen schmiert
        (11.60, 13.40, C3, 10.40, False),# Shark saugt + wischt
        (13.40, 14.45, C3, 13.50, False),# Boden trocken
        (14.45, 16.75, C5, 0.00, True),  # Runde 3: rohes Ei
        (16.75, 19.05, C5, 3.00, False), # Lappen verschmiert Ei ("dachte, das schafft er nicht")
        (19.05, 20.00, C5, 8.50, False), # Zack, weg
        (20.00, 22.15, C2, 8.00, False), # Station putzt sich selbst
        (22.15, 25.70, C2, 2.30, False), # Preis
        (25.70, 29.03, C5, 16.22, True), # Tank mit Ei, Schluss
    ]
    OV = [(0.00, 2.10, "LAPPEN vs. SHARK", "Hook"),
          (2.10, 3.65, "RUNDE 1", "Runde"), (3.65, 7.45, "NEIN", "No"), (7.45, 9.30, "JA", "Ja"),
          (9.30, 10.55, "RUNDE 2", "Runde"), (10.55, 11.60, "NEIN", "No"), (11.60, 14.45, "JA", "Ja"),
          (14.45, 16.75, "RUNDE 3", "Runde"), (16.75, 19.05, "NEIN", "No"), (19.05, 20.00, "JA", "Ja")]
    PRICE = (22.15, 25.70)
    SUB_FROM = 0.0
    HOOK = "lappenvsshark"
    if V == "C":  # anderes erstes Bild (Lappen verschmiert Ei), andere Hook-Zeile
        EDL[0] = (0.00, 2.10, C5, 3.00, False)
        EDL[10] = (16.75, 17.65, C5, 5.10, False)
        EDL.insert(11, (17.65, 19.05, C5, 6.00, False))   # Shark rollt aufs Ei zu
        OV[0] = (0.00, 2.10, "Der Lappen\\Nverliert.", "Hook")
        OV[8] = (16.75, 17.65, "NEIN", "No"); OV[9] = (17.65, 20.00, "JA", "Ja")   # NEIN nur auf dem Lappen
        HOOK = "lappenverliert"

# --- Prüfungen: lückenlos, Länge, keine Dopplung innerhalb der Variante
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

# 1) Segmente (ohne Ton)
segs = []
for n, (a, b, src, inp, zoom) in enumerate(EDL):
    dur = round(b - a, 3); frames = round(dur * 30)
    vf = ""
    if src in HDR:  # HLG/HDR -> SDR bt709
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

# 2) Preiskarte (aus Ollis Screenshot, ohne Lieferdatum/Lesezeichen) mit Pop-Animation
card_w = 860
if not os.path.exists("work/card.png"):
    shot = Image.open("assets/preis_screenshot.jpg").convert("RGB").crop((0, 0, 720, 618))
    ImageDraw.Draw(shot).rectangle((640, 470, 720, 540), fill="white")   # Lesezeichen weg
    shot = shot.resize((card_w - 40, int(618 * (card_w - 40) / 720)), Image.LANCZOS)
    w, h = card_w, shot.height + 40
    card = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + w, 26 + h), 36, fill=(0, 0, 0, 110))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle((0, 0, w - 1, h - 1), 36, fill="white", outline=(0, 0, 0, 255), width=6)
    body.paste(shot, (20, 20))
    card.alpha_composite(body, (20, 20))
    card.save("work/card.png")
card = Image.open("work/card.png")
pa, pb = PRICE
pdur = pb - pa
os.makedirs(f"work/cardseq_{V}", exist_ok=True)
nfr = round(pdur * 30)
for k in range(nfr):
    t = k / 30
    s = 0.55 + 0.53 * (t / 0.18) if t < 0.18 else (1.08 - 0.08 * ((t - 0.18) / 0.12) if t < 0.30 else 1.0)
    if t > pdur - 0.15: s = max(0.01, (pdur - t) / 0.15)
    fr = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    c = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.LANCZOS)
    fr.alpha_composite(c, ((1080 - c.width) // 2 - 50, 300 + (card.height - c.height) // 2))
    fr.save(f"work/cardseq_{V}/{k:04d}.png")
card_bottom = 300 + card.height

# 3) Untertitel (.ass)
FIX = {"Körnischer": "Körniger", "Frischköse.": "Frischkäse.", "riecht": "wischt", "erwarte": "wartet",
       "ihr": "ihr", "Rosei.": "rohes Ei."}
words = []
for s in json.load(open(WHISPER)):
    words += [dict(w=w["w"], s=w["s"], e=w["e"]) for w in s["words"]]
for i, w in enumerate(words):
    w["w"] = FIX.get(w["w"], w["w"])
    if w["w"] == "putzt" and i + 1 < len(words) and words[i + 1]["w"] == "ihr": words[i + 1]["w"] = "es"
    if w["w"] == "war" and i + 1 < len(words) and words[i + 1]["w"] == "der":
        w["w"] = "warte"; words[i + 1]["w"] = ""
    if w["w"] == "199": w["w"] = "199"
words = [w for w in words if w["w"] and w["s"] >= SUB_FROM]
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w["w"][-1] in ",.?!":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def ts(t):
    t = max(t, 0); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

YEL = "&H000AD6FF&"
st = "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
def style(name, font, size, col, outline, align, mv):
    return f"Style: {name},{FONT} {font},{size},{col},&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{outline},3,{align},70,150,{mv},1"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0",
       "ScaledBorderAndShadow: yes", "", "[V4+ Styles]", st,
       style("Sub", "ExtraBold", 70, "&H00FFFFFF", 6, 2, 640),
       style("Hook", "Black", 100, "&H00FFFFFF", 10, 8, 300),
       style("Ov", "Black", 84, "&H00FFFFFF", 9, 8, 300),
       style("Runde", "Black", 110, "&H000AD6FF", 10, 8, 300),
       style("No", "Black", 150, RED.rstrip("&"), 11, 8, 280),
       style("Ja", "Black", 150, GREEN.rstrip("&"), 11, 8, 280),
       style("Price", "Black", 76, "&H00FFFFFF", 9, 8, card_bottom + 30),
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a, b, txt, s in OV:
    pop = "{\\fscx60\\fscy60\\t(0,120,\\fscx108\\fscy108)\\t(120,200,\\fscx100\\fscy100)}" if s in ("No", "Ja", "Runde") else ""
    ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},{s},,0,0,0,,{pop}{txt}")
ass.append(f"Dialogue: 1,{ts(pa + 0.2)},{ts(pb)},Price,,0,0,0,,199,98 € mit Coupon")
for ci, ch in enumerate(chunks):
    nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
    for wi, w in enumerate(ch):
        start = w["s"]; end = ch[wi + 1]["s"] if wi + 1 < len(ch) else min(nxt, w["e"] + 0.6)
        if end <= start: continue
        # Untertitel während der Preiskarte weiter nach unten (kein Überlappen)
        txt = " ".join((f"{{\\c{YEL}}}{x['w']}{{\\c&HFFFFFF&}}" if k == wi else x["w"]) for k, x in enumerate(ch))
        mv = "0"
        if pa <= start < pb: mv = "560"
        ass.append(f"Dialogue: 0,{ts(start)},{ts(end)},Sub,,0,0,{mv},,{txt}")
open(f"work/subs_{V}.ass", "w").write("\n".join(ass) + "\n")

# 4) Finale: Karte drüber, Untertitel einbrennen, nur Voice-over als Ton
name = f"out/sauger_{V}_{HOOK}.mp4"
run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"work/seg/{V}_all.mov",
     "-framerate", "30", "-itsoffset", str(pa), "-i", f"work/cardseq_{V}/%04d.png", "-i", VOICE,
     "-filter_complex",
     f"[0:v][1:v]overlay=0:0:eof_action=pass:enable='between(t,{pa},{pb})'[c];"
     f"[c]subtitles=work/subs_{V}.ass:fontsdir=/usr/local/share/fonts/montserrat[v];"
     "[2:a]aresample=48000,aformat=channel_layouts=stereo[a]",
     "-map", "[v]", "-map", "[a]", "-t", str(DUR),
     "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", "30",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", name])
print("fertig:", name)
