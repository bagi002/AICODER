# Automation & Documentation Workflow

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
