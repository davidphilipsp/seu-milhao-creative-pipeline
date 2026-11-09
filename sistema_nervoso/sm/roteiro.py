"""Roteiro quadro a quadro (planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md) → partitura.json + decupagem.json; validação sem custo."""
import re, unicodedata
from .raiz import raiz, criativo_dir, ler_json, gravar_json, hoje
from .memoria import glossario, fato
from .lint import lint_texto
from . import partitura as P

ORIGENS = {"ia": ("GERAR", "veo-3.1-padrao-1080p"), "apresentador réplica": ("GERAR", "veo-3.1-padrao-1080p"), "apresentador replica": ("GERAR", "veo-3.1-padrao-1080p"),
           "foto real da instituicao": ("GERAR", "ffmpeg-foto-animada"), "foto real da instituição": ("GERAR", "ffmpeg-foto-animada"), "banco de takes": ("REUSO", "veo-3.1-padrao-1080p"), "gravação real": ("GERAR", "gravacao_real"), "gravacao real": ("GERAR", "gravacao_real")}
LIGACOES = {"continuidade direta": "continuidade_direta", "corte casado": "corte_casado", "corte seco": "corte_seco", "abertura": "abertura", "fecho": "fecho"}
MOVIMENTOS = {"quebra": 1, "ancoragem": 2, "escada": 3, "empilhamento": 4, "escalonamento": 5, "cta": 6}
CUSTO = {"quadro": 0.07, "teste": 0.80, "final_padrao": 3.20, "final_fast": 0.96}


def _norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")


def _slug(s):
    return re.sub(r"[^A-Z0-9]+", "-", _norm(s).upper()).strip("-")[:24]


def _tags(texto):
    """casa palavras do texto com o vocabulário do glossário (lugar, elemento, acao)."""
    t = _norm(texto); g = glossario()["tags"]; out = {}
    sin = {"lugar": {"feira": "feira", "onibus": "ponto_de_onibus", "padaria": "padaria", "canteiro": "canteiro_de_obra", "obra": "canteiro_de_obra", "instituicao": "instituicao", "varanda": "varanda", "rua": "rua", "mesa": "mesa", "cozinha": "cozinha", "escritorio": "escritorio"},
           "elemento": {"moeda": "moeda", "mao": "mao", "rosto": "rosto", "apresentador": "apresentador", "crianca": "crianca_real", "logo": "logo_casa", "titulo": "titulo_tela"},
           "acao": {"recebe": "recebe_moeda", "olha a moeda": "olha_moeda", "olha para a moeda": "olha_moeda", "sorri": "sorri", "gargalh": "sorri", "fecha a mao": "fecha_mao", "estende": "estende_moeda", "oferece": "estende_moeda", "toca aqui": "toca_aqui", "vem": "gesto_vem", "foto": "foto_animada", "parad": "parado"}}
    for k, m in sin.items():
        vals = [v for chave, v in m.items() if chave in t and v in g[k]]
        out[k] = sorted(set(vals))
    return out


def parse(md: str) -> dict:
    sec = {}
    atual = None
    for l in md.splitlines():
        m = re.match(r"^##\s+(.*)", l)
        if m: atual = _norm(m.group(1)).strip(); sec[atual] = []; continue
        if atual: sec[atual].append(l)
    def bloco(nome):
        k = next((k for k in sec if k.startswith(nome)), None)
        return "\n".join(sec[k]).strip() if k else ""
    cab = {}
    tax = {}
    for l in bloco("cabecalho").splitlines():
        m = re.match(r"^\s*-\s*(?:-\s*)?([^:]+):\s*(.*)$", l)
        if not m: continue
        k, v = _norm(m.group(1)).strip(), m.group(2).strip()
        if l.startswith("  ") or l.startswith("\t"):
            tax[k] = v
        else:
            cab[k] = v
    narr = bloco("narracao")
    narr = "\n".join(l for l in narr.splitlines() if not l.strip().startswith("<!--")).strip()
    quadros = []
    linhas = [l for l in bloco("quadros").splitlines() if l.strip().startswith("|")]
    if len(linhas) >= 2:
        cab_tab = [_norm(c).strip() for c in linhas[0].strip().strip("|").split("|")]
        for l in linhas[2:]:
            cels = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cels) < len(cab_tab): cels += [""] * (len(cab_tab) - len(cels))
            q = dict(zip(cab_tab, cels))
            if not q.get("no") and not q.get("n") and not q.get("nº"): pass
            quadros.append(q)
    return {"cabecalho": cab, "taxonomia": tax, "narracao": narr, "quadros": quadros}


