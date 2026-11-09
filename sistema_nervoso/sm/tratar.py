"""sm tratar-celular: pós-processamento determinístico que faz o take parecer vídeo de celular de espectador.
Tremor sintético (senos de baixa frequência + rotação leve, recorte 3%), curva de celular (saturação à meta, pretos levantados,
realces estourando acima do joelho), nitidez leve com halo, grão só na luminância (mais nas sombras), ciclo de compressão a 4–6 Mbps,
depois master CRF 16. Nunca remove marca d'água nem assinatura invisível. Parâmetros em estilos/<estilo>/pos.json."""
import json, math, pathlib, subprocess
import numpy as np
from .raiz import raiz, ler_json
from .midia import sh, probe


def params(estilo="realismo-celular"):
    return ler_json(raiz() / "estilos" / estilo / "pos.json")


def _frames(arquivo, n=8, largura=270):
    """n quadros como arrays RGB uint8 (amostragem uniforme)."""
    from PIL import Image
    d = probe(arquivo)["duracao"]; out = []
    tmp = raiz() / "painel" / "_cache"; tmp.mkdir(exist_ok=True)
    for i in range(n):
        t = max(0.0, min(d - 0.05, d * (i + 0.5) / n))
        p = tmp / f"_m_{abs(hash(str(arquivo)))}_{i}.png"
        sh("ffmpeg", "-y", "-v", "error", "-ss", t, "-i", arquivo, "-frames:v", "1", "-vf", f"scale={largura}:-2", p)
        out.append(np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) / 255.0); p.unlink(missing_ok=True)
    return out


def metricas(arquivo, n=8) -> dict:
    """saturação média (HSV), % de realces estourados (luma>0.97), alta frequência (var. do laplaciano da luma), tremor (deslocamento médio entre quadros consecutivos, px a 270 de largura)."""
    fr = _frames(arquivo, n)
    sats, est, hf, desl = [], [], [], []
    prev = None
    for im in fr:
        mx, mn = im.max(axis=2), im.min(axis=2)
        s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
        sats.append(float(s.mean()))
        y = 0.299 * im[..., 0] + 0.587 * im[..., 1] + 0.114 * im[..., 2]
        est.append(float((y > 0.97).mean() * 100))
        lap = -4 * y[1:-1, 1:-1] + y[:-2, 1:-1] + y[2:, 1:-1] + y[1:-1, :-2] + y[1:-1, 2:]
        hf.append(float(lap.var() * 1e3))
    desl = _tremor(arquivo)
    return {"saturacao": round(float(np.mean(sats)), 3), "realces_pct": round(float(np.mean(est)), 2),
            "alta_freq": round(float(np.mean(hf)), 3), "tremor_px": round(float(np.mean(desl)) if desl else 0.0, 2)}


def _tremor(arquivo, pontos=4, largura=540, salto=6):
    """deslocamento entre os quadros n e n+salto (0,25 s a 24 fps) em alguns instantes, a 540 px de largura: tremor de câmera acumulado, não corte de cena (ignora pares com deslocamento > 15% da largura)."""
    from PIL import Image
    d = probe(arquivo)["duracao"]; tmp = raiz() / "painel" / "_cache"; tmp.mkdir(exist_ok=True); out = []
    for i in range(pontos):
        t = max(0.0, min(d - 0.2, d * (i + 0.5) / pontos))
        base = tmp / f"_tr_{abs(hash(str(arquivo)))}_{i}_%02d.png"
        sh("ffmpeg", "-y", "-v", "error", "-ss", t, "-i", arquivo, "-frames:v", str(salto + 1), "-vf", f"scale={largura}:-2", str(base))
        fr = []
        for k in (1, salto + 1):
            q = pathlib.Path(str(base) % k)
            if q.exists(): fr.append(np.asarray(Image.open(q).convert("L"), dtype=np.float32) / 255.0)
        for k in range(1, salto + 2): pathlib.Path(str(base) % k).unlink(missing_ok=True)
        if len(fr) == 2:
            v = _deslocamento(fr[0], fr[1])
            if v <= 0.15 * largura: out.append(v)
    return out


def _deslocamento(a, b):
    """correlação de fase entre dois quadros de luma → módulo do deslocamento (px na escala amostrada)."""
    A, B = np.fft.fft2(a - a.mean()), np.fft.fft2(b - b.mean())
    R = A * np.conj(B); R /= np.maximum(np.abs(R), 1e-9)
    r = np.fft.ifft2(R).real
    idx = np.unravel_index(np.argmax(r), r.shape)
    dy = idx[0] if idx[0] <= a.shape[0] // 2 else idx[0] - a.shape[0]
    dx = idx[1] if idx[1] <= a.shape[1] // 2 else idx[1] - a.shape[1]
    return float(math.hypot(dx, dy))


def _expr_tremor(amp, fq, pesos, fases, eixo):
    """expressão ffmpeg em t: soma de senos (determinística)."""
    termos = [f"{amp*w:.3f}*sin(2*PI*{f}*t+{ph + (0.9 if eixo == 'y' else 0)})" for f, w, ph in zip(fq, pesos, fases)]
    return "+".join(termos)


