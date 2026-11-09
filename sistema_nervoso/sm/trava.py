"""Trava de geração: nada paga roda com a trava fechada, mesmo com --confirmar. Só o usuário libera, um criativo por vez."""
from .fluxo import estado_global, gravar_global

MENSAGEM = "geração travada: aguardando roteiro aprovado"


def liberada_para(cid: str) -> bool:
    g = estado_global()
    return bool(g.get("geracao_liberada")) and g.get("geracao_liberada_para") == cid


def exigir(cid: str):
    if not liberada_para(cid):
        raise SystemExit(MENSAGEM)


def liberar(cid: str) -> str:
    g = estado_global(); g["geracao_liberada"] = True; g["geracao_liberada_para"] = cid; gravar_global(g)
    return f"geração liberada para {cid} (um criativo por vez; `sm travar-geracao` fecha)"


def travar() -> str:
    g = estado_global(); g["geracao_liberada"] = False; g["geracao_liberada_para"] = None; gravar_global(g)
    return "geração travada"