def _col(q, *nomes):
    for n in nomes:
        for k, v in q.items():
            if _norm(k).startswith(_norm(n)): return v
    return ""


def importar(arquivo, cid=None) -> str:
    md = open(arquivo, encoding="utf-8").read()
    d = parse(md)
    cab = d["cabecalho"]
    nome = cab.get("nome", "")
    cid = cid or cab.get("id") or _slug(nome)
    if not cid: raise SystemExit("cabeçalho sem Nome/ID")
    pps, origem_pps = P.pps()
    g = glossario()
    seg = _norm(cab.get("segmento", "popular")).replace(" ", "_").replace("classe_media", "classe_media")
    seg = {"classe media": "classe_media", "alto ticket": "alto_ticket"}.get(_norm(cab.get("segmento", "")), seg)
    ang = _norm(cab.get("angulo", "solidario")).replace(" ", "_")
    estilo = cab.get("estilo", "realismo-celular").strip() or "realismo-celular"
    dmax = float(re.sub(r"[^\d.,]", "", cab.get("duracao maxima (s)", cab.get("duracao maxima", "30")) or "30").replace(",", ".") or 30)
    campos_tax = [c["id"] for c in g["taxonomia_8_campos"]["campos"]]
    nomes_tax = {"angulo": "angulo", "tom": "tom", "hook": "hook", "gatilho": "gatilho", "elemento": "elemento", "persona-alvo": "persona_alvo", "persona alvo": "persona_alvo", "camada de objecao": "camada_objecao", "risco de politica": "risco_politica"}
    taxonomia = {nomes_tax.get(k, k): v for k, v in d["taxonomia"].items()}
    for c in campos_tax: taxonomia.setdefault(c, "")
    falas, takes, t0 = [], [], 0.0
    for i, q in enumerate(d["quadros"], 1):
        trecho = _col(q, "trecho")
        n = len(trecho.split())
        origem_txt = _norm(_col(q, "origem"))
        origem, modelo = next((v for k, v in ORIGENS.items() if _norm(k) in origem_txt), ("GERAR", "veo-3.1-padrao-1080p"))
        if "apresentador" in origem_txt: modelo = "veo-3.1-padrao-1080p"
        dur = round(n / pps, 2) if n else (4.0 if modelo == "ffmpeg-foto-animada" else 1.5)
        func = _norm(_col(q, "funcao"))
        mov = next((v for k, v in MOVIMENTOS.items() if k in func), None)
        mnum = re.search(r"\b([1-6])\b", func)
        if mnum: mov = int(mnum.group(1))
        lig_txt = _norm(_col(q, "ligacao"))
        lig = next((v for k, v in LIGACOES.items() if _norm(k) in lig_txt), "corte_seco")
        if i == 1: lig = "abertura"
        quem, acao, emocao = _col(q, "quem"), _col(q, "acao"), _col(q, "emocao")
        tags = _tags(" ".join([quem, acao, origem_txt, _col(q, "enquadramento")]))
        if "apresentador" in origem_txt: tags["elemento"] = sorted(set(tags.get("elemento", []) + ["apresentador", "rosto"]))
        if "foto real" in origem_txt: tags["elemento"] = sorted(set(tags.get("elemento", []) + ["crianca_real"])); tags["acao"] = sorted(set(tags.get("acao", []) + ["foto_animada"])); tags["lugar"] = sorted(set(tags.get("lugar", []) + ["instituicao"]))
        fid, tid = f"F{i}", f"T{i}"
        falas.append({"id": fid, "movimento": mov, "texto": trecho, "palavras": n, "duracao_s": dur, "respiro_s": 0.0, "texto_tela": _col(q, "texto de tela", "texto"), "enfase": "", "quadro": i})
        takes.append({"id": tid, "falas": [fid], "inicio_s": round(t0, 2), "duracao_s": dur, "descricao": f"{quem}. {acao}. Emoção: {emocao}".strip(". "), "quem": quem, "acao_texto": acao, "emocao": emocao,
                      "enquadramento": _col(q, "enquadramento"), "movimento_camera": _col(q, "camera") or "single continuous handheld shot, slight constant shake", "ligacao": lig, "casa_com": _col(q, "ligacao") if lig == "corte_casado" else None,
                      "origem": origem, "origem_roteiro": _col(q, "origem"), "modelo": modelo, "tags": tags, "texto_tela": _col(q, "texto de tela", "texto"), "funcao": _col(q, "funcao"), "observacoes": _col(q, "observac")})
        t0 += dur
    cd = criativo_dir(cid)
    if not (cd / "estado.json").exists():
        from .criativo import novo
        novo(cid, nome or cid, float(fato("tecnica.teto_padrao_conjunto")), atual=False)
    gravar_json(cd / "partitura.json", {"criativo": cid, "titulo": nome, "segmento": seg, "angulo": ang, "persona": cab.get("persona", ""), "objetivo": cab.get("objetivo e destino", cab.get("objetivo", "")),
                                        "duracao_max_s": dmax, "calibracao": {"palavras_por_s": pps, "origem": origem_pps}, "narracao": d["narracao"], "taxonomia": taxonomia, "falas": falas, "importado_de": str(arquivo), "data": hoje()})
    gravar_json(cd / "decupagem.json", {"criativo": cid, "estilo": estilo, "takes": takes, "importado_de": str(arquivo), "data": hoje()})
    return f"importado {cid}: {len(takes)} quadros · {sum(f['duracao_s'] for f in falas):.1f} s (calibração {pps} p/s, {origem_pps}) → criativos/{cid}/partitura.json + decupagem.json\nagora: ./sm validar roteiro {cid}"


