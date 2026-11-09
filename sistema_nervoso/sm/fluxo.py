"""Micro-passos: fluxo/passos.yaml (produção, por criativo) e fluxo/reestruturacao.yaml (missão), estado global e por criativo."""
import pathlib, yaml
from .raiz import raiz, ler_json, gravar_json, agora, criativo_dir

STATUS = ("pendente", "ok", "falhou", "aguardando_voce", "bloqueado")


def carregar_passos(arquivo: str) -> list[dict]:
    p = raiz() / "fluxo" / arquivo
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    return d["passos"]


def validar_passos(passos: list[dict]) -> list[str]:
    erros, ids = [], [p["id"] for p in passos]
    for p in passos:
        for c in ("id", "descricao", "executor", "linha"):
            if c not in p: erros.append(f"{p.get('id','?')}: sem '{c}'")
        for d in p.get("depende_de", []) or []:
            if d not in ids: erros.append(f"{p['id']}: depende de '{d}' inexistente")
    # ciclo
    graf = {p["id"]: list(p.get("depende_de", []) or []) for p in passos}
    estado = {}
    def visita(n):
        if estado.get(n) == 1: return True
        if estado.get(n) == 2: return False
        estado[n] = 1
        if any(visita(m) for m in graf.get(n, [])): return True
        estado[n] = 2; return False
    for n in graf:
        if visita(n): erros.append(f"ciclo de dependências envolvendo {n}"); break
    return erros


# ---------- estado global ----------
def estado_global() -> dict:
    return ler_json(raiz() / "fluxo" / "estado.json", {"criativo_atual": None, "reestruturacao": {"passos": {}}, "atualizado": None})


def gravar_global(est: dict):
    est["atualizado"] = agora()
    gravar_json(raiz() / "fluxo" / "estado.json", est)


# ---------- estado do criativo ----------
def estado_criativo(cid: str) -> dict:
    return ler_json(criativo_dir(cid) / "estado.json")


def gravar_criativo(cid: str, est: dict):
    est["atualizado"] = agora()
    est.setdefault("eventos", [])
    gravar_json(criativo_dir(cid) / "estado.json", est)


def evento(est: dict, acao: str, valor=None, origem="sm"):
    est.setdefault("eventos", []).append({"data": agora(), "acao": acao, "valor": valor, "origem": origem})


def _mapa(passos):
    return {p["id"]: p for p in passos}


def escopo(passo_id: str | None, cid: str | None):
    """Decide se o passo é da reestruturação (R..) ou de produção (P..)."""
    if passo_id and passo_id.upper().startswith("R"):
        return "reestruturacao", None
    g = estado_global()
    cid = cid or g.get("criativo_atual")
    return "producao", cid


def status_passos(arquivo: str, registro: dict) -> list[tuple[str, str, str, str]]:
    out = []
    for p in carregar_passos(arquivo):
        st = registro.get(p["id"], {}).get("status", "pendente")
        out.append((p["id"], st, p["executor"], p["descricao"]))
    return out


def proximo_passo(arquivo: str, registro: dict) -> dict | None:
    passos = carregar_passos(arquivo)
    for p in passos:
        st = registro.get(p["id"], {}).get("status", "pendente")
        if st == "ok":
            continue
        deps_ok = all(registro.get(d, {}).get("status") == "ok" for d in (p.get("depende_de") or []))
        if deps_ok or st in ("falhou", "aguardando_voce"):
            return p
    return None


def registrar(passo_id: str, status: str, nota: str | None = None, cid: str | None = None):
    esc, cid = escopo(passo_id, cid)
    if esc == "reestruturacao":
        g = estado_global()
        g.setdefault("reestruturacao", {}).setdefault("passos", {})[passo_id] = {"status": status, "data": agora(), "nota": nota}
        gravar_global(g)
    else:
        est = estado_criativo(cid)
        est.setdefault("passos", {})[passo_id] = {"status": status, "data": agora(), "nota": nota}
        evento(est, f"passo_{passo_id}", status)
        gravar_criativo(cid, est)


def registro_de(esc: str, cid: str | None) -> dict:
    if esc == "reestruturacao":
        return estado_global().get("reestruturacao", {}).get("passos", {})
    return estado_criativo(cid).get("passos", {}) if cid else {}


def falhas_consecutivas(passo_id: str, cid: str | None) -> int:
    esc, cid = escopo(passo_id, cid)
    reg = registro_de(esc, cid).get(passo_id, {})
    return int(reg.get("falhas", 0))


def marcar_falha(passo_id: str, erro: str, cid: str | None):
    esc, cid = escopo(passo_id, cid)
    if esc == "reestruturacao":
        g = estado_global(); r = g.setdefault("reestruturacao", {}).setdefault("passos", {}).setdefault(passo_id, {})
        r.update({"status": "falhou", "data": agora(), "nota": erro[:300], "falhas": int(r.get("falhas", 0)) + 1}); gravar_global(g)
    else:
        est = estado_criativo(cid); r = est.setdefault("passos", {}).setdefault(passo_id, {})
        r.update({"status": "falhou", "data": agora(), "nota": erro[:300], "falhas": int(r.get("falhas", 0)) + 1}); gravar_criativo(cid, est)
