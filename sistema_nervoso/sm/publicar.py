"""Biblioteca: catálogo, README com miniaturas, publicação só com G4, teste do gancho. --seco espelha em _seco/biblioteca/."""
import datetime, json, pathlib, re, shutil, subprocess
from .raiz import raiz, criativo_dir, ler_json, gravar_json, rel, hoje, agora
from .memoria import fato
from .midia import sh, probe

ISENTOS = {"README.md", "CATALOGO.md", "catalogo.json", ".gitattributes", ".gitignore", ".lfs-cota"}
PASTAS_ISENTAS = (".githooks/", "playbook/", "_miniaturas/")
SECOES = [("referencias/estilo", "Estilo"), ("referencias/moeda50", "Moeda de 50 centavos"), ("referencias/apresentador", "Apresentador (réplica autorizada)"),
          ("referencias/instituicao", "Instituição Parceira (fotos reais)"), ("referencias/marca", "Marca"),
          ("regulamento", "Regulamento e consultas"), ("aprovados", "Vídeos aprovados (G4) · banco de takes")]
EMOJI = {"liberado": "🟢", "provisorio": "🟡", "bloqueado": "🔴"}


def bib(seco=False):
    return raiz() / ("_seco/biblioteca" if seco else "biblioteca")


def git(b, *a):
    return subprocess.run(["git", "-C", str(b), *a], text=True, capture_output=True)


def carregar(b):
    p = b / "catalogo.json"
    return ler_json(p, {"versao": 1, "atualizado": None, "itens": []})


def salvar(b, cat):
    cat["atualizado"] = agora(); cat["itens"].sort(key=lambda i: i["caminho"]); gravar_json(b / "catalogo.json", cat)


def add(b, caminho, tipo, origem, licenca, autorizacao, status, tags=None, take_origem=None, nota="", id=None):
    cat = carregar(b)
    if not (b / caminho).exists(): raise SystemExit(f"arquivo não existe na biblioteca: {caminho}")
    item = {"id": id or re.sub(r"[^a-z0-9]+", "-", caminho.lower().replace("referencias/", "").rsplit(".", 1)[0]).strip("-"), "tipo": tipo, "caminho": caminho,
            "origem": origem, "licenca": licenca, "autorizacao": autorizacao, "status": status, "data": hoje(), "take_origem": take_origem,
            "tags": {"persona": [], "angulo": [], "lugar": [], "elemento": [], **(tags or {})}, "nota": nota}
    cat["itens"] = [i for i in cat["itens"] if i["caminho"] != caminho] + [item]
    salvar(b, cat); return item["id"]


def check(b) -> list[str]:
    cat = carregar(b); caminhos = {i["caminho"] for i in cat["itens"]}; e = []
    out = git(b, "ls-files", "--cached", "--others", "--exclude-standard").stdout if (b / ".git").exists() else "\n".join(str(p.relative_to(b)) for p in b.rglob("*") if p.is_file())
    for p in out.splitlines():
        if not p.strip() or p in ISENTOS or p.startswith(PASTAS_ISENTAS) or pathlib.Path(p).name in ISENTOS: continue
        if p not in caminhos: e.append(f"sem entrada no catálogo: {p}")
    for i in cat["itens"]:
        if not (b / i["caminho"]).exists(): e.append(f"entrada sem arquivo: {i['id']}")
        if not i.get("origem") or not i.get("licenca"): e.append(f"{i['id']}: sem origem/licença")
    return e


