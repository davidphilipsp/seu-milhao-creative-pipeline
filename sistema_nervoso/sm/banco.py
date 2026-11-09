"""Banco de takes: casa a decupagem com biblioteca/catalogo.json por tags → REUSO ou GERAR."""
from .raiz import raiz, criativo_dir, ler_json, gravar_json


def catalogo():
    p = raiz() / "biblioteca" / "catalogo.json"
    return ler_json(p, {"itens": []})["itens"]


def _lista(x):
    return x if isinstance(x, list) else ([x] if x else [])


def candidatos(take, itens):
    out = []
    for i in itens:
        if i.get("tipo") != "video" or i.get("status") != "liberado": continue
        tg = i.get("tags", {})
        ok = all(set(_lista(take["tags"].get(k, []))) <= set(_lista(tg.get(k, []))) for k in ("lugar", "elemento", "acao") if take["tags"].get(k))
        if ok and take["tags"].get("lugar"): out.append(i["id"])
    return out


def buscar(cid) -> str:
    arq = criativo_dir(cid) / "decupagem.json"
    d = ler_json(arq)
    itens = catalogo()
    linhas = []
    for t in d["takes"]:
        if t.get("origem") == "REUSO" and t.get("reuso_id"):
            linhas.append(f"{t['id']}: REUSO {t['reuso_id']} (mantido)"); continue
        c = candidatos(t, itens)
        if c:
            t["origem"], t["reuso_id"] = "REUSO", c[0]
            linhas.append(f"{t['id']}: REUSO {c[0]}" + (f" (+{len(c)-1})" if len(c) > 1 else ""))
        else:
            t["origem"], t["reuso_id"] = "GERAR", None
            linhas.append(f"{t['id']}: GERAR")
    gravar_json(arq, d)
    n_r = sum(1 for t in d["takes"] if t["origem"] == "REUSO")
    return f"banco: {n_r} REUSO · {len(d['takes'])-n_r} GERAR\n" + "\n".join(linhas[:12])
