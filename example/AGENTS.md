# General Guidelines for AI Agents

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
- **High-level edits by AI**: AI may change status of a related high-level requirement to "In Review" when its software requirements are modified, but must not change its content.