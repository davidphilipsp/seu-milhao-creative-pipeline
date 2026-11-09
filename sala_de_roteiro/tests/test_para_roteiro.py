"""Casca aprovada → saida/<id>_ROTEIRO.md no formato exato do modelo da produção."""
import re
import shutil

import pytest

from sala_de_roteiro.ferramentas.para_roteiro import converter
from sala_de_roteiro.ferramentas.validar_casca import tabela


def test_so_converte_aprovada(sala):
    with pytest.raises(SystemExit):
        converter("EX-OK", sala)


def test_formato_do_modelo(sala):
    shutil.move(sala / "cascas/rascunho/EX-OK.md", sala / "cascas/aprovadas/EX-OK.md")
    converter("EX-OK", sala)
    out = (sala / "saida" / "EX-OK_ROTEIRO.md").read_text(encoding="utf-8")
    modelo = (sala / "insumos" / "modelo_roteiro.snapshot.md").read_text(encoding="utf-8")
    cab_modelo = next(l for l in modelo.splitlines() if l.startswith("| nº |"))
    assert cab_modelo in out.splitlines()
    for sec in ("## Cabeçalho", "## Narração completa", "## Quadros"):
        assert sec in out
    for k in ("Nome", "ID", "Segmento", "Persona", "Ângulo", "Objetivo e destino", "Duração máxima (s)", "Estilo"):
        assert re.search(rf"^- {re.escape(k)}: .+", out, re.M), k
    assert len(re.findall(r"^  - ", out, re.M)) == 8  # taxonomia aninhada, como o parser da produção espera
    quadros = tabela(out.split("## Quadros", 1)[1])
    assert len(quadros) == 10  # 11 batidas, 1 suspensa
    assert quadros[0]["ligacao"] == "abertura"
    assert all(q["origem"] in ("IA", "Apresentador réplica", "foto real da Instituição", "banco de takes", "gravação real") for q in quadros)
    assert all(re.match(r"^[1-6] ", q["funcao"]) for q in quadros)
    assert "5 escalonamento" not in [q["funcao"] for q in quadros]
    assert quadros[2]["origem"] == "banco de takes"  # "padaria" contém "ia": a origem não pode cair em IA
    assert "trecho seguinte do mesmo take do quadro 2" in quadros[4]["observacoes"]
