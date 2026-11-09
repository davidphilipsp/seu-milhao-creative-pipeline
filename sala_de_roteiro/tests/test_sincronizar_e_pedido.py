"""sincronizar: copia, grava hash e histórico; o hash muda quando a produção muda. pedido: interpreta o texto."""
import io
import json
import shutil
import zipfile

from sala_de_roteiro.ferramentas import sincronizar as S
from sala_de_roteiro.ferramentas.cli import interpretar
from sala_de_roteiro.tests.conftest import SALA


def _producao(tmp_path):
    p = tmp_path / "prod"
    pares = {"memoria/fatos.json": "fatos.snapshot.json", "memoria/glossario.json": "glossario.snapshot.json",
             "memoria/calibracao.json": "calibracao.snapshot.json", "planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md": "modelo_roteiro.snapshot.md",
             "docs/01_PLAYBOOK_RESUMO.md": "playbook_resumo.snapshot.md", "planejamento/segmentos/popular.md": "segmentos/popular.md",
             "estilos/realismo-celular/licoes.md": "estilos/realismo-celular/licoes.md"}
    for dst, src in pares.items():
        (p / dst).parent.mkdir(parents=True, exist_ok=True); shutil.copy(SALA / "insumos" / src, p / dst)
    (p / "biblioteca").mkdir(); (p / "biblioteca/catalogo.json").write_text(json.dumps({"itens": [{"id": "x", "tipo": "video", "status": "liberado", "tags": {}}]}))
    c = p / "fontes/corpus"; c.mkdir(parents=True)
    (c / "ROTEIROS - Atemporal.pdf").write_bytes(b"%PDF fake"); (c / "Mensagem Texto - Comunidade.pdf").write_bytes(b"%PDF fake")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", "<w:p><w:t>Painho com um calendário</w:t></w:p>")
    (c / "Meta - Comunidade.docx").write_bytes(buf.getvalue())
    return p


def test_sincronizar_hash_e_desatualizacao(tmp_path, monkeypatch):
    prod, sala = _producao(tmp_path), tmp_path / "sala_de_roteiro"
    sala.mkdir()
    monkeypatch.setenv("SALA_RAIZ", str(sala)); monkeypatch.setenv("SALA_PRODUCAO", str(prod))
    monkeypatch.setattr(S, "_texto_pdf", lambda p: "texto do pdf")
    S.sincronizar()
    m1 = json.loads((sala / "insumos/MANIFESTO.json").read_text())
    assert (sala / "insumos/limites_producao.md").exists()
    assert "Painho com um calendário" in (sala / "insumos/corpus/meta_comunidade.txt").read_text()
    assert (sala / "insumos/historico" / f"{m1['hash']}.json").exists()
    S.sincronizar()
    assert json.loads((sala / "insumos/MANIFESTO.json").read_text())["hash"] == m1["hash"]  # determinístico
    (prod / "estilos/realismo-celular/licoes.md").write_text("- lição nova\n")
    S.sincronizar()
    m2 = json.loads((sala / "insumos/MANIFESTO.json").read_text())
    assert m2["hash"] != m1["hash"] and "lição nova" in (sala / "insumos/limites_producao.md").read_text()


def test_sincronizar_para_sem_corpus(tmp_path, monkeypatch):
    prod, sala = _producao(tmp_path), tmp_path / "sala_de_roteiro"
    sala.mkdir(); shutil.rmtree(prod / "fontes/corpus"); (prod / "fontes/corpus").mkdir()
    monkeypatch.setenv("SALA_RAIZ", str(sala)); monkeypatch.setenv("SALA_PRODUCAO", str(prod))
    try:
        S.sincronizar(); assert False
    except SystemExit as e:
        assert "corpus incompleto" in str(e)


def test_pedido_interpreta_o_texto():
    d = interpretar("segmento popular, ângulo solidário, destino grupo, 30 s, 3 cascas")
    assert d == {"segmento": "popular", "angulo": "solidario", "destino": "grupo", "duracao_s": 30, "quantidade": 3, "personas": []}
