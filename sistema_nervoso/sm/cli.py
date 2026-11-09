"""CLI `sm`. Saída curta (≤ 5 linhas) por padrão."""
import json, pathlib, subprocess, sys, typer
from typing import Optional
from .raiz import raiz, ler_json, criativo_dir, rel
from . import memoria, fluxo as F, validadores as V

app = typer.Typer(help="sm — sistema nervoso do Seu Milhão (reflexos sem token)", no_args_is_help=True, add_completion=False)


def _ok(msg): typer.echo(msg)
def _erro(msg, code=1): typer.echo(msg, err=True); raise typer.Exit(code)


# ---------------- fluxo ----------------
@app.command()
def status(id: Optional[str] = typer.Argument(None, help="criativo (padrão: criativo_atual)")):
    """Onde estamos: próximo micro-passo, passos [VOCÊ] pendentes, custo e saldo."""
    g = F.estado_global()
    reg_r = g.get("reestruturacao", {}).get("passos", {})
    prox_r = F.proximo_passo("reestruturacao.yaml", reg_r)
    linhas = []
    if prox_r and prox_r["id"] != "R18":
        n_ok = sum(1 for v in reg_r.values() if v.get("status") == "ok")
        linhas.append(f"Reestruturação: {n_ok}/18 ok · próximo {prox_r['id']} ({prox_r['executor']}): {prox_r['descricao']}")
    cid = id or g.get("criativo_atual")
    if cid and (criativo_dir(cid) / "estado.json").exists():
        est = F.estado_criativo(cid)
        reg = est.get("passos", {})
        prox = F.proximo_passo("passos.yaml", reg)
        voce = [p for p, v in reg.items() if v.get("status") == "aguardando_voce"]
        from .custo import gasto_de
        gasto, teto = gasto_de(cid), float(est.get("teto_usd", memoria.fato("tecnica.teto_padrao_conjunto")))
        linhas.append(f"{cid} · {est.get('titulo','')} · passo {prox['id'] if prox else 'P18 ok'}: {prox['descricao'] if prox else 'concluído'} [{prox['executor'] if prox else '-'}]")
        if voce: linhas.append(f"[VOCÊ] pendente: {', '.join(voce)}")
        pct = 100 * gasto / teto if teto else 0
        linhas.append(f"custo US$ {gasto:.2f} de {teto:.2f} ({pct:.0f}%) · saldo {teto - gasto:.2f}" + (" ⚠️ ≥80%" if pct >= 80 else ""))
    elif cid:
        linhas.append(f"{cid}: sem criativos/{cid}/estado.json")
    _ok("\n".join(linhas[:5]) or "nada em andamento")


@app.command()
def proximo(id: Optional[str] = typer.Argument(None)):
    """Descreve o próximo micro-passo e quem executa (script, agente ou VOCÊ)."""
    g = F.estado_global()
    reg_r = g.get("reestruturacao", {}).get("passos", {})
    prox_r = F.proximo_passo("reestruturacao.yaml", reg_r)
    if prox_r and prox_r["id"] != "R18":
        p = prox_r
    else:
        cid = id or g.get("criativo_atual")
        p = F.proximo_passo("passos.yaml", F.estado_criativo(cid).get("passos", {})) if cid else None
    if not p: return _ok("nenhum passo pendente")
    ex = p["executor"]
    quem = "VOCÊ (dê o check: sm aprovar %s)" % p["id"] if ex == "VOCÊ" else ("script (sm validar %s)" % p["id"] if ex == "script" else f"agente {ex}")
    _ok(f"{p['id']} · {p['linha']} · {p['descricao']}\nexecutor: {quem}\nvalidador: {p.get('validador') or '—'}\ndepende de: {', '.join(p.get('depende_de') or []) or '—'}")


