#!/usr/bin/env python3
"""
Project Setup Script

This script creates a complete project structure based on the AGENTS.md guidelines.
It prompts the user for configuration options and generates the necessary folders,
files, and scripts for a full-stack application template.
"""

import os
import sys
import shutil
from pathlib import Path

def get_user_input():
    """Collect user input for project configuration."""
    print("=== Project Setup Script ===")
    print("This script will create a complete project structure template.\n")

    target_dir = input("Target directory for the new project (default = current): ").strip()
    if not target_dir:
        target_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.expanduser(target_dir))
    try:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Cannot use target directory '{target_dir}': {e}")
        sys.exit(1)

    lang = input("Choose language (en/sr) [en]: ").strip().lower() or "en"
    if lang not in ("en", "sr"):
        lang = "en"

    # Project name
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        sys.exit(1)

    # Project type and components
    project_types = {
        "1": ("Web App (default)", ["backend", "frontend"]),
        "2": ("Embedded/IoT", ["firmware", "hardware", "backend"]),
        "3": ("Data/ML", ["data", "ml", "backend"]),
    }
    print("\nSelect project type:")
    for key, (label, comps) in project_types.items():
        print(f" {key}) {label} - default components: {', '.join(comps)}")
    choice = input("Choose 1/2/3 (default 1): ").strip() or "1"
    label, components = project_types.get(choice, project_types["1"])

    custom = input("Custom components (comma separated, leave empty to keep defaults): ").strip()
    if custom:
        components = [c.strip() for c in custom.split(",") if c.strip()]
        if not components:
            components = project_types["1"][1]

    # Create virtual environment
    create_venv = input("Create Python virtual environment? (y/n): ").strip().lower() == 'y'

    # Initialize Git repository
    use_git = input("Initialize Git repository? (y/n): ").strip().lower() == 'y'

    # Install basic dependencies
    install_deps = input("Install basic dependencies (Python pip, Node.js npm)? (y/n): ").strip().lower() == 'y'

    return {
        'project_name': project_name,
        'target_dir': target_dir,
        'language': lang,
        'components': components,
        'project_type': label,
        'create_venv': create_venv,
        'use_git': use_git,
        'install_deps': install_deps
    }

def create_base_structure(project_path, components):
    """Create the base folder structure from AGENTS.md."""
    folders = [
        '.vscode',
        'Automation',
        'Docs',
        'Docs/requirements',
        'Docs/architecture'
    ] + components

    for folder in folders:
        Path(project_path / folder).mkdir(parents=True, exist_ok=True)
        # Add .gitkeep to empty folders
        gitkeep_path = Path(project_path / folder / '.gitkeep')
        if not any(Path(project_path / folder).iterdir()):
            gitkeep_path.touch()

def create_vscode_settings(project_path):
    """Create .vscode/settings.json with predefined content."""
    settings_content = """{
    "highlight.regexes": {
        "(In Progress)": {
            "regexFlags": "gi",
            "filterFileRegex": ".*\\.yaml",
            "decorations": [
                {"color": "black", "backgroundColor": "yellow"}
            ]
        },
        "(Draft)": {
            "regexFlags": "gi",
            "filterFileRegex": ".*\\.yaml",
            "decorations": [
                {"color": "white", "backgroundColor": "red"}
            ]
        },
        "(Finished)": {
            "regexFlags": "gi",
            "filterFileRegex": ".*\\.yaml",
            "decorations": [
                {"color": "white", "backgroundColor": "green"}
            ]
        },
        "(In Review)": {
            "regexFlags": "gi",
            "filterFileRegex": ".*\\.yaml",
            "decorations": [
                {"color": "black", "backgroundColor": "white"}
            ]
        },
        "(In progress)": {
            "regexFlags": "gi",
            "filterFileRegex": ".*\\.yaml",
            "decorations": [
                {"color": "black", "backgroundColor": "yellow"}
            ]
        }
    },
    "github.copilot.chat.codeGeneration.instructions": [
        {
            "text": "Follow project architecture. Do not modify unrelated files. Return full files only."
        },
        {
            "text": "Before answering, read AGENTS.md and remind the user that high-level requirements must be written by a human in Docs/requirements/high_level_requirements.yaml before AI work begins."
        }
    ]
}"""
    Path(project_path / '.vscode/settings.json').write_text(settings_content)

