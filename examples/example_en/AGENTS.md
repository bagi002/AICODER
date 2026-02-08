# General Guidelines for AI Agents in Projects

## Overview
This document defines strict, formal, and unambiguous rules that AI agents must follow when processing user requests in software projects. All steps must be executed in order, without exception, unless otherwise specified. The document assumes a standard project folder structure, which can be adapted to specific needs.
**Before every task, be sure to read this AGENTS.md instruction before analyzing the request.**

## Steps for Processing Requests
For each received prompt request, the AI agent must perform the following steps in the specified order:

1. **Read and understand the notes**: First, read and understand all important notes at the end of this document.
2. **Understand the user's request**: Read and fully understand the user's request.
3. **Check high-level requirements**: Review the high-level requirements defined in `Docs/requirements/high_level_requirements.yaml` and identify which ones are covered by the received request.
4. **Check software requirements**:
	 - Check if there are defined software requirements in the `Docs/` folder that inherit relevant high-level requirements (the `refines` field).
	 - If they exist, read and understand those software requirements.
	 - Write new software requirements if needed or if none exist, to cover the received request.
5. **Write system architecture and design**:
	 - Based on the software requirements, write or update the system architecture and design.
	 - Implementation should be shown through PUML files.
6. **Implement functionalities in relevant components** (backend, frontend, firmware, data, etc.).
7. **Implement functionalities in other components** according to the project structure.

## Expected Project Folder Structure
- `.vscode/`: VS Code settings.
- `Automation/`: Automation scripts (includes `docs_builder.py`).
- Project components (e.g., `backend/`, `frontend/`, `firmware/`, ...).
- `Docs/`:
	- `requirements/`: high-level and software requirements.
	- `architecture/`: PUML diagrams (runtime, class, block).

## Requirements Structure
```yaml
- id: REQ-XXX
	name: Functionality name
	status: [Status]
	refines: REQ-YYY   # Mandatory for software requirements
	description: >
		Requirement description.
```

## Requirement Statuses
- **Draft**: Newly written, not implemented.
- **In Progress**: Implementation in progress.
- **In Review**: Implementation finished, awaiting review.
- **Finished**: Completed, set only by a human.

## Important Notes
- Every implemented requirement must be in "In Review" status.
- AI may only set "Draft" or "In Review"; "Finished" is set by a human.
- Every software requirement must have a valid `refines` to a high-level requirement; without it, it is invalid.