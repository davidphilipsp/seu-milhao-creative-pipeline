import re, shutil, pytest
from sm.raiz import raiz, criativo_dir, ler_json
from sm.roteiro import importar, validar, parse

MODELO = raiz() / "planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md"


@pytest.fixture(scope="module")
def exemplo(tmp_path_factory):
    md = MODELO.read_text(encoding="utf-8")
    ex = md.split("# EXEMPLO", 1)[1]
    p = tmp_path_factory.mktemp("rot") / "exemplo.md"; p.write_text("# ROTEIRO\n" + ex, encoding="utf-8")
    shutil.rmtree(criativo_dir("EXEMPLO-01"), ignore_errors=True)
    yield p
    shutil.rmtree(criativo_dir("EXEMPLO-01"), ignore_errors=True)
    (raiz() / "ponte_capcut" / "EXEMPLO-01").rmdir() if (raiz() / "ponte_capcut" / "EXEMPLO-01").exists() else None


def test_parse_exemplo(exemplo):
    d = parse(exemplo.read_text(encoding="utf-8"))
    assert d["cabecalho"]["id"] == "EXEMPLO-01" and len(d["quadros"]) == 3 and len(d["taxonomia"]) == 8
    assert "Vem com a gente" in d["narracao"]


def test_importar_gera_partitura_e_decupagem(exemplo):
    msg = importar(exemplo)
    assert "importado EXEMPLO-01: 3 quadros" in msg
    part = ler_json(criativo_dir("EXEMPLO-01") / "partitura.json"); dec = ler_json(criativo_dir("EXEMPLO-01") / "decupagem.json")
    assert [f["movimento"] for f in part["falas"]] == [2, 4, 6]
    assert dec["takes"][0]["ligacao"] == "abertura" and dec["takes"][1]["ligacao"] == "corte_casado" and dec["takes"][2]["ligacao"] == "corte_seco"
    assert dec["takes"][1]["origem"] == "REUSO" and "apresentador" in dec["takes"][2]["tags"]["elemento"]
    assert all(f["duracao_s"] > 0 for f in part["falas"])


def test_validar_roteiro_relatorio(exemplo):
    importar(exemplo)
    rel = validar("EXEMPLO-01")
    assert rel.startswith("ROTEIRO EXEMPLO-01: 3 quadros") and len(rel.splitlines()) <= 10
    assert "custo estimado US$" in rel and "NADA gerado" in rel
    v = ler_json(criativo_dir("EXEMPLO-01") / "esteira" / "validacao_roteiro.json")
    assert not any("criança" in b for b in v["bloqueios"])
    assert any("termo_apresentador" in a for a in v["avisos"])
    assert any("ritmo" in a for a in v["avisos"])  # frases longas estouram 2 s por quadro de IA


def test_validar_bloqueia_crianca_em_ia(exemplo, tmp_path):
    md = exemplo.read_text(encoding="utf-8").replace("| 1 | Tem gente", "| 1 | Tem gente").replace("feirante, mulher de 50 anos", "criança de 6 anos")
    p = tmp_path / "ruim.md"; p.write_text(md.replace("EXEMPLO-01", "EXEMPLO-02"), encoding="utf-8")
    importar(p, "EXEMPLO-02")
    v_txt = validar("EXEMPLO-02")
    assert "criança em origem IA" in v_txt
    shutil.rmtree(criativo_dir("EXEMPLO-02"), ignore_errors=True)