def create_docs_files(project_path, components, lang):
    """Create documentation files."""
    comp_list = ", ".join(components)

    if lang == "sr":
        hl_req_content = """# High-level Requirements
# Ovaj fajl sadrži high-level requirements koje pišu ljudi.

- id: REQ-001
  name: Osnovno postavljanje aplikacije
  status: Draft
  description: >
    Postaviti osnovnu strukturu projekta sa izabranim komponentama.
"""
        sw_req_content = """# Software Requirements
# Ovaj fajl sadrži softverske requirements koje piše AI agent.

- id: REQ-SW-001
  name: Osnovne funkcionalnosti komponenti
  status: Draft
  refines: REQ-001
  description: >
    Implementirati osnovnu funkcionalnost za izabrane komponente (npr. API-je, servise).
"""
    else:
        hl_req_content = """# High-level Requirements
# This file contains high-level requirements written by humans.

- id: REQ-001
  name: Basic Application Setup
  status: Draft
  description: >
    Set up the basic application structure with the selected components.
"""
        sw_req_content = """# Software Requirements
# This file contains software requirements written by AI agents.

- id: REQ-SW-001
  name: Core Component Functionality
  status: Draft
  refines: REQ-001
  description: >
    Implement basic functionality for the selected components (e.g., APIs, services).
"""

    Path(project_path / 'Docs/requirements/high_level_requirements.yaml').write_text(hl_req_content)
    Path(project_path / 'Docs/requirements/software_requirements.yaml').write_text(sw_req_content)

    # PUML files
    puml_content = """@startuml Runtime Diagram
title Runtime Diagram

actor User
participant Frontend
participant Backend
participant Database

User -> Frontend: Request
Frontend -> Backend: API Call
Backend -> Database: Query
Database --> Backend: Response
Backend --> Frontend: Data
Frontend --> User: Display

@enduml
"""
    Path(project_path / 'Docs/architecture/runtime_diagram.puml').write_text(puml_content)

    Path(project_path / 'Docs/architecture/class_diagram.puml').write_text("@startuml Class Diagram\n'TODO: Add class diagram\n@enduml")
    Path(project_path / 'Docs/architecture/block_diagram.puml').write_text("@startuml Block Diagram\n'TODO: Add block diagram\n@enduml")

def create_agents_md(project_path, lang):
    """Create AGENTS.md file with full content."""
    sr_agents_content = """# Opšta Uputstva za AI Agente u Projektima

## Opšti Pregled
Ovaj dokument definiše stroga, formalna i nedvosmislena pravila koja AI agenti moraju slediti prilikom obrade korisničkih zahteva u softverskim projektima. Svi koraci moraju biti izvršeni redom, bez izuzetaka, osim ako nije drugačije navedeno. Dokument pretpostavlja standardnu folder strukturu projekta, koja se može prilagoditi specifičnim potrebama.
**Pre svakog zadatka obavezno pročitaj ovo AGENTS.md uputstvo pre nego što analiziraš zahtev.**

## Koraci za Obradu Zahteva
Za svaki dobijeni prompt zahtjev, AI agent mora izvršiti sledeće korake u navedenom redosledu:

1. **Pročitati i razumeti napomene**: Prvo pročitati i razumeti sve bitne napomene na kraju ovog dokumenta.
2. **Razumeti zahtjev korisnika**: Pročitati i potpuno razumeti zahtjev koji je korisnik postavio.
3. **Proveriti high-level requirements**: Pregledati high-level requirements definisane u fajlu `Docs/requirements/high_level_requirements.yaml` i identifikovati koje od njih pokriva dobijeni zahtjev.
4. **Proveriti softverske requirements**: 
   - Proveriti da li u folderu `Docs/` postoje definisani softverski requirements koji nasleđuju relevantne high-level requirements (polje `refines`).
   - Ako postoje, pročitati i razumeti te softverske requirements.
   - Napisati nove softverske requirements ako su potrebni ili ako uopšte ne postoje, kako bi se pokrio dobijeni zahtjev.
5. **Napisati arhitekturu i dizajn sistema**:
   - Na osnovu softverskih requirements, napisati ili ažurirati arhitekturu i dizajn sistema.
   - Implementacija treba da bude prikazana kroz PUML fajlove.
6. **Implementirati funkcionalnosti u relevantnim komponentama** (backend, frontend, firmware, data, itd.).
7. **Implementirati funkcionalnosti u ostalim komponentama** prema strukturi projekta.

## Očekivana Folder Struktura Projekta
- `.vscode/`: Podešavanja za VS Code.
- `Automation/`: Skripte za automatizaciju (uključuje `docs_builder.py`).
- Komponente projekta (npr. `backend/`, `frontend/`, `firmware/`, ...).
- `Docs/`:
  - `requirements/`: high-level i softverski requirements.
  - `architecture/`: PUML dijagrami (runtime, class, block).

## Struktura Requirements
```yaml
- id: REQ-XXX
  name: Naziv funkcionalnosti
  status: [Status]
  refines: REQ-YYY   # Obavezno za softverske requirements
  description: >
    Opis requirements.
```

## Statusi Requirements
- **Draft**: Novo napisano, nije implementirano.
- **In Progress**: Implementacija u toku.
- **In Review**: Implementacija završena, čeka pregled.
- **Finished**: Završeno, postavlja samo čovek.

## Bitne Napomene
- Svaki implementirani requirement mora biti u statusu "In Review".
- AI sme da postavlja samo "Draft" ili "In Review"; "Finished" postavlja čovek.
- Svaki softverski requirement mora imati važeći `refines` ka high-level requirementu; bez toga je nevažeći.
- Uvek ažurirati runtime, class i block dijagram kada se menja requirement.
- Svaki izmenjeni requirement se vraća na status "In Review".
- AI piše samo softverske requirements i arhitekturu/dizajn; čovek može pisati i high-level.
- AI sme da promeni status high-level requirementa u "In Review" ako je menjao povezane softverske requirements, ali ne sme da menja sadržaj."""

    en_agents_content = """# General Guidelines for AI Agents

## Overview
This document sets strict, unambiguous rules that AI agents must follow when handling user requests in software projects. Steps must be executed in order unless explicitly stated otherwise. It assumes the standard project folder structure but can be adapted.
**Always read this AGENTS.md first, then analyze the user request in line with these rules.**

## Processing Steps
1. **Read the notes** at the end of this document.
2. **Understand the user request** fully.
3. **Check high-level requirements** in `Docs/requirements/high_level_requirements.yaml` and identify which ones the request touches.
4. **Check software requirements**:
   - Software requirements must refine an existing high-level requirement through the `refines` field.
   - Read existing software requirements in `Docs/requirements/software_requirements.yaml`.
   - Write new software requirements if needed so every impacted high-level requirement is covered.
5. **Write / update architecture & design** based on software requirements (PUML files).
6. **Implement backend or other relevant components** according to the chosen project structure.
7. **Implement frontend or other relevant components** as applicable.

## Expected Folder Structure (relative to project root)
- `.vscode/` – editor settings
- `Automation/` – automation scripts (includes `docs_builder.py`)
- Component folders (e.g., `backend/`, `frontend/`, `firmware/`, etc.)
- `Docs/`
  - `requirements/`
    - `high_level_requirements.yaml` (human-written)
    - `software_requirements.yaml` (AI-written)
  - `architecture/`
    - `runtime_diagram.puml`
    - `class_diagram.puml`
    - `block_diagram.puml`

## Requirement Schema
```yaml
- id: REQ-XXX          # Unique identifier, e.g., REQ-011
  name: Feature name   # Short descriptive name
  status: [Status]     # See status list below
  refines: REQ-YYY     # Required for every software requirement; points to a high-level requirement
  description: >       # Detailed description
    Requirement details.
```

## Requirement Statuses
- **Draft**: Newly written, not implemented.
- **In Progress**: Implementation underway.
- **In Review**: Implementation finished, awaiting review.
- **Finished**: Final status, set by a human only.

## Important Notes
- **Implemented items must be In Review**: Any requirement with implemented work (high-level or software) must be set to "In Review".
- **AI status limits**: AI may set only "Draft" for new requirements or "In Review" for implemented AI requirements. Only humans set "Finished".
- **Software requirements inheritance**: Every software requirement **must** have a valid `refines` pointing to an existing high-level requirement; otherwise it is invalid and must not be implemented.
- **Architectures**: Always update runtime, class, and block diagrams when requirements change.
- **Status on change**: Any modified requirement is reset to "In Review".
- **Writing scope**: AI writes only software requirements and architecture/design. Humans may write both high-level and software requirements and architectures/design.
- **High-level edits by AI**: AI may change status of a related high-level requirement to "In Review" when its software requirements are modified, but must not change its content."""
    content = en_agents_content if lang == "en" else sr_agents_content
    Path(project_path / 'AGENTS.md').write_text(content)

