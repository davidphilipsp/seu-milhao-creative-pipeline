import pytest
from sm.lint import lint_texto
from sm.memoria import fatos, fato

CASOS = [
    ("ganhe", "Ganhe um prêmio hoje", "concorre"),
    ("aposta", "Faça sua aposta", None),
    ("ganho_certo", "aqui é ganho certo", None),
    ("transformar_vida", "vai transformar sua vida", "concorrer a R$ 100.000"),
    ("vai_direto", "o dinheiro vai direto pra quem precisa", fato("redacoes_fixas.destinacao")),
    ("cota_bilhete", "compre sua cota", "título"),
    ("socio_patrocinador", "somos patrocinadores da Instituição", "parceiro"),
    ("nao_perde_nunca", "aqui você não perde nunca", None),
    ("pix_premio", "prêmio de R$ 100.000 no Pix", None),
    ("sorteio_emissora", "sorteio realizado pela Emissora", fato("redacoes_fixas.sorteio_texto")),
    ("loteria_como_nome", "entra na nossa loteria", "título"),
    ("investimento", "um ótimo investimento", None),
    ("atributo_segunda_pessoa", "você que está endividado", None),
]


@pytest.mark.parametrize("pid,texto,sub", CASOS)
def test_cada_proibido_e_pego(pid, texto, sub):
    vs = [v for v in lint_texto(texto) if v.tipo == "proibido" and v.id == pid]
    assert vs, f"{pid} não foi pego em: {texto}"
    assert vs[0].substituir == sub


def test_todos_os_proibidos_do_fatos_tem_caso():
    ids = {p["id"] for p in fatos()["proibidos"]["lista"]}
    assert ids == {c[0] for c in CASOS}


def test_texto_limpo_passa():
    t = ("Apresentador convida: vem com a gente. Você concorre a R$ 100.000 no dia 29/11. "
         "Parte da sua compra apoia o trabalho da Instituição Parceira, que cuida de crianças com câncer. "
         "O resultado sai da Loteria Federal. Cada título conta.")
    assert lint_texto(t) == []


def test_fatos_divergentes():
    assert any(v.id == "premio" for v in lint_texto("concorra a R$ 50.000 hoje"))
    assert any(v.id == "promocao_comercial" for v in lint_texto("prêmio de R$ 5.000 na hora"))
    assert any(v.id == "sorteio_data" for v in lint_texto("sorteio no dia 30/11"))
    assert any(v.id == "sorteio_data" for v in lint_texto("o resultado sai dia 14 de outubro"))
    assert any(v.id == "susep" for v in lint_texto("Processo SUSEP 12345.678901/2026-99"))
    assert any(v.id == "premio" for v in lint_texto("concorra a um milhão"))


def test_rodape_ausente_e_presente():
    assert any(v.tipo == "rodape_ausente" for v in lint_texto("texto sem rodapé", exigir_rodape=True))
    assert not any(v.tipo == "rodape_ausente" for v in lint_texto(fato("redacoes_fixas.rodape"), exigir_rodape=True))


def test_texto_com_5_violacoes():
    t = ("Ganhe agora! Faça sua aposta e compre sua cota.\n"
         "Nosso patrocinador garante: aqui você não perde nunca.")
    vs = lint_texto(t)
    assert len({v.id for v in vs}) >= 5
