"""./sala sincronizar — copia para insumos/ o que a produção deixa ler, grava hash e data, gera limites_producao.md.
Só LÊ a produção. Nunca escreve fora de sala_de_roteiro/."""
import glob
import html
import pathlib
import re
import shutil
import subprocess
import zipfile

from .base import (agora, gravar_json, hash_conjunto, ler_json, producao_raiz, sala_raiz, sha256_arquivo)

# (destino em insumos/, origem relativa à produção)
COPIAS = [
    ("fatos.snapshot.json", "memoria/fatos.json"),
    ("glossario.snapshot.json", "memoria/glossario.json"),
    ("calibracao.snapshot.json", "memoria/calibracao.json"),
    ("modelo_roteiro.snapshot.md", "planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md"),
    ("playbook_resumo.snapshot.md", "docs/01_PLAYBOOK_RESUMO.md"),
]
GLOBS = [("segmentos/{nome}", "planejamento/segmentos/*.md"),
         ("estilos/{pasta}/{nome}", "estilos/*/bloco.txt"),
         ("estilos/{pasta}/{nome}", "estilos/*/negativos.txt"),
         ("estilos/{pasta}/{nome}", "estilos/*/licoes.md")]
CORPUS = [("roteiros_100mil_atemporal.txt", "ROTEIROS*Atemporal*.pdf"),
          ("mensagens_comunidade.txt", "Mensagem*Comunidade*.pdf"),
          ("meta_comunidade.txt", "Meta*Comunidade*.docx")]
CAMPOS_BANCO = ("id", "tipo", "caminho", "status", "autorizacao", "take_origem", "tags", "nota")


def _texto_pdf(p) -> str:
    if not shutil.which("pdftotext"):
        raise SystemExit("pdftotext não encontrado (brew install poppler)")
    return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, check=True).stdout


def _texto_docx(p) -> str:
    with zipfile.ZipFile(p) as z:
        x = z.read("word/document.xml").decode("utf-8")
    x = re.sub(r"</w:p>", "\n", x)
    return html.unescape(re.sub(r"<[^>]+>", "", x))


def _achar_corpus(pasta: pathlib.Path, padrao: str):
    cands = sorted(pathlib.Path(c) for c in glob.glob(str(pasta / padrao)))
    if padrao.endswith(".docx"):
        cands = [c for c in cands if zipfile.is_zipfile(c)]
    cands.sort(key=lambda c: (-c.stat().st_size, c.name))
    return cands[0] if cands else None


