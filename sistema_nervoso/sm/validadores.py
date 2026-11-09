"""Definição de pronto de cada micro-passo. Cada função devolve lista de erros (vazia = passou)."""
import json, pathlib, re, subprocess, sys
from .raiz import raiz, ler_json, criativo_dir
from . import memoria

VALORES_PRODUTO = ["100.000", "0,49", "00000.000000", "00.000.000", "29/11/2026"]


def _pytest(*arquivos) -> list[str]:
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *[str(raiz() / "sistema_nervoso" / "tests" / a) for a in arquivos]]
    r = subprocess.run(cmd, text=True, capture_output=True, cwd=str(raiz() / "sistema_nervoso"))
    if r.returncode:
        return ["pytest falhou:\n" + (r.stdout + r.stderr)[-1200:]]
    return []


# ---------------- reestruturação ----------------
def r01_inventario():
    return [] if (raiz() / "inventario.md").exists() else ["inventario.md não existe"]


def r03_hierarquia():
    exig = ["docs", "memoria", "fluxo", "planejamento/cartoes", "planejamento/segmentos", "estilos/realismo-celular", "estilos/realismo-cuidado",
            "estilos/cinematografico", "criativos", "sistema_nervoso/sm", "sistema_nervoso/tests", "painel", "biblioteca", "ponte_capcut",
            "fontes/autorizacoes", "fontes/calibracao", ".claude/agents", "_arquivo"]
    e = [f"falta {d}" for d in exig if not (raiz() / d).is_dir()]
    if (raiz() / "takes").exists(): e.append("takes/ ainda existe (deveria ser criativos/)")
    if (raiz() / "scripts").exists(): e.append("scripts/ ainda existe")
    return e


def r04_memoria():
    memoria.limpar_cache()
    return memoria.validar_fatos()


def r05_sm_base():
    return _pytest("test_memoria.py", "test_fluxo.py")


def r06_lint():
    return _pytest("test_lint.py")


def r07_producao():
    return _pytest("test_seco.py")


def r08_docs():
    e = []
    cl = raiz() / "CLAUDE.md"
    if not cl.exists(): return ["CLAUDE.md não existe"]
    n = len(cl.read_text(encoding="utf-8").splitlines())
    if n > 60: e.append(f"CLAUDE.md tem {n} linhas (máx. 60)")
    docs = ["00_MAPA.md", "01_PLAYBOOK.md", "01_PLAYBOOK_RESUMO.md", "02_MACROSSISTEMA.md", "03_ESTEIRA.md", "04_SISTEMA_NERVOSO.md", "05_BIBLIOTECA.md", "06_EXPEDICAO.md"]
    for d in docs:
        if not (raiz() / "docs" / d).exists(): e.append(f"falta docs/{d}")
    res = raiz() / "docs" / "01_PLAYBOOK_RESUMO.md"
    if res.exists():
        t = res.read_text(encoding="utf-8")
        if len(t.splitlines()) > 70 or len(t) > 6000: e.append("01_PLAYBOOK_RESUMO.md passa de 1 página (≤70 linhas, ≤6000 caracteres)")
    for p in [cl, *(raiz() / "docs").glob("*.md"), *(raiz() / ".claude" / "agents").glob("*.md")]:
        if not p.exists(): continue
        t = p.read_text(encoding="utf-8")
        for v in VALORES_PRODUTO:
            if v in t: e.append(f"{p.relative_to(raiz())}: valor de produto duplicado '{v}' (use `sm fato`)")
    return e


def r09_agentes():
    e = []
    pasta = raiz() / ".claude" / "agents"
    exig = ["estrategista", "roteirista", "diretor", "auditor", "diretor-de-quadros", "operador-de-video", "inspetor", "finalizador", "bibliotecario"]
    nomes = {}
    for p in pasta.glob("*.md"):
        t = p.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
        if not m: e.append(f"{p.name}: sem frontmatter"); continue
        fm, corpo = m.groups()
        nm = re.search(r"^name:\s*(\S+)", fm, re.M)
        if not nm or not re.search(r"^description:", fm, re.M): e.append(f"{p.name}: frontmatter sem name/description"); continue
        nomes[nm.group(1)] = corpo
        if "01_PLAYBOOK_RESUMO" not in corpo: e.append(f"{p.name}: não cita 01_PLAYBOOK_RESUMO.md")
        if "sm " not in corpo: e.append(f"{p.name}: não cita comandos sm")
    for n in exig:
        if n not in nomes: e.append(f"falta agente {n}")
    return e


def r10_passos():
    from .fluxo import carregar_passos, validar_passos
    e = validar_passos(carregar_passos("passos.yaml"))
    e += validar_passos(carregar_passos("reestruturacao.yaml"))
    ids = [p["id"] for p in carregar_passos("passos.yaml")]
    if ids != [f"P{i:02d}" for i in range(1, 19)]: e.append("passos.yaml não tem P01..P18 em ordem")
    return e


