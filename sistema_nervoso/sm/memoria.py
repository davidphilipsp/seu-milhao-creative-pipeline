"""memoria/fatos.json e glossario.json: fonte única de verdade. `sm fato <chave>`."""
import functools, pathlib
from .raiz import raiz, ler_json

CAMPOS_FOLHA = ("valor", "fonte", "data")


@functools.lru_cache(maxsize=1)
def fatos() -> dict:
    return ler_json(raiz() / "memoria" / "fatos.json")


@functools.lru_cache(maxsize=1)
def glossario() -> dict:
    return ler_json(raiz() / "memoria" / "glossario.json")


def limpar_cache():
    fatos.cache_clear(); glossario.cache_clear()


def e_folha(d) -> bool:
    return isinstance(d, dict) and "valor" in d and "fonte" in d


def fato(chave: str, so_valor: bool = True):
    """Resolve 'produto.premio' → folha (ou só o valor). Chave parcial devolve o ramo."""
    no = fatos()
    for parte in chave.split("."):
        if not isinstance(no, dict) or parte not in no:
            raise KeyError(f"fato não encontrado: {chave}")
        no = no[parte]
    if so_valor and e_folha(no):
        return no["valor"]
    return no


def folhas(no=None, prefixo=""):
    """Itera (chave, folha) por todos os fatos."""
    if no is None:
        no = fatos()
    for k, v in no.items():
        if k.startswith("_") or k in ("versao", "atualizado"):
            continue
        ch = f"{prefixo}{k}"
        if e_folha(v):
            yield ch, v
        elif isinstance(v, dict):
            yield from folhas(v, ch + ".")


def validar_fatos() -> list[str]:
    """Nenhum fato sem fonte/data; proibidos com regex válida; pendências com dono e status."""
    import re
    erros = []
    f = fatos()
    for ch, folha in folhas():
        for c in CAMPOS_FOLHA:
            if not folha.get(c):
                erros.append(f"{ch}: sem '{c}'")
    for p in f.get("proibidos", {}).get("lista", []):
        for c in ("id", "regex", "motivo"):
            if c not in p:
                erros.append(f"proibidos.{p.get('id','?')}: sem '{c}'")
        try:
            re.compile(p.get("regex", ""), re.I)
        except re.error as e:
            erros.append(f"proibidos.{p.get('id')}: regex inválida ({e})")
    for k, v in f.get("pendencias", {}).items():
        if not isinstance(v, dict) or not v.get("dono") or not v.get("status"):
            erros.append(f"pendencias.{k}: sem dono/status")
    g = glossario()
    for k in ("taxonomia_8_campos", "esqueleto_6_movimentos", "personas", "segmentos", "tags", "ligacoes"):
        if k not in g:
            erros.append(f"glossario: falta '{k}'")
    if len(g.get("taxonomia_8_campos", {}).get("campos", [])) != 8:
        erros.append("glossario: taxonomia não tem 8 campos")
    if len(g.get("esqueleto_6_movimentos", {}).get("movimentos", [])) != 6:
        erros.append("glossario: esqueleto não tem 6 movimentos")
    return erros


def tags_validas() -> dict:
    return glossario()["tags"]