@app.command()
def validar(passo: str, alvo: Optional[str] = typer.Argument(None, help="id do criativo em `sm validar roteiro <id>`"), id: Optional[str] = typer.Option(None, "--id", help="criativo (passos P)")):
    """Roda o validador do passo; check automático se passar. Falhou 2 vezes: PARE e mostre o erro. Também: `sm validar roteiro <id>` e `sm validar coerencia`."""
    if passo.lower() == "roteiro":
        from .roteiro import validar as vr
        if not (alvo or id): _erro("uso: sm validar roteiro <id>")
        return _ok(vr(alvo or id))
    if passo.lower() == "coerencia":
        e = V.coerencia()
        _erro("coerência FALHOU:\n" + "\n".join(f"  - {x}" for x in e[:12])) if e else _ok("coerência ✓ (fatos.json única fonte; RESUMO, PLAYBOOK e fatos sem contradição; MDs apontam para fatos.json)")
        return
    passo = passo.upper()
    esc, cid = F.escopo(passo, id)
    arquivo = "reestruturacao.yaml" if esc == "reestruturacao" else "passos.yaml"
    p = {x["id"]: x for x in F.carregar_passos(arquivo)}.get(passo)
    if not p: _erro(f"passo {passo} não existe em {arquivo}")
    if p["executor"] == "VOCÊ": _erro(f"{passo} é [VOCÊ]: use sm aprovar {passo}")
    nome = p.get("validador")
    fn = V.VALIDADORES.get(nome)
    if not fn: _erro(f"{passo}: validador '{nome}' não implementado")
    erros = fn(cid) if esc == "producao" else fn()
    if erros:
        F.marcar_falha(passo, "; ".join(erros), cid)
        n = F.falhas_consecutivas(passo, cid)
        _erro(f"{passo} FALHOU ({n}ª vez{' — PARE e mostre ao usuário' if n >= 2 else ''}):\n" + "\n".join(f"  - {e}" for e in erros[:8]))
    F.registrar(passo, "ok", "validador passou", cid)
    _ok(f"{passo} ✓ ({p['descricao']})")


@app.command()
def aprovar(passo: str, nota: Optional[str] = typer.Argument(None), id: Optional[str] = typer.Option(None, "--id"), reprovar: bool = typer.Option(False, "--reprovar")):
    """Registra o seu check num passo [VOCÊ] (também acionado pelo painel)."""
    passo = passo.upper()
    esc, cid = F.escopo(passo, id)
    F.registrar(passo, "falhou" if reprovar else "ok", nota or ("reprovado pelo usuário" if reprovar else "aprovado pelo usuário"), cid)
    _ok(f"{passo} {'reprovado' if reprovar else '✓ aprovado'}" + (f" · {nota}" if nota else ""))


@app.command()
def pendente(passo: str, id: Optional[str] = typer.Option(None, "--id")):
    """Marca um passo [VOCÊ] como aguardando o seu check (o chefe de linha chama ao chegar no portão)."""
    esc, cid = F.escopo(passo.upper(), id)
    F.registrar(passo.upper(), "aguardando_voce", "aguardando o usuário", cid)
    _ok(f"{passo.upper()} aguardando VOCÊ")


# ---------------- memória ----------------
@app.command()
def fato(chave: str, completo: bool = typer.Option(False, "--completo", help="mostra fonte e data")):
    """Devolve um fato de memoria/fatos.json (ex.: sm fato produto.premio)."""
    try:
        v = memoria.fato(chave, so_valor=not completo)
    except KeyError as e:
        _erro(str(e))
    _ok(json.dumps(v, ensure_ascii=False, indent=1) if isinstance(v, (dict, list)) else str(v))


@app.command()
def fatos(prefixo: str = typer.Argument("")):
    """Lista as chaves de fatos (filtro por prefixo)."""
    _ok("\n".join(k for k, _ in memoria.folhas() if k.startswith(prefixo)))


