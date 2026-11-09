"""Linter de política, determinístico: proibidos de fatos.json, fatos divergentes, rodapé ausente, data/valor errados."""
import json, pathlib, re
from dataclasses import dataclass, asdict
from .memoria import fatos, fato


@dataclass
class Violacao:
    tipo: str        # proibido | fato_divergente | rodape_ausente | susep_errado
    id: str
    linha: int
    trecho: str
    motivo: str
    substituir: str | None = None


def _linhas(texto: str):
    for i, l in enumerate(texto.splitlines(), 1):
        yield i, l


def _valor_premio_ok(num: str) -> bool:
    n = re.sub(r"[^\d]", "", num)
    return n in ("100000",)


def lint_texto(texto: str, exigir_rodape: bool = False) -> list[Violacao]:
    f = fatos()
    v: list[Violacao] = []
    for p in f["proibidos"]["lista"]:
        rx = re.compile(p["regex"], re.I)
        for i, l in _linhas(texto):
            for m in rx.finditer(l):
                sub = p.get("substituir")
                if sub and "." in sub and not sub.startswith("R$"):
                    try: sub = fato(sub)
                    except KeyError: pass
                v.append(Violacao("proibido", p["id"], i, m.group(0), p["motivo"], sub))
    # valores de prêmio: qualquer "R$ N" com N em milhares diferente de 100.000 em contexto de prêmio/concorre
    rx_premio = re.compile(r"(concorr\w*|pr[eê]mio\w*|ganh\w*|mil reais|cem mil|R\$\s?[\d\.]{4,})", re.I)
    rx_valor = re.compile(r"R\$\s?(\d{1,3}(?:\.\d{3})+|\d{4,})(?:,\d{2})?")
    for i, l in _linhas(texto):
        if rx_premio.search(l):
            for m in rx_valor.finditer(l):
                if not _valor_premio_ok(m.group(1)) and m.group(1).replace(".", "") not in ("0",):
                    val = m.group(1).replace(".", "")
                    if val in ("5000", "1000", "200"):
                        v.append(Violacao("fato_divergente", "promocao_comercial", i, m.group(0), "prêmios da promoção comercial estão bloqueados (fatos.produto.promocao_comercial)"))
                    elif int(val) >= 1000:
                        v.append(Violacao("fato_divergente", "premio", i, m.group(0), f"prêmio é {fato('produto.premio')} (fatos.produto.premio)"))
    # "cem mil" por extenso é ok; "um milhão" como prêmio é divergente
    for i, l in _linhas(texto):
        if re.search(r"\b(um|1) milh[aã]o\b", l, re.I) and re.search(r"concorr|pr[eê]mio|ganh|sorte", l, re.I):
            v.append(Violacao("fato_divergente", "premio", i, "um milhão", f"prêmio é {fato('produto.premio')}, não um milhão (o nome do produto é Seu Milhão)"))
    # datas de sorteio diferentes de 29/11
    data_ok = fato("produto.sorteio_data")  # 29/11/2026
    dia_mes = data_ok[:5]
    for i, l in _linhas(texto):
        if re.search(r"sorteio|resultado|dia do|no dia", l, re.I):
            for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", l):
                dm = f"{int(m.group(1)):02d}/{int(m.group(2)):02d}"
                if dm != dia_mes:
                    v.append(Violacao("fato_divergente", "sorteio_data", i, m.group(0), f"data do sorteio é {data_ok} (fatos.produto.sorteio_data)"))
            for m in re.finditer(r"\b(\d{1,2}) de (janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b", l, re.I):
                if not (m.group(1) == "29" and m.group(2).lower() == "novembro"):
                    v.append(Violacao("fato_divergente", "sorteio_data", i, m.group(0), f"data do sorteio é {data_ok}"))
    # número SUSEP
    susep = fato("produto.susep_processo")
    for i, l in _linhas(texto):
        for m in re.finditer(r"\b\d{5}\.\d{6}/\d{4}-\d{2}\b", l):
            if m.group(0) not in (susep, fato("produto.susep_processo_promocao")):
                v.append(Violacao("susep_errado", "susep", i, m.group(0), f"processo SUSEP do título é {susep}"))
    if exigir_rodape:
        rod = fato("redacoes_fixas.rodape")
        if rod not in texto and fato("redacoes_fixas.rodape_sem_numero") not in texto:
            v.append(Violacao("rodape_ausente", "rodape", 0, "", "rodapé legal ausente (fatos.redacoes_fixas.rodape)"))
    return v


def lint_arquivo(p: pathlib.Path, exigir_rodape: bool = False) -> list[Violacao]:
    texto = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        # lint só nos textos: falas, texto_tela, copies, descrições
        d = json.loads(texto)
        partes = []
        def coleta(x):
            if isinstance(x, dict):
                for k, val in x.items():
                    if k in ("texto", "texto_tela", "titulo", "apoio", "fala", "copy", "descricao", "enfase"):
                        if isinstance(val, str): partes.append(val)
                    coleta(val)
            elif isinstance(x, list):
                for y in x: coleta(y)
        coleta(d)
        texto = "\n".join(partes)
    return lint_texto(texto, exigir_rodape)


def formatar(vs: list[Violacao]) -> str:
    if not vs:
        return "lint OK: nenhuma violação"
    out = [f"lint: {len(vs)} violação(ões)"]
    for x in vs:
        s = f"  L{x.linha} [{x.tipo}:{x.id}] '{x.trecho}' — {x.motivo}"
        if x.substituir: s += f" → use: {x.substituir}"
        out.append(s)
    return "\n".join(out)
