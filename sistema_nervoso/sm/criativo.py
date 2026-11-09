"""Abre criativos/<id>/ (um worktree por criativo)."""
from .raiz import raiz, criativo_dir, agora, gravar_json
from .fluxo import estado_global, gravar_global
from .custo import CABECALHO

SUBPASTAS = ["esteira", "prompts", "quadros", "tomadas/teste", "tomadas/final", "inspecao", "aprovados"]


def novo(cid, titulo, teto=45.0, atual=True):
    d = criativo_dir(cid)
    if (d / "estado.json").exists():
        return f"{cid} já existe"
    for s in SUBPASTAS: (d / s).mkdir(parents=True, exist_ok=True)
    (raiz() / "ponte_capcut" / cid).mkdir(parents=True, exist_ok=True)
    est = {"id": cid, "titulo": titulo, "criado": agora(), "teto_usd": float(teto), "gasto_usd": 0.0, "tokens": 0,
           "passos": {}, "takes": {}, "ajustes": {"manter": "", "mudar": "", "nunca": ""}, "eventos": [], "publicado": None, "custo_fechado": None}
    gravar_json(d / "estado.json", est)
    (d / "custos.md").write_text(f"# Custos · {cid} · {titulo}\n\nTeto: US$ {float(teto):.2f} (alerta a 80%).\n\n{CABECALHO}", encoding="utf-8")
    if atual:
        g = estado_global(); g["criativo_atual"] = cid; gravar_global(g)
    return f"OK: criativos/{cid}/ aberto (teto US$ {float(teto):.2f}); P01 = cartão em planejamento/cartoes/{cid}.json"