# ---------------- lint ----------------
@app.command()
def lint(arquivo: pathlib.Path, rodape: bool = typer.Option(False, "--rodape", help="exige o rodapé legal")):
    """Linter de política: proibidos, fatos divergentes, rodapé ausente, data e valor errados."""
    from .lint import lint_arquivo, formatar
    vs = lint_arquivo(arquivo, rodape)
    typer.echo(formatar(vs))
    raise typer.Exit(1 if vs else 0)


# ---------------- produção ----------------
@app.command()
def calibrar(audio: Optional[pathlib.Path] = typer.Argument(None)):
    """Mede palavras/s do Apresentador (Whisper local) → memoria/calibracao.json; sem gravação usa 2,4 (estimativa)."""
    from .calibrar import calibrar as c
    _ok(c(audio))


partitura_app = typer.Typer(help="partitura.json"); app.add_typer(partitura_app, name="partitura")
@partitura_app.command("validar")
def partitura_validar(id: str):
    from .partitura import validar
    e = validar(id)
    _erro("\n".join(e)) if e else _ok(f"partitura {id} OK")

decupagem_app = typer.Typer(help="decupagem.json"); app.add_typer(decupagem_app, name="decupagem")
@decupagem_app.command("validar")
def decupagem_validar(id: str):
    from .decupagem import validar
    e = validar(id)
    _erro("\n".join(e)) if e else _ok(f"decupagem {id} OK")

banco_app = typer.Typer(help="banco de takes (catálogo da biblioteca)"); app.add_typer(banco_app, name="banco")
@banco_app.command("buscar")
def banco_buscar(id: str):
    from .banco import buscar
    _ok(buscar(id))

quadro_app = typer.Typer(help="quadros (Nano Banana)"); app.add_typer(quadro_app, name="quadro")
@quadro_app.command("gerar")
def quadro_gerar(id: str, take: str, fim: bool = typer.Option(False, "--fim"), seco: bool = typer.Option(False, "--seco"), confirmar: bool = typer.Option(False, "--confirmar")):
    from .gerar import quadro
    _ok(quadro(id, take, fim=fim, seco=seco, confirmar=confirmar))

veo_app = typer.Typer(help="Veo (único caminho de gasto em vídeo)"); app.add_typer(veo_app, name="veo")
@veo_app.command("gerar")
def veo_gerar(id: str, take: str, modo: str = typer.Option("teste", "--modo", help="teste | final"), confirmar: bool = typer.Option(False, "--confirmar"), seco: bool = typer.Option(False, "--seco"), tentativa: int = typer.Option(1, "--tentativa")):
    from .gerar import veo
    _ok(veo(id, take, modo=modo, confirmar=confirmar, seco=seco, tentativa=tentativa))


@app.command()
def folha(id: str, tipo: str = typer.Argument("tomadas", help="quadros | tomadas"), take: Optional[str] = None):
    """Folhas de contato reduzidas."""
    from .midia import folhas
    _ok(folhas(id, tipo, take))


@app.command("tira-moeda")
def tira_moeda(id: str, take: Optional[str] = None):
    from .midia import tira_moeda as tm
    _ok(tm(id, take))


@app.command()
def inspecionar(id: str, etapa: str = typer.Option("teste", "--etapa")):
    """Checagens automáticas (dimensão, fps, duração, áudio ausente, quadros pretos, OCR) + folhas."""
    from .midia import inspecionar as insp
    _ok(insp(id, etapa))


@app.command()
def padronizar(id: str, take: str, entrada: Optional[str] = None, trecho: str = "0-4"):
    from .midia import padronizar as pz
    _ok(pz(id, take, entrada, trecho))


@app.command("ultimo-quadro")
def ultimo_quadro(id: str, take: str):
    from .midia import ultimo_quadro as uq
    _ok(uq(id, take))


@app.command()
def emendar(id: str):
    from .midia import emendar as em
    _ok(em(id))


