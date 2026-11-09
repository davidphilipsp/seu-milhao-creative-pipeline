"""./sala validar <id> — definição de pronto de uma casca. Determinístico, sem token, sem importar o sm."""
import pathlib
import re

from .base import (PALAVRAS_POR_S_PADRAO, gravar_json, hoje, ler_json, norm, palavras, sala_raiz, tirar_aspas)

FAMILIAS = ["objeto fora do lugar", "contradição", "atrito de dupla", "cena em andamento", "pergunta",
            "ritual da rua", "data como evento", "convite", "corrente"]
SECOES = {"A": "conceito", "B": "gancho", "C": "esqueleto", "D": "matriz", "E": "ficha", "F": "taxonomia", "G": "variações", "H": "riscos"}
CAMPOS_A = ["frase", "tensão", "por que esta persona"]
CAMPOS_B = ["ação física", "lugar", "hora e luz", "fundo", "não pode aparecer", "quem filma", "plano", "altura e ângulo",
            "lente", "distância", "profundidade de campo", "movimento", "obstrução", "figurino", "objeto principal",
            "primeira fala", "texto na tela", "som ambiente", "teste do mudo"]
CAMPOS_E = ["duração", "reuso × gerar", "pendências que travam", "custo estimado"]
CAMPOS_F = ["ângulo", "tom", "hook", "gatilho", "elemento", "persona-alvo", "camada de objeção", "risco de política"]
CAMPOS_G = ["família", "ação física", "primeira fala", "texto na tela"]
COLUNAS_C = ["#", "mov", "uso", "intenção", "fala-guia", "quem", "onde", "ação", "emoção", "enquadramento", "câmera", "ligação", "origem", "tela"]
COLUNAS_D = ["#", "o que se vê", "em cena", "coerência"]
ORIGENS = ["ia", "apresentador réplica", "foto real da instituicao", "banco", "gravação real"]
LIGACOES = ["abertura", "continuidade direta", "corte casado", "corte seco", "fecho"]
PROVIDENCIA = r"n[aã]o (apareceu|chegou|veio) (pra voc[eê] |pra ti |para voc[eê] )?por acaso"
DEUS_AUTOR = r"\bdeus (te |me |vai |j[aá] )?(deu|d[aá]|mandou|manda|dar|escolhe|escolheu|reservou)\b"
URGENCIA = r"\b(agora mesmo|corre|corra|correndo|[uú]ltima chance|s[oó] hoje|acaba|faltam|n[aã]o perca|n[aã]o deixe .{0,20}passar|antes que)\b"
ESCALONAMENTO = r"mais t[ií]tulos|mais chances?|\b\d+ ?x\b|vezes mais|aumenta(m)? (as |suas |tuas )?chances"
CRIANCA = r"crian[cç]|menin[oa]|beb[eê]|filh[oa] pequen"
GRUPO = r"\bgrupo de pessoas\b|multid[aã]o|v[aá]rias pessoas|duas pessoas|tr[eê]s (pessoas|jogadores)|\bcasal\b|fam[ií]lia (toda|reunida)|torcida|plateia"
LENTE = r"olha(ndo)? (para|pra|na|direto (para|pra|na)) (a )?(lente|c[aâ]mera)|encara a c[aâ]mera|olhar na lente"


# ---------- leitura ----------
def ler_casca(texto: str) -> dict:
    fm, corpo = {}, texto
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if m:
        for l in m.group(1).splitlines():
            if ":" in l:
                k, v = l.split(":", 1); fm[norm(k).strip()] = v.strip()
        corpo = m.group(2)
    secoes, atual = {}, None
    for l in corpo.splitlines():
        s = re.match(r"^##\s+([A-H])\s*·", l)
        if s:
            atual = s.group(1); secoes[atual] = []; continue
        if atual:
            secoes[atual].append(l)
    return {"fm": fm, "secoes": {k: "\n".join(v) for k, v in secoes.items()}}


def campos(bloco: str) -> dict:
    out = {}
    for l in bloco.splitlines():
        m = re.match(r"^\s*-\s*\*{0,2}([^:*]+?)\*{0,2}:\s*(.*)$", l)
        if m:
            out[norm(m.group(1)).strip()] = m.group(2).strip()
    return out


