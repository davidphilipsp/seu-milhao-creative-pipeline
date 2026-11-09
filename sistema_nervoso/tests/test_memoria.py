from sm import memoria


def test_fatos_sem_erros():
    assert memoria.validar_fatos() == []


def test_fato_valor_e_folha():
    assert memoria.fato("produto.premio").startswith("R$ 100.000")
    folha = memoria.fato("produto.premio", so_valor=False)
    assert folha["fonte"] and folha["data"]


def test_fato_inexistente():
    import pytest
    with pytest.raises(KeyError):
        memoria.fato("produto.nao_existe")


def test_glossario_tem_8_campos_e_6_movimentos():
    g = memoria.glossario()
    assert len(g["taxonomia_8_campos"]["campos"]) == 8
    assert [m["n"] for m in g["esqueleto_6_movimentos"]["movimentos"]] == [1, 2, 3, 4, 5, 6]
    assert 5 in g["esqueleto_6_movimentos"]["suspensos_nivel_1"]