def sincronizar(corpus: str | None = None) -> str:
    sala, prod = sala_raiz(), producao_raiz()
    ins = sala / "insumos"
    ins.mkdir(parents=True, exist_ok=True)
    arquivos, origem = {}, {}

    def registrar(rel, src):
        arquivos[rel] = sha256_arquivo(ins / rel)
        origem[rel] = str(src)

    for dst, src in COPIAS:
        s = prod / src
        if not s.exists():
            raise SystemExit(f"insumo ausente na produção: {src}")
        shutil.copyfile(s, ins / dst); registrar(dst, src)
    for molde, padrao in GLOBS:
        for s in sorted(prod.glob(padrao)):
            rel = molde.format(pasta=s.parent.name, nome=s.name)
            (ins / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(s, ins / rel); registrar(rel, s.relative_to(prod))
    # banco de takes: catálogo da biblioteca, só os campos de busca
    cat = prod / "biblioteca" / "catalogo.json"
    itens = []
    if cat.exists():
        d = ler_json(cat)
        itens = d.get("itens", d) if isinstance(d, dict) else d
    gravar_json(ins / "banco.snapshot.json", {"origem": "biblioteca/catalogo.json", "itens": [{k: i.get(k) for k in CAMPOS_BANCO} for i in itens]})
    registrar("banco.snapshot.json", "biblioteca/catalogo.json")
    # corpus: texto extraído + hash do original
    pasta = pathlib.Path(corpus).expanduser() if corpus else prod / "fontes" / "corpus"
    faltam = []
    (ins / "corpus").mkdir(exist_ok=True)
    corpus_orig = {}
    for dst, padrao in CORPUS:
        f = _achar_corpus(pasta, padrao)
        if not f:
            faltam.append(padrao); continue
        txt = _texto_pdf(f) if f.suffix.lower() == ".pdf" else _texto_docx(f)
        (ins / "corpus" / dst).write_text(txt, encoding="utf-8")
        registrar(f"corpus/{dst}", f)
        corpus_orig[dst] = {"arquivo": f.name, "sha256_original": sha256_arquivo(f)}
    if faltam:
        raise SystemExit(f"corpus incompleto em {pasta}: faltam {', '.join(faltam)}")
    limites = gerar_limites(ins)
    h = hash_conjunto(arquivos)
    manifesto = {"hash": h, "data": agora(), "producao_raiz": str(prod), "corpus_pasta": str(pasta),
                 "corpus_originais": corpus_orig, "arquivos": arquivos, "origem": origem,
                 "derivados": {"limites_producao.md": "gerado de fatos + estilos/*/licoes.md + playbook (fora do hash)"}}
    gravar_json(ins / "MANIFESTO.json", manifesto)
    gravar_json(ins / "historico" / f"{h}.json", {"hash": h, "data": manifesto["data"], "arquivos": arquivos})
    return f"insumos sincronizados · hash {h} · {len(arquivos)} arquivos · limites_producao.md ({limites} linhas)"


def gerar_limites(ins: pathlib.Path) -> int:
    f = ler_json(ins / "fatos.snapshot.json")
    v = lambda *ks: _valor(f, ks)
    L = ["# Limites de produção (GERADO por ./sala sincronizar; não edite)", "",
         "Fonte: fatos.snapshot.json, estilos/*/licoes.md, playbook_resumo.snapshot.md. Toda casca precisa caber aqui.", "",
         "## Vertex / Veo",
         f"- Modelos: teste {v('tecnica','modelo_teste')} · final rosto/mão {v('tecnica','modelo_final_rosto_mao')} · final lugar {v('tecnica','modelo_final_lugar')}.",
         f"- Duração de uso: {v('tecnica','duracao_trecho')}.",
         f"- Ritmo: {v('tecnica','ritmo_montagem')}.",
         f"- Regra de custo: {v('tecnica','regra_custo')}. Teto padrão US$ {v('tecnica','teto_padrao_conjunto')} (alerta {v('tecnica','alerta_teto')})."]
    L += [f"- Lição: {x}" for x in (v("tecnica", "licoes_veo") or [])]
    L += ["", "## Pessoas",
          f"- Adultos por IA: {v('pessoas','adultos_ia')}.",
          f"- Apresentador: {v('pessoas','apresentador')}.",
          f"- Crianças: {v('pessoas','criancas')}.",
          f"- Instituição: {v('pessoas','casa_nunca_ia')}.",
          f"- Voz: {v('pessoas','voz')}.",
          f"- Texto de prêmio: {v('pessoas','texto_premio_posicao')}.",
          "", "## Moeda",
          f"- {v('moeda','referencia')}.", f"- {v('moeda','frente')}.", f"- {v('moeda','legibilidade')}.",
          f"- {v('moeda','acoes_proibidas')}.", f"- Banco Central: {v('moeda','banco_central')}.",
          "", "## Estilo e texto",
          f"- Regra de ouro: {v('estilo','regra_de_ouro')}.",
          "- Texto, número, data, logo e rodapé nunca vêm do gerador (só o '50' da moeda): entram na montagem.",
          f"- Rótulo IA: {v('marca','rotulo_ia')}.", ""]
    for p in sorted((ins / "estilos").glob("*/licoes.md")):
        corpo = [l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
        if corpo:
            L += [f"## Lições · {p.parent.name}"] + corpo + [""]
    (ins / "limites_producao.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return len(L)


def _valor(f, ks):
    x = f
    for k in ks:
        x = x.get(k, {}) if isinstance(x, dict) else {}
    return x.get("valor") if isinstance(x, dict) and "valor" in x else (x or None)
