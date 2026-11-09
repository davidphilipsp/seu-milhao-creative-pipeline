"""Base comum da Sala de Roteiro: caminhos, JSON, hash, normalização. Só biblioteca padrão; nunca importa o pacote sm."""
import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import subprocess
import unicodedata

CONTRATO_VERSAO = "1.0"
PALAVRAS_POR_S_PADRAO = 2.4


def sala_raiz() -> pathlib.Path:
    """Pasta sala_de_roteiro/ (ou SALA_RAIZ, usado nos testes)."""
    env = os.environ.get("SALA_RAIZ")
    return pathlib.Path(env).resolve() if env else pathlib.Path(__file__).resolve().parent.parent


def repo_raiz(sala: pathlib.Path | None = None) -> pathlib.Path:
    return (sala or sala_raiz()).parent


def producao_raiz() -> pathlib.Path:
    """Checkout principal da produção (SALA_PRODUCAO ou o primeiro worktree do repositório). Só leitura."""
    env = os.environ.get("SALA_PRODUCAO")
    if env:
        return pathlib.Path(env).resolve()
    try:
        out = subprocess.run(["git", "-C", str(repo_raiz()), "worktree", "list", "--porcelain"],
                             capture_output=True, text=True, check=True).stdout
        primeiro = next(l.split(" ", 1)[1] for l in out.splitlines() if l.startswith("worktree "))
        return pathlib.Path(primeiro).resolve()
    except Exception:
        return repo_raiz()


def hoje() -> str:
    return _dt.date.today().isoformat()


def agora() -> str:
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def ler_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def gravar_json(p, dados):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def sha256_arquivo(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


def hash_conjunto(arquivos: dict) -> str:
    """hash curto (12) de {caminho_relativo: sha256}."""
    linhas = "\n".join(f"{k}:{arquivos[k]}" for k in sorted(arquivos))
    return hashlib.sha256(linhas.encode()).hexdigest()[:12]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def palavras(s: str) -> int:
    """mesma conta da produção: palavras separadas por espaço."""
    return len(tirar_aspas(s).split())


def tirar_aspas(s: str) -> str:
    return (s or "").strip().strip('"“”\'').strip()
