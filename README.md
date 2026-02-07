# README za `project_setup.py`

Dokument opisuje sta radi skripta `project_setup.py`, koji fajlovi i mape se automatski prave i kako primer u folderu `example/` izgleda u praksi. Cilj je da se omoguci preciznije i konciznije programiranje uz pomoc AI-a: ti pises jasne high-level zahteve, AI razradjuje softverske zahteve, arhitekturu i kod, a skripta obezbedjuje strukturu i alatke koje taj ciklus drze pod kontrolom.

## Kako koristiti ovaj repozitorijum
1. Kloniraj repo lokalno (`git clone ...`).
2. Pokreni skriptu: `python3 project_setup.py`.
3. Na početku izaberi gde na disku da se napravi projekat (target direktorijum), pa ime projekta, jezik, komponente i ostale opcije.
4. Skripta generiše kompletan kostur projekta u zadatom direktorijumu; dalje obavezno prati `AGENTS.md` i uputstva iz `Automation/README.md` za AI‑vođeni razvoj (pisanje zahtjeva, dijagrami, kod, dokumentacija).

## Sta skripta radi
- Interaktivno trazi jezik (en/sr), ime projekta, tip projekta (web, embedded/IoT, data/ML), listu komponenti i opcije za venv, Git i bazne dependencije.
- Kreira kompletan projekat u izabranom direktorijumu: `.vscode`, `Automation/`, `Docs/` (requirements + arhitektura), komponente (npr. `backend/`, `frontend/`), start/setup skripte i `.gitignore`.
- Popunjava pocetne fajlove koji usmeravaju rad AI agenta: `AGENTS.md`, YAML sablone za high-level i softverske zahteve, minimalne PUML dijagrame i VS Code podesavanja koja vizuelno isticu statuse zahtjeva.
- Postavlja dedicirani `Automation/docs_venv` sa `pyyaml` i `requests` i generise `Automation/docs_builder.py` – skriptu za auto-build dokumentacije koja čita YAML zahteve + PUML dijagrame i pravi HTML pregled.
- Opcionalno kreira klasicni `venv/`, pokrece `git init` i pravi inicijalni commit.

## Kako pokrenuti
```bash
python3 project_setup.py
# prati pitanja u konzoli (jezik, ime projekta, tip, komponente, venv, git...)
```
Rezultat je novi folder sa svim strukturama i skriptama spremnim za rad.

## Sta se automatski generise (glavne tacke)
- `.vscode/settings.json` – regex highlight statusa (Draft, In Progress, In Review, Finished) u YAML fajlovima sa zahtjevima + Copilot instrukcija da pre odgovora pročita `AGENTS.md` i podseti na obavezne high-level requirements (ljudski unos).
- `AGENTS.md` – striktna pravila kako AI treba da cita zahtjeve, pise softverske zahtjeve, azurira dijagrame i implementira kod. Svaki put pre slanja zahteva AI agentu pročitaj ovaj fajl.
- `Docs/requirements/` – 
  - `high_level_requirements.yaml` (ljudi pisu high-level ciljeve)
  - `software_requirements.yaml` (AI pise, svaki ima obavezan `refines` na high-level ID)
- `Docs/architecture/` – tri PUML fajla (`runtime_diagram.puml`, `class_diagram.puml`, `block_diagram.puml`) kao stubovi za arhitekturu.
- `Automation/` – `docs_builder.py` (auto-build HTML dokumentacije), `bootstrap_envs.sh` (rekreira oba venv okruženja posle `git clone`), `README.md` sa uputstvom, plus `docs_venv/` sa potrebnim paketima za renderovanje dokumenata.
- Korisne skripte u korenu projekta: `setup.sh` i `start.sh` (kosturi za kasniju dopunu).
- Komponente prema izboru (npr. `backend/`, `frontend/`) sa `.gitkeep` fajlovima.
- Opsti `.gitignore` koji pokriva Python, Node i editore.

## Auto-build dokumentacije (šta radi i kako)
- `Automation/docs_builder.py` čita `Docs/requirements/*.yaml` i `Docs/architecture/*.puml`, validira da svaki softverski zahtev ima `refines` i renderuje HTML stranice u `Docs/build/`.
- PUML dijagrami se renderuju preko PlantUML servera; ako nije dostupno, ubacuje fallback sa čistim tekstom dijagrama.
- Ulaz: YAML + PUML; izlaz: `Docs/build/index.html` sa navigacijom na arhitekturu i zahteve (high-level i softverske).
- Pokretanje: `cd Automation && source docs_venv/bin/activate && python3 docs_builder.py`.

## Primer: sta je u `example/`
Folder `example/` je dobijen pokretanjem skripte sa podrazumevanim izborima (jezik en, tip web app, komponente `backend` i `frontend`, venv i docs_venv). Kljucevi fajlovi:
- `example/AGENTS.md` – pravila rada za AI agenta.
- `example/.vscode/settings.json` – ista sema highlight-a statusa zahtjeva.
- `example/Docs/requirements/high_level_requirements.yaml` i `software_requirements.yaml` – minimalni primer sa REQ-001 i REQ-SW-001 koji ga refinira.
- `example/Docs/architecture/*.puml` – stub dijagrami spremni za popunu.
- `example/Automation/docs_builder.py` + `example/Automation/README.md` – alat i uputstvo za generisanje HTML dokumentacije.
- `example/setup.sh`, `example/start.sh`, komponente `backend/`, `frontend/`, kao i `example/venv/` i `example/Automation/docs_venv/` (kreirani tokom seta).

## Workflow za precizno/koncizno programiranje uz AI
1. **Napisite ili azurirajte high-level zahtjeve** u `Docs/requirements/high_level_requirements.yaml` (ljudski unos, statusi po AGENTS.md).
2. **AI razradi softverske zahtjeve** u `Docs/requirements/software_requirements.yaml` – svaki mora imati `refines` ka odgovarajucem high-level ID-u; statusi dozvoljeni: Draft ili In Review.
3. **Azurirajte arhitekturu** u `Docs/architecture/*.puml` (runtime, class, block) da prati softverske zahtjeve.
4. **Generisite HTML pregled** iz `Automation/`: 
   ```bash
   cd Automation
   source docs_venv/bin/activate
   python3 docs_builder.py
   ```
   Otvorite `Docs/build/index.html` i koristite linkove da proverite da nijedan softverski zahtjev ne „visi“ bez `refines` i da svi dijagrami postoje.
5. **Implementirajte kod** unutar komponenti (npr. `backend/`, `frontend/`) uz konsultaciju AGENTS.md, a VS Code highlight pomaze da vidite statuse zahtjeva tokom rada.

## Brzi start sa primerom
```bash
cd example
./Automation/bootstrap_envs.sh          # rekreira root venv i docs_venv (oba su u .gitignore)
source Automation/docs_venv/bin/activate
python3 Automation/docs_builder.py
open Docs/build/index.html   # ili xdg-open / start, zavisno od OS-a
```
Zatim izmenite YAML i PUML fajlove, ponovo pokrenite `docs_builder.py` i pratite promene u generisanoj dokumentaciji.

## Napomene
- Skripta ne instalira projekat-specificke dependencije; samo minimalne alate za dokumentaciju. Dodajte svoje u `setup.sh` i `start.sh`.
- Ako izaberete Git inicijalizaciju, skripta odmah pravi inicijalni commit svih generisanih fajlova.
- Jezik interfejsa i inicijalnih fajlova (en/sr) birate na pocetku; kasnije ih mozete slobodno menjati.
