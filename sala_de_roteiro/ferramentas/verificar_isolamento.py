"""verificar_isolamento.py — compara o branch com o principal (commits + alterações não salvas + arquivos novos)
e FALHA se qualquer arquivo alterado estiver fora das áreas de escrita permitidas. Rode antes de cada commit."""
import pathlib
import subprocess
import sys

PERMITIDO_PREFIXO = ("sala_de_roteiro/",)
PERMITIDO_NOVO = (".claude/agents/idealizador.md", "sala")  # só se não existirem no principal
# 'sala' = lançador de 2 linhas da CLI própria (./sala); exceção declarada no README e no relatório.


def _git(repo, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def alterados(repo, base="main") -> set[str]:
    s = set()
    s |= set(_git(repo, "diff", "--name-only", f"{base}...HEAD").split("\n"))
    s |= set(_git(repo, "diff", "--name-only", "HEAD").split("\n"))
    s |= set(_git(repo, "diff", "--name-only", "--cached").split("\n"))
    s |= set(_git(repo, "ls-files", "--others", "--exclude-standard").split("\n"))
    return {x.strip() for x in s if x.strip()}


def existe_na_base(repo, base, caminho) -> bool:
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{base}:{caminho}"], capture_output=True).returncode == 0


def verificar(repo=None, base="main") -> tuple[bool, list[str], int]:
    repo = pathlib.Path(repo or pathlib.Path(__file__).resolve().parents[2])
    arqs = alterados(repo, base)
    proibidos = []
    for a in sorted(arqs):
        if a.startswith(PERMITIDO_PREFIXO):
            continue
        if a in PERMITIDO_NOVO and not existe_na_base(repo, base, a):
            continue
        proibidos.append(a)
    return (not proibidos), proibidos, len(arqs)


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    base = argv[0] if argv else "main"
    ok, ruins, n = verificar(base=base)
    if ok:
        print(f"ISOLAMENTO OK · {n} arquivo(s) alterado(s) contra {base}, todos em áreas permitidas")
        return 0
    print(f"ISOLAMENTO FALHOU · {len(ruins)} arquivo(s) fora das áreas permitidas:")
    for r in ruins[:20]:
        print(f"  ✗ {r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
