"""Geração paga (Vertex AI): quadros no Nano Banana e vídeo no Veo. --seco simula sem custo; --confirmar obrigatório para gastar."""
import mimetypes, os, pathlib, subprocess, time
from .raiz import raiz, criativo_dir, ler_json, gravar_json, rel
from .memoria import fato
from . import custo as C

MODELOS_VEO = {"padrao": "veo-3.1-generate-001", "fast": "veo-3.1-fast-generate-001", "lite": "veo-3.1-lite-generate-001"}
MODELO_IMG = "gemini-3.1-flash-image"


def _env():
    env = raiz() / ".env"
    if env.exists():
        for l in env.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1); k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and k not in os.environ: os.environ[k] = v


def cliente(location=None):
    _env()
    from google import genai
    proj = os.environ.get("GOOGLE_CLOUD_PROJECT") or (_ for _ in ()).throw(SystemExit("GOOGLE_CLOUD_PROJECT não definido (.env)"))
    loc = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    return genai.Client(vertexai=True, project=proj, location=loc), loc


def testar_vertex() -> str:
    out = []
    try:
        for m, loc in [("veo-3.1-fast-generate-001", None), ("veo-3.1-generate-001", None), (MODELO_IMG, "global")]:
            c, l = cliente(loc); c.models.get(model=m); out.append(f"{m}: acessível")
    except Exception as e:
        out.append(f"ERRO: {str(e)[:160]} → `gcloud auth application-default login` com a conta owner@example.com")
    return "\n".join(out) + "\n(nada foi cobrado)"


def precos():
    return fato("tecnica.precos_usd")


def _estilo(cid):
    d = ler_json(criativo_dir(cid) / "decupagem.json")
    e = raiz() / "estilos" / d["estilo"]
    bloco = (e / "bloco.txt").read_text(encoding="utf-8").strip()
    neg = (e / "negativos.txt").read_text(encoding="utf-8").strip() if (e / "negativos.txt").exists() else ""
    return d, bloco, neg


def _take(d, take):
    for t in d["takes"]:
        if t["id"] == take: return t
    raise SystemExit(f"take {take} não existe na decupagem")


def _refs(t):
    refs = [raiz() / "biblioteca/referencias/moeda50/M50_ref.png"]
    if "apresentador" in (t.get("tags", {}).get("elemento") or []):
        refs += sorted((raiz() / "biblioteca/referencias/apresentador").glob("ref_*.png"))[:3]
    return [r for r in refs if r.exists()]


def prompt_quadro(cid, take, fim=False) -> pathlib.Path:
    d, bloco, neg = _estilo(cid); t = _take(d, take)
    p = criativo_dir(cid) / "prompts" / f"{take}_quadro-{'fim' if fim else 'inicio'}.txt"
    if p.exists(): return p
    refs = _refs(t)
    papeis = []
    for i, r in enumerate(refs, 1):
        papeis.append(f"Image {i} = " + ("the single 50 centavos coin, reverse side with the 50" if "M50" in r.name else "the man's face and hair, keep his identity exactly"))
    apresentador = "apresentador" in (t.get("tags", {}).get("elemento") or [])
    exc = "\nException for this shot only: the man looks straight into the lens." if apresentador else ""
    corpo = (f"Create a realistic smartphone photo, vertical 9:16. {t['enquadramento']}. {t['descricao']}"
             f"{' This is the LAST frame of the shot: ' + t['fim'] if fim and t.get('fim') else ''}")
    txt = (f"# {cid} {take} · quadro de {'fim' if fim else 'início'} · gerado por sm (edite antes de gerar se precisar)\n{bloco}{exc}\n"
           + ("; ".join(papeis) + ".\n" if papeis else "") + corpo + "\n"
           + (neg + "\n" if neg else "") + "No text, no numbers, no logos, no signs, nothing written anywhere, no child, no other person.\n")
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt, encoding="utf-8")
    return p


