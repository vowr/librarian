cmake_minimum_required(VERSION 2.8.4)

project(LIBRARIAN NONE)

include(./UseLATEX.cmake)

set(PDFLATEX_COMPILER lualatex)

add_latex_document(document.tex)
