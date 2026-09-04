# Compila los decks Beamer del curso.  Uso:  make   |   make clean
TEX := $(wildcard 0?_*.tex)
PDF := $(TEX:.tex=.pdf)

all: $(PDF)

%.pdf: %.tex preambulo.tex
	pdflatex -interaction=nonstopmode -halt-on-error $<
	pdflatex -interaction=nonstopmode -halt-on-error $<
	@rm -f $*.aux $*.log $*.nav $*.snm $*.toc $*.out $*.vrb

clean:
	rm -f *.aux *.log *.nav *.snm *.toc *.out *.vrb

cleanall: clean
	rm -f $(PDF)

.PHONY: all clean cleanall
