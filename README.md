# engenharia-economica-seminario

Seminário 2/2026 de Engenharia Econômica para Software (PUC Minas, Prof. Michelle Hanne Soares de Andrade).
**Tema 1:** estimativa baseada em histórias de usuário.

## Estrutura

```
artigo/
├── main.tex                    # preâmbulo (classe abntex2) e ordem das seções
├── referencias.bib             # referências (dados conferidos no Crossref)
├── secoes/
│   ├── 00-capa.tex             # capa e lista de integrantes
│   ├── 01-introducao.tex
│   ├── 02-marco-teorico.tex
│   ├── 03-exemplos-aplicacoes.tex
│   └── 04-conclusao.tex
└── figuras/                    # imagens (logo-pucminas.png, do site pucminas.br, 146x120 px)
build.py                        # compila o artigo com pytinytex
```

O sumário e a lista de referências são gerados automaticamente. Para citar,
use `\cite{chave}` (entre parênteses) ou `\citeonline{chave}` (no texto) com a
chave de `referencias.bib`.

## Como compilar

Linux, WSL e macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build.py
```

Windows (PowerShell ou cmd):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python build.py
```

O PDF sai em `build/artigo.pdf`. Use `python build.py --clean` para recompilar do zero.

Na primeira execução, o `build.py` baixa o TinyTeX para `~/.pytinytex` (cerca de 100 MB; em
Linux e macOS isso é automático) e instala os pacotes LaTeX que faltam. O `tlmgr` do TinyTeX
precisa de `perl`, que já vem no Ubuntu/WSL e no macOS. Nada é instalado no sistema.

### TinyTeX no Windows

O `pytinytex` 0.5.1 baixa o TinyTeX procurando um `.zip`, mas as releases atuais do Windows
são um `.exe` autoextraível (7z), então `pytinytex.download_tinytex()` falha. Alternativa
usada aqui, sem executar o `.exe`: baixar `TinyTeX-1-windows-<versão>.exe` em
<https://github.com/rstudio/tinytex-releases/releases>, extrair o payload 7z com `py7zr` e
copiar a pasta `TinyTeX` para `~/.pytinytex`. Os pacotes LaTeX restantes (abntex2, memoir,
hifenização em português etc.) são instalados pelo próprio `build.py` na primeira execução.
