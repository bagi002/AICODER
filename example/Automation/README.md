# Automation & Documentation Workflow

This guide explains how to manage documentation and generate the HTML docs.

## Before any request to the AI agent
- Read `AGENTS.md` (mandatory).
- Write/update high-level requirements in `Docs/requirements/high_level_requirements.yaml` (human-authored) *before* asking the AI to draft software requirements/architecture/code.

## After `git clone`
Rebuild both virtualenvs (root `venv/` and `Automation/docs_venv/`, both are gitignored):
```bash
cd Automation
./bootstrap_envs.sh
```
Then activate what you need:
- `source ../venv/bin/activate` for coding
- `source docs_venv/bin/activate` for `docs_builder.py`

## When you only have High-Level requirements
- Add them to `Docs/requirements/high_level_requirements.yaml` (human authored).
- For each high-level requirement, add software requirements in `Docs/requirements/software_requirements.yaml` with a mandatory `refines` pointing to the high-level ID.
- A software requirement without `refines` is invalid and must be fixed before implementation.

## Writing and updating docs
1. Update YAML files in `Docs/requirements/`.
2. Update PUML diagrams in `Docs/architecture/` (`runtime_diagram.puml`, `class_diagram.puml`, `block_diagram.puml`).
3. Generate the HTML site:
   ```bash
   cd Automation
   source docs_venv/bin/activate  # optional if you want to use the venv
   python3 docs_builder.py
   ```
4. Open `Docs/build/index.html` in your browser.

## What's in Docs/
- `requirements/` – high-level and software requirements (YAML).
- `architecture/` – PlantUML diagrams (runtime, class, block).
- `build/` – generated HTML (created by `docs_builder.py`).

## Rules while the agent writes code
- Before coding: write or update software requirements (with `refines`) and set status per AGENTS.md.
- After changes: refresh PUML diagrams and rerun `docs_builder.py`.
- If a software requirement lacks a valid `refines`, stop and fix it before implementing code.
