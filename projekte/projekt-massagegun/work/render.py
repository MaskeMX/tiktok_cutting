#!/usr/bin/env python3
"""Gymtastic Massagepistole – rendert eine Variante: python3 work/render.py A|B|C
Clip-Ton stumm (Wunsch Olli), nur Voice-over."""
import json, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFilter

V = sys.argv[1]
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
FONT = "Montserrat"
O, T, H = "raw/ohne_titel.mov", "raw/teil1.mov", "raw/highlite.mov"
HDR = set()
DARK = {H}   # Highlight-Clip ist dunkel -> aufhellen

RED, GREEN = "&H00303BFF&", "&H0059C734&"

# (start, ende, quelle, in, zoom)
if V in ("A", "C"):
    VOICE, WHISPER, DUR = "voice/A.wav", "work/whisper_A.json", 29.60
    EDL = [
        (0.00, 2.30, H, 0.50, False),    # Hook: Orange wird zerdrückt (Nahaufnahme)
        (2.30, 4.70, T, 1.00, True),     # Koffer offen mit allem ("bevor du diese 3 Dinge weißt")
        (4.70, 6.70, T, 16.00, False),   # 1. Kraft: Orange
        (6.70, 7.80, H, 2.90, False),    # "Guck dir das an"
        (7.80, 9.70, T, 24.70, False),   # 2. Aufsätze: Orange platt, Aufsätze liegen da
        (9.70, 10.75, T, 3.40, True),    # Aufsätze im Koffer
        (10.75, 13.00, T, 26.60, False), # Aufsatz wechseln: "2 Sekunden, zack, drauf"
        (13.00, 15.00, O, 14.00, False), # 3. Koffer (Logo)
        (15.00, 17.90, T, 5.00, True),   # Koffer offen, alles ordentlich drin
        (17.90, 19.90, O, 3.00, False),  # Bonus: Bananenbrei
        (19.90, 21.95, O, 8.00, False),  # Bananenbrei 2 ("lieber nicht nachmachen")
        (21.95, 24.65, T, 12.70, False), # Display/Stufen ("normal 170 Euro")
        (24.65, 27.35, T, 19.70, False), # Orange (unter der Preiskarte)
        (27.35, 29.60, H, 4.00, True),   # Orange Nahaufnahme, Schluss
    ]
    OV = [(0.00, 2.60, "Nicht kaufen, bevor\\Ndu DAS weißt!", "Hook"),
          (4.70, 7.80, "1. KRAFT", "Runde"), (7.80, 13.00, "2. AUFSÄTZE", "Runde"),
          (13.00, 17.90, "3. KOFFER", "Runde"), (17.90, 20.60, "BONUS:\\NBananenbrei", "Ov"),
          (20.60, 21.95, "Nicht nachmachen!", "Ov")]
    PRICE = (23.40, 28.30)
    SUB_FROM = 0.0
    HOOK = "3dinge"
    if V == "C":  # gleiches Voice-over A, Bananenbrei nach vorne, anderer Hook
        EDL[0] = (0.00, 2.30, O, 3.00, False)
        EDL[9] = (17.90, 19.90, O, 5.30, False)
        OV[0] = (0.00, 2.60, "Bananenbrei mit der\\NMassagepistole?!", "Hook")
        HOOK = "bananenbrei"
else:
    VOICE, WHISPER, DUR = "voice/B.wav", "work/whisper_B.json", 28.00
    EDL = [
        (0.00, 2.20, O, 3.50, False),    # Hook: Banane wird zu Brei
        (2.20, 4.10, T, 13.00, False),   # Display ("nur Gym-Spielzeug")
        (4.10, 6.60, T, 17.00, False),   # Orange ("am Ende verstehst du ...")
        (6.60, 8.60, O, 19.90, False),   # NEIN: Koffer wird aufgemacht
        (8.60, 10.30, T, 2.00, True),    # NEIN: mehrere Aufsätze im Koffer
        (10.30, 13.50, T, 25.90, False), # NEIN: Aufsatz in 2 Sekunden gewechselt
        (13.50, 15.10, H, 1.00, False),  # JA: Kraft – Orange Nahaufnahme
        (15.10, 16.70, O, 9.00, False),  # JA: Banane zu Brei
        (16.70, 18.70, O, 10.60, False), # "dafür ist sie nicht gedacht"
        (18.70, 20.60, T, 20.00, False), # Orange
        (20.60, 22.60, H, 3.00, True),   # "aber krass, dass es schon geht"
        (22.60, 25.50, T, 5.00, True),   # Koffer (unter der Preiskarte)
        (25.50, 28.00, T, 22.00, False), # Orange, Schluss
    ]
    OV = [(0.00, 2.60, "Nur Gym-Spielzeug?", "Hook"),
          (6.60, 13.50, "NEIN", "No"), (13.50, 16.70, "JA", "Ja")]
    PRICE = (22.60, 27.40)
    SUB_FROM = 0.0
    HOOK = "gymspielzeug"

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
    if src in DARK:
        vf = "eq=brightness=0.06:contrast=1.08:gamma=1.35:saturation=1.15,"
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
    shot = Image.open("assets/preis_screenshot.jpg").convert("RGB").crop((0, 0, 720, 620))
    ImageDraw.Draw(shot).rectangle((630, 470, 720, 540), fill="white")   # Lesezeichen weg
    shot = shot.resize((card_w - 40, int(620 * (card_w - 40) / 720)), Image.LANCZOS)
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
FIX = {"Kauft": "Kauf", "1.": "Erstens,", "2.": "Zweitens,", "3.": "drittens,", "Aufwärze": "Aufsätze",
       "Gymspielzeug,": "Gym-Spielzeug,", "prei": "Brei", "gibt.": "geht."}
words = []
for s in json.load(open(WHISPER)):
    words += [dict(w=w["w"], s=w["s"], e=w["e"]) for w in s["words"]]
for i, w in enumerate(words):
    w["w"] = FIX.get(w["w"], w["w"])
    if w["w"] == "putzt" and i + 1 < len(words) and words[i + 1]["w"] == "ihr": words[i + 1]["w"] = "es"
    if w["w"] == "war" and i + 1 < len(words) and words[i + 1]["w"] == "der":
        w["w"] = "warte"; words[i + 1]["w"] = ""
    if w["w"] == "Kauf" and i + 1 < len(words) and words[i + 1]["w"] == "ihr": words[i + 1]["w"] = "dir"
    if w["w"] == "einen" and i + 1 < len(words) and words[i + 1]["w"] == "TikTok": w["w"] = "im"
    if w["w"] == "war" and i + 1 < len(words) and words[i + 1]["w"] == "doch":
        w["w"] = "warte"; words[i + 1]["w"] = ""
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
ass.append(f"Dialogue: 1,{ts(pa + 0.2)},{ts(pb)},Price,,0,0,0,,69 € mit Coupon")
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
name = f"out/massagegun_{V}_{HOOK}.mp4"
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
