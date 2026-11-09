"""Montagem: sequência sem copies (emendar) e com copies (título Anton ouro 3D + apoio + rodapé via Pillow + ffmpeg overlay)."""
from PIL import Image, ImageDraw, ImageFont
from .raiz import raiz, criativo_dir, ler_json, rel
from .memoria import fato
from .midia import sh, emendar, probe

FONTES = raiz() / "biblioteca/referencias/marca/fontes"


def _fonte(nome, px, var=None):
    f = ImageFont.truetype(str(FONTES / nome), px)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f


def quebrar(dr, texto, fonte, larg):
    linhas, atual = [], ""
    for w in texto.split():
        t = (atual + " " + w).strip()
        if dr.textlength(t, font=fonte) > larg and atual: linhas.append(atual); atual = w
        else: atual = t
    if atual: linhas.append(atual)
    return linhas


def rodape_png(dest):
    img = Image.new("RGBA", (1080, 92), (0, 8, 44, 199)); d = ImageDraw.Draw(img)
    f = _fonte("Montserrat-wght.ttf", 24, "ExtraBold")
    linhas = quebrar(d, fato("redacoes_fixas.rodape"), f, 950)
    y = 46 - 15 * len(linhas)
    for l in linhas: d.text((540, y), l, font=f, fill=(255, 255, 255, 230), anchor="mt"); y += 30
    img.save(dest); return dest


def overlay_png(dest, titulo="", apoio=""):
    """Camada 1080×1920 com título ouro 3D (Anton) à esquerda em y 1180–1375, apoio Montserrat 800, rodapé em 1408–1500."""
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 1180
    if titulo:
        f = _fonte("Anton-Regular.ttf", 104)
        linhas = quebrar(d, titulo.upper(), f, 860)[:2]
        for l in linhas:
            for off, cor in ((12, (140, 94, 0, 255)), (9, (168, 116, 0, 255)), (6, (197, 143, 0, 255)), (3, (217, 164, 0, 255))):
                d.text((64, y + off), l, font=f, fill=cor)
            d.text((64, y), l, font=f, fill=(255, 206, 0, 255))
            y += 100
    if apoio:
        f2 = _fonte("Montserrat-wght.ttf", 44, "ExtraBold")
        for l in quebrar(d, apoio, f2, 860)[:2]:
            d.text((66, y + 2), l, font=f2, fill=(0, 0, 0, 160)); d.text((64, y), l, font=f2, fill=(255, 255, 255, 255)); y += 54
    rod = Image.open(rodape_png(dest.parent / "_rodape.png")).convert("RGBA")
    img.alpha_composite(rod, (0, 1408))
    img.save(dest); return dest


def montar(cid) -> str:
    d = criativo_dir(cid); dec = ler_json(d / "decupagem.json"); part = ler_json(d / "partitura.json")
    falas = {f["id"]: f for f in part["falas"]}
    ap = d / "aprovados"; ap.mkdir(parents=True, exist_ok=True)
    copies_txt, feitos = [], []
    for t in dec["takes"]:
        src = ap / f"{t['id']}_take.mp4"
        if not src.exists(): continue
        titulo = t.get("titulo_tela") or ""
        apoio = " ".join(falas[f].get("texto_tela", "") for f in t["falas"] if f in falas and falas[f].get("texto_tela")).strip()
        if not titulo and apoio and len(apoio) <= 24: titulo, apoio = apoio, ""
        if titulo and apoio and apoio.strip().lower() == titulo.strip().lower(): apoio = ""  # não duplicar título e apoio
        ov = ap / f"_overlay_{t['id']}.png"; overlay_png(ov, titulo, apoio)
        out = ap / f"{t['id']}_take_copies.mp4"
        sh("ffmpeg", "-y", "-v", "error", "-i", src, "-i", ov, "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto", "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "24", "-g", "24", out)
        feitos.append(t["id"]); copies_txt.append(f"[{t['id']}] {titulo} {apoio}".strip())
    copies_txt.append(fato("redacoes_fixas.rodape"))
    (ap / "copies.txt").write_text("\n".join(copies_txt) + "\n", encoding="utf-8")
    r1 = emendar(cid, "_take.mp4", "sequencia.mp4"); r2 = emendar(cid, "_take_copies.mp4", "sequencia_copies.mp4")
    rodape_png(ap / "rodape_legal.png")
    return f"montagem {cid}: {len(feitos)} takes com copies · {r1} · {r2}"