def campo(d: dict, nome: str) -> str:
    n = norm(nome)
    for k, v in d.items():
        if k.startswith(n):
            return v
    return ""


def tabela(bloco: str) -> list[dict]:
    linhas = [l for l in bloco.splitlines() if l.strip().startswith("|")]
    if len(linhas) < 2:
        return []
    cab = [norm(c).strip() for c in linhas[0].strip().strip("|").split("|")]
    out = []
    for l in linhas[2:]:
        cels = [c.strip() for c in l.strip().strip("|").split("|")]
        cels += [""] * (len(cab) - len(cels))
        cab_orig = [c.strip().lower() for c in linhas[0].strip().strip("|").split("|")]
        d = dict(zip(cab, cels)); d.update(zip(cab_orig, cels))  # chave sem acento e com acento
        out.append(d)
    return out


def variacoes(bloco: str) -> list[dict]:
    partes = re.split(r"^###\s+", bloco, flags=re.M)[1:]
    return [campos(p) | {"_titulo": p.splitlines()[0].strip()} for p in partes]


# ---------- lint ----------
def regras(sala: pathlib.Path) -> list[dict]:
    f = ler_json(sala / "insumos" / "fatos.snapshot.json")
    r = [{"id": p["id"], "regex": p["regex"], "motivo": p["motivo"], "fonte": "fatos"} for p in f["proibidos"]["lista"]]
    lx = sala / "hooks" / "lexico.json"
    if lx.exists():
        r += [{"id": p["id"], "regex": p["regex"], "motivo": p["motivo"], "fonte": "lexico"} for p in ler_json(lx).get("proibidos_extra", [])]
    return r


def lint_texto(texto: str, sala: pathlib.Path) -> list[str]:
    erros = []
    f = ler_json(sala / "insumos" / "fatos.snapshot.json")
    preco = f["produto"]["preco"]["valor"].replace("R$", "").strip()  # 0,49
    data = f["produto"]["sorteio_data"]["valor"][:5]  # 29/11
    dia = data.split("/")[0]
    for linha in texto.splitlines():
        for p in regras(sala):
            for m in re.finditer(p["regex"], linha, re.I):
                erros.append(f"lint [{p['id']}] '{m.group(0)}': {p['motivo']}")
        for m in re.finditer(r"R\$\s?(\d{1,3}(?:\.\d{3})+|\d{4,})(?:,\d{2})?", linha):
            if m.group(1).replace(".", "") != "100000":
                erros.append(f"lint [fato_premio] '{m.group(0)}': prêmio único nos fatos é R$ 100.000 (promoção comercial bloqueada)")
        for m in re.finditer(r"R\$\s?(\d+)\s?mil\b", linha, re.I):
            if m.group(1) != "100":
                erros.append(f"lint [fato_premio] '{m.group(0)}': prêmio único nos fatos é R$ 100.000 (promoção comercial bloqueada)")
        for m in re.finditer(r"R\$\s?0,(\d{2})", linha):
            if f"0,{m.group(1)}" not in (preco, "0,50"):  # 0,50 = valor de face da moeda (fatos → moeda.referencia)
                erros.append(f"lint [fato_preco] '{m.group(0)}': preço nos fatos é R$ {preco}")
        for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})\b", linha):
            if f"{int(m.group(1)):02d}/{int(m.group(2)):02d}" != data:
                erros.append(f"lint [fato_data] '{m.group(0)}': a data nos fatos é {data}")
        for m in re.finditer(r"\bdia (\d{1,2})\b", linha, re.I):
            if m.group(1) != dia:
                erros.append(f"lint [fato_data] '{m.group(0)}': o sorteio é dia {dia}")
        if re.search(r"\b(um|1) milh[aã]o\b", linha, re.I):
            erros.append("lint [fato_premio] 'um milhão': o prêmio é R$ 100.000 (Seu Milhão é só o nome)")
        if re.search(r"\bcaixa\b", linha, re.I) and re.search(r"escolh|sorte", linha, re.I):
            erros.append("lint [fato_sorteio] 'Caixa': quem sorteia é a Loteria Federal (redação fixa)")
    return erros


