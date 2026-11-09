"""decupagem.json: takes alinhados às falas, enquadramento, ligação, REUSO/GERAR, estilo."""
from .raiz import raiz, criativo_dir, ler_json
from .memoria import glossario
from . import partitura as P

LIGACOES = ("abertura", "continuidade_direta", "corte_casado", "corte_seco", "fecho")


def carregar(cid):
    return ler_json(criativo_dir(cid) / "decupagem.json")


def validar(cid) -> list[str]:
    arq = criativo_dir(cid) / "decupagem.json"
    if not arq.exists(): return ["falta decupagem.json"]
    d = ler_json(arq)
    e = [f"sem campo '{k}'" for k in ("criativo", "estilo", "takes") if k not in d]
    if e: return e
    if not (raiz() / "estilos" / d["estilo"] / "bloco.txt").exists(): e.append(f"estilo '{d['estilo']}' sem pacote (estilos/{d['estilo']}/bloco.txt)")
    g = glossario(); tags = g["tags"]
    parq = criativo_dir(cid) / "partitura.json"
    falas = {f["id"]: f for f in ler_json(parq)["falas"]} if parq.exists() else {}
    cobertas, t_ant, soma, ids = set(), None, 0.0, set()
    for i, t in enumerate(d["takes"]):
        tid = t.get("id", f"#{i}")
        if tid in ids: e.append(f"take {tid} duplicado")
        ids.add(tid)
        for k in ("id", "falas", "inicio_s", "duracao_s", "descricao", "enquadramento", "ligacao", "tags", "modelo"):
            if k not in t: e.append(f"take {tid}: sem '{k}'")
        if "falas" not in t: continue
        for fid in t["falas"]:
            if falas and fid not in falas: e.append(f"take {tid}: fala {fid} não existe na partitura")
            cobertas.add(fid)
        if t.get("ligacao") not in LIGACOES: e.append(f"take {tid}: ligação '{t.get('ligacao')}' inválida ({LIGACOES})")
        if t.get("ligacao") == "corte_casado" and not t.get("casa_com"): e.append(f"take {tid}: corte casado sem 'casa_com'")
        if i == 0 and t.get("ligacao") != "abertura": e.append(f"take {tid}: o primeiro take deve ter ligação 'abertura'")
        if t.get("origem") not in (None, "GERAR", "REUSO"): e.append(f"take {tid}: origem inválida")
        if not (1.0 <= float(t.get("duracao_s", 0)) <= 8.0): e.append(f"take {tid}: duracao_s fora de 1–8 s")
        for k, vals in (t.get("tags") or {}).items():
            if k not in tags: e.append(f"take {tid}: tag '{k}' fora do glossário"); continue
            for v in (vals if isinstance(vals, list) else [vals]):
                if v not in tags[k]: e.append(f"take {tid}: valor '{v}' fora do vocabulário de '{k}' (glossario.json)")
        if t.get("modelo") not in tags["modelo"]: e.append(f"take {tid}: modelo '{t.get('modelo')}' fora do vocabulário")
        if t_ant is not None:
            esperado = float(t_ant["inicio_s"]) + float(t_ant["duracao_s"])
            if abs(float(t.get("inicio_s", 0)) - esperado) > 0.11: e.append(f"take {tid}: inicio_s {t.get('inicio_s')} ≠ fim do anterior {esperado:.2f}")
        soma += float(t.get("duracao_s", 0)); t_ant = t
    if falas:
        falt = set(falas) - cobertas
        if falt: e.append(f"falas sem take: {sorted(falt)}")
        tot = P.total_s(ler_json(parq))
        if abs(soma - tot) > 1.0: e.append(f"soma dos takes {soma:.2f} s ≠ total da partitura {tot:.2f} s (±1 s)")
    return e
