##
# Formal Containment: communications
#
# @file
# @version 0.1

# Default target
all: odyssey lesswrong trajectory_labs

# Compile typst document in whitepaper directory
odyssey: odyssey/main.pdf

odyssey/main.pdf: odyssey/main.typ odyssey/refs.bib
	pushd ./odyssey && typst compile main.typ main.pdf && popd

# Convert org file to docx in lesswrong directory
lesswrong: lesswrong/post.docx

lesswrong/post.docx: lesswrong/post.org
	pushd ./lesswrong && pandoc post.org -o post.docx && popd

trajectory_labs: trajectory_labs/template.pdf

trajectory_labs/template.pdf: trajectory_labs/template.typ
	pushd ./trajectory_labs && typst compile template.typ template.pdf && popd

# Clean generated files
clean:
	rm -f odyssey/main.pdf lesswrong/post.docx trajectory_labs/template.pdf

# Phony targets
.PHONY: all odyssey lesswrong trajectory_labs clean

# end