# ---------- validação ----------
def localizar(cid: str, sala: pathlib.Path) -> pathlib.Path:
    for pasta in ("rascunho", "aprovadas"):
        p = sala / "cascas" / pasta / f"{cid}.md"
        if p.exists():
            return p
    raise SystemExit(f"casca {cid} não encontrada em cascas/rascunho nem cascas/aprovadas")


def _precos(sala):
    p = ler_json(sala / "insumos" / "fatos.snapshot.json")["tecnica"]["precos_usd"]["valor"]
    return {"quadro": p["nano_banana_1k"], "teste": p["veo_fast_720p_por_s"] * 8,
            "final_padrao": p["veo_padrao_por_s"] * 8, "final_fast": p["veo_fast_1080p_por_s"] * 8}


def _pps(sala):
    c = sala / "insumos" / "calibracao.snapshot.json"
    return (float(ler_json(c)["palavras_por_s"]), ler_json(c).get("origem", "?")) if c.exists() else (PALAVRAS_POR_S_PADRAO, "estimativa")


def _origem(txt: str) -> str:
    t = norm(txt)
    for o in ("apresentador replica", "foto real da instituicao", "banco", "gravacao real"):
        if o in t:
            return o
    return "ia" if re.search(r"\bia\b", t) else ""


def duracao_linha(l: dict, pps: float) -> float:
    n = palavras(l.get("fala-guia", ""))
    if n:
        return round(n / pps, 2)
    return 4.0 if _origem(l.get("origem", "")) == "foto real da instituicao" else 1.5


def similar(a: str, b: str) -> float:
    ta = {w for w in re.findall(r"\w+", norm(a)) if len(w) >= 4}
    tb = {w for w in re.findall(r"\w+", norm(b)) if len(w) >= 4}
    return len(ta & tb) / len(ta | tb) if ta and tb else 0.0