@app.command("animar-foto")
def animar_foto(foto: pathlib.Path, saida: pathlib.Path, zoom: float = 1.06, deslize_px: int = 0, duracao: float = 4.0):
    from .midia import animar_foto as af
    _ok(af(foto, saida, zoom, deslize_px, duracao))


@app.command()
def montar(id: str):
    """Sequência com grafismos e rodapé; versões com e sem copies."""
    from .montar import montar as mt
    _ok(mt(id))


@app.command()
def ponte(id: str):
    from .ponte import ponte as pt
    _ok(pt(id))


@app.command()
def publicar(id: str, seco: bool = typer.Option(False, "--seco"), completo: bool = typer.Option(False, "--conjunto-completo")):
    """Biblioteca: só com G4; catálogo, tags, README, commit, push."""
    from .publicar import publicar as pb
    _ok(pb(id, seco=seco, completo=completo))


custo_app = typer.Typer(help="custos"); app.add_typer(custo_app, name="custo")
@custo_app.callback(invoke_without_command=True)
def custo_cb(ctx: typer.Context):
    if ctx.invoked_subcommand: return
    from .custo import resumo
    _ok(resumo(None))
@custo_app.command("ver")
def custo_ver(id: str):
    from .custo import resumo
    _ok(resumo(id))
@custo_app.command("fechar")
def custo_fechar(id: str):
    from .custo import fechar
    _ok(fechar(id))
@custo_app.command("tokens")
def custo_tokens(id: str, n: int, nota: str = ""):
    from .custo import registrar_tokens
    _ok(registrar_tokens(id, n, nota))


@app.command()
def inventario():
    from .inventario import gerar
    _ok(gerar())


@app.command()
def painel(porta: int = 8765):
    """Sobe o painel local (só 127.0.0.1; nunca gera)."""
    subprocess.run([sys.executable, str(raiz() / "painel" / "servidor.py"), "--porta", str(porta)])


@app.command()
def novo(id: str, titulo: str, teto: float = 45.0):
    """Abre criativos/<id>/ com estado.json e custos.md (o cartão em planejamento/cartoes/<id>.json é o P01)."""
    from .criativo import novo as nv
    _ok(nv(id, titulo, teto))


@app.command()
def vertex():
    """Testa o acesso à Vertex AI sem custo."""
    from .gerar import testar_vertex
    _ok(testar_vertex())


@app.command("tratar-celular")
def tratar_celular(arquivo: pathlib.Path, saida: Optional[pathlib.Path] = typer.Argument(None), intensidade: str = typer.Option("leve", "--intensidade", help="leve | media"), estilo: str = "realismo-celular"):
    """Pós-processamento de celular (tremor, curva, nitidez, grão, ciclo de compressão). Parâmetros em estilos/<estilo>/pos.json."""
    from .tratar import tratar
    _ok(tratar(arquivo, saida, intensidade, estilo))


@app.command()
def comparar(arquivos: list[pathlib.Path], referencia: Optional[pathlib.Path] = typer.Option(None, "--referencia"), saida: Optional[pathlib.Path] = typer.Option(None, "--saida")):
    """Folha antes × depois × referência + tabela de métricas (saturação, realces, alta frequência, tremor)."""
    from .tratar import comparar as cp
    _ok(cp([str(a) for a in arquivos], str(referencia) if referencia else None, saida))


@app.command("liberar-geracao")
def liberar_geracao(id: str):
    """Destrava a geração paga para UM criativo (só o usuário)."""
    from .trava import liberar
    _ok(liberar(id))


@app.command("travar-geracao")
def travar_geracao():
    from .trava import travar
    _ok(travar())


@app.command("importar-roteiro")
def importar_roteiro(arquivo: pathlib.Path, id: Optional[str] = typer.Option(None, "--id")):
    """Lê o ROTEIRO_QUADRO_A_QUADRO.md preenchido → criativos/<id>/partitura.json + decupagem.json. Nada é gerado."""
    from .roteiro import importar
    _ok(importar(arquivo, id))


if __name__ == "__main__":
    app()
