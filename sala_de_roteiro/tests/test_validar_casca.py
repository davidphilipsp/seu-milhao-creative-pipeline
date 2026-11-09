"""Uma casca válida passa; a mesma casca com 1 violação de cada tipo é barrada, cada uma com a sua mensagem."""
import json
import re

import pytest

from sala_de_roteiro.ferramentas.validar_casca import validar

# (nome, função que injeta a violação no texto da casca, trecho esperado em bloqueios ou avisos)
VIOLACOES = [
    ("seção ausente", lambda t: re.sub(r"## H · Riscos.*", "", t, flags=re.S), "seção H"),
    ("campo de câmera ausente", lambda t: re.sub(r"^- Lente:.*\n", "", t, flags=re.M), "campo 'lente'"),
    ("primeira fala longa", lambda t: t.replace('- Primeira fala: "Olha esse cheque aqui."', '- Primeira fala: "Olha esse cheque aqui que eu trouxe pra mostrar pra vocês hoje."'), "primeira fala com"),
    ("texto de tela longo", lambda t: t.replace('- Texto na tela: "O NOME TÁ EM BRANCO"', '- Texto na tela: "O NOME DESSE CHEQUE TÁ EM BRANCO"'), "texto na tela com"),
    ("lint dos fatos", lambda t: t.replace('"Concorre a cem mil."', '"Ganhe cem mil."'), "lint [ganhe]"),
    ("lint do léxico", lambda t: t.replace('"Pode ser o teu."', '"Vai cair na sua conta."'), "lint [cair_na_conta]"),
    ("fala sem matriz", lambda t: re.sub(r"^\| 4 \| o cheque encostado.*\n", "", t, flags=re.M), "#4 sem linha na matriz"),
    ("criança por IA", lambda t: t.replace("| mão do Apresentador | mesma calçada | a ponta da caneta", "| criança | mesma calçada | a ponta da caneta").replace("| Apresentador réplica | Nome: ________ |", "| IA | Nome: ________ |"), "criança em origem"),
    ("grupo gerado", lambda t: t.replace("| mão do Apresentador | mesma calçada | a caneta se afasta", "| três pessoas | mesma calçada | a caneta se afasta"), "grupo gerado"),
    ("rosto de IA na lente", lambda t: t.replace("| Apresentador | calçada, capô do carro | encosta", "| vizinho | calçada, capô do carro | encosta").replace("| médio, de três quartos, cheque e mão em primeiro plano | celular de espectador, tremor | corte seco | Apresentador réplica |", "| médio, olha para a lente | celular de espectador, tremor | corte seco | IA |"), "rosto de IA olhando"),
    ("plano longo", lambda t: t.replace('"Nome ainda em branco."', '"Nome ainda em branco nesse cheque gigante aqui."'), "> 2 s fora do plano real"),
    ("duração acima do pedido", lambda t: t.replace("pedido: P-001", "pedido: P-CURTO"), "duração"),
    ("escalonamento usado", lambda t: t.replace("| 9 | 5 | suspenso: nível 1 (escalonamento não entra; solidário fala de causa, não de volume) | — |", "| 9 | 5 | usado | volume | \"Mais títulos.\" | Apresentador | calçada | sorri | alegria | médio | celular | corte seco | Apresentador réplica (mesmo take de #10) |"), "movimento 5"),
    ("providência 2 vezes", lambda t: t.replace('"Menos que essa moeda."', '"Não apareceu por acaso."').replace('"Vem com a gente."', '"Não chegou por acaso."'), "providência mais de 1 vez"),
    ("variações da mesma família", lambda t: t.replace("- Família: pergunta", "- Família: objeto fora do lugar"), "mesma família"),
    ("gancho repetido sem declarar", lambda t: t.replace('- Primeira fala: "Falta uma coisa nesse cheque."', '- Primeira fala: "Almoço acabou. O prato daquela cadeira continua cheio."'), "repete PIL-CV-H08"),
]


def _casca(sala, texto, cid="EX-V"):
    (sala / "cascas" / "rascunho" / f"{cid}.md").write_text(texto.replace("id: EX-OK", f"id: {cid}"), encoding="utf-8")
    return cid


def _curto(sala):
    (sala / "pedidos" / "P-CURTO.md").write_text("- id: P-CURTO\n- duracao_s: 10\n", encoding="utf-8")


def test_casca_valida_passa(sala):
    r = validar("EX-OK", sala)
    assert r["status"] == "OK", r["bloqueios"]
    assert r["gerar"] == ["1", "2", "4", "10"] and r["reuso"] == ["3"]
    assert r["custo_estimado_usd"] == pytest.approx(16.28)


@pytest.mark.parametrize("nome,injeta,esperado", VIOLACOES, ids=[v[0] for v in VIOLACOES])
def test_cada_violacao_e_detectada(sala, nome, injeta, esperado):
    _curto(sala)
    base = (sala / "cascas" / "rascunho" / "EX-OK.md").read_text(encoding="utf-8")
    novo = injeta(base)
    assert novo != base, f"a injeção '{nome}' não mudou nada"
    r = validar(_casca(sala, novo), sala)
    msgs = r["bloqueios"] + r["avisos"]
    assert any(esperado in m for m in msgs), (nome, msgs)
    if esperado != "> 2 s fora do plano real":
        assert r["status"] != "OK"


def test_exemplo_com_uma_violacao_de_cada_tipo(sala):
    """a casca de exemplo exigida: todas as violações juntas, todas reportadas."""
    _curto(sala)
    t = (sala / "cascas" / "rascunho" / "EX-OK.md").read_text(encoding="utf-8")
    for _, injeta, _ in VIOLACOES:
        t = injeta(t)
    r = validar(_casca(sala, t, "EX-TODAS"), sala)
    msgs = r["bloqueios"] + r["avisos"]
    faltando = [e for _, _, e in VIOLACOES if not any(e in m for m in msgs)]
    # algumas injeções se sobrepõem (a mesma linha muda duas vezes); as que sobrevivem têm de aparecer
    assert faltando == [], faltando
    assert r["status"] == "BLOQUEADA"


def test_insumos_mudaram_marca_desatualizada(sala):
    man = json.loads((sala / "insumos" / "MANIFESTO.json").read_text())
    antigo = dict(man["arquivos"]); antigo["fatos.snapshot.json"] = "0" * 64
    (sala / "insumos" / "historico" / "aaaaaaaaaaaa.json").write_text(json.dumps({"hash": "aaaaaaaaaaaa", "arquivos": antigo}))
    t = (sala / "cascas" / "rascunho" / "EX-OK.md").read_text(encoding="utf-8").replace(f"insumos_hash: {man['hash']}", "insumos_hash: aaaaaaaaaaaa")
    r = validar(_casca(sala, t, "EX-VELHA"), sala)
    assert r["status"] == "DESATUALIZADA"
    assert r["mudou"] == ["fatos.snapshot.json"]
