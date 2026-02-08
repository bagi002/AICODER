# Automation & Documentation Workflow

This guide describes how to maintain documentation and generate the HTML overview.

## Before every request to the AI agent
- Read `AGENTS.md` (mandatory).
- First write or update high-level requirements in `Docs/requirements/high_level_requirements.yaml` (written by a human), then send a request to the AI agent to write software requirements/architecture/code.

## After `git clone`
Run the script that recreates both venv environments (root `venv/` and `Automation/docs_venv/`, which are in .gitignore):
```bash
cd Automation
./bootstrap_envs.sh
```
Then activate the environments as needed:
- `source ../venv/bin/activate` for code work
- `source docs_venv/bin/activate` for `docs_builder.py`

## When only High-Level requirements exist
- Enter them in `Docs/requirements/high_level_requirements.yaml` (written by a human).
- For each high-level requirement, add software requirements in `Docs/requirements/software_requirements.yaml` with mandatory `refines` to the high-level ID.
- A software requirement without `refines` is invalid and must be corrected before implementation.

## Writing and updating documentation
1. Update YAML files in `Docs/requirements/`.
2. Update PUML diagrams in `Docs/architecture/` (`runtime_diagram.puml`, `class_diagram.puml`, `block_diagram.puml`).
3. Generate the HTML site:
	```bash
	cd Automation
	source docs_venv/bin/activate  # optional
	python3 docs_builder.py
	```
4. Open `Docs/build/index.html` in your browser.

## What is in Docs/
- `requirements/` – high-level and software requirements (YAML)
- `architecture/` – PlantUML diagrams (runtime, class, block)
- `build/` – generated HTML (`docs_builder.py`)

## Rules while the agent writes code
- Before code: write/update software requirements (with `refines`) and status according to AGENTS.md.
- After changes: refresh PUML diagrams and run `docs_builder.py`.
- If a software requirement does not have a valid `refines`, correct it first, then implement.