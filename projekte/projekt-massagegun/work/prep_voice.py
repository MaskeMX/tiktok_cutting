#!/usr/bin/env python3
"""Baut Voice-over A und B aus den Rohaufnahmen: Takes auswählen, Pausen kürzen, auf -14 LUFS bringen."""
import subprocess, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

def silences(wav, noise="-42dB", d=0.3):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", f"silencedetect=noise={noise}:d={d}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(l.split("silence_start: ")[1]) for l in out.splitlines() if "silence_start" in l]
    en = [float(l.split("silence_end: ")[1].split()[0]) for l in out.splitlines() if "silence_end" in l]
    return list(zip(st, en))

def piece(src, a, b, sil, target, minlen=0.35):
    """Bereich a-b aus src, Pausen > minlen innerhalb auf target kürzen -> Liste von (src, s, e)."""
    out, t = [], a
    for s, e in sil:
        if s > a and e < b and e - s > minlen:
            mid = (s + e) / 2
            out.append((src, t, mid - target / 2)); t = mid + target / 2
    out.append((src, t, b))
    return out

def build(name, parts, gap=0.0):
    """parts: Liste von Listen (src,s,e); zwischen den Teilen 'gap' Sekunden Stille."""
    srcs = sorted({p[0] for part in parts for p in part})
    idx = {s: i for i, s in enumerate(srcs)}
    f, labels, n = [], [], 0
    for pi, part in enumerate(parts):
        for src, s, e in part:
            f.append(f"[{idx[src]}:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[p{n}]"); labels.append(f"[p{n}]"); n += 1
        if gap and pi < len(parts) - 1:
            f.append(f"anullsrc=r=48000:cl=mono,atrim=0:{gap}[g{pi}]"); labels.append(f"[g{pi}]")
    f.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[c]")
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for s in srcs: cmd += ["-i", s]
    cmd += ["-filter_complex", ";".join(f), "-map", "[c]", f"work/{name}_cut.wav"]
    subprocess.run(cmd, check=True)
    # Kompressor + 2-Pass-Loudnorm auf -14 LUFS / -1.5 dBTP
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"work/{name}_cut.wav", "-af",
                    "highpass=f=80,volume=22dB,acompressor=threshold=-20dB:ratio=4:attack=5:release=120:makeup=3,"
                    "alimiter=limit=0.5:level=false", f"work/{name}_comp.wav"], check=True)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"work/{name}_comp.wav", "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    d = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:"
          f"measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"work/{name}_comp.wav", "-af", ln,
                    "-ar", "48000", f"voice/{name}.wav"], check=True)

T = "voice/tonspuren.wav"
sT = silences(T)
# A: "Kauf dir auf keinen Fall ... bevor du diese 3 Dinge weißt"
build("A", [piece(T, 0.00, 30.50, sT, 0.15)])
# B: "Am Anfang dachte ich ... Gym-Spielzeug" + Preis/Link
build("B", [piece(T, 57.95, 74.70, sT, 0.15), piece(T, 77.30, 80.85, sT, 0.15), piece(T, 93.35, 99.05, sT, 0.15)], gap=0.28)  # 1. Anlauf "dafür ist nicht ge-" (74.9-76.7) raus
for n in ("A", "B"):
    print(n, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                             f"voice/{n}.wav"], capture_output=True, text=True).stdout.strip())
