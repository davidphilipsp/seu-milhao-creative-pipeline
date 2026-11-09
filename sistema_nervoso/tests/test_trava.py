import pytest
from sm import trava, fluxo as F
from sm.gerar import quadro, veo


@pytest.fixture
def estado_restaurado():
    g = F.estado_global(); antes = (g.get("geracao_liberada"), g.get("geracao_liberada_para"))
    yield
    g = F.estado_global(); g["geracao_liberada"], g["geracao_liberada_para"] = antes; F.gravar_global(g)


def test_trava_bloqueia_mesmo_com_confirmar(estado_restaurado):
    trava.travar()
    with pytest.raises(SystemExit) as e:
        quadro("SECO-DEMO", "T1", confirmar=True)
    assert str(e.value) == trava.MENSAGEM
    with pytest.raises(SystemExit) as e:
        veo("SECO-DEMO", "T1", modo="teste", confirmar=True)
    assert str(e.value) == trava.MENSAGEM


def test_liberacao_vale_so_para_o_id(estado_restaurado):
    trava.liberar("OUTRO-ID")
    assert trava.liberada_para("OUTRO-ID") and not trava.liberada_para("SECO-DEMO")
    with pytest.raises(SystemExit) as e:
        quadro("SECO-DEMO", "T1", confirmar=True)
    assert str(e.value) == trava.MENSAGEM
    trava.liberar("SECO-DEMO")
    assert trava.liberada_para("SECO-DEMO") and not trava.liberada_para("OUTRO-ID")
