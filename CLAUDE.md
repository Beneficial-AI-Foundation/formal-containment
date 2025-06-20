# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python (fcp/ directory)
```bash
cd fcp
uv sync                                    # Install dependencies
uv run contain protocol "x > 0" "x > 6"   # Run containment protocol with precondition/postcondition
uv run contain experiments                 # Run full experimental evaluation
uv run ruff check src                      # Lint code
uv run ruff format src                     # Format code  
uv run pyright src                         # Type check
uv run pytest                             # Run tests
uv run pytest --ignore src/tests/networked/*.py  # Run tests (excluding networked)
```

### Lean 4 (imp/ directory)
```bash
cd imp
lake build    # Build Lean code
```

### Experiments
```bash
cd experiments
./main.sh     # Run full experiment suite with multiple AI models
./test.sh     # Run test experiments
```

### Documentation
```bash
cd comms/odyssey
typst compile main.typ    # Compile academic paper
cd ../trajectory_labs  
typst compile template.typ # Compile presentation
```

## Architecture Overview

This is a **Formal Containment Protocol** research project combining Lean 4 formal verification with Python LLM integration for AI safety.

### Core Components

**imp/** - Lean 4 implementation of minimal imperative language ("Imp") with Hoare logic
- Based on David Christiansen's tutorial with added Hoare logic support
- Provides formal verification capabilities for generated code
- Uses Lake build system (lakefile.toml, lean-toolchain pinned to v4.20.1)

**fcp/** - Python package implementing the containment protocol
- CLI interface via `contain` command with typer
- LLM integration via litellm (supports Claude, GPT-4, O3, Grok models)
- MCP (Model Context Protocol) server for external tool integration
- Uses Pantograph for Lean-Python bridge communication
- uv for package management (pyproject.toml, uv.lock)

**experiments/** - Experimental framework and data
- Configuration in data.toml (samples, model definitions)
- Automated experiment runners (main.sh, test.sh) 
- Results logging and analysis infrastructure

### Key Protocols

1. **Containment Workflow**: User provides precondition/postcondition → LLM generates Imp code → System attempts formal proof → Only verified code allowed
2. **Model Configuration**: experiments/data.toml defines available AI models with human_name/provider/model_pin
3. **Proof System**: Hoare logic triples {P} C {Q} where P=precondition, C=generated code, Q=postcondition

### Environment Setup

Requires `.env` file with:
- `ANTHROPIC_API_KEY` - For Claude models  
- `OPENAI_API_KEY` - For OpenAI models
- `LOGFIRE_TOKEN` - Optional telemetry (logfire.pydantic.dev project: formal-containment)

Use Nix flake (`nix develop`) or install manually: uv, elan, typst, nodejs, pantograph

### Project Structure Context

- **comms/** - Academic communications (LessWrong posts, Odyssey conference submission, presentations)
- **txt/** - LLM prompt templates for system/user interactions
- Hybrid academic/research codebase targeting AI alignment through formal verification
- CI pipeline runs Lean builds, Python checks, and Typst compilation in parallel

### Testing and Linting

Always run before committing:
```bash
cd fcp && uv run ruff check src && uv run ruff format src && uv run pyright src && uv run pytest
cd imp && lake build
```