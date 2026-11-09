"""FFmpeg e Pillow: folhas, tira da moeda, inspeção automática, padronizar, último quadro, emendar, animar foto."""
import json, pathlib, re, shutil, subprocess
from .raiz import raiz, criativo_dir, ler_json, gravar_json, rel, agora


def sh(*cmd, check=True):
    r = subprocess.run([str(c) for c in cmd], text=True, capture_output=True)
    if check and r.returncode: raise SystemExit(f"erro: {' '.join(str(c) for c in cmd[:3])}…\n{r.stderr[-800:]}")
    return r


def probe(p) -> dict:
    r = sh("ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", p)
    d = json.loads(r.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    return {"largura": int(v.get("width", 0)), "altura": int(v.get("height", 0)), "fps": round(int(num) / max(int(den), 1), 3),
            "duracao": round(float(d.get("format", {}).get("duration", 0)), 3), "audio": bool(a)}


def dimensao(p):
    from PIL import Image
    with Image.open(p) as im: return im.size


def _takes_gerar(cid):
    d = ler_json(criativo_dir(cid) / "decupagem.json")
    return [t for t in d["takes"] if t.get("origem") != "REUSO"]


def folhas(cid, tipo="tomadas", take=None) -> str:
    from PIL import Image, ImageDraw
    out = criativo_dir(cid) / "inspecao"; out.mkdir(parents=True, exist_ok=True)
    feitas = []
    if tipo == "quadros":
        qs = sorted((criativo_dir(cid) / "quadros").glob(f"{take or '*'}_*.png"))
        qs = [q for q in qs if "_folha" not in q.name and "_mascara" not in q.name]
        if not qs: return "nenhum quadro"
        w, h = 240, 427
        folha = Image.new("RGB", (w * len(qs), h + 24), (20, 20, 30)); dr = ImageDraw.Draw(folha)
        for i, q in enumerate(qs):
            with Image.open(q) as im: im = im.convert("RGB"); im.thumbnail((w, h)); folha.paste(im, (i * w, 24))
            dr.text((i * w + 4, 4), q.stem, fill=(255, 206, 0))
        dest = out / f"folha_quadros{'_' + take if take else ''}.jpg"; folha.save(dest, quality=85); feitas.append(dest)
    else:
        for pasta in ("teste", "final"):
            for v in sorted((criativo_dir(cid) / "tomadas" / pasta).glob(f"{take or '*'}_*.mp4")):
                dest = out / f"folha_{v.stem}.jpg"
                sh("ffmpeg", "-y", "-v", "error", "-i", v, "-vf", "fps=2,scale=270:-1,tile=8x2", "-frames:v", "1", dest); feitas.append(dest)
    return "folhas: " + ", ".join(rel(f) for f in feitas) if feitas else "nada para montar"


def tira_moeda(cid, take=None, centro=(0.52, 0.66), largura=0.22) -> str:
    """Recorta a região esperada da moeda em 0 / 1,5 / 3 / 4,5 s e põe ao lado do verso_scan e da M50_ref."""
    from PIL import Image
    out = criativo_dir(cid) / "inspecao"; out.mkdir(parents=True, exist_ok=True)
    refs = [raiz() / "biblioteca/referencias/moeda50/verso_scan.webp", raiz() / "biblioteca/referencias/moeda50/M50_ref.png"]
    feitas = []
    for pasta in ("teste", "final"):
        for v in sorted((criativo_dir(cid) / "tomadas" / pasta).glob(f"{take or '*'}_*.mp4")):
            pr = probe(v); W, H = pr["largura"], pr["altura"]
            lw = int(W * largura); cx, cy = int(W * centro[0]), int(H * centro[1])
            paineis = []
            for tms in (0, 1.5, 3, 4.5):
                tmp = out / f"_q_{v.stem}_{tms}.png"
                sh("ffmpeg", "-y", "-v", "error", "-ss", tms, "-i", v, "-frames:v", "1", "-vf", f"crop={lw}:{lw}:{cx-lw//2}:{cy-lw//2},scale=320:320", tmp)
                paineis.append(Image.open(tmp).convert("RGB")); tmp.unlink()
            for r in refs:
                if r.exists():
                    with Image.open(r) as im: im = im.convert("RGB"); im.thumbnail((320, 320)); paineis.append(im)
            tira = Image.new("RGB", (320 * len(paineis), 320), (0, 0, 0))
            for i, p in enumerate(paineis): tira.paste(p, (i * 320, 0))
            dest = out / f"tira_moeda_{v.stem}.jpg"; tira.save(dest, quality=88); feitas.append(dest)
    return "tiras: " + ", ".join(rel(f) for f in feitas) if feitas else "nenhuma tomada"


def _ocr(p) -> str:
    if not shutil.which("tesseract"): return "ocr indisponível"
    r = sh("tesseract", p, "stdout", "--psm", "11", check=False)
    txt = re.sub(r"\s+", " ", r.stdout).strip()
    return txt


def inspecionar(cid, etapa="teste") -> str:
    out = criativo_dir(cid) / "inspecao"; out.mkdir(parents=True, exist_ok=True)
    erros, tomadas = [], {}
    for t in _takes_gerar(cid):
        if t.get("modelo") == "ffmpeg-foto-animada": continue
        vids = sorted((criativo_dir(cid) / "tomadas" / etapa).glob(f"{t['id']}_*.mp4"))
        if not vids: erros.append(f"{t['id']}: sem tomada de {etapa}"); continue
        for v in vids:
            pr = probe(v); e = []
            if abs(pr["largura"] / max(pr["altura"], 1) - 9 / 16) > 0.02: e.append(f"proporção {pr['largura']}×{pr['altura']}")
            if abs(pr["fps"] - 24) > 0.5: e.append(f"fps {pr['fps']}")
            if not (3.5 <= pr["duracao"] <= 8.5): e.append(f"duração {pr['duracao']} s")
            if pr["audio"]: e.append("tem áudio")
            bd = sh("ffmpeg", "-v", "info", "-i", v, "-vf", "blackdetect=d=0.5:pic_th=0.98", "-an", "-f", "null", "-", check=False).stderr
            if "black_start" in bd and "SECO" not in v.read_bytes()[:0].decode(errors="ignore"):
                # tomadas simuladas são pretas de propósito: só marca
                e.append("quadros pretos ≥0,5 s" if not _e_seca(cid, v) else "")
            frame = out / f"_ocr_{v.stem}.png"
            sh("ffmpeg", "-y", "-v", "error", "-ss", 2, "-i", v, "-frames:v", "1", frame)
            ocr = _ocr(frame); frame.unlink(missing_ok=True)
            texto_lido = [w for w in ocr.split() if len(w) >= 3 and w.lower() != "50"] if "indisponível" not in ocr else []
            if texto_lido: e.append(f"ocr leu texto: {' '.join(texto_lido[:6])}")
            e = [x for x in e if x]
            tomadas[rel(v)] = {"probe": pr, "erros": e, "ocr": ocr[:120]}
            erros += [f"{v.name}: {x}" for x in e]
    folhas_txt = folhas(cid, "tomadas"); tira_txt = tira_moeda(cid)
    ficha = {"criativo": cid, "etapa": etapa, "data": agora(), "automatico_ok": not erros, "erros": erros, "tomadas": tomadas,
             "folhas": folhas_txt, "tiras": tira_txt, "avaliacao_do_inspetor": None, "passou": [], "descartes": []}
    gravar_json(criativo_dir(cid) / "esteira" / f"inspetor_{etapa}.json", ficha)
    return (f"inspeção {etapa}: {'OK' if not erros else str(len(erros)) + ' erro(s)'} · {len(tomadas)} tomada(s) · ficha esteira/inspetor_{etapa}.json\n"
            + "\n".join(erros[:5]))


def _e_seca(cid, v) -> bool:
    c = criativo_dir(cid) / "custos.md"
    return c.exists() and f"{v.name} |" in c.read_text(encoding="utf-8") and "SECO" in [l for l in c.read_text(encoding="utf-8").splitlines() if v.name in l][-1]


def padronizar(cid, take, entrada=None, trecho="0-4") -> str:
    d = criativo_dir(cid)
    src = d / entrada if entrada else None
    if not src:
        fin = sorted((d / "tomadas" / "final").glob(f"{take}_f*.mp4"))
        if not fin: raise SystemExit(f"sem tomada final de {take}")
        src = fin[-1]
    a, b = [float(x.replace(",", ".")) for x in re.split(r"[-–]", trecho)]
    out = d / "aprovados" / f"{take}_take.mp4"; out.parent.mkdir(parents=True, exist_ok=True)
    sh("ffmpeg", "-y", "-v", "error", "-ss", a, "-to", b, "-i", src, "-an", "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
       "-r", "24", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "24", "-keyint_min", "24", "-movflags", "+faststart", out)
    est = ler_json(d / "estado.json"); est.setdefault("takes", {}).setdefault(take, {}).update({"aprovado": f"aprovados/{take}_take.mp4", "trecho_uso": trecho, "fonte": rel(src)}); gravar_json(d / "estado.json", est)
    return f"OK: {rel(out)} ({probe(out)['duracao']} s)"


def ultimo_quadro(cid, take) -> str:
    d = criativo_dir(cid)
    src = d / "aprovados" / f"{take}_take.mp4"
    if not src.exists(): raise SystemExit("padronize antes")
    out = d / "aprovados" / f"{take}_ultimo_quadro.png"
    sh("ffmpeg", "-y", "-v", "error", "-sseof", "-0.05", "-i", src, "-frames:v", "1", "-update", "1", out)
    est = ler_json(d / "estado.json"); est.setdefault("takes", {}).setdefault(take, {})["ultimo_quadro"] = f"aprovados/{take}_ultimo_quadro.png"; gravar_json(d / "estado.json", est)
    return f"OK: {rel(out)}"


def emendar(cid, sufixo="_take.mp4", nome="sequencia.mp4") -> str:
    d = criativo_dir(cid); dec = ler_json(d / "decupagem.json")
    arqs = []
    for t in dec["takes"]:
        if (d / "aprovados" / f"{t['id']}{sufixo}").exists():  # versão local (com ou sem copies) tem prioridade sobre o catálogo
            arqs.append(d / "aprovados" / f"{t['id']}{sufixo}"); continue
        if t.get("origem") == "REUSO" and t.get("reuso_id"):
            cand = raiz() / "biblioteca" / "aprovados"  # reuso: procura o arquivo catalogado
            from .banco import catalogo
            item = next((i for i in catalogo() if i["id"] == t["reuso_id"]), None)
            if item: arqs.append(raiz() / "biblioteca" / item["caminho"]); continue
        p = d / "aprovados" / f"{t['id']}{sufixo}"
        if p.exists(): arqs.append(p)
    if not arqs: return "nada para emendar"
    lista = d / "aprovados" / f"_lista_{nome}.txt"; lista.write_text("".join(f"file '{p.resolve()}'\n" for p in arqs), encoding="utf-8")
    out = d / "aprovados" / nome
    sh("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-an", "-r", "24", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "24", "-movflags", "+faststart", out)
    return f"OK: {rel(out)} ({probe(out)['duracao']} s, {len(arqs)} takes)"


def animar_foto(foto, saida, zoom=1.06, deslize_px=0, duracao=4.0) -> str:
    """Zoom e deslize sem IA generativa; rosto intacto (sem parallax: só com máscara limpa, fora deste reflexo)."""
    foto, saida = pathlib.Path(foto), pathlib.Path(saida)
    n = int(round(duracao * 24))
    z = f"min(zoom+{(zoom-1)/n:.6f},{zoom})"
    sh("ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", foto, "-vf",
       f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='{z}':x='iw/2-(iw/zoom/2)+{deslize_px}*on/{n}':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=24,format=yuv420p",
       "-t", duracao, "-c:v", "libx264", "-crf", "16", "-an", saida)
    return f"OK: {saida} ({duracao} s, zoom {zoom}, deslize {deslize_px}px)"
