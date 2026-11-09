"""O verificador passa com escrita só nas áreas permitidas e FALHA com uma escrita proibida simulada."""
import subprocess

import pytest

from sala_de_roteiro.ferramentas.verificar_isolamento import verificar


def git(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "prod"
    for p in ("fluxo/estado.json", "memoria/fatos.json", ".claude/agents/roteirista.md", "decisoes.md"):
        (r / p).parent.mkdir(parents=True, exist_ok=True); (r / p).write_text("{}\n")
    git(r, "init", "-q", "-b", "main"); git(r, "config", "user.email", "t@t"); git(r, "config", "user.name", "t")
    git(r, "add", "-A"); git(r, "commit", "-qm", "base")
    git(r, "checkout", "-qb", "sala-de-roteiro")
    (r / "sala_de_roteiro").mkdir(); (r / "sala_de_roteiro" / "README.md").write_text("ok\n")
    (r / ".claude/agents/idealizador.md").write_text("novo\n")
    (r / "sala").write_text("#!/bin/sh\n")
    git(r, "add", "-A"); git(r, "commit", "-qm", "sala")
    return r


def test_areas_permitidas_passam(repo):
    ok, ruins, n = verificar(repo)
    assert ok and ruins == [] and n == 3


@pytest.mark.parametrize("caminho", ["fluxo/estado.json", "memoria/fatos.json", ".claude/agents/roteirista.md", "decisoes.md", "criativos/TK-03/x.json"])
def test_escrita_proibida_nao_salva_falha(repo, caminho):
    (repo / caminho).parent.mkdir(parents=True, exist_ok=True)
    (repo / caminho).write_text('{"geracao_liberada": true}\n')
    ok, ruins, _ = verificar(repo)
    assert not ok and caminho in ruins


def test_escrita_proibida_commitada_falha(repo):
    (repo / "fluxo/estado.json").write_text('{"geracao_liberada": true}\n')
    git(repo, "commit", "-qam", "proibido")
    ok, ruins, _ = verificar(repo)
    assert not ok and ruins == ["fluxo/estado.json"]


def test_idealizador_so_se_for_novo(tmp_path):
    r = tmp_path / "p2"
    (r / ".claude/agents").mkdir(parents=True); (r / ".claude/agents/idealizador.md").write_text("antigo\n")
    git(r, "init", "-q", "-b", "main"); git(r, "config", "user.email", "t@t"); git(r, "config", "user.name", "t")
    git(r, "add", "-A"); git(r, "commit", "-qm", "base"); git(r, "checkout", "-qb", "x")
    (r / ".claude/agents/idealizador.md").write_text("mudado\n")
    ok, ruins, _ = verificar(r)
    assert not ok and ruins == [".claude/agents/idealizador.md"]