def validar(cid) -> str:
    cd = criativo_dir(cid)
    part, dec = ler_json(cd / "partitura.json"), ler_json(cd / "decupagem.json")
    pend = fato("pendencias", so_valor=False)
    ok, bloq, avisos = [], [], []
    pps, origem_pps = part.get("calibracao", {}).get("palavras_por_s", 2.4), part.get("calibracao", {}).get("origem", "estimativa")
    tot = sum(float(f["duracao_s"]) for f in part["falas"])
    if tot <= float(part["duracao_max_s"]): ok.append(f"duração {tot:.1f} s ≤ {part['duracao_max_s']} s")
    else: bloq.append(f"duração {tot:.1f} s > máximo {part['duracao_max_s']} s")
    if origem_pps == "estimativa": avisos.append(f"calibração é estimativa ({pps} p/s): grave o Apresentador em fontes/calibracao/ e rode sm calibrar")
    lentos = [t["id"] for t in dec["takes"] if t["origem"] == "GERAR" and t["modelo"] != "ffmpeg-foto-animada" and float(t["duracao_s"]) > 2.0]
    if lentos: avisos.append(f"ritmo: quadros de IA acima de 2 s: {', '.join(lentos)} (1–2 s; só o plano real da criança segura mais)")
    curtos = [t["id"] for t in dec["takes"] if t["origem"] == "GERAR" and t["modelo"] != "ffmpeg-foto-animada" and float(t["duracao_s"]) < 1.0]
    if curtos: avisos.append(f"ritmo: quadros de IA abaixo de 1 s: {', '.join(curtos)}")
    sem_funcao = [f["id"] for f in part["falas"] if not f.get("movimento")]
    if sem_funcao: bloq.append(f"sem função no esqueleto (gera algo bonito que não vai ser usado): {', '.join(sem_funcao)}")
    else: ok.append("todo quadro tem função no esqueleto")
    textos = (part.get("narracao", "") + "\n" + "\n".join(f.get("texto_tela", "") for f in part["falas"]))
    vs = lint_texto(textos)
    if vs: bloq += [f"lint [{v.id}] '{v.trecho}': {v.motivo}" for v in vs[:5]]
    else: ok.append("lint limpo (narração e textos de tela)")
    for t in dec["takes"]:
        o = _norm(t.get("origem_roteiro", "")); quem = _norm(t.get("quem", "") + " " + t.get("acao_texto", "") + " " + t.get("enquadramento", ""))
        ia = t["origem"] == "GERAR" and t["modelo"] not in ("ffmpeg-foto-animada", "gravacao_real")
        if ia and re.search(r"crianc|menin|bebe", quem): bloq.append(f"{t['id']}: criança em origem IA (só foto real da Instituição)")
        if ia and re.search(r"\bgrupo\b|multidao|varias pessoas|duas pessoas|casal|familia", quem): avisos.append(f"{t['id']}: grupo em IA (a Vertex bloqueia grupos; um adulto por plano)")
        if ia and re.search(r"olha(ndo)? (para|pra) a (lente|camera)|para a camera|olhar na lente", quem) and "apresentador" not in o: bloq.append(f"{t['id']}: olhar para a lente em IA (só o Apresentador réplica)")
        deps = []
        if "foto real" in o: deps += ["termo_instituicao", "origem_fotos_1_3"]
        if "apresentador" in o: deps += ["termo_apresentador", "fotos_apresentador_originais"]
        if "moeda" in quem or "moeda" in (t.get("tags", {}).get("elemento") or []): deps.append("banco_central")
        deps = [d for d in dict.fromkeys(deps) if pend.get(d, {}).get("status") not in (None, "confirmado")]
        if deps: avisos.append(f"{t['id']}: depende de {', '.join(deps)} (veiculação)")
    from .banco import buscar
    buscar(cid); dec = ler_json(cd / "decupagem.json")
    gerar = [t for t in dec["takes"] if t["origem"] == "GERAR" and t["modelo"] not in ("ffmpeg-foto-animada", "gravacao_real")]
    reuso = [t["id"] for t in dec["takes"] if t["origem"] == "REUSO"]
    custo = sum(CUSTO["quadro"] + CUSTO["teste"] + (CUSTO["final_padrao"] if "padrao" in t["modelo"] else CUSTO["final_fast"]) for t in gerar)
    rel = [f"ROTEIRO {cid}: {len(dec['takes'])} quadros · {len(ok)} ok · {len(bloq)} bloqueio(s) · {len(avisos)} aviso(s)"]
    rel += [f"✓ {x}" for x in ok][:3] + [f"✗ {x}" for x in bloq][:4] + [f"! {x}" for x in avisos][:4]
    rel.append(f"a gerar: {', '.join(t['id'] for t in gerar) or 'nada'}{(' · reuso: ' + ', '.join(reuso)) if reuso else ''} · custo estimado US$ {custo:.2f} (quadro {CUSTO['quadro']} + teste {CUSTO['teste']} + final por take; NADA gerado)")
    gravar_json(cd / "esteira" / "validacao_roteiro.json", {"ok": ok, "bloqueios": bloq, "avisos": avisos, "a_gerar": [t["id"] for t in gerar], "reuso": reuso, "custo_estimado_usd": round(custo, 2), "data": hoje()})
    return "\n".join(rel[:10])
