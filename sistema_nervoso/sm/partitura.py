"""partitura.json: falas exatas, duração pela calibração, respiros, texto de tela, ênfase, taxonomia."""
from .raiz import raiz, criativo_dir, ler_json
from .memoria import glossario
from .lint import lint_arquivo

TOLERANCIA = 0.20  # ±20% na duração estimada da fala


def pps() -> tuple[float, str]:
    c = raiz() / "memoria" / "calibracao.json"
    if c.exists():
        d = ler_json(c); return float(d["palavras_por_s"]), d.get("origem", "?")
    return 2.4, "estimativa"


def total_s(p: dict) -> float:
    return round(sum(float(f.get("duracao_s", 0)) + float(f.get("respiro_s", 0)) for f in p["falas"]), 2)


def validar(cid) -> list[str]:
    arq = criativo_dir(cid) / "partitura.json"
    if not arq.exists(): return ["falta partitura.json"]
    p = ler_json(arq)
    e = []
    for k in ("criativo", "duracao_max_s", "falas", "taxonomia"):
        if k not in p: e.append(f"sem campo '{k}'")
    if e: return e
    g = glossario()
    campos_tax = {c["id"] for c in g["taxonomia_8_campos"]["campos"]}
    falt = campos_tax - set(p["taxonomia"].keys())
    if falt: e.append(f"taxonomia sem campos: {sorted(falt)}")
    v, origem = pps()
    ids = set()
    for f in p["falas"]:
        fid = f.get("id", "?")
        if fid in ids: e.append(f"fala {fid} duplicada")
        ids.add(fid)
        for k in ("id", "movimento", "texto", "duracao_s", "respiro_s", "texto_tela", "enfase"):
            if k not in f: e.append(f"fala {fid}: sem '{k}'")
        if "texto" not in f: continue
        n = len(f["texto"].split())
        if f.get("palavras") not in (None, n): e.append(f"fala {fid}: palavras={f.get('palavras')} mas o texto tem {n}")
        if n:
            est = n / v
            if not (est * (1 - TOLERANCIA) <= float(f.get("duracao_s", 0)) <= est * (1 + TOLERANCIA) + 0.3):
                e.append(f"fala {fid}: duracao_s {f.get('duracao_s')} fora de {est*(1-TOLERANCIA):.1f}–{est*(1+TOLERANCIA)+0.3:.1f} s ({n} palavras a {v} p/s, {origem})")
        elif float(f.get("duracao_s", 0)) <= 0:
            e.append(f"fala {fid}: sem texto e sem duração (plano mudo precisa de duracao_s)")
        if not (0 <= float(f.get("respiro_s", 0)) <= 1.5): e.append(f"fala {fid}: respiro_s fora de 0–1,5")
        mv = f.get("movimento")
        if mv not in range(1, 7): e.append(f"fala {fid}: movimento {mv} inválido")
        if mv in g["esqueleto_6_movimentos"]["suspensos_nivel_1"] and not f.get("movimento_liberado"):
            e.append(f"fala {fid}: movimento {mv} suspenso no nível 1 (marque movimento_liberado=true com o motivo)")
        if f.get("enfase") and f["enfase"].lower() not in f["texto"].lower(): e.append(f"fala {fid}: ênfase '{f['enfase']}' não está no texto")
    tot = total_s(p)
    if tot > float(p["duracao_max_s"]) + 0.01: e.append(f"total {tot} s > duracao_max_s {p['duracao_max_s']}")
    vs = lint_arquivo(arq)
    e += [f"lint L{x.linha} [{x.id}] '{x.trecho}': {x.motivo}" for x in vs]
    return e