def create_gitignore(project_path):
    """Create .gitignore file."""
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Project build artifacts
Automation/docs_venv/
Docs/build/

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Diagnostic reports (https://nodejs.org/api/report.html)
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
jspm_packages/

# TypeScript v1 declaration files
typings/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# OS generated files
Thumbs.db
ehthumbs.db
Desktop.ini
"""
    Path(project_path / '.gitignore').write_text(gitignore_content)

def create_scripts(project_path, config):
    """Create setup and startup scripts."""
    # setup.sh
    setup_content = """#!/bin/bash

echo "Setting up project environment..."

# Create virtual environment if requested
# python3 -m venv venv

# Activate virtual environment
# source venv/bin/activate

# Install Python dependencies
# pip install -r requirements.txt

# Install Node.js dependencies
# npm install

echo "Setup complete!"
"""
    Path(project_path / 'setup.sh').write_text(setup_content)
    Path(project_path / 'setup.sh').chmod(0o755)

    # start.sh
    start_content = """#!/bin/bash

echo "Starting project..."

# Start backend
# python app.py

# Start frontend
# npm start

echo "Project started!"
"""
    Path(project_path / 'start.sh').write_text(start_content)
    Path(project_path / 'start.sh').chmod(0o755)

def create_automation_readme(project_path, lang):
    """Create Automation/README.md with workflow guidance."""
    if lang == "sr":
        content = """# Automation & Documentation Workflow

Ovaj vodič opisuje kako da se održava dokumentacija i generiše HTML pregled.

## Pre svakog zahteva ka AI agentu
- Pročitaj `AGENTS.md` (obavezno).
- Prvo napiši ili ažuriraj high-level requirements u `Docs/requirements/high_level_requirements.yaml` (piše čovek), pa tek onda šalji zahtev AI agentu da piše softverske requirements/arch/kod.

## Posle `git clone`
Pokreni skriptu koja rekreira oba venv okruženja (root `venv/` i `Automation/docs_venv/`, koja su u .gitignore):
```bash
cd Automation
./bootstrap_envs.sh
```
Zatim aktiviraj okruženja po potrebi:
- `source ../venv/bin/activate` za rad na kodu
- `source docs_venv/bin/activate` za `docs_builder.py`

## Kada postoje samo High-Level requirements
- Unesi ih u `Docs/requirements/high_level_requirements.yaml` (piše čovek).
- Za svaki high-level dodaj softverske requirements u `Docs/requirements/software_requirements.yaml` sa obaveznim `refines` ka high-level ID-u.
- Softverski requirement bez `refines` je nevažeći i mora se ispraviti pre implementacije.

## Pisanje i ažuriranje dokumentacije
1. Ažuriraj YAML fajlove u `Docs/requirements/`.
2. Ažuriraj PUML dijagrame u `Docs/architecture/` (`runtime_diagram.puml`, `class_diagram.puml`, `block_diagram.puml`).
3. Generiši HTML sajt:
   ```bash
   cd Automation
   source docs_venv/bin/activate  # opciono
   python3 docs_builder.py
   ```
4. Otvori `Docs/build/index.html` u browseru.

## Šta je u Docs/
- `requirements/` – high-level i softverski requirements (YAML)
- `architecture/` – PlantUML dijagrami (runtime, class, block)
- `build/` – generisani HTML (`docs_builder.py`)

## Pravila dok agent piše kod
- Pre koda: napiši/ ažuriraj softverske requirements (sa `refines`) i status prema AGENTS.md.
- Posle izmena: osveži PUML dijagrame i pokreni `docs_builder.py`.
- Ako softverski requirement nema validan `refines`, prvo ga ispravi pa tek onda implementiraj.
"""
    else:
        content = """# Automation & Documentation Workflow

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
"""
    Path(project_path / 'Automation' / 'README.md').write_text(content)

def create_readme(project_path, config):
    """Create skeletal README.md file for the root project."""
    components = ", ".join(config["components"])

    if config["language"] == "sr":
        readme_content = f"""# {config['project_name']}

Kostur README-a — popuniti čim projekat dobije konkretne specifikacije.

## Prvo popuni
- Opis problema / ciljeve
- Tehnologije i verzije (po komponenti)
- Komande za lokalno i CI/CD pokretanje
- Kontakti (owner, reviewer, ops)

## Mapa repozitorijuma
- `Automation/` — alati i `docs_builder.py` (workflow u `Automation/README.md`)
- `Docs/` — requirements i arhitektura (YAML + PUML + HTML)
- Komponente: {components if components else 'custom components'} (ovde ide stvarni kod/servisi)
- `.vscode/` — editorska podešavanja i isticanje statusa requirements

## Brzi start (primer)
0) Posle `git clone`: `cd Automation && ./bootstrap_envs.sh` (rekreira root `venv/` i `docs_venv/`)
1) `./setup.sh`
2) `cd Automation && source docs_venv/bin/activate && python3 docs_builder.py`
3) Otvori `Docs/build/index.html`