def tratar(entrada, saida=None, intensidade="leve", estilo="realismo-celular") -> str:
    entrada = pathlib.Path(entrada)
    P = params(estilo); I = P["intensidade"][intensidade]
    pr = probe(entrada); W, H = pr["largura"], pr["altura"]
    esc = W / P["largura_ref"]
    amp = I["tremor_px"] * esc; rot = I["rotacao_graus"] * math.pi / 180
    fq, pw, ph = P["tremor"]["frequencias_hz"], P["tremor"]["pesos"], P["tremor"]["fases"]
    ex, ey = _expr_tremor(amp, fq, pw, ph, "x"), _expr_tremor(amp, fq, pw, ph, "y")
    rec = P["recorte_borda"]; Wc, Hc = int(W * (1 + 2 * rec)) // 2 * 2, int(H * (1 + 2 * rec)) // 2 * 2
    # saturação: mede a de entrada e escala para a meta
    s0 = metricas(entrada, 6)["saturacao"]; alvo = I["saturacao_alvo"]
    fator = max(0.05, min(1.5, alvo / max(s0, 1e-3)))
    pm = P["curva"]["preto_minimo"]; jo = P["curva"]["joelho_realce"]
    curva = f"curves=all='0/{pm:.3f} 0.25/{0.25*(1-pm)+pm:.3f} 0.75/0.78 {jo}/1 1/1'"
    grao = max(1, int(round(I["grao_pct"] * 2.4)))  # noise c0s ~ 0–100; 1,5–2,5% ≈ 4–6
    vf = (f"scale={Wc}:{Hc}:flags=lanczos,"
          f"rotate='{rot:.5f}*sin(2*PI*{fq[0]}*t+0.4)':c=black@0:ow={Wc}:oh={Hc},"
          f"crop={W}:{H}:x='({Wc}-{W})/2+({ex})':y='({Hc}-{H})/2+({ey})',"
          f"eq=saturation={fator:.3f}:contrast=1.06,"
          f"{curva},"
          f"unsharp=5:5:{I['unsharp']:.2f}:5:5:0.0,"
          f"noise=c0s={grao}:c0f=t+u:c1s=0:c2s=0,"
          "format=yuv420p")
    saida = pathlib.Path(saida) if saida else entrada.with_name(entrada.stem + "_celular.mp4")
    inter = saida.with_name(saida.stem + "_tmp_celular.mp4")
    mbps = I["mbps"]
    lo, hi = P["meta_saturacao"]
    for _ in range(3):  # ciclo de compressão + correção da saturação até a meta (a curva e o eq interagem)
        vf_i = vf.replace(f"eq=saturation={fator:.3f}", f"eq=saturation={fator:.3f}") if False else vf
        vf_i = vf_i.replace("eq=saturation=", "eq=saturation=").replace(vf_i.split("eq=saturation=")[1].split(":")[0], f"{fator:.3f}", 1)
        sh("ffmpeg", "-y", "-v", "error", "-i", entrada, "-an", "-vf", vf_i, "-r", str(int(round(pr["fps"]))), "-c:v", "libx264", "-profile:v", "main",
           "-b:v", f"{mbps}M", "-maxrate", f"{mbps+1}M", "-bufsize", f"{2*mbps}M", "-pix_fmt", "yuv420p", inter)
        s1 = metricas(inter, 6)["saturacao"]
        if lo <= s1 <= hi or s1 < 1e-3: break
        fator = max(0.05, min(1.5, fator * alvo / s1))
    sh("ffmpeg", "-y", "-v", "error", "-i", inter, "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", str(int(round(pr["fps"]))), "-movflags", "+faststart", saida)
    inter.unlink(missing_ok=True)
    m = metricas(saida, 6)
    return f"OK: {saida} · saturação {s0:.3f}→{m['saturacao']:.3f} (meta {P['meta_saturacao']}) · realces {m['realces_pct']}% · tremor {m['tremor_px']} px · {intensidade}"


def comparar(arquivos: list, referencia=None, saida=None, rotulos=None) -> str:
    """folha: um quadro (meio) de cada arquivo lado a lado, mais um quadro da referência; devolve o caminho e a tabela de métricas."""
    from PIL import Image, ImageDraw
    itens = list(arquivos) + ([referencia] if referencia else [])
    rot = list(rotulos or [pathlib.Path(a).stem for a in arquivos]) + (["referência"] if referencia else [])
    paineis, linhas = [], []
    for a, r in zip(itens, rot):
        fr = _frames(a, 3, 360)[1]
        im = Image.fromarray((fr * 255).astype(np.uint8)); paineis.append(im)
        m = metricas(a, 6); linhas.append(f"| {r} | {m['saturacao']:.3f} | {m['realces_pct']:.1f}% | {m['alta_freq']:.2f} | {m['tremor_px']:.2f} |")
    w = max(p.width for p in paineis); h = max(p.height for p in paineis)
    folha = Image.new("RGB", (w * len(paineis), h + 22), (15, 15, 20)); d = ImageDraw.Draw(folha)
    for i, (p, r) in enumerate(zip(paineis, rot)):
        folha.paste(p, (i * w, 22)); d.text((i * w + 4, 4), r, fill=(255, 206, 0))
    saida = pathlib.Path(saida) if saida else raiz() / "criativos" / "_comparacoes" / "tratar_celular.jpg"
    saida.parent.mkdir(parents=True, exist_ok=True); folha.save(saida, quality=88)
    tabela = "| clipe | saturação | realces >0,97 | alta freq. | tremor px |\n|---|---|---|---|---|\n" + "\n".join(linhas)
    return f"{saida}\n{tabela}"
