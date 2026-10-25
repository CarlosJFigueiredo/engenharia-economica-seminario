"""Compila o artigo do seminário (artigo/main.tex) para build/artigo.pdf.

Uso, a partir da raiz do repositório:

    python build.py            # compila (pdflatex -> bibtex -> pdflatex x2)
    python build.py --clean    # apaga build/ antes de compilar

Usa a biblioteca pytinytex (TinyTeX). Pacotes LaTeX ausentes são instalados
automaticamente pelo tlmgr na primeira compilação.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytinytex

RAIZ = Path(__file__).resolve().parent
FONTE = RAIZ / "artigo"
SAIDA = RAIZ / "build"
DOCUMENTO = "main"

# Pacotes que o auto-instalador do pytinytex não detecta sozinho (classe, .bst, idioma).
PACOTES = ["memoir", "abntex2", "babel-portuges", "hyphen-portuguese"]


def reconstruir_formato() -> None:
    """Recria o pdflatex.fmt para que a hifenização em português entre no formato."""
    fmtutil = Path(pytinytex.get_tinytex_path()) / "fmtutil-sys.exe"
    subprocess.run([str(fmtutil), "--byfmt", "pdflatex"], check=True, capture_output=True)


def garantir_pacotes() -> None:
    instalados = {p["name"] for p in pytinytex.list_installed() if p["installed"]}
    novos = [p for p in PACOTES if p not in instalados]
    for pacote in novos:
        print(f"Instalando pacote LaTeX: {pacote}")
        pytinytex.install(pacote)
    if "hyphen-portuguese" in novos:
        reconstruir_formato()


def compilar(passes: int) -> pytinytex.CompileResult:
    return pytinytex.compile(
        FONTE / f"{DOCUMENTO}.tex",
        output_dir=str(SAIDA),
        num_runs=passes,
        auto_install=True,
        max_install_attempts=15,
    )


def rodar_bibtex() -> None:
    bibtex = Path(pytinytex.get_tinytex_path()) / "bibtex.exe"
    if not bibtex.exists():
        bibtex = bibtex.with_suffix("")
    env = {**os.environ, "BIBINPUTS": f"{FONTE}{os.pathsep}"}
    proc = subprocess.run(
        [str(bibtex), DOCUMENTO], cwd=SAIDA, env=env, capture_output=True, text=True
    )
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr, sep="\n")
        sys.exit("bibtex falhou (veja build/main.blg).")


def relatar(resultado: pytinytex.CompileResult) -> None:
    for erro in resultado.errors:
        local = f"{erro.file}:{erro.line}" if erro.file else "log"
        print(f"ERRO [{local}] {erro.message}")
    if not resultado.success:
        sys.exit(f"Compilação falhou. Log completo em {resultado.log_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--clean", action="store_true", help="apaga build/ antes")
    args = parser.parse_args()

    if args.clean and SAIDA.exists():
        shutil.rmtree(SAIDA)
    SAIDA.mkdir(exist_ok=True)

    garantir_pacotes()
    os.chdir(FONTE)  # \input e figuras são relativos a artigo/

    relatar(compilar(passes=1))
    rodar_bibtex()
    relatar(compilar(passes=2))

    pdf = SAIDA / f"{DOCUMENTO}.pdf"
    destino = SAIDA / "artigo.pdf"
    shutil.copyfile(pdf, destino)
    print(f"PDF gerado: {destino}")


if __name__ == "__main__":
    main()
