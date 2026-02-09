# Uputstva za AI Agente u Projektu

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
6. **Implementirati funkcionalnosti u relevantnim komponentama**
7. **Opisi pokretanja i načini korišćenja kao i osnovne informacije o projektu u README.md fajlu u root folderu projekta se uvek moraju nalaziti**


## Očekivana Folder Struktura Projekta
- `.vscode/`: Podešavanja za VS Code.
- `Automation/`: Skripte za automatizaciju (uključuje `docs_builder.py`). Ai ne dira
- Komponente projekta (npr. `backend/`, `frontend/`, `firmware/`, ...). U njima je kod, AI implementira funkcionalnosti.
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
- AI sme da promeni status high-level requirementa u "In Review" ako je menjao povezane softverske requirements, ali ne sme da menja sadržaj.