def r11_planejamento():
    e = []
    for est in ("realismo-celular", "realismo-cuidado", "cinematografico"):
        for f in ("bloco.txt", "negativos.txt", "paleta.md", "modelos.md", "licoes.md"):
            if not (raiz() / "estilos" / est / f).exists(): e.append(f"falta estilos/{est}/{f}")
    m = raiz() / "planejamento" / "matriz.json"
    if not m.exists(): return e + ["falta planejamento/matriz.json"]
    d = ler_json(m)
    cartoes = d.get("cartoes", [])
    if len(cartoes) < 6: e.append(f"matriz tem {len(cartoes)} cartões (mínimo 6)")
    from .cartao import validar_cartao
    for c in cartoes:
        p = raiz() / "planejamento" / "cartoes" / f"{c}.json"
        if not p.exists(): e.append(f"falta cartão {c}"); continue
        e += [f"{c}: {x}" for x in validar_cartao(ler_json(p))]
    for s in ("popular.md", "classe_media.md", "alto_ticket.md"):
        if not (raiz() / "planejamento" / "segmentos" / s).exists(): e.append(f"falta planejamento/segmentos/{s}")
    return e


def r12_calibracao():
    p = raiz() / "memoria" / "calibracao.json"
    if not p.exists(): return ["memoria/calibracao.json não existe (rode sm calibrar)"]
    d = ler_json(p)
    return [] if d.get("palavras_por_s") and d.get("origem") in ("medida", "estimativa") else ["calibracao.json incompleto"]


def r13_biblioteca():
    from .publicar import testar_gancho
    return testar_gancho()


def r14_painel():
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/api/fluxo", timeout=3) as r:
            d = json.loads(r.read())
        return [] if "reestruturacao" in d and "criativos" in d else ["painel respondeu sem fluxo/criativos"]
    except Exception as ex:
        return [f"painel não responde em 127.0.0.1:8765 ({ex}); rode `sm painel`"]


def r15_seco():
    g = ler_json(raiz() / "fluxo" / "estado.json")
    cid = g.get("teste_seco_criativo")
    if not cid: return ["nenhum criativo de teste a seco registrado em fluxo/estado.json (teste_seco_criativo)"]
    est = ler_json(criativo_dir(cid) / "estado.json")
    faltam = [f"P{i:02d}" for i in range(1, 19) if est.get("passos", {}).get(f"P{i:02d}", {}).get("status") != "ok"]
    e = [f"{cid}: passos não ok: {faltam}"] if faltam else []
    if float(est.get("gasto_usd", 0)) != 0.0: e.append(f"{cid}: gasto US$ {est.get('gasto_usd')} ≠ 0")
    return e


def r16_reflexos():
    e = []
    if not (raiz() / "sistema_nervoso" / "REFLEXOS.md").exists(): e.append("falta sistema_nervoso/REFLEXOS.md")
    t = (raiz() / "custos.md").read_text(encoding="utf-8") if (raiz() / "custos.md").exists() else ""
    if "Reestruturação" not in t and "reestruturação" not in t: e.append("custos.md sem o registro desta missão")
    return e


# ---------------- produção ----------------
def _est(cid): return ler_json(criativo_dir(cid) / "estado.json")


def p01_cartao(cid):
    from .cartao import validar_cartao
    p = raiz() / "planejamento" / "cartoes" / f"{cid}.json"
    if not p.exists(): return [f"falta planejamento/cartoes/{cid}.json"]
    return validar_cartao(ler_json(p))


def p03_partitura(cid):
    from .partitura import validar
    return validar(cid)


def p04_decupagem(cid):
    from .decupagem import validar
    return validar(cid)


def p05_banco(cid):
    d = ler_json(criativo_dir(cid) / "decupagem.json")
    return [f"take {t['id']} sem origem REUSO/GERAR" for t in d["takes"] if t.get("origem") not in ("REUSO", "GERAR")]


def p06_auditoria(cid):
    from .lint import lint_arquivo
    e = []
    for nome in ("partitura.json", "decupagem.json"):
        vs = lint_arquivo(criativo_dir(cid) / nome)
        if vs: e.append(f"{nome}: {len(vs)} violação(ões) de lint")
    f = criativo_dir(cid) / "esteira" / "auditor_G1.json"
    if not f.exists(): return e + ["falta esteira/auditor_G1.json"]
    d = ler_json(f)
    if d.get("veredito") != "carimbado": e.append(f"auditor: {d.get('veredito')} — {d.get('motivo')}")
    return e


def p08_quadros(cid):
    from .midia import dimensao
    d = ler_json(criativo_dir(cid) / "decupagem.json")
    e = []
    for t in d["takes"]:
        if t.get("origem") != "GERAR" or t.get("modelo") == "ffmpeg-foto-animada": continue
        q = criativo_dir(cid) / "quadros" / f"{t['id']}_inicio.png"
        if not q.exists(): e.append(f"falta quadros/{t['id']}_inicio.png"); continue
        w, h = dimensao(q)
        if abs(w / h - 9 / 16) > 0.02: e.append(f"{q.name}: proporção {w}×{h} não é 9:16")
    return e


