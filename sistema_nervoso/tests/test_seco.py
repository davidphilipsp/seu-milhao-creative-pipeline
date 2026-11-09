"""Ponta a ponta A SECO: cartão fictício, P01–P18 sem gasto. Usa criativos/SECO-TESTE/ e _seco/biblioteca/."""
import json, pathlib, shutil, pytest
from sm.raiz import raiz, criativo_dir, gravar_json, ler_json
from sm import criativo, validadores as V, fluxo as F
from sm.gerar import quadro, veo
from sm.midia import inspecionar, padronizar, ultimo_quadro
from sm.montar import montar
from sm.ponte import ponte
from sm.publicar import publicar
from sm.custo import fechar, gasto_de
from sm.banco import buscar

CID = "SECO-TESTE"


def _limpar():
    shutil.rmtree(criativo_dir(CID), ignore_errors=True)
    shutil.rmtree(raiz() / "ponte_capcut" / CID, ignore_errors=True)
    shutil.rmtree(raiz() / "_seco", ignore_errors=True)
    (raiz() / "planejamento" / "cartoes" / f"{CID}.json").unlink(missing_ok=True)


@pytest.fixture(scope="module")
def seco():
    _limpar()
    g = F.estado_global(); atual = g.get("criativo_atual")
    criativo.novo(CID, "Teste a seco", 10.0, atual=False)
    gravar_json(raiz() / "planejamento/cartoes" / f"{CID}.json", {"id": CID, "titulo": "Teste a seco", "segmento": "popular", "angulo": "solidario", "estilo": "realismo-celular",
                "duracao_max_s": 12, "personas": ["P1"], "hipotese": "cartão fictício para validar a esteira sem gasto", "teto_usd": 10, "status": "aprovado"})
    gravar_json(criativo_dir(CID) / "partitura.json", {"criativo": CID, "titulo": "Teste a seco", "duracao_max_s": 12, "segmento": "popular", "angulo": "solidario",
                "taxonomia": {"angulo": "solidario", "tom": "caloroso", "hook": "visual", "gatilho": "pertencimento", "elemento": "moeda", "persona_alvo": "P1", "camada_objecao": "isso é pra mim?", "risco_politica": "baixo"},
                "falas": [{"id": "F1", "movimento": 1, "texto": "Vem com a gente.", "palavras": 4, "duracao_s": 1.7, "respiro_s": 0.4, "texto_tela": "VEM COM A GENTE", "enfase": "gente"},
                          {"id": "F2", "movimento": 2, "texto": "Cada título conta, e você concorre.", "palavras": 6, "duracao_s": 2.5, "respiro_s": 0.4, "texto_tela": "", "enfase": "concorre"}]})
    gravar_json(criativo_dir(CID) / "decupagem.json", {"criativo": CID, "estilo": "realismo-celular", "takes": [
        {"id": "T1", "falas": ["F1"], "inicio_s": 0, "duracao_s": 2.0, "descricao": "mão com a moeda", "enquadramento": "close na mão", "ligacao": "abertura", "tags": {"lugar": ["varanda"], "elemento": ["moeda", "mao"], "acao": ["estende_moeda"]}, "modelo": "veo-3.1-padrao-1080p", "titulo_tela": "VEM COM A GENTE"},
        {"id": "T2", "falas": ["F2"], "inicio_s": 2.0, "duracao_s": 2.6, "descricao": "feirante olha a moeda", "enquadramento": "três quartos, peito para cima", "ligacao": "corte_casado", "casa_com": "moeda", "tags": {"lugar": ["feira"], "elemento": ["moeda", "rosto"], "acao": ["olha_moeda", "sorri"]}, "modelo": "veo-3.1-padrao-1080p"}]})
    yield CID
    _limpar()
    g = F.estado_global(); g["criativo_atual"] = atual; g.pop("_seco_tmp", None); F.gravar_global(g)


def test_p01_a_p06(seco):
    assert V.p01_cartao(CID) == []
    assert V.p03_partitura(CID) == []
    assert V.p04_decupagem(CID) == []
    assert "GERAR" in buscar(CID)
    assert V.p05_banco(CID) == []
    gravar_json(criativo_dir(CID) / "esteira" / "auditor_G1.json", {"veredito": "carimbado", "motivo": "teste"})
    assert V.p06_auditoria(CID) == []


def test_p08_a_p13_seco(seco):
    for t in ("T1", "T2"):
        assert "SECO" in quadro(CID, t, seco=True)
    assert V.p08_quadros(CID) == []
    for t in ("T1", "T2"):
        assert "SECO" in veo(CID, t, modo="teste", seco=True)
    assert V.p10_testes(CID) == []
    out = inspecionar(CID, "teste")
    assert "ficha" in out
    assert V.p11_inspecao(CID) == [], ler_json(criativo_dir(CID) / "esteira" / "inspetor_teste.json")["erros"]
    for t in ("T1", "T2"):
        assert "SECO" in veo(CID, t, modo="final", seco=True)
    assert V.p13_finais(CID) == []
    assert gasto_de(CID) == 0.0


from sm.montar import FONTES


@pytest.mark.skipif(not (FONTES / "Anton-Regular.ttf").exists(), reason="fontes OFL (Anton, Montserrat) ausentes em biblioteca/referencias/marca/fontes")
def test_p14_a_p18_seco(seco):
    for t, tr in (("T1", "0-2"), ("T2", "0-2.6")):
        padronizar(CID, t, trecho=tr); ultimo_quadro(CID, t)
    assert "takes com copies" in montar(CID)
    assert V.p14_montagem(CID) == []
    assert "ponte" in ponte(CID)
    assert V.p16_ponte(CID) == []
    est = ler_json(criativo_dir(CID) / "estado.json"); est.setdefault("passos", {})["P15"] = {"status": "ok"}; gravar_json(criativo_dir(CID) / "estado.json", est)
    assert "SECO" in publicar(CID, seco=True)
    assert V.p17_publicacao(CID) == []
    assert "fechado" in fechar(CID)
    assert V.p18_custo(CID) == []
    assert gasto_de(CID) == 0.0
    assert (raiz() / "_seco/biblioteca/aprovados" / CID / "FICHA.md").exists()