## Status dokumentacije
- High-level: `Docs/requirements/high_level_requirements.yaml`
- Softverski: `Docs/requirements/software_requirements.yaml` (svaki ima `refines`)
- Dijagrami: `Docs/architecture/*.puml`

Napomena: ovaj README je kostur — zameni ga stvarnim detaljima projekta.
"""
    else:
        readme_content = f"""# {config['project_name']}

Starter README — update with project-specific details as soon as they are known.

## Fill These First
- Problem statement / goals
- Tech stack and versions (list per component)
- Local and CI/CD run commands
- Owners / reviewers / ops contacts

## Repository Map
- `Automation/` — automation tools and `docs_builder.py` (workflow in `Automation/README.md`)
- `Docs/` — requirements and architecture (YAML + PUML + generated HTML)
- Components: {components if components else 'custom components'} (implement actual services/code inside these folders)
- `.vscode/` — editor settings and requirement status highlighting

## Quick Start (example, adjust as needed)
0) After `git clone`: `cd Automation && ./bootstrap_envs.sh` (recreates root `venv/` and `docs_venv/`)
1) `./setup.sh`
2) `cd Automation && source docs_venv/bin/activate && python3 docs_builder.py`
3) Open `Docs/build/index.html`

## Documentation Status
- High-level requirements: `Docs/requirements/high_level_requirements.yaml`
- Software requirements: `Docs/requirements/software_requirements.yaml` (each must have `refines` pointing to a high-level requirement)
- Diagrams: `Docs/architecture/*.puml`