def quadro(cid, take, fim=False, seco=False, confirmar=False) -> str:
    if not seco:
        from .trava import exigir; exigir(cid)  # trava de geração: só o usuário libera, um criativo por vez (antes de qualquer outra checagem)
    d, _, _ = _estilo(cid); t = _take(d, take)
    saida = criativo_dir(cid) / "quadros" / f"{take}_{'fim' if fim else 'inicio'}.png"
    if saida.exists(): return f"{rel(saida)} já existe (apague para regerar)"
    p = prompt_quadro(cid, take, fim)
    custo = float(precos()["nano_banana_1k"])
    if seco:
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (1080, 1920), (40, 44, 60)); ImageDraw.Draw(im).text((60, 900), f"SECO · {cid} {take} {'fim' if fim else 'início'}", fill=(255, 206, 0))
        saida.parent.mkdir(parents=True, exist_ok=True); im.save(saida)
        C.registrar(cid, MODELO_IMG, "imagem 1K 9:16 (simulada)", 0.0, rel(saida), seco=True)
        return f"SECO: {rel(saida)} (custo simulado US$ {custo:.2f}, cobrado 0)"
    bloq = C.checar_teto(cid, custo)
    if bloq: raise SystemExit(bloq)
    if not confirmar:
        return f"SIMULAÇÃO: {MODELO_IMG} · 1K 9:16 · prompt {rel(p)} · custo US$ {custo:.2f} · gasto {C.gasto_de(cid):.2f}/{C.teto_de(cid):.2f}. Repita com --confirmar."
    from google.genai import types
    c, loc = cliente("global")
    prompt = "\n".join(l for l in p.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#")).strip()
    partes = [prompt] + [types.Part.from_bytes(data=r.read_bytes(), mime_type=mimetypes.guess_type(str(r))[0] or "image/png") for r in _refs(t)]
    for tentativa in range(3):
        try:
            resp = c.models.generate_content(model=MODELO_IMG, contents=partes, config=types.GenerateContentConfig(response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="9:16", image_size="1K")))
            break
        except Exception as e:
            if "429" in str(e) and tentativa < 2: time.sleep(60); continue
            raise
    imgs = [pt.inline_data for cd in (resp.candidates or []) for pt in (cd.content.parts or []) if getattr(pt, "inline_data", None)]
    if not imgs: raise SystemExit(f"nenhuma imagem devolvida: {getattr(resp, 'prompt_feedback', None)}")
    saida.parent.mkdir(parents=True, exist_ok=True); saida.write_bytes(imgs[0].data)
    C.registrar(cid, f"{MODELO_IMG} (Vertex {loc})", "imagem 1K 9:16", custo, rel(saida))
    return f"OK: {rel(saida)} · US$ {custo:.2f} · gasto {C.gasto_de(cid):.2f}/{C.teto_de(cid):.2f}{C.alerta_80(cid)}"


def prompt_veo(cid, take) -> pathlib.Path:
    d, bloco, neg = _estilo(cid); t = _take(d, take)
    p = criativo_dir(cid) / "prompts" / f"{take}_veo.txt"
    if p.exists(): return p
    apresentador = "apresentador" in (t.get("tags", {}).get("elemento") or [])
    exc = "\nException for this shot only: the man looks straight into the lens." if apresentador else ""
    acao = t.get("acao_tempo") or t["descricao"]
    txt = (f"# {cid} {take} · Veo · 8 s · uso 0–{t['duracao_s']} s · gerado por sm (edite antes de gerar se precisar)\n{bloco}{exc}\n"
           "Maintain the scene, the person and the same single 50 centavos coin from the first frame" + ("; end exactly on the last frame.\n" if (criativo_dir(cid) / 'quadros' / f'{take}_fim.png').exists() else ".\n")
           + f"Action, timed: {acao}\n"
           + ("He never speaks and never articulates words; the mouth only smiles. His other hand stays out of frame the whole time.\n" if apresentador
              else "Exactly ONE coin ever appears. The person's eyes stay on the coin the whole time; the head never turns toward the camera; the lips stay together while the smile widens, the mouth never opens, never laughs. No other hand ever enters the frame and nobody else touches the coin.\n")
           + f"Camera: {t.get('movimento_camera', 'single continuous handheld shot at eye level, slight breathing, deep focus, no zoom')}.\n"
           "The coin never flies, falls, stacks, flips or turns into anything else; only one coin, always showing its back. The other hand stays out of frame; no waving.\n"
           + (neg + "\n" if neg else "") + "No other person, no child. No text, no logos, no readable signs, no watermark, no captions.\n")
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt, encoding="utf-8")
    return p


def _modelo_final(t):
    m = t.get("modelo", "")
    if "padrao" in m: return "padrao", "1080p"
    if "fast-1080p" in m: return "fast", "1080p"
    el = set(t.get("tags", {}).get("elemento") or [])
    return ("padrao", "1080p") if el & {"rosto", "apresentador", "mao"} else ("fast", "1080p")


