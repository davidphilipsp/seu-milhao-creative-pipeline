"""Calibração: palavras/s do Apresentador a partir de uma gravação em fontes/calibracao/ (Whisper local via hyperframes transcribe)."""
import json, pathlib, re, subprocess
from .raiz import raiz, gravar_json, hoje
from .midia import probe

ESTIMATIVA = 2.4


def calibrar(audio=None) -> str:
    pasta = raiz() / "fontes" / "calibracao"
    arqs = [pathlib.Path(audio)] if audio else sorted(p for p in pasta.glob("*") if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".mp4", ".mov", ".aac"))
    dest = raiz() / "memoria" / "calibracao.json"
    if not arqs:
        gravar_json(dest, {"palavras_por_s": ESTIMATIVA, "origem": "estimativa", "fonte": "guia 29/09/2026 (2,3 p/s) ajustado para fala popular; sem gravação em fontes/calibracao/", "data": hoje(), "arquivos": []})
        return f"calibracao.json: {ESTIMATIVA} palavras/s (ESTIMATIVA; coloque uma gravação do Apresentador em fontes/calibracao/ e rode de novo)"
    tot_p, tot_s, usados = 0, 0.0, []
    for a in arqs:
        wav = raiz() / "memoria" / "_calib.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(a), "-ac", "1", "-ar", "16000", str(wav)], check=True)
        r = subprocess.run(["npx", "hyperframes", "transcribe", str(wav), "--json", "--model", "large-v3", "--language", "pt"], text=True, capture_output=True, cwd=str(raiz()))
        txt = r.stdout
        m = re.search(r"\{.*\}", txt, re.S)
        palavras = None
        if m:
            try:
                d = json.loads(m.group(0))
                ws = d.get("words") or d.get("segments") or []
                palavras = len(ws) if ws and isinstance(ws[0], dict) and "word" in ws[0] else len(" ".join(s.get("text", "") for s in ws).split())
                if not palavras and d.get("text"): palavras = len(d["text"].split())
            except Exception: pass
        if palavras is None:
            r2 = subprocess.run(["whisper-cli", "-m", str(pathlib.Path.home() / ".cache/whisper/ggml-large-v3.bin"), "-l", "pt", "-nt", "-f", str(wav)], text=True, capture_output=True)
            palavras = len(re.sub(r"\[.*?\]", "", r2.stdout).split()) or None
        wav.unlink(missing_ok=True)
        if not palavras: return f"não consegui transcrever {a.name}: confira `npx hyperframes doctor` (whisper)"
        dur = probe(a)["duracao"]; tot_p += palavras; tot_s += dur; usados.append({"arquivo": str(a.relative_to(raiz())), "palavras": palavras, "duracao_s": dur})
    pps = round(tot_p / tot_s, 2)
    gravar_json(dest, {"palavras_por_s": pps, "origem": "medida", "fonte": "Whisper local sobre fontes/calibracao/", "data": hoje(), "arquivos": usados})
    return f"calibracao.json: {pps} palavras/s (medida em {len(usados)} arquivo(s), {tot_p} palavras / {tot_s:.1f} s)"
