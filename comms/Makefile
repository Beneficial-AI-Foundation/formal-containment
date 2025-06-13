##
# Formal Containment: communications
#
# @file
# @version 0.1

# Default target
all: whitepaper lesswrong toronto-talk

# Compile typst document in whitepaper directory
whitepaper: whitepaper/main.pdf

whitepaper/main.pdf: whitepaper/main.typ whitepaper/refs.bib
	pushd ./whitepaper && typst compile main.typ main.pdf && popd

# Convert org file to docx in lesswrong directory
lesswrong: lesswrong/post.docx

lesswrong/post.docx: lesswrong/post.org
	pushd ./lesswrong && pandoc post.org -o post.docx && popd

toronto-talk: talks/toronto/template.pdf

talks/toronto/template.pdf: talks/toronto/template.typ
	pushd ./talks/toronto && typst compile template.typ template.pdf && popd

# Clean generated files
clean:
	rm -f whitepaper/main.pdf lesswrong/post.docx talks/toronto/template.pdf

# Phony targets
.PHONY: all whitepaper lesswrong clean

# end
