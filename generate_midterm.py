#!/usr/bin/env python3
"""Generate a six-chapter discrete mathematics practice midterm and answer key.

Run: python3 generate_midterm.py
Outputs: midterm_questions.pdf and midterm_answer_key.pdf
For an Overleaf upload: python3 generate_midterm.py --latex

The questions are original practice questions aligned with the topics in
Chapters 1–6 of Discrete Mathematics with Applications (5th ed.).
"""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


CHAPTERS = [
    {
        "title": "Speaking Mathematically",
        "questions": [
            r"Let $A=\{1,2,3\}$ and $B=\{a,b\}$. Define a relation $R$ from $A$ to $B$ by $xRy$ exactly when $x$ is odd. List $R$ as a set of ordered pairs. Is $R$ a function from $A$ to $B$? Explain.",
            r"Consider the undirected graph with vertex set $\{u,v,w,x\}$ and edge set $\{\{u,v\},\{u,w\},\{v,w\},\{w,x\}\}$. Find the degree of each vertex and the total degree. Is the graph connected?",
        ],
        "answers": [
            r"The odd elements of $A$ are 1 and 3, and each is related to both elements of $B$. Thus $R=\{(1,a),(1,b),(3,a),(3,b)\}$. It is not a function from $A$ to $B$: 1 and 3 each have two outputs, while 2 has no output.",
            r"The degrees are $\deg(u)=2$, $\deg(v)=2$, $\deg(w)=3$, and $\deg(x)=1$. The total degree is $2+2+3+1=8$, which also equals twice the four edges. The graph is connected: every vertex can be reached from every other by a path (in particular, $x$ connects through $w$).",
        ],
    },
    {
        "title": "The Logic of Compound Statements",
        "questions": [
            r"Let $p$ mean “the server is online” and $q$ mean “the database responds.” Write $\neg(p\land q)$ in an equivalent form using $\lor$ and negations only. State when this compound statement is true.",
            r"Determine whether this argument is valid. Identify the rule of inference if it is valid: If the alarm is set, the light blinks. The light does not blink. Therefore, the alarm is not set.",
        ],
        "answers": [
            r"By De Morgan's law, $\neg(p\land q)\equiv(\neg p\lor\neg q)$. It is true whenever at least one of the two statements is false: the server is offline or the database does not respond (or both).",
            r"The argument is valid by modus tollens. In symbolic form, $p\to q$ and $\neg q$ imply $\neg p$.",
        ],
    },
    {
        "title": "The Logic of Quantified Statements",
        "questions": [
            r"Over the integers, write “Every even integer has an integer whose double is that integer” using quantifiers. Then negate your quantified statement and simplify the negation.",
            r"Over the real numbers, negate $\forall x\,\exists y\,(y>x\land y^2=x^2+1)$. Do not leave a negation symbol in front of a quantified statement or parenthesized condition.",
        ],
        "answers": [
            r"One translation is $\forall n\in\mathbb Z\,(\text{$n$ is even}\to\exists k\in\mathbb Z\,(2k=n))$. Its negation is $\exists n\in\mathbb Z\,(\text{$n$ is even}\land\forall k\in\mathbb Z\,(2k\ne n))$. The negation says that some even integer is not twice any integer.",
            r"Switch each quantifier and negate the condition: $\exists x\in\mathbb R\,\forall y\in\mathbb R\,(y\le x\lor y^2\ne x^2+1)$.",
        ],
    },
    {
        "title": "Elementary Number Theory and Methods of Proof",
        "questions": [
            r"Prove directly: for every integer $n$, if $n$ is odd, then $n^2$ is odd.",
            r"Use a proof by contradiction to show that $\sqrt{3}$ is irrational. You may use the fact that if 3 divides $a^2$, then 3 divides $a$.",
        ],
        "answers": [
            r"Let $n$ be an odd integer. Then $n=2k+1$ for some integer $k$. Hence $n^2=(2k+1)^2=2(2k^2+2k)+1$. Since $2k^2+2k$ is an integer, $n^2$ has the form $2m+1$ and is odd.",
            r"Assume for contradiction that $\sqrt3=a/b$ for relatively prime positive integers $a,b$. Then $a^2=3b^2$, so 3 divides $a^2$ and therefore 3 divides $a$. Write $a=3c$. Substitution gives $9c^2=3b^2$, hence $b^2=3c^2$, so 3 divides $b$ as well. This contradicts that $a$ and $b$ are relatively prime. Thus $\sqrt3$ is irrational.",
        ],
    },
    {
        "title": "Sequences, Mathematical Induction, and Recursion",
        "questions": [
            r"A sequence is defined recursively by $a_1=2$ and $a_n=3a_{n-1}+1$ for $n\ge2$. Find $a_2,a_3,a_4$.",
            r"Use mathematical induction to prove that $1+3+5+\cdots+(2n-1)=n^2$ for every positive integer $n$.",
        ],
        "answers": [
            r"Apply the recurrence: $a_2=3(2)+1=7$, $a_3=3(7)+1=22$, and $a_4=3(22)+1=67$.",
            r"Base case: for $n=1$, the left side is 1 and $1^2=1$. Inductive step: assume $1+3+\cdots+(2k-1)=k^2$. Then $1+3+\cdots+(2k-1)+(2(k+1)-1)=k^2+(2k+1)=(k+1)^2$. Thus the formula holds for $k+1$. By induction, it holds for every positive integer $n$.",
        ],
    },
    {
        "title": "Set Theory",
        "questions": [
            r"Let $U=\{1,2,3,4,5,6\}$, $A=\{1,2,3,4\}$, and $B=\{3,4,5\}$. Find $A\cup B$, $A\cap B$, and $A^c$ (with complement taken relative to $U$).",
            r"Prove the set identity $A\cap(B\cup C)=(A\cap B)\cup(A\cap C)$ using the element method.",
        ],
        "answers": [
            r"$A\cup B=\{1,2,3,4,5\}$, $A\cap B=\{3,4\}$, and $A^c=U\setminus A=\{5,6\}$.",
            r"Let $x$ be arbitrary. Then $x\in A\cap(B\cup C)$ iff $x\in A$ and ($x\in B$ or $x\in C$). By distributivity of “and” over “or,” this is equivalent to $(x\in A\land x\in B)\lor(x\in A\land x\in C)$, which holds iff $x\in(A\cap B)\cup(A\cap C)$. Since this equivalence holds for every $x$, the sets are equal.",
        ],
    },
]


