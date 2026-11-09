from sm import fluxo as F


def test_passos_sem_ciclo_e_em_ordem():
    p = F.carregar_passos("passos.yaml")
    assert F.validar_passos(p) == []
    assert [x["id"] for x in p] == [f"P{i:02d}" for i in range(1, 19)]
    r = F.carregar_passos("reestruturacao.yaml")
    assert F.validar_passos(r) == []
    assert [x["id"] for x in r] == [f"R{i:02d}" for i in range(1, 19)]


def test_detecta_ciclo():
    p = [{"id": "A", "descricao": "a", "executor": "script", "linha": "x", "depende_de": ["B"]},
         {"id": "B", "descricao": "b", "executor": "script", "linha": "x", "depende_de": ["A"]}]
    assert any("ciclo" in e for e in F.validar_passos(p))


def test_proximo_respeita_dependencias():
    passos_reg = {"P01": {"status": "ok"}}
    p = F.proximo_passo("passos.yaml", passos_reg)
    assert p["id"] == "P02" and p["executor"] == "VOCÊ"
    assert F.proximo_passo("passos.yaml", {})["id"] == "P01"


def test_escopo():
    assert F.escopo("R05", None)[0] == "reestruturacao"
    assert F.escopo("P03", "X")[0] == "producao"