Note: This README is a scaffold—replace with real project specifics when available.
"""
    Path(project_path / 'README.md').write_text(readme_content)

def create_virtual_env(project_path, create_venv):
    """Create Python virtual environment if requested."""
    if create_venv:
        os.chdir(project_path)
        os.system('python3 -m venv venv')
        os.chdir('..')

def install_dependencies(project_path, install_deps):
    """Install basic dependencies if requested."""
    if install_deps:
        os.chdir(project_path)
        # Install Python pip if not present
        os.system('python3 -m ensurepip --upgrade')
        # For Node.js, assume npm is available
        print("Basic dependencies installation requested. Please run setup.sh manually.")
        os.chdir('..')

def initialize_git(project_path, use_git):
    """Initialize Git repository if requested."""
    if use_git:
        os.chdir(project_path)
        os.system('git init')
        os.system('git add .')
        os.system('git commit -m "Initial project structure"')
        os.chdir('..')

def create_docs_builder_script(project_path):
    """Generate docs_builder.py directly into the new project's Automation folder."""
    docs_builder_content = r'''#!/usr/bin/env python3
"""
Documentation Builder Script

This script generates HTML pages from the Docs folder content for easy browsing.
It creates a build folder with index.html and linked pages for requirements and architecture.
"""

import os
import sys
from pathlib import Path

# Check if running in docs_venv, if not, restart in venv
venv_python = Path(__file__).parent / 'docs_venv' / 'bin' / 'python'
if venv_python.exists() and sys.executable != str(venv_python):
    import subprocess
    result = subprocess.run([str(venv_python), __file__], check=False)
    sys.exit(result.returncode)

import yaml
import requests
import shutil
import zlib


def log_warning(message: str):
    print(f"WARNING: {message}")


def log_error(message: str):
    print(f"ERROR: {message}")


def validate_requirement_list(data, label, required_keys, add_error):
    """Validate a requirement YAML list; returns a cleaned list (invalid entries skipped)."""
    if data is None:
        return []
    if not isinstance(data, list):
        add_error(f"{label} YAML must be a list of items.")
        return []

    cleaned = []
    seen_ids = set()
    allowed_status = {"draft", "in progress", "in review", "finished"}

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            add_error(f"{label}[{idx}] must be a mapping/dict.")
            continue

        missing = [k for k in required_keys if k not in item or item[k] in (None, "")]
        if missing:
            add_error(f"{label}[{idx}] missing required fields: {', '.join(missing)}.")
            continue

        item_id = item.get("id")
        if item_id in seen_ids:
            add_error(f"{label} duplicate id '{item_id}'.")
            continue
        seen_ids.add(item_id)

        status = str(item.get("status", "")).lower()
        if status and status not in allowed_status:
            add_error(f"{label} '{item_id}' has unknown status '{item['status']}'.")

        cleaned.append(item)

    return cleaned


def load_yaml(file_path):
    """Load YAML file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        log_error(f"Failed to load YAML '{file_path}': {e}")
        return None


def load_puml(file_path):
    """Load PUML file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log_error(f"Failed to load PUML '{file_path}': {e}")
        return None


def _plantuml_encode(puml_text: str) -> str:
    """Encode PlantUML text using the official deflate + 6-bit algorithm."""
    # Raw DEFLATE (no zlib header) is required; wbits=-15 turns off headers/checksums
    compressor = zlib.compressobj(level=9, wbits=-zlib.MAX_WBITS)
    compressed = compressor.compress(puml_text.encode("utf-8")) + compressor.flush()

    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    encoded_chars = []

    for i in range(0, len(compressed), 3):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0

        encoded_chars.append(alphabet[(b1 >> 2) & 0x3F])
        encoded_chars.append(alphabet[((b1 & 0x03) << 4) | ((b2 >> 4) & 0x0F)])

        if i + 1 < len(compressed):
            encoded_chars.append(alphabet[((b2 & 0x0F) << 2) | ((b3 >> 6) & 0x03)])
        if i + 2 < len(compressed):
            encoded_chars.append(alphabet[b3 & 0x3F])

    return "".join(encoded_chars)


def render_puml_to_svg(puml_text):
    """Render PUML text to SVG using PlantUML server."""
    try:
        if not isinstance(puml_text, str) or not puml_text.strip():
            raise ValueError("PUML source is empty or invalid.")

        encoded = _plantuml_encode(puml_text)
        url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200 and '<svg' in response.text:
            return response.text

        log_warning(
            f"PlantUML render fallback (status={response.status_code}, content-type={response.headers.get('Content-Type')})"
        )

        # Fallback to text view
        return (
            "<div class='puml-fallback'><h4>PlantUML Diagram (Text View)</h4>"
            f"<pre>{puml_text}</pre>"
            "<p>Unable to render. Copy to <a href='https://www.plantuml.com/plantuml/uml' target='_blank'>PlantUML Online Editor</a> to visualize.</p></div>"
        )

    except Exception as e:
        log_warning(f"PlantUML render failed: {e}")
        return (
            "<div class='puml-fallback'><h4>PlantUML Diagram (Text View)</h4>"
            f"<pre>{puml_text}</pre>"
            f"<p>Error: {e}</p></div>"
        )


def generate_html_head(title):
    """Generate HTML head section with improved styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Project Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #000;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        nav {{
            background-color: #f8f9fa;
            padding: 1rem 0;
            border-bottom: 1px solid #e9ecef;
        }}
        nav .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }}
        nav a {{
            margin: 0 1rem;
            text-decoration: none;
            color: #495057;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }}
        nav a:hover {{
            background-color: #007bff;
            color: white;
        }}
        nav .active {{
            background-color: #007bff;
            color: white;
        }}
        main {{
            padding: 2rem;
        }}
        h1, h2, h3 {{
            color: #000;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 2rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
        }}
        h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
        }}
        .requirement {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 5px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .requirement:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .status-draft {{ border-left-color: #ffc107; }}
        .status-in-progress {{ border-left-color: #17a2b8; }}
        .status-in-review {{ border-left-color: #6c757d; }}
        .status-finished {{ border-left-color: #28a745; }}
        
        .status-badge {{
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-left: 0.5rem;
        }}
        .badge-draft {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .badge-in-progress {{ background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .badge-in-review {{ background-color: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; }}
        .badge-finished {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .requirement h3 {{
            color: #495057;
            margin-bottom: 0.5rem;
        }}
        .requirement p {{
            margin-bottom: 0.5rem;
        }}
        .diagram {{
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .diagram svg {{
            max-width: 100%;
            height: auto;
        }}
        .puml-fallback {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 1rem;
            border-radius: 5px;
        }}
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 1rem;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 2rem;
        }}
        .btn {{
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }}
        .btn:hover {{
            background-color: #0056b3;
        }}
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2rem;
            }}
            nav .nav-container {{
                flex-direction: column;
            }}
            nav a {{
                margin: 0.25rem 0;
            }}
            main {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Project Documentation</h1>
            <p>Comprehensive project overview and requirements</p>
        </header>
"""


def generate_html_footer():
    """Generate HTML footer section."""
    return """
        <footer>
            <p>&copy; 2026 Project Documentation. Generated automatically.</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_navigation(current_page):
    """Generate navigation menu."""
    pages = {
        'index': 'Home',
        'architecture': 'Architecture',
        'high_level': 'High-Level Requirements',
        'software': 'Software Requirements'
    }
    nav = '<nav><div class="nav-container">'
    for page, title in pages.items():
        active_class = ' active' if page == current_page else ''
        nav += f'<a href="{page}.html" class="{active_class}">{title}</a>'
    nav += '</div></nav>'
    return nav


def generate_index_html():
    """Generate index.html page."""
    content = f"""
{generate_html_head("Home")}
{generate_navigation('index')}
<main>
    <h1>Welcome to Project Documentation</h1>
    <p>This documentation provides a comprehensive overview of the project, including architecture diagrams, requirements, and implementation details. Use the navigation above to explore different sections.</p>

    <h2>Documentation Sections</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div class="requirement">
            <h3>🏗️ Architecture</h3>
            <p>View system architecture diagrams including runtime, class, and block diagrams.</p>
            <a href="architecture.html" class="btn">View Architecture</a>
        </div>
        <div class="requirement">
            <h3>📋 High-Level Requirements</h3>
            <p>Browse high-level requirements that define the overall project scope.</p>
            <a href="high_level.html" class="btn">View Requirements</a>
        </div>
        <div class="requirement">
            <h3>⚙️ Software Requirements</h3>
            <p>Explore detailed software requirements with implementation status.</p>
            <a href="software.html" class="btn">View Requirements</a>
        </div>
    </div>
</main>
{generate_html_footer()}
"""
    return content


def generate_architecture_html(docs_path):
    """Generate a hub page for architecture diagrams with links to per-diagram pages."""
    content = f"""
{generate_html_head("Architecture")}
{generate_navigation('architecture')}
<main>
    <h1>System Architecture Diagrams</h1>
    <p>Select a diagram to view it on its dedicated page.</p>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div class="requirement">
            <h3>Runtime Diagram</h3>
            <p>Sequence of runtime interactions.</p>
            <a class="btn" href="runtime.html">Open runtime diagram</a>
        </div>
        <div class="requirement">
            <h3>Class Diagram</h3>
            <p>Class structure and relationships.</p>
            <a class="btn" href="class.html">Open class diagram</a>
        </div>
        <div class="requirement">
            <h3>Block Diagram</h3>
            <p>High-level blocks and data flows.</p>
            <a class="btn" href="block.html">Open block diagram</a>
        </div>
    </div>
</main>
{generate_html_footer()}
"""
    return content


def generate_single_diagram_page(docs_path, filename, title, page_slug):
    """Generate a dedicated page for one PlantUML diagram."""
    puml_path = docs_path / 'architecture' / filename
    puml_source = load_puml(puml_path)

    if puml_source is None:
        svg = f"<div class='puml-fallback'><p>Missing or unreadable file: {puml_path.name}</p></div>"
        log_warning(f"Skipping render for missing/invalid PUML: {puml_path}")
    else:
        if "@startuml" not in puml_source or "@enduml" not in puml_source:
            log_warning(f"PUML file may be invalid (missing @startuml/@enduml): {puml_path}")
        svg = render_puml_to_svg(puml_source)

    content = f"""
{generate_html_head(title)}
{generate_navigation('architecture')}
<main>
    <h1>{title}</h1>
    <p>Rendered from {filename}. Edit the PUML file and rebuild docs to refresh.</p>
    <div class="diagram">
        {svg}
    </div>
    <p style="text-align:center; margin-top:1rem;"><a class="btn" href="architecture.html">⬅ Back to Architecture Hub</a></p>
</main>
{generate_html_footer()}
"""
    return content


def generate_requirements_html(requirements_data, title, page_name, links=None):
    """Generate requirements HTML page."""
    if links is None:
        links = {}
    
    if isinstance(requirements_data, str):
        # Error message
        content = f"""
{generate_html_head(title)}
{generate_navigation(page_name)}
<main>
    <h1>{title}</h1>
    <p>{requirements_data}</p>
</main>
{generate_html_footer()}
"""
        return content

    content = f"""
{generate_html_head(title)}
{generate_navigation(page_name)}
<main>
    <h1>{title}</h1>
    <p>This section contains all {title.lower()} with their current status and details.</p>
"""

    for req in requirements_data:
        status = req.get('status', 'draft')
        status_slug = status.lower().replace(' ', '-')
        status_class = f"status-{status_slug}"
        req_id = req['id']
        
        if page_name == 'software':
            refines = req.get('refines', 'N/A')
            refines_link = links.get(f"sw_{req_id}", "#")
            if refines_link != "#":
                refines = f'<a href="{refines_link}">{refines}</a>'
        else:
            refines = req.get('refines', 'N/A')
        
        content += f"""
    <div class="requirement {status_class}" id="{req_id}">
        <h3>{req_id}: {req['name']}</h3>
        <p><strong>Status:</strong> <span class="status-badge badge-{status_slug}">{status}</span></p>
        <p><strong>Refines:</strong> {refines}</p>
        <p><strong>Description:</strong></p>
        <p>{req.get('description', 'N/A').replace('> ', '').strip()}</p>
"""
        
        # For high-level, add list of refining software requirements
        if page_name == 'high_level':
            refining_links = links.get(f"hl_{req_id}", [])
            if refining_links:
                content += "<p><strong>Refined by:</strong></p><ul>"
                for link in refining_links:
                    sw_id = link.split('#')[1]
                    content += f'<li><a href="{link}">{sw_id}</a></li>'
                content += "</ul>"
        
        content += "</div>"

    content += """
</main>
"""
    content += generate_html_footer()
    return content


def build_docs(docs_path):
    """Build HTML documentation from Docs folder."""
    build_path = docs_path / 'build'
    build_path.mkdir(exist_ok=True)

    errors = []

    def add_error(msg):
        errors.append(msg)
        log_error(msg)

    # Load requirements
    hl_req_path = docs_path / 'requirements/high_level_requirements.yaml'
    sw_req_path = docs_path / 'requirements/software_requirements.yaml'

    hl_req_data = load_yaml(hl_req_path)
    sw_req_data = load_yaml(sw_req_path)

    # Validate YAML load results
    if hl_req_data is None:
        add_error(f"Could not load {hl_req_path}")
    if sw_req_data is None:
        add_error(f"Could not load {sw_req_path}")

    # Validate requirement schema
    hl_req_data = validate_requirement_list(
        hl_req_data, "High-level", ["id", "name", "status", "description"], add_error
    )
    sw_req_data = validate_requirement_list(
        sw_req_data, "Software", ["id", "name", "status", "refines", "description"], add_error
    )

    # Build links and detect dangling software requirements
    links = {}
    dangling_sw = []

    if isinstance(hl_req_data, list) and isinstance(sw_req_data, list):
        # Map high-level IDs
        hl_ids = {req['id']: req for req in hl_req_data}
        # For each software req, add link to high-level
        for sw_req in sw_req_data:
            refines = sw_req.get('refines')
            if refines and refines in hl_ids:
                links[f"sw_{sw_req['id']}"] = f"high_level.html#{refines}"
            else:
                dangling_sw.append(sw_req.get('id', '<unknown>'))

        # For each high-level, find software that refines it
        for hl_req in hl_req_data:
            hl_id = hl_req['id']
            refining_sw = [sw['id'] for sw in sw_req_data if sw.get('refines') == hl_id]
            if refining_sw:
                links[f"hl_{hl_id}"] = [f"software.html#{sw_id}" for sw_id in refining_sw]
    else:
        if not isinstance(hl_req_data, list):
            add_error("High-level requirements YAML must be a list of entries.")
        if not isinstance(sw_req_data, list):
            add_error("Software requirements YAML must be a list of entries.")

    # Generate pages
    index_html = generate_index_html()
    architecture_html = generate_architecture_html(docs_path)
    runtime_html = generate_single_diagram_page(docs_path, 'runtime_diagram.puml', 'Runtime Diagram', 'runtime')
    class_html = generate_single_diagram_page(docs_path, 'class_diagram.puml', 'Class Diagram', 'class')
    block_html = generate_single_diagram_page(docs_path, 'block_diagram.puml', 'Block Diagram', 'block')

    high_level_html = generate_requirements_html(hl_req_data, "High-Level Requirements", 'high_level', links)
    software_html = generate_requirements_html(sw_req_data, "Software Requirements", 'software', links)

    # Write files
    (build_path / 'index.html').write_text(index_html, encoding='utf-8')
    (build_path / 'architecture.html').write_text(architecture_html, encoding='utf-8')
    (build_path / 'runtime.html').write_text(runtime_html, encoding='utf-8')
    (build_path / 'class.html').write_text(class_html, encoding='utf-8')
    (build_path / 'block.html').write_text(block_html, encoding='utf-8')
    (build_path / 'high_level.html').write_text(high_level_html, encoding='utf-8')
    (build_path / 'software.html').write_text(software_html, encoding='utf-8')

    if dangling_sw:
        add_error(f"Dangling software requirements (no matching high-level refines): {', '.join(dangling_sw)}")

    if errors:
        print("\nBuild completed with issues:")
        for err in errors:
            print(f" - {err}")
    else:
        print(f"Documentation built successfully in {build_path}")
    print(f"Open {build_path / 'index.html'} in your browser to view the documentation.")


def main():
    # Script is run from Automation folder
    automation_path = Path.cwd()
    project_root = automation_path.parent
    docs_path = project_root / 'Docs'

    if not docs_path.exists():
        print("Docs folder not found. Please run this script from the Automation folder within the project.")
        return

    build_docs(docs_path)


if __name__ == "__main__":
    main()
'''
    dest = project_path / 'Automation' / 'docs_builder.py'
    dest.write_text(docs_builder_content, encoding='utf-8')
    dest.chmod(0o755)