def document(title: str, answer_key: bool) -> str:
    parts = [
        r"\documentclass[12pt]{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage[T1]{fontenc}",
        r"\title{" + title + r"}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
    ]
    if not answer_key:
        parts.extend([r"Name: \rule{2.5in}{0.4pt}\hfill Date: \rule{1.2in}{0.4pt}", r"\vspace{1em}"])
        parts.append(r"\noindent Two questions are provided for each chapter. Show your reasoning.")

    for number, chapter in enumerate(CHAPTERS, start=1):
        parts.append(r"\section*{Chapter " + str(number) + ": " + chapter["title"] + "}")
        parts.append(r"\begin{enumerate}")
        field = "answers" if answer_key else "questions"
        for item in chapter[field]:
            parts.append(r"\item " + item)
        parts.append(r"\end{enumerate}")
    parts.append(r"\end{document}")
    return "\n\n".join(parts) + "\n"


def make_latex_zip() -> None:
    with ZipFile("overleaf_midterm.zip", "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            "midterm_questions.tex",
            document("Discrete Mathematics Midterm Practice: Chapters 1--6", False),
        )
        archive.writestr(
            "midterm_answer_key.tex",
            document("Answer Key: Discrete Mathematics Midterm Practice", True),
        )
    print("Wrote overleaf_midterm.zip with the questions and answer key")


def make_pdfs() -> None:
    compiler = shutil.which("pdflatex")
    if compiler is None:
        raise SystemExit(
            "Could not find pdflatex. Install a LaTeX distribution (such as TeX Live or MiKTeX), "
            "or run this program with --latex to create an Overleaf ZIP instead."
        )

    documents = [
        ("midterm_questions", "Discrete Mathematics Midterm Practice: Chapters 1--6", False),
        ("midterm_answer_key", "Answer Key: Discrete Mathematics Midterm Practice", True),
    ]
    with tempfile.TemporaryDirectory(prefix="midterm_latex_") as temp_dir:
        source_dir = Path(temp_dir)
        for filename, title, is_answer_key in documents:
            tex_path = source_dir / f"{filename}.tex"
            tex_path.write_text(document(title, is_answer_key), encoding="utf-8")
            result = subprocess.run(
                [
                    compiler,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-output-directory={Path.cwd()}",
                    str(tex_path),
                ],
                cwd=source_dir,
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                details = result.stdout + result.stderr
                raise SystemExit(
                    f"pdflatex could not build {tex_path.name}. Compiler output:\n{details}"
                )
    print("Wrote midterm_questions.pdf and midterm_answer_key.pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a discrete mathematics practice midterm.")
    parser.add_argument(
        "--latex",
        action="store_true",
        help="create an Overleaf ZIP containing the LaTeX source instead of PDFs",
    )
    args = parser.parse_args()
    if args.latex:
        make_latex_zip()
    else:
        make_pdfs()


if __name__ == "__main__":
    main()
