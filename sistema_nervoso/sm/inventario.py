"""Inventário: mapa de todos os arquivos atuais → destino na hierarquia (docs/00_MAPA.md descreve a hierarquia)."""
import collections, datetime, re
from .raiz import raiz

IGN = ("node_modules", ".venv", "biblioteca/.git", "__pycache__", ".DS_Store", "painel/_cache", ".git/", "_seco/")
REGRAS = [
    (r"^CLAUDE\.md$", "raiz: roteador"), (r"^docs/", "docs/"), (r"^memoria/", "memoria/"), (r"^fluxo/", "fluxo/"), (r"^planejamento/", "planejamento/"),
    (r"^estilos/", "estilos/"), (r"^criativos/", "criativos/<id>/"), (r"^sistema_nervoso/", "sistema_nervoso/"), (r"^painel/", "painel/"),
    (r"^biblioteca/", "biblioteca/ (clone)"), (r"^ponte_capcut/", "ponte_capcut/"), (r"^fontes/autorizacoes/", "fontes/autorizacoes/ (fora do git)"),
    (r"^fontes/", "fontes/"), (r"^\.claude/agents/", ".claude/agents/"), (r"^\.claude/", ".claude/skills"), (r"^_arquivo/", "_arquivo/"),
    (r"^(decisoes|achados-para-o-time|creditos|custos|inventario)\.md$", "raiz: registros"), (r"^(\.env|\.env\.exemplo|\.gitignore|package\.json|package-lock\.json|sm)$", "raiz: config"),
]


def gerar() -> str:
    R = raiz(); rows = []
    for p in sorted(R.rglob("*")):
        if not p.is_file(): continue
        s = str(p.relative_to(R))
        if any(i in s for i in IGN): continue
        dest = next((d for rx, d in REGRAS if re.search(rx, s)), "A DECIDIR")
        rows.append((s, dest))
    cnt = collections.Counter(d for _, d in rows)
    md = [f"# Inventário · {datetime.date.today()} · {len(rows)} arquivos", "", "| Pasta/destino | Arquivos |", "|---|---|"] + [f"| {d} | {n} |" for d, n in cnt.most_common()]
    md += ["", "## Arquivo a arquivo", "", "| Arquivo | Pasta/destino |", "|---|---|"] + [f"| {s} | {d} |" for s, d in rows if not s.startswith("_arquivo/")]
    (R / "inventario.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return f"inventario.md: {len(rows)} arquivos · a decidir: {cnt.get('A DECIDIR', 0)}"
