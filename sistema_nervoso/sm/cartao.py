"""Cartão de criativo (planejamento/cartoes/<id>.json)."""
from .raiz import raiz
from .memoria import glossario

CAMPOS = ["id", "titulo", "segmento", "angulo", "estilo", "duracao_max_s", "personas", "hipotese", "teto_usd", "status"]


def validar_cartao(c: dict) -> list[str]:
    g = glossario()
    e = [f"sem campo '{k}'" for k in CAMPOS if k not in c]
    if e: return e
    if c["segmento"] not in g["tags"]["segmento"]: e.append(f"segmento '{c['segmento']}' fora do glossário")
    if c["angulo"] not in g["tags"]["angulo"]: e.append(f"ângulo '{c['angulo']}' fora do glossário")
    if c["estilo"] != "a definir" and not (raiz() / "estilos" / c["estilo"] / "bloco.txt").exists(): e.append(f"estilo '{c['estilo']}' sem pacote em estilos/")
    if not (0 < float(c["duracao_max_s"]) <= 30): e.append("duracao_max_s deve estar entre 1 e 30")
    if not isinstance(c["personas"], list): e.append("personas deve ser lista")
    if not isinstance(c["hipotese"], str) or len(c["hipotese"]) < 10: e.append("hipotese curta demais")
    if float(c["teto_usd"]) <= 0: e.append("teto_usd inválido")
    if c["status"] not in ("rascunho", "aprovado", "em_producao", "concluido", "arquivado"): e.append("status inválido")
    return e