def validar(cid: str, sala: pathlib.Path | None = None, gravar: bool = True) -> dict:
    sala = sala or sala_raiz()
    caminho = localizar(cid, sala)
    c = ler_casca(caminho.read_text(encoding="utf-8"))
    fm, S = c["fm"], c["secoes"]
    bloq, avis = [], []
    # 0. cabeçalho
    for k in ("id", "pedido", "data", "insumos_hash", "segmento", "persona", "angulo", "destino", "familia", "variacao_de", "confianca"):
        if not fm.get(k):
            bloq.append(f"cabeçalho sem '{k}'")
    # 1. seções A a H
    for letra in SECOES:
        if not S.get(letra, "").strip():
            bloq.append(f"seção {letra} ({SECOES[letra]}) ausente ou vazia")
    A, B, E, F = campos(S.get("A", "")), campos(S.get("B", "")), campos(S.get("E", "")), campos(S.get("F", ""))
    for nome, lista, d in (("A", CAMPOS_A, A), ("B", CAMPOS_B, B), ("E", CAMPOS_E, E), ("F", CAMPOS_F, F)):
        for k in lista:
            if not campo(d, k):
                bloq.append(f"{nome}: campo '{k}' vazio")
    # 2. gancho: câmera, ambiente, limites de palavras
    pf, tt = tirar_aspas(campo(B, "primeira fala")), tirar_aspas(campo(B, "texto na tela"))
    if palavras(pf) > 10:
        bloq.append(f"B: primeira fala com {palavras(pf)} palavras (máx. 10)")
    if palavras(tt) > 6:
        bloq.append(f"B: texto na tela com {palavras(tt)} palavras (máx. 6)")
    if pf and not re.search(r"\b(esse|essa|esses|essas|isso|aqui|olha|este|esta|isto|ali|daqui|nesse|nessa)\b", norm(pf)):
        avis.append("B: primeira fala sem referência física ao que está em cena")
    fundo = [x for x in re.split(r";", campo(B, "fundo")) if x.strip()]
    if fundo and not 3 <= len(fundo) <= 5:
        bloq.append(f"B: fundo com {len(fundo)} elementos (3 a 5, separados por ';')")
    lente = campo(B, "lente")
    if lente and not re.search(r"\d{2}\s?mm", lente):
        bloq.append("B: lente sem equivalente em mm (24–28 mm; frontal ~23 mm)")
    prof = norm(campo(B, "profundidade de campo"))
    if prof and "desfoque" in prof and "porque" not in prof and "justific" not in prof and "natural" not in prof:
        avis.append("B: desfoque sem justificativa (padrão é foco profundo)")
    # 3. esqueleto
    linhas = tabela(S.get("C", ""))
    if not linhas:
        bloq.append("C: tabela de batidas ausente")
    else:
        faltam = [col for col in COLUNAS_C if norm(col) not in linhas[0]]
        if faltam:
            bloq.append(f"C: colunas ausentes: {', '.join(faltam)}")
    usadas = [l for l in linhas if norm(l.get("uso", "")).startswith("usad")]
    movs = {}
    for l in linhas:
        m = re.search(r"[1-6]", l.get("mov", ""))
        if m:
            movs.setdefault(int(m.group(0)), []).append(l)
    for n in range(1, 7):
        if n not in movs:
            bloq.append(f"C: movimento {n} não declarado (usado ou suspenso, com o porquê)")
    for l in linhas:
        u = norm(l.get("uso", ""))
        if u.startswith("suspens") and len(u) < 12:
            bloq.append(f"C #{l.get('#')}: suspenso sem o porquê")
        if not (u.startswith("usad") or u.startswith("suspens")):
            bloq.append(f"C #{l.get('#')}: uso deve ser 'usado' ou 'suspenso: motivo'")
    for l in movs.get(5, []):
        if norm(l.get("uso", "")).startswith("usad"):
            bloq.append("C: movimento 5 (escalonamento) usado: suspenso no nível 1")
    pps, origem_pps = _pps(sala)
    if origem_pps == "estimativa":
        avis.append(f"duração pela calibração ESTIMADA ({pps} p/s)")
    for l in usadas:
        i = l.get("#", "?")
        fala = tirar_aspas(l.get("fala-guia", ""))
        if palavras(fala) > 15:
            bloq.append(f"C #{i}: fala-guia com {palavras(fala)} palavras (máx. 15)")
        o = _origem(l.get("origem", ""))
        if not o:
            bloq.append(f"C #{i}: origem inválida (IA | Apresentador réplica | foto real da Instituição | banco | gravação real)")
        if not any(norm(x) in norm(l.get("ligação", "")) for x in LIGACOES):
            bloq.append(f"C #{i}: ligação inválida")
        vis = norm(" ".join(l.get(k, "") for k in ("quem", "ação", "enquadramento", "onde")))
        if o in ("ia", "apresentador replica"):
            if re.search(CRIANCA, vis):
                bloq.append(f"C #{i}: criança em origem {o} (só foto real da Instituição)")
            if re.search(GRUPO, vis):
                bloq.append(f"C #{i}: grupo gerado (um adulto por plano)")
            if o == "ia" and re.search(LENTE, vis):
                bloq.append(f"C #{i}: rosto de IA olhando para a lente (só o Apresentador réplica)")
            if o == "apresentador replica" and re.search(r"\b(fala|diz|conta|explica)\b", norm(l.get("ação", ""))):
                avis.append(f"C #{i}: Apresentador réplica não fala (narração em off)")
        if o in ("ia", "apresentador replica", "banco") and duracao_linha(l, pps) > 2.0:
            avis.append(f"C #{i}: plano de {duracao_linha(l, pps):.1f} s > 2 s fora do plano real")
        mt = re.search(r"mesmo take de #?(\w+)", norm(l.get("origem", "")))
        if mt and not any(x.get("#", "").strip() == mt.group(1) for x in usadas):
            bloq.append(f"C #{i}: 'mesmo take de #{mt.group(1)}' aponta para batida inexistente")
        if o == "banco":
            item = re.search(r"banco[:\s]+([\w.-]+)", l.get("origem", ""), re.I)
            banco = ler_json(sala / "insumos" / "banco.snapshot.json")["itens"] if (sala / "insumos" / "banco.snapshot.json").exists() else []
            achado = next((b for b in banco if item and b["id"] == item.group(1)), None)
            if not achado:
                avis.append(f"C #{i}: banco sem item válido no banco.snapshot (vira GERAR)")
            elif achado.get("tipo") != "video" or achado.get("status") != "liberado":
                avis.append(f"C #{i}: item {achado['id']} não é vídeo liberado (vira GERAR)")
    if usadas and pf and similar(tirar_aspas(usadas[0].get("fala-guia", "")), pf) < 0.5 and palavras(usadas[0].get("fala-guia", "")):
        avis.append("C #1: fala-guia da abertura diferente da primeira fala do gancho")
    # 4. matriz
    mat = {l.get("#", "").strip(): l for l in tabela(S.get("D", ""))}
    for l in usadas:
        i = l.get("#", "").strip()
        if not palavras(l.get("fala-guia", "")):
            continue
        if i not in mat:
            bloq.append(f"D: fala-guia #{i} sem linha na matriz")
        else:
            ec = norm(mat[i].get("em cena", ""))
            if not (ec.startswith("sim") or ec.startswith("justificad")):
                bloq.append(f"D #{i}: fala fora da cena sem justificativa")
    # 5. lint (falas, textos de tela, variações; a seção H cita o original e fica fora)
    G = variacoes(S.get("G", ""))
    textos = [pf, tt] + [tirar_aspas(l.get("fala-guia", "")) for l in usadas] + [l.get("tela", "") for l in usadas]
    textos += [tirar_aspas(campo(g, "primeira fala")) for g in G] + [tirar_aspas(campo(g, "texto na tela")) for g in G]
    todo = "\n".join(t for t in textos if t)
    bloq += list(dict.fromkeys(lint_texto(todo, sala)))
    if len(re.findall(PROVIDENCIA, norm(todo))) > 1:
        bloq.append("providência mais de 1 vez")
    if re.search(DEUS_AUTOR, norm(todo)):
        bloq.append("Deus como autor do prêmio")
    # 6. travas de persona e segmento
    pers, seg = fm.get("persona", "").upper(), norm(fm.get("segmento", ""))
    if "P4" in pers and re.search(URGENCIA, norm(todo)):
        bloq.append("P4: urgência proibida")
    if "P4" in pers and any(norm(l.get("uso", "")).startswith("usad") for l in movs.get(5, [])):
        bloq.append("P4: escalonamento proibido")
    if "alto" in seg and re.search(ESCALONAMENTO, norm(todo)):
        bloq.append("alto ticket: compra em volume para ganhar (fale de contribuição para a causa)")
    if ("alto" in seg or "media" in seg) and "hipotese" not in norm(fm.get("confianca", "")):
        bloq.append("classe média / alto ticket: confiança precisa ser declarada como hipótese")
    # 7. famílias e repetição
    fam = norm(fm.get("familia", ""))
    if fam and fam not in [norm(x) for x in FAMILIAS]:
        bloq.append(f"família '{fm.get('familia')}' fora da lista")
    if len(G) < 2:
        bloq.append("G: são exigidas 2 variações de gancho")
    fams_g = [norm(campo(g, "família")) for g in G[:2]]
    for g, fg in zip(G[:2], fams_g):
        for k in CAMPOS_G:
            if not campo(g, k):
                bloq.append(f"G {g['_titulo']}: campo '{k}' vazio")
        if fg and fg not in [norm(x) for x in FAMILIAS]:
            bloq.append(f"G {g['_titulo']}: família fora da lista")
        if fg == fam:
            bloq.append(f"G {g['_titulo']}: mesma família do gancho principal")
        if palavras(tirar_aspas(campo(g, "primeira fala"))) > 10:
            bloq.append(f"G {g['_titulo']}: primeira fala > 10 palavras")
        if palavras(tirar_aspas(campo(g, "texto na tela"))) > 6:
            bloq.append(f"G {g['_titulo']}: texto na tela > 6 palavras")
        if re.search(CRIANCA, norm(campo(g, "ação física"))):
            bloq.append(f"G {g['_titulo']}: criança na ação física")
    if len(fams_g) == 2 and fams_g[0] and fams_g[0] == fams_g[1]:
        bloq.append("G: as duas variações são da mesma família")
    hooks_p = sala / "hooks" / "biblioteca_hooks.json"
    if hooks_p.exists():
        declarado = norm(fm.get("variacao_de", ""))
        for h in ler_json(hooks_p)["itens"]:
            for rot, fala in [("gancho", pf)] + [(f"G {g['_titulo']}", tirar_aspas(campo(g, "primeira fala"))) for g in G]:
                if fala and similar(fala, h.get("texto_original", "")) >= 0.6 and norm(h["id"]) not in declarado and norm(h["id"]) not in norm(str(G)):
                    bloq.append(f"{rot}: repete {h['id']} sem declarar variação")
    # 8. duração e custo
    dur = round(sum(duracao_linha(l, pps) for l in usadas), 1)
    dmax = None
    ped = sala / "pedidos" / f"{fm.get('pedido', '')}.md"
    if ped.exists():
        m = re.search(r"duracao_s:\s*(\d+)", ped.read_text(encoding="utf-8"))
        dmax = float(m.group(1)) if m else None
    elif fm.get("pedido"):
        bloq.append(f"pedido {fm.get('pedido')} não encontrado")
    dmax = dmax or float(re.sub(r"[^\d.]", "", fm.get("duracao_alvo_s", "") or "0") or 0) or None
    if dmax and dur > dmax:
        bloq.append(f"duração {dur:.1f} s > pedido {dmax:.0f} s")
    pr = _precos(sala)
    custo, gerar, reuso, trechos = 0.0, [], [], []
    for l in usadas:
        o, i = _origem(l.get("origem", "")), l.get("#", "?")
        if re.search(r"mesmo take", norm(l.get("origem", ""))):
            trechos.append(i); continue
        if o in ("ia", "apresentador replica"):
            padrao = o == "apresentador replica" or re.search(r"rosto|m[aã]o|moeda|close|cheque", norm(l.get("enquadramento", "") + " " + l.get("ação", "")))
            custo += pr["quadro"] + pr["teste"] + (pr["final_padrao"] if padrao else pr["final_fast"]); gerar.append(i)
        elif o == "banco":
            reuso.append(i)
    # 9. insumos atualizados
    status = "OK"
    man = sala / "insumos" / "MANIFESTO.json"
    mudou = []
    if not man.exists():
        bloq.append("insumos nunca sincronizados (./sala sincronizar)")
    else:
        atual = ler_json(man)
        if fm.get("insumos_hash") != atual["hash"]:
            status = "DESATUALIZADA"
            antigo = sala / "insumos" / "historico" / f"{fm.get('insumos_hash')}.json"
            if antigo.exists():
                a, b = ler_json(antigo)["arquivos"], atual["arquivos"]
                mudou = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            bloq.append(f"DESATUALIZADA: insumos {fm.get('insumos_hash')} → {atual['hash']}" + (f" (mudou: {', '.join(mudou[:6])})" if mudou else ""))
    if status == "OK" and bloq:
        status = "BLOQUEADA"
    res = {"id": cid, "arquivo": str(caminho.relative_to(sala)), "status": status, "bloqueios": bloq, "avisos": avis,
           "duracao_s": dur, "duracao_max_s": dmax, "custo_estimado_usd": round(custo, 2), "gerar": gerar, "reuso": reuso, "trechos_do_mesmo_take": trechos,
           "insumos_hash": fm.get("insumos_hash"), "mudou": mudou, "data": hoje()}
    if gravar:
        gravar_json(caminho.with_suffix(".validacao.json"), res)
    return res


def relatorio(r: dict) -> str:
    L = [f"CASCA {r['id']}: {r['status']} · {len(r['bloqueios'])} bloqueio(s) · {len(r['avisos'])} aviso(s) · {r['duracao_s']} s"
         f"{' de ' + str(int(r['duracao_max_s'])) if r['duracao_max_s'] else ''} · custo estimado US$ {r['custo_estimado_usd']:.2f} (NADA gerado)"]
    L.append(f"  gerar: {', '.join(r['gerar']) or '—'} · trechos do mesmo take: {', '.join(r.get('trechos_do_mesmo_take', [])) or '—'} · reuso do banco: {', '.join(r['reuso']) or '—'}")
    L += [f"✗ {x}" for x in r["bloqueios"][:6]] + [f"! {x}" for x in r["avisos"][:3]]
    return "\n".join(L[:10])