def lfs_uso(b):
    tot = 0.0
    for l in git(b, "lfs", "ls-files", "-s").stdout.splitlines():
        m = re.search(r"\(([\d.]+)\s*(B|KB|MB|GB)\)", l)
        if m: tot += float(m.group(1)) * {"B": 1 / 1024 / 1024, "KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]
    cota = 1024.0
    if (b / ".lfs-cota").exists():
        try: cota = float((b / ".lfs-cota").read_text().strip())
        except ValueError: pass
    return tot, cota


def readme(b) -> str:
    cat = carregar(b); itens = cat["itens"]
    def mini(i):
        p = b / i["caminho"]; ext = p.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp"): return i["caminho"]
        if ext in (".mp4", ".mov"):
            m = b / "_miniaturas" / (i["id"] + ".jpg"); m.parent.mkdir(exist_ok=True)
            if not m.exists(): subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", str(p), "-frames:v", "1", "-vf", "scale=320:-2", str(m)])
            return f"_miniaturas/{m.name}" if m.exists() else None
        return None
    L = ["# seu-milhao-biblioteca", "", f"Referências catalogadas e **somente** takes e sequências com G4. Gerado por `sm publicar` em {datetime.datetime.now():%d/%m/%Y %H:%M}. {len(itens)} itens.", "",
         "🟢 liberado · 🟡 provisório · 🔴 bloqueado · autorização sim/não/pendente", ""]
    for pref, tit in SECOES:
        sel = [i for i in itens if i["caminho"].startswith(pref + "/")]
        if not sel: continue
        L += [f"## {tit}", "", "<table><tr>"]
        for n, i in enumerate(sel, 1):
            m = mini(i); cel = (f'<a href="{i["caminho"]}"><img src="{m}" width="150"></a><br>' if m else "") + f'<a href="{i["caminho"]}"><code>{i["id"]}</code></a><br>{EMOJI.get(i["status"], "")} {i["status"]} · aut. {i["autorizacao"]}<br><small>{i["tipo"]}' + (f' · {", ".join(i["tags"].get("lugar", []))}' if i["tags"].get("lugar") else "") + "</small>"
            L.append(f'<td valign="top" width="170">{cel}</td>' + ("</tr><tr>" if n % 5 == 0 else ""))
        L += ["</tr></table>", ""]
    tot, cota = lfs_uso(b)
    L += ["## Espaço (LFS)", "", f"Uso local: **{tot:.1f} MiB** de {cota:.0f} MiB ({100*tot/cota:.0f}%)" + (" ⚠️ ≥80%" if tot >= 0.8 * cota else "") + ". Cota real: github.com/settings/billing.", ""]
    (b / "README.md").write_text("\n".join(L), encoding="utf-8")
    C = ["# Catálogo", "", "| id | tipo | caminho | status | aut. | origem | licença | data | take | tags |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i in itens:
        tg = "; ".join(f"{k}: {', '.join(v)}" for k, v in i["tags"].items() if v)
        C.append(f"| `{i['id']}` | {i['tipo']} | [{i['caminho']}]({i['caminho']}) | {i['status']} | {i['autorizacao']} | {i['origem']} | {i['licenca']} | {i['data']} | {i.get('take_origem') or ''} | {tg} |")
    (b / "CATALOGO.md").write_text("\n".join(C) + "\n", encoding="utf-8")
    return f"README/CATALOGO ({len(itens)} itens) · LFS {tot:.1f}/{cota:.0f} MiB ({100*tot/cota:.0f}%)"


def publicar(cid, seco=False, completo=False) -> str:
    d = criativo_dir(cid); est = ler_json(d / "estado.json")
    if est.get("passos", {}).get("P15", {}).get("status") != "ok" and not est.get("portoes", {}).get("G4", {}).get("decisao") == "aprovado":
        raise SystemExit(f"RECUSADO: {cid} sem G4 (P15) aprovado")
    dec = ler_json(d / "decupagem.json"); part = ler_json(d / "partitura.json")
    b = bib(seco); dest = b / "aprovados" / cid; (dest / "takes").mkdir(parents=True, exist_ok=True)
    if seco and (raiz() / "biblioteca" / ".gitattributes").exists() and not (b / ".gitattributes").exists():
        shutil.copy(raiz() / "biblioteca" / ".gitattributes", b / ".gitattributes")  # espelho a seco começa com catálogo vazio
    ap = d / "aprovados"; ids = []
    tags_c = {"segmento": [part.get("segmento") or est.get("segmento") or "popular"], "angulo": [part.get("angulo") or est.get("angulo") or "solidario"]}
    for i, t in enumerate(dec["takes"], 1):
        src = ap / f"{t['id']}_take.mp4"
        if not src.exists() or t.get("origem") == "REUSO": continue
        for suf, lab in (("", "sem texto"), ("_copies", "com texto")):
            s = ap / f"{t['id']}_take{suf}.mp4"
            if not s.exists(): continue
            out = dest / "takes" / f"{i:02d}_take{suf}.mp4"
            sh("ffmpeg", "-y", "-v", "error", "-i", s, "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "24", "-movflags", "+faststart", out)
            tg = {**tags_c, **{k: (v if isinstance(v, list) else [v]) for k, v in (t.get("tags") or {}).items()}, "ligacao": [t.get("ligacao")], "duracao": [f"{int(round(float(t['duracao_s'])))}s"], "estilo": [dec["estilo"]], "modelo": [t.get("modelo")]}
            ids.append(add(b, f"aprovados/{cid}/takes/{i:02d}_take{suf}.mp4", "video", f"{t.get('modelo')} · {cid} {t['id']} · G4", "produção própria (saída do modelo, conta do projeto)", "sim", "liberado", tg, f"{cid}/{t['id']}", f"take reutilizável ({lab}); trecho {est.get('takes', {}).get(t['id'], {}).get('trecho_uso', '')}", id=f"{cid.lower()}-{t['id'].lower()}-take{suf.replace('_','-')}"))
    for n in ("sequencia.mp4", "sequencia_copies.mp4", "copies.txt", "rodape_legal.png"):
        if (ap / n).exists():
            shutil.copy(ap / n, dest / n)
            ids.append(add(b, f"aprovados/{cid}/{n}", "video" if n.endswith(".mp4") else ("imagem" if n.endswith(".png") else "texto"), f"esteira {cid} (sm montar)", "produção própria", "sim", "liberado", tags_c, cid, id=f"{cid.lower()}-{n.replace('.', '-').replace('_','-')}"))
    pc = raiz() / "ponte_capcut" / cid
    for n in ("partitura.srt", "guia_copies.srt"):
        if (pc / n).exists():
            shutil.copy(pc / n, dest / n); ids.append(add(b, f"aprovados/{cid}/{n}", "texto", f"esteira {cid} (sm ponte)", "produção própria", "sim", "liberado", tags_c, cid, id=f"{cid.lower()}-{n.replace('.', '-').replace('_','-')}"))
    # FICHA
    from .custo import gasto_de
    pend = "\n".join(f"- {k}: {v['valor']} — {v['status']} (dono: {v['dono']})" for k, v in fato("pendencias", so_valor=False).items() if v.get("status") not in ("confirmado",))
    tax = "\n".join(f"- {k}: {v}" for k, v in part.get("taxonomia", {}).items())
    prompts = "\n\n".join(f"### {p.name}\n```\n{p.read_text(encoding='utf-8').strip()}\n```" for p in sorted((d / "prompts").glob("*.txt")) if not re.search(r"api_key|token|secret", p.read_text(encoding='utf-8'), re.I))
    (dest / "FICHA.md").write_text(f"# FICHA · {cid} · {part.get('titulo', est.get('titulo', ''))}\n\nPublicado em {hoje()} · custo US$ {gasto_de(cid):.2f} · estilo {dec['estilo']} · {len(dec['takes'])} takes · {'SECO (simulado)' if seco else 'G4 aprovado'}\n\n## Taxonomia\n{tax}\n\n## Falas\n" + "\n".join(f"- {f['id']} (mov. {f['movimento']}, {f['duracao_s']} s): {f['texto']}" for f in part['falas']) + f"\n\n## Takes\n" + "\n".join(f"- {t['id']}: {t['descricao']} · {t['ligacao']} · {t.get('origem')}" for t in dec['takes']) + f"\n\n## Prompts\n{prompts}\n\n## Pendências de veiculação\n{pend}\n", encoding="utf-8")
    ids.append(add(b, f"aprovados/{cid}/FICHA.md", "documento", f"esteira {cid}", "produção própria", "sim", "liberado", tags_c, cid, id=f"{cid.lower()}-ficha"))
    e = check(b)
    if e: raise SystemExit("catálogo inconsistente:\n" + "\n".join(e[:6]))
    r = readme(b)
    commit = None
    if not seco:
        git(b, "add", "-A")
        rc = git(b, "-c", "user.name=Operator", "-c", "user.email=user@example.com", "commit", "-q", "-m", f"{cid} · publicado · custo US$ {gasto_de(cid):.2f}")
        if rc.returncode: raise SystemExit("commit recusado pelo gancho:\n" + rc.stderr[-800:])
        commit = git(b, "rev-parse", "--short", "HEAD").stdout.strip()
        push = git(b, "push", "-q", "origin", "HEAD")
        if push.returncode: raise SystemExit("push falhou: " + push.stderr[-300:])
        if completo:
            base, v = cid.lower(), 1
            while git(b, "rev-parse", "-q", "--verify", f"refs/tags/{base}-v{v}").returncode == 0: v += 1
            git(b, "tag", "-a", f"{base}-v{v}", "-m", f"{cid} completo"); git(b, "push", "origin", f"{base}-v{v}")
    est["publicado"] = {"data": agora(), "seco": seco, "commit": commit, "itens": ids}
    gravar_json(d / "estado.json", est)
    tot, cota = lfs_uso(b)
    return f"publicado {cid}{' (SECO em _seco/biblioteca)' if seco else ' · commit ' + str(commit)} · {len(ids)} itens · {r}" + (" ⚠️ LFS ≥80%" if tot >= 0.8 * cota else "")


def testar_gancho() -> list[str]:
    """Cria arquivos proibidos na biblioteca real, tenta commit, espera recusa, limpa. Devolve erros (vazio = gancho funciona)."""
    b = bib(False)
    if not (b / ".git").exists(): return ["biblioteca/ não é um clone git"]
    (b / "aprovados" / "TK-99" / "takes").mkdir(parents=True, exist_ok=True); (b / "fontes" / "autorizacoes").mkdir(parents=True, exist_ok=True)
    f1 = b / "aprovados/TK-99/takes/01_take.mp4"; f2 = b / "fontes/autorizacoes/termo.md"; f3 = b / "referencias/estilo/_teste_sem_catalogo.txt"
    try:
        sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.5", "-r", "24", f1)
        f2.write_text("termo falso"); f3.write_text("sem catálogo")
        git(b, "add", "-A")
        rc = git(b, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "teste: deve ser bloqueado")
        if rc.returncode == 0:
            git(b, "reset", "-q", "--soft", "HEAD~1"); return ["o gancho NÃO bloqueou o commit de teste"]
        motivos = rc.stderr
        e = []
        for chave in ("TK-99", "autorizacoes", "sem entrada"):
            if chave not in motivos: e.append(f"gancho não citou '{chave}'")
        return e
    finally:
        git(b, "reset", "-q", "HEAD", "--", "aprovados/TK-99", "fontes", "referencias/estilo/_teste_sem_catalogo.txt")
        shutil.rmtree(b / "aprovados" / "TK-99", ignore_errors=True); shutil.rmtree(b / "fontes", ignore_errors=True); f3.unlink(missing_ok=True)
