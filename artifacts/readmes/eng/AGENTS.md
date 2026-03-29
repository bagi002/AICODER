# Instructions for AI Agents in the Project

## Steps for Processing Requests
For each received prompt request, the AI agent must execute the following steps in the specified order:

1. **Read and understand the notes**: First, read and understand all important notes at the end of this document.
2. **Understand the user's request**: Read and fully understand the request submitted by the user.
3. **Check high-level requirements**: Review the high-level requirements defined in `Docs/requirements/high_level_requirements.yaml` and identify which of them are covered by the received request.
4. **Check software requirements**:
   - Check whether software requirements are defined in the `Docs/` folder that inherit relevant high-level requirements (the `refines` field).
   - If they exist, read and understand those software requirements.
   - Write new software requirements if needed, or if none exist at all, in order to cover the received request.
5.1. **Review and understand the current architecture and system design**: Review the existing PUML diagrams (runtime, class, block) and understand how the functionalities related to the received request are currently implemented.
5.2. **Write architecture and system design**:
   - Based on the software requirements, write or update the system architecture and design.
   - The implementation should be shown through PUML files.
6. **Implement functionalities in relevant components**
7. **Descriptions of startup and usage methods, as well as basic project information, must always be present in the `README.md` file in the project's root folder**
8. **Update `.sh` scripts in the project's root folder**: If needed, update `.sh` scripts located in the project's root folder to ensure all functionalities are properly started and integrated.
9. **Every code file larger than 200 lines should be split into multiple smaller files when possible**: Maintain code modularity and avoid large files that are difficult to maintain.
10. **Update the status of all relevant requirements**: After implementation, update the status of all relevant requirements to "In Review" and notify a human to review the High-Level and Software Requirements implementation.

## Expected Project Folder Structure
- `.vscode/`: Settings for VS Code.
- `Automation/`: Automation scripts (includes `docs_builder.py`). AI does not touch this.
- Project components (e.g., `backend/`, `frontend/`, `firmware/`, ...). Source code lives here, AI implements functionalities.
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
- You must never run build or start the application; that is a human's task.
- Every implemented requirement must be in "In Review" status.
- AI may set only "Draft" or "In Review"; "Finished" is set by a human.
- Every software requirement must have a valid `refines` to a high-level requirement; without it, it is invalid.
- Always update runtime, class, and block diagrams when a requirement is changed.
- Every modified requirement is returned to "In Review" status.
- AI writes only software requirements and architecture/design; a human can write high-level requirements too.
- AI may change the status of a high-level requirement to "In Review" if related software requirements were changed, but it must not change the content.
- Large files should not exist in the system; code should remain modular.
