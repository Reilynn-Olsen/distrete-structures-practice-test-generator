# Discrete Mathematics Midterm Practice Generator

This program creates a practice set with two questions for each of Chapters 1–6, along with a separate answer key. The questions are original practice questions based on the topics in *Discrete Mathematics with Applications* (5th edition). They are included in the Python script, so the textbook PDF is not needed to run or share the program.

## Requirements

- Python 3
- For PDF output: `pdflatex` from a LaTeX distribution
- For an Overleaf ZIP: no LaTeX installation is needed

On Arch Linux, install the LaTeX compiler with:

```bash
sudo pacman -Syu texlive-latex
```

Other operating systems can use TeX Live or MiKTeX. If you only need the Overleaf ZIP, install Python 3 and skip the LaTeX setup.

## Generate PDFs

Open a terminal in the folder containing `generate_midterm.py` and run:

```bash
python3 generate_midterm.py
```

This creates:

- `midterm_questions.pdf`
- `midterm_answer_key.pdf`

## Create an Overleaf upload

Run:

```bash
python3 generate_midterm.py --latex
```

This creates `overleaf_midterm.zip`. In Overleaf, choose **New Project → Upload Project** and upload that ZIP. The project includes both `.tex` documents. Set `midterm_questions.tex` or `midterm_answer_key.tex` as the main document to compile the one you want.

## Share the program

Share `generate_midterm.py` and this README. The textbook PDF is not required. PDF generation requires `pdflatex`; the `--latex` option only requires Python 3.