def veo(cid, take, modo="teste", confirmar=False, seco=False, tentativa=1) -> str:
    if not seco:
        from .trava import exigir; exigir(cid)  # trava de geração (antes de qualquer outra checagem)
    d, _, _ = _estilo(cid); t = _take(d, take)
    if t.get("origem") == "REUSO": return f"{take} é REUSO ({t.get('reuso_id')}): nada a gerar"
    if t.get("modelo") == "ffmpeg-foto-animada": return f"{take} é foto animada: use sm animar-foto"
    modelo, res = ("fast", "720p") if modo == "teste" else _modelo_final(t)
    pasta = criativo_dir(cid) / "tomadas" / ("teste" if modo == "teste" else "final")
    saida = pasta / f"{take}_{'t' if modo == 'teste' else 'f'}{tentativa}.mp4"
    if saida.exists(): return f"{rel(saida)} já existe (use --tentativa 2)"
    if modo == "teste" and tentativa > 2: raise SystemExit("máximo de 2 tomadas de teste por take (fatos.tecnica.regra_custo)")
    ini = criativo_dir(cid) / "quadros" / f"{take}_inicio.png"
    fim = criativo_dir(cid) / "quadros" / f"{take}_fim.png"
    if not ini.exists(): raise SystemExit(f"falta {rel(ini)} (sm quadro gerar)")
    p = prompt_veo(cid, take)
    pr = precos()
    custo = 8 * float(pr[f"veo_{modelo}_{res}_por_s" if modelo != "padrao" else "veo_padrao_por_s"])
    nome = f"{MODELOS_VEO[modelo]} · 8s {res} 9:16 s/ áudio"
    if seco:
        pasta.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x282c3c:s=720x1280:d=8:r=24", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(saida)], check=True)
        C.registrar(cid, MODELOS_VEO[modelo], f"8s {res} (simulado)", 0.0, rel(saida), seco=True)
        return f"SECO: {rel(saida)} (custo simulado US$ {custo:.2f}, cobrado 0)"
    bloq = C.checar_teto(cid, custo)
    if bloq: raise SystemExit(bloq)
    if not confirmar:
        return f"SIMULAÇÃO: {nome} · prompt {rel(p)} · início {ini.name}{' + fim ' + fim.name if fim.exists() else ''} · custo US$ {custo:.2f} · gasto {C.gasto_de(cid):.2f}/{C.teto_de(cid):.2f}. Repita com --confirmar."
    from google.genai import types
    c, loc = cliente()
    img = lambda q: types.Image(image_bytes=q.read_bytes(), mime_type="image/png")
    prompt = "\n".join(l for l in p.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#")).strip()
    cfg = dict(aspect_ratio="9:16", resolution=res, duration_seconds=8, number_of_videos=1, generate_audio=False, person_generation="allow_adult")
    if fim.exists(): cfg["last_frame"] = img(fim)
    op = c.models.generate_videos(model=MODELOS_VEO[modelo], prompt=prompt, image=img(ini), config=types.GenerateVideosConfig(**cfg))
    t0 = time.time()
    while not op.done:
        if time.time() - t0 > 900: raise SystemExit("tempo esgotado: confira o console antes de repetir")
        time.sleep(10); op = c.operations.get(op)
    if getattr(op, "error", None): raise SystemExit(f"erro do Veo: {op.error}")
    resp = op.response or op.result
    vids = getattr(resp, "generated_videos", None) or []
    if not vids:
        C.registrar(cid, MODELOS_VEO[modelo], f"8s {res} BLOQUEADA pelo filtro ({getattr(resp, 'rai_media_filtered_reasons', None)}), sem custo", 0.0, rel(saida))
        raise SystemExit("nenhum vídeo devolvido (filtro de segurança): sem cobrança; devolva ao chefe de linha")
    pasta.mkdir(parents=True, exist_ok=True)
    v = vids[0].video
    if getattr(v, "video_bytes", None): saida.write_bytes(v.video_bytes)
    else: c.files.download(file=v); v.save(str(saida))
    C.registrar(cid, f"{MODELOS_VEO[modelo]} (Vertex {loc})", f"8s {res} 9:16 s/ áudio", custo, rel(saida))
    return f"OK: {rel(saida)} · US$ {custo:.2f} · gasto {C.gasto_de(cid):.2f}/{C.teto_de(cid):.2f}{C.alerta_80(cid)}"