def create_env_bootstrap_script(project_path):
    """Create a helper script to (re)build both venvs after git clone."""
    script_content = """#!/bin/bash
set -euo pipefail

# Rebuilds the main venv (project root) and docs_venv (Automation/) so that
# a freshly cloned repo gets working environments without committing them to git.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AUTO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/2] Creating main venv at $ROOT_DIR/venv"
python3 -m venv "$ROOT_DIR/venv"
"$ROOT_DIR/venv/bin/pip" install --upgrade pip >/dev/null

echo "[2/2] Creating docs_venv at $AUTO_DIR/docs_venv"
python3 -m venv "$AUTO_DIR/docs_venv"
"$AUTO_DIR/docs_venv/bin/pip" install --upgrade pip >/dev/null
"$AUTO_DIR/docs_venv/bin/pip" install pyyaml requests >/dev/null

cat <<EOT

Environments ready.
- Activate main venv:   source "$ROOT_DIR/venv/bin/activate"
- Activate docs_venv:   source "$AUTO_DIR/docs_venv/bin/activate"  # for docs_builder.py
EOT
"""

    dest = project_path / 'Automation' / 'bootstrap_envs.sh'
    dest.write_text(script_content)
    dest.chmod(0o755)

def setup_docs_venv(project_path):
    """Create dedicated virtual environment for docs building with all required packages."""
    print("Setting up documentation build environment...")
    venv_path = project_path / 'Automation' / 'docs_venv'
    
    # Create venv
    import subprocess
    subprocess.run(['python3', '-m', 'venv', str(venv_path)], check=True)
    
    # Install required packages (zlib is built-in, no need to install)
    pip_path = venv_path / 'bin' / 'pip'
    packages = ['pyyaml', 'requests']
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([str(pip_path), 'install', package], check=True)
    
    print("Documentation build environment ready!")

def main():
    config = get_user_input()

    # Create project directory
    base_path = Path(config['target_dir']).expanduser()
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)

    project_path = base_path / config['project_name']
    if project_path.exists():
        print(f"Directory {config['project_name']} already exists. Please choose a different name.")
        sys.exit(1)

    project_path.mkdir()

    # Create structure and files
    create_base_structure(project_path, config['components'])
    create_vscode_settings(project_path)
    create_docs_files(project_path, config['components'], config['language'])
    create_agents_md(project_path, config['language'])
    create_gitignore(project_path)
    create_scripts(project_path, config)
    create_automation_readme(project_path, config['language'])
    create_readme(project_path, config)
    create_docs_builder_script(project_path)
    create_env_bootstrap_script(project_path)
    setup_docs_venv(project_path)

    # Optional setups
    create_virtual_env(project_path, config['create_venv'])
    install_dependencies(project_path, config['install_deps'])
    initialize_git(project_path, config['use_git'])

    print(f"\nProject '{config['project_name']}' created successfully!")
    print(f"Navigate to {config['project_name']} to get started.")
    if config['create_venv']:
        print("Virtual environment created in venv/ directory.")
    if config['use_git']:
        print("Git repository initialized with initial commit.")

if __name__ == "__main__":
    main()
