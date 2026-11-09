import pathlib
import shutil

import pytest

SALA = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def sala(tmp_path, monkeypatch):
    """cópia isolada da sala (insumos, hooks, pedido P-001, casca C-001-A) num diretório temporário."""
    s = tmp_path / "sala_de_roteiro"
    shutil.copytree(SALA / "insumos", s / "insumos")
    shutil.copytree(SALA / "hooks", s / "hooks")
    (s / "pedidos").mkdir(parents=True)
    shutil.copy(SALA / "pedidos" / "P-001.md", s / "pedidos" / "P-001.md")
    for p in ("cascas/rascunho", "cascas/aprovadas", "saida"):
        (s / p).mkdir(parents=True)
    shutil.copy(SALA / "tests" / "exemplos" / "casca_valida.md", s / "cascas" / "rascunho" / "EX-OK.md")
    monkeypatch.setenv("SALA_RAIZ", str(s))
    return s
