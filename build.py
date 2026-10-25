"""Compila o artigo do seminário (artigo/main.tex) para build/artigo.pdf.

Funciona em Windows, Linux (inclusive WSL) e macOS.

Uso, a partir da raiz do repositório:

    python build.py            # compila (pdflatex -> bibtex -> pdflatex x2)
    python build.py --clean    # apaga build/ antes de compilar

Usa a biblioteca pytinytex (TinyTeX). Se o TinyTeX ainda não estiver instalado,
o script tenta baixá-lo (uma única vez). Pacotes LaTeX ausentes são instalados
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
PACOTES = ["memoir", "abntex2", "babel-portuges", "hyphen-portuguese", "rsfs"]

# Sufixo dos executáveis do TinyTeX: ".exe" só no Windows.
EXE = ".exe" if os.name == "nt" else ""


def garantir_tinytex() -> None:
    """Confirma que o TinyTeX existe; se não, baixa (Linux e macOS) ou orienta (Windows)."""
    try:
        pytinytex.get_tinytex_path()
        return
    except Exception:
        pass

    print("TinyTeX não encontrado; baixando (só na primeira vez)...")
    try:
        pytinytex.download_tinytex()
    except Exception as erro:
        if os.name == "nt":
            sys.exit(
                f"Não foi possível baixar o TinyTeX automaticamente ({erro}).\n"
                "No Windows, siga a seção 'TinyTeX no Windows' do README."
            )
        sys.exit(
            f"Não foi possível baixar o TinyTeX automaticamente ({erro}).\n"
            "Verifique a conexão e tente de novo."
        )


def ferramenta(nome: str) -> Path:
    """Caminho de um executável do TinyTeX (bibtex, fmtutil-sys...) em qualquer sistema."""
    pasta_bin = Path(pytinytex.get_tinytex_path())
    for candidato in (nome + EXE, nome):
        caminho = pasta_bin / candidato
        if caminho.exists():
            return caminho
    sys.exit(f"Executável '{nome}' não encontrado em {pasta_bin}.")


def reconstruir_formato() -> None:
    """Recria o pdflatex.fmt para que a hifenização em português entre no formato."""
    fmtutil = ferramenta("fmtutil-sys")
    proc = subprocess.run(
        [str(fmtutil), "--byfmt", "pdflatex"], capture_output=True, text=True
    )
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr, sep="\n")
        sys.exit("Falha ao reconstruir o formato do pdflatex (fmtutil-sys).")


def garantir_pacotes() -> None:
    # O pytinytex resolve o symlink do tlmgr; no Linux/macOS o tlmgr.pl então procura o
    # kpsewhich ao lado de si para descobrir a raiz do TeX Live. Um symlink resolve.
    raiz = Path(pytinytex.get_tinytex_path())
    atalho = raiz.parents[1] / "texmf-dist" / "scripts" / "texlive" / "kpsewhich"
    if os.name != "nt" and not atalho.exists():
        atalho.symlink_to(raiz / "kpsewhich")
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
    bibtex = ferramenta("bibtex")
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

    garantir_tinytex()
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
