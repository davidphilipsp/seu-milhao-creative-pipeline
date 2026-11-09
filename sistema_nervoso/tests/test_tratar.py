import pathlib, subprocess, pytest
from sm.raiz import raiz
from sm.tratar import tratar, metricas, params
from sm.midia import probe


@pytest.fixture(scope="module")
def clipe(tmp_path_factory):
    """clipe sintético saturado 1080×1920 24 fps 3 s (gradiente colorido + ruído), sem áudio."""
    p = tmp_path_factory.mktemp("tratar") / "sintetico.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=24:d=3", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", str(p)], check=True)
    return p


def test_tratar_mantem_dimensao_fps_sem_audio_e_satura_na_meta(clipe):
    out = clipe.with_name("tratado.mp4")
    msg = tratar(clipe, out, "media")
    assert out.exists() and "OK" in msg
    a, b = probe(clipe), probe(out)
    assert (a["largura"], a["altura"]) == (b["largura"], b["altura"])
    assert abs(a["fps"] - b["fps"]) < 0.01
    assert not b["audio"]
    lo, hi = params()["meta_saturacao"]
    s = metricas(out, 6)["saturacao"]
    assert lo - 0.03 <= s <= hi + 0.03, f"saturação {s} fora da meta {lo}-{hi}"


def test_metricas_detectam_tremor(clipe):
    out = clipe.with_name("tratado2.mp4"); tratar(clipe, out, "media")
    assert metricas(out, 6)["tremor_px"] >= metricas(clipe, 6)["tremor_px"]
