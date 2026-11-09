"""./sala para-roteiro <id> — casca APROVADA → saida/<id>_ROTEIRO.md no formato exato de planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md.
A sala nunca roda ./sm importar-roteiro: só deixa o arquivo pronto."""
import re

from .base import hoje, norm, sala_raiz, tirar_aspas
from .validar_casca import _origem, campo, campos, ler_casca, tabela, validar

NOMES_MOV = {1: "1 quebra de padrão física", 2: "2 ancoragem", 3: "3 escada do sonho", 4: "4 empilhamento",
             5: "5 escalonamento", 6: "6 CTA com providência"}
ORIGEM_MODELO = {"ia": "IA", "apresentador replica": "Apresentador réplica", "foto real da instituicao": "foto real da Instituição",
                 "banco": "banco de takes", "gravacao real": "gravação real"}
SEG = {"popular": "popular", "classe_media": "classe média", "classe media": "classe média", "alto_ticket": "alto ticket", "alto ticket": "alto ticket"}


def _cabecalho_tabela(modelo: str) -> tuple[str, str]:
    for i, l in enumerate(modelo.splitlines()):
        if l.startswith("| nº |"):
            return l, modelo.splitlines()[i + 1]
    raise SystemExit("modelo sem cabeçalho de quadros")


def _cel(s: str) -> str:
    return (s or "").replace("|", "/").strip()


def converter(cid: str, sala=None) -> str:
    sala = sala or sala_raiz()
    p = sala / "cascas" / "aprovadas" / f"{cid}.md"
    if not p.exists():
        raise SystemExit(f"{cid} não está em cascas/aprovadas/ (aprovação é só por ./sala aprovar, comando do usuário)")
    r = validar(cid, sala)
    if r["status"] != "OK":
        raise SystemExit(f"{cid}: {r['status']} — rode ./sala validar {cid}")
    c = ler_casca(p.read_text(encoding="utf-8"))
    fm, S = c["fm"], c["secoes"]
    A, B, F = campos(S["A"]), campos(S["B"]), campos(S["F"])
    modelo = (sala / "insumos" / "modelo_roteiro.snapshot.md").read_text(encoding="utf-8")
    cab, sep = _cabecalho_tabela(modelo)
    usadas = [l for l in tabela(S["C"]) if norm(l.get("uso", "")).startswith("usad")]
    camera_gancho = "; ".join(x for x in (campo(B, "quem filma"), campo(B, "altura e ângulo"), campo(B, "lente"), campo(B, "movimento")) if x)
    linhas = []
    numero = {l.get("#", "").strip(): n for n, l in enumerate(usadas, 1)}
    for n, l in enumerate(usadas, 1):
        mov = int(re.search(r"[1-6]", l["mov"]).group(0))
        o = norm(l.get("origem", ""))
        origem = ORIGEM_MODELO.get(_origem(l.get("origem", "")), "IA")
        mt = re.search(r"mesmo take de #?(\w+)", o)
        trecho = f"trecho seguinte do mesmo take do quadro {numero.get(mt.group(1), mt.group(1))} (não gerar de novo)" if mt else ""
        banco = re.search(r"banco[:\s]+([\w.-]+)", l.get("origem", ""), re.I)
        obs = "; ".join(x for x in (trecho, (f"banco: {banco.group(1)}" if banco else ""), f"onde: {l.get('onde', '')}", f"intenção: {l.get('intenção', '')}",
                                    f"casca {cid}", ("olha para a lente (exceção do Apresentador)" if origem == "Apresentador réplica" else "")) if x)
        camera = camera_gancho if n == 1 else l.get("câmera", "")
        cel = [str(n), tirar_aspas(l.get("fala-guia", "")), l.get("quem", ""), l.get("ação", ""), l.get("emoção", ""),
               l.get("enquadramento", ""), camera, ("abertura" if n == 1 else l.get("ligação", "")), origem,
               tirar_aspas(l.get("tela", "")), NOMES_MOV[mov], obs]
        linhas.append("| " + " | ".join(_cel(x) for x in cel) + " |")
    narr = " ".join(tirar_aspas(l.get("fala-guia", "")) for l in usadas if tirar_aspas(l.get("fala-guia", "")))
    seg = SEG.get(norm(fm.get("segmento", "")), fm.get("segmento", ""))
    out = ["# ROTEIRO QUADRO A QUADRO", "",
           f"Gerado pela Sala de Roteiro em {hoje()} a partir da casca aprovada {cid} (insumos {fm['insumos_hash']}). "
           f"Entrada na produção: `./sm importar-roteiro <este-arquivo.md>` e depois `./sm validar roteiro {cid}`. Nada é gerado nessa etapa.", "",
           "## Cabeçalho",
           f"- Nome: {fm.get('titulo', cid)}", f"- ID: {cid}", f"- Segmento: {seg}", f"- Persona: {fm.get('persona', '')}",
           f"- Ângulo: {norm(fm.get('angulo', ''))}", f"- Objetivo e destino: {fm.get('destino', '')}",
           f"- Duração máxima (s): {int(r['duracao_max_s'] or 30)}", f"- Estilo: {fm.get('estilo', 'realismo-celular')}", "- Taxonomia:"]
    for k in ("Ângulo", "Tom", "Hook", "Gatilho", "Elemento", "Persona-alvo", "Camada de Objeção", "Risco de Política"):
        out.append(f"  - {k}: {campo(F, k)}")
    out += ["", "## Narração completa", narr, "", "## Quadros",
            "Uma linha por quadro. Ligação: continuidade direta | corte casado | corte seco. Origem: IA | Apresentador réplica | foto real da Instituição | banco de takes | gravação real. "
            "Função: 1 quebra de padrão física · 2 ancoragem · 3 escada do sonho · 4 empilhamento · 5 escalonamento (suspenso no nível 1) · 6 CTA com providência.", "",
            cab, sep] + linhas + ["", f"<!-- conceito: {campo(A, 'frase')} -->", ""]
    dst = sala / "saida" / f"{cid}_ROTEIRO.md"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text("\n".join(out), encoding="utf-8")
    return f"{dst.relative_to(sala.parent)} · {len(linhas)} quadros · {r['duracao_s']} s · pronto para ./sm importar-roteiro (a produção roda)"
