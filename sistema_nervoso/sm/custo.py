"""Custos em US$ e tokens por criativo. Ledger: criativos/<id>/custos.md (+ custos.md global)."""
import re
from .raiz import raiz, criativo_dir, agora, hoje
from .fluxo import estado_criativo, gravar_criativo, evento
from .memoria import fato

CABECALHO = "| Data | Modelo | Detalhe | Custo | Arquivo |\n|---|---|---|---|---|\n"


def _ledger(cid):
    p = criativo_dir(cid) / "custos.md"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# Custos · {cid}\n\n{CABECALHO}", encoding="utf-8")
    return p


def gasto_de(cid) -> float:
    p = criativo_dir(cid) / "custos.md"
    tot = 0.0
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.startswith("| ") and "US$" in l and not l.startswith("| Data"):
                try: tot += float(l.split("US$")[1].split("|")[0].strip().replace(",", "."))
                except ValueError: pass
    return round(tot, 2)


def registrar(cid, modelo, detalhe, custo_usd, arquivo, seco=False):
    linha = f"| {agora().replace('T', ' ')[:16]} | {modelo} | {detalhe}{' · SECO' if seco else ''} | US$ {custo_usd:.2f} | {arquivo} |\n"
    with _ledger(cid).open("a", encoding="utf-8") as f: f.write(linha)
    g = raiz() / "custos.md"
    if g.exists() and not seco:
        with g.open("a", encoding="utf-8") as f: f.write(linha)
    est = estado_criativo(cid)
    est["gasto_usd"] = gasto_de(cid)
    gravar_criativo(cid, est)
    return linha.strip()


def teto_de(cid) -> float:
    est = estado_criativo(cid)
    return float(est.get("teto_usd") or fato("tecnica.teto_padrao_conjunto"))


def checar_teto(cid, custo_novo) -> str | None:
    """Devolve mensagem de bloqueio se estourar; aviso se passar de 80%."""
    gasto, teto = gasto_de(cid), teto_de(cid)
    if gasto + custo_novo > teto:
        return f"TETO: {gasto:.2f} + {custo_novo:.2f} > {teto:.2f}"
    return None


def alerta_80(cid) -> str:
    gasto, teto = gasto_de(cid), teto_de(cid)
    return f" ⚠️ {100*gasto/teto:.0f}% do teto" if teto and gasto >= 0.8 * teto else ""


def registrar_tokens(cid, n, nota=""):
    est = estado_criativo(cid)
    est["tokens"] = int(est.get("tokens", 0)) + int(n)
    evento(est, "tokens", {"n": n, "nota": nota})
    gravar_criativo(cid, est)
    return f"{cid}: tokens acumulados {est['tokens']}"


def resumo(cid=None):
    from .fluxo import estado_global
    cid = cid or estado_global().get("criativo_atual")
    if not cid: return "sem criativo atual"
    est = estado_criativo(cid)
    gasto, teto = gasto_de(cid), teto_de(cid)
    return f"{cid}: US$ {gasto:.2f} de {teto:.2f} ({100*gasto/teto:.0f}%) · tokens {est.get('tokens', 0)}{alerta_80(cid)}"


def fechar(cid):
    est = estado_criativo(cid)
    gasto = gasto_de(cid)
    est["custo_fechado"] = {"usd": gasto, "tokens": est.get("tokens", 0), "data": agora()}
    evento(est, "custo_fechado", est["custo_fechado"])
    gravar_criativo(cid, est)
    with _ledger(cid).open("a", encoding="utf-8") as f:
        f.write(f"\n**Fechamento {hoje()}:** US$ {gasto:.2f} · tokens {est.get('tokens', 0)}\n")
    return f"{cid} fechado: US$ {gasto:.2f} · tokens {est.get('tokens', 0)}"
