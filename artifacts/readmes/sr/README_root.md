# example_sr

Kostur README-a — popuniti čim projekat dobije konkretne specifikacije.

## Prvo popuni
- Opis problema / ciljeve
- Tehnologije i verzije (po komponenti)
- Komande za lokalno i CI/CD pokretanje
- Kontakti (owner, reviewer, ops)

## Mapa repozitorijuma
- `Automation/` — alati i `docs_builder.py` (workflow u `Automation/README.md`)
- `Docs/` — requirements i arhitektura (YAML + PUML + HTML)
- Komponente: backend, frontend (ovde ide stvarni kod/servisi)
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