def _tomadas(cid, pasta):
    d = ler_json(criativo_dir(cid) / "decupagem.json")
    e = []
    for t in d["takes"]:
        if t.get("origem") != "GERAR" or t.get("modelo") == "ffmpeg-foto-animada": continue
        arqs = list((criativo_dir(cid) / "tomadas" / pasta).glob(f"{t['id']}_*.mp4"))
        if not arqs: e.append(f"falta tomada de {pasta} do take {t['id']}")
    custos = criativo_dir(cid) / "custos.md"
    if not custos.exists(): e.append("custos.md do criativo não existe")
    return e


def p10_testes(cid): return _tomadas(cid, "teste")


def p11_inspecao(cid):
    f = criativo_dir(cid) / "esteira" / "inspetor_teste.json"
    if not f.exists(): return ["falta esteira/inspetor_teste.json (rode sm inspecionar e o inspetor avalia)"]
    d = ler_json(f)
    return [] if d.get("automatico_ok") else [f"inspeção automática falhou: {d.get('erros')}"]


def p13_finais(cid): return _tomadas(cid, "final")


def p14_montagem(cid):
    from .lint import lint_arquivo
    e = []
    for n in ("sequencia.mp4", "sequencia_copies.mp4"):
        if not (criativo_dir(cid) / "aprovados" / n).exists(): e.append(f"falta aprovados/{n}")
    cop = criativo_dir(cid) / "aprovados" / "copies.txt"
    if cop.exists():
        vs = lint_arquivo(cop, exigir_rodape=True)
        if vs: e.append(f"copies.txt: {len(vs)} violação(ões)")
    else:
        e.append("falta aprovados/copies.txt (texto da versão com copies, para o lint)")
    return e


def p16_ponte(cid):
    p = raiz() / "ponte_capcut" / cid
    return [f"falta ponte_capcut/{cid}/{n}" for n in ("sequencia.mp4", "partitura.srt", "guia_copies.srt", "rodape_legal.png", "LEIA-ME.txt") if not (p / n).exists()]


def p17_publicacao(cid):
    est = _est(cid)
    return [] if est.get("publicado") else ["criativo não publicado (sm publicar)"]


def p18_custo(cid):
    est = _est(cid)
    return [] if est.get("custo_fechado") else ["custo não fechado (sm custo fechar <id>)"]


def coerencia():
    """nenhum valor de produto fora de fatos.json; sem regra contraditória entre RESUMO, PLAYBOOK, fatos e estilos; todos os MDs apontam para fatos.json."""
    e = r08_docs()
    memoria.limpar_cache(); f = memoria.fatos()
    docs = {p: p.read_text(encoding="utf-8") for p in [raiz() / "CLAUDE.md", *(raiz() / "docs").glob("*.md"), *(raiz() / "estilos").glob("*/*.md"), *(raiz() / "estilos").glob("*/*.txt"), *(raiz() / ".claude/agents").glob("*.md")]}
    expr = f["pessoas"]["adultos_ia"]["valor"]; trecho = f["tecnica"]["duracao_trecho"]["valor"]
    pico = "pico" in expr; curto = "1 a 2 s" in trecho or "1–2 s" in trecho
    for p, t in docs.items():
        nome = str(p.relative_to(raiz()))
        if "licoes" in nome or "_v1" in nome or nome.startswith("_arquivo"): continue
        if pico and re.search(r"express(ão|ões|ions?) contida|restrained natural expressions", t): e.append(f"{nome}: diz 'expressão contida' mas fatos.pessoas.adultos_ia pede emoção no pico")
        if curto and re.search(r"\b3\s*(a|–|-)\s*4\s*s\b|3–4 s por (take|plano|trecho)", t) and "(v1" not in t: e.append(f"{nome}: diz '3–4 s' mas fatos.tecnica.duracao_trecho é 1–2 s")
        for m in re.finditer(r"golden hour|warm sunset|late-afternoon sun", t):
            antes = t[max(0, m.start() - 40):m.start()].lower()
            linha = t[t.rfind("\n", 0, m.start()) + 1:m.start()].lower()
            if "negativos" in nome or linha.startswith("negative") or "negative:" in linha or re.search(r"nada de|sem |\bno\b|proíb|proib|não ", antes): continue
            e.append(f"{nome}: pede luz de fim de tarde (realismo v2 proíbe golden hour)"); break
    for p in [raiz() / "CLAUDE.md", *(raiz() / "docs").glob("*.md")]:
        if "fatos.json" not in p.read_text(encoding="utf-8") and "sm fato" not in p.read_text(encoding="utf-8"): e.append(f"{p.relative_to(raiz())}: não aponta para memoria/fatos.json")
    return e


VALIDADORES = {k: v for k, v in globals().items() if re.match(r"^[rp]\d\d_", k)}
