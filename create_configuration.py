#!/usr/bin/env python3
"""
Interactive configuration creator/editor for project_setup.py.
"""

import copy
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIGURATIONS_DIR = SCRIPT_DIR / "configurations"
OWNER_DIR = CONFIGURATIONS_DIR / "owner"
USER_GENERATED_DIR = CONFIGURATIONS_DIR / "user_generated"
INDEX_FILE = CONFIGURATIONS_DIR / "index.json"
PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")
ALLOWED_PLACEHOLDERS = {"lang", "lang_folder", "project_name"}
ALLOWED_POST_PROCESS = {"none", "replace_first_heading_with_project_name"}


def default_folders():
    return [
        ".vscode",
        "Automation",
        "Docs",
        "Docs/requirements",
        "Docs/architecture",
        "backend",
        "frontend",
    ]


def default_files():
    return [
        {
            "id": "vscode_settings",
            "source": ".vscode/settings.json",
            "target": ".vscode/settings.json",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "docs_builder",
            "source": "scripts/docs_builder.py",
            "target": "Automation/docs_builder.py",
            "enabled": True,
            "executable": True,
            "post_process": "none",
        },
        {
            "id": "bootstrap_envs",
            "source": "scripts/bootstrap_envs.sh",
            "target": "Automation/bootstrap_envs.sh",
            "enabled": True,
            "executable": True,
            "post_process": "none",
        },
        {
            "id": "high_level_requirements",
            "source": "docs/requirements/high_level_requirements.yaml",
            "target": "Docs/requirements/high_level_requirements.yaml",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "software_requirements",
            "source": "docs/requirements/software_requirements.yaml",
            "target": "Docs/requirements/software_requirements.yaml",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "runtime_diagram",
            "source": "docs/architecture/runtime_diagram.puml",
            "target": "Docs/architecture/runtime_diagram.puml",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "class_diagram",
            "source": "docs/architecture/class_diagram.puml",
            "target": "Docs/architecture/class_diagram.puml",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "block_diagram",
            "source": "docs/architecture/block_diagram.puml",
            "target": "Docs/architecture/block_diagram.puml",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "agents_md",
            "source": "readmes/{lang_folder}/AGENTS.md",
            "target": "AGENTS.md",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "automation_readme",
            "source": "readmes/{lang_folder}/README_Automation.md",
            "target": "Automation/README.md",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "root_readme",
            "source": "readmes/{lang_folder}/README_root.md",
            "target": "README.md",
            "enabled": True,
            "executable": False,
            "post_process": "replace_first_heading_with_project_name",
        },
        {
            "id": "root_gitignore",
            "source": ".gitignore",
            "target": ".gitignore",
            "enabled": True,
            "executable": False,
            "post_process": "none",
        },
        {
            "id": "setup_script",
            "source": "scripts/setup.sh",
            "target": "setup.sh",
            "enabled": True,
            "executable": True,
            "post_process": "none",
        },
        {
            "id": "start_script",
            "source": "scripts/start.sh",
            "target": "start.sh",
            "enabled": True,
            "executable": True,
            "post_process": "none",
        },
    ]


def default_runtime():
    return {
        "setup_docs_venv": True,
        "docs_venv_path": "Automation/docs_venv",
        "docs_packages": ["pyyaml", "requests"],
    }


def default_behavior():
    return {
        "add_gitkeep_to_empty_folders": True,
    }


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def load_json_file(path: Path, label: str):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"Missing {label}: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {label} '{path}': {exc}")


def write_json_file(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def ensure_layout() -> None:
    OWNER_DIR.mkdir(parents=True, exist_ok=True)
    USER_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = USER_GENERATED_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

    if not INDEX_FILE.exists():
        initial = {
            "version": 1,
            "description": "Main registry that links all project setup configurations.",
            "configurations": [],
        }
        write_json_file(INDEX_FILE, initial)


def normalize_config_id(raw_id: str) -> str:
    value = raw_id.strip().lower().replace("-", "_").replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def normalize_relative_path(raw_path: str, label: str) -> str:
    value = raw_path.strip().replace("\\", "/").strip("/")
    if not value:
        fail(f"{label} cannot be empty.")
    if value.startswith("/") or value.startswith("~"):
        fail(f"{label} must be relative, got '{raw_path}'.")
    parts = [part for part in value.split("/") if part]
    if any(part == ".." for part in parts):
        fail(f"{label} contains invalid '..': '{raw_path}'.")
    return value


def validate_placeholders(value: str, label: str) -> None:
    for placeholder in PLACEHOLDER_PATTERN.findall(value):
        if placeholder not in ALLOWED_PLACEHOLDERS:
            fail(
                f"{label} uses unsupported placeholder '{{{placeholder}}}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_PLACEHOLDERS))}"
            )


def normalize_folders(raw_folders):
    if not isinstance(raw_folders, list):
        fail("'folders' must be a list.")
    normalized = []
    seen = set()
    for item in raw_folders:
        if not isinstance(item, str):
            fail("Every folder path must be a string.")
        folder = normalize_relative_path(item, "Folder path")
        if folder not in seen:
            seen.add(folder)
            normalized.append(folder)
    return normalized


def normalize_file_rule(raw_rule, index: int):
    if not isinstance(raw_rule, dict):
        fail(f"File rule at index {index} must be an object.")

    rule_id = str(raw_rule.get("id", "")).strip() or f"rule_{index+1}"

    source = raw_rule.get("source")
    target = raw_rule.get("target")
    if not isinstance(source, str) or not source.strip():
        fail(f"File rule '{rule_id}' requires a non-empty string 'source'.")
    if not isinstance(target, str) or not target.strip():
        fail(f"File rule '{rule_id}' requires a non-empty string 'target'.")

    source = source.strip().replace("\\", "/")
    target = target.strip().replace("\\", "/")
    validate_placeholders(source, f"File rule '{rule_id}' source")
    validate_placeholders(target, f"File rule '{rule_id}' target")

    enabled = raw_rule.get("enabled", True)
    executable = raw_rule.get("executable", False)
    if not isinstance(enabled, bool):
        fail(f"File rule '{rule_id}' field 'enabled' must be boolean.")
    if not isinstance(executable, bool):
        fail(f"File rule '{rule_id}' field 'executable' must be boolean.")

    post_process = str(raw_rule.get("post_process", "none")).strip() or "none"
    if post_process not in ALLOWED_POST_PROCESS:
        fail(
            f"File rule '{rule_id}' uses unsupported post_process '{post_process}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_POST_PROCESS))}"
        )

    return {
        "id": rule_id,
        "source": source,
        "target": target,
        "enabled": enabled,
        "executable": executable,
        "post_process": post_process,
    }


def normalize_files(raw_files):
    if not isinstance(raw_files, list):
        fail("'files' must be a list.")
    normalized = []
    seen_ids = set()
    for index, item in enumerate(raw_files):
        rule = normalize_file_rule(item, index)
        if rule["id"] in seen_ids:
            fail(f"Duplicate file rule id '{rule['id']}'.")
        seen_ids.add(rule["id"])
        normalized.append(rule)
    return normalized


def normalize_runtime(raw_runtime):
    baseline = default_runtime()
    if raw_runtime is None:
        return baseline
    if not isinstance(raw_runtime, dict):
        fail("'runtime' must be an object.")
    normalized = dict(baseline)

    if "setup_docs_venv" in raw_runtime:
        if not isinstance(raw_runtime["setup_docs_venv"], bool):
            fail("runtime.setup_docs_venv must be boolean.")
        normalized["setup_docs_venv"] = raw_runtime["setup_docs_venv"]

    if "docs_venv_path" in raw_runtime:
        if not isinstance(raw_runtime["docs_venv_path"], str):
            fail("runtime.docs_venv_path must be string.")
        normalized["docs_venv_path"] = normalize_relative_path(
            raw_runtime["docs_venv_path"], "runtime.docs_venv_path"
        )

    if "docs_packages" in raw_runtime:
        packages = raw_runtime["docs_packages"]
        if not isinstance(packages, list) or any(not isinstance(item, str) for item in packages):
            fail("runtime.docs_packages must be a list of strings.")
        normalized["docs_packages"] = [item.strip() for item in packages if item.strip()]

    return normalized


def normalize_behavior(raw_behavior):
    baseline = default_behavior()
    if raw_behavior is None:
        return baseline
    if not isinstance(raw_behavior, dict):
        fail("'behavior' must be an object.")
    normalized = dict(baseline)

    if "add_gitkeep_to_empty_folders" in raw_behavior:
        value = raw_behavior["add_gitkeep_to_empty_folders"]
        if not isinstance(value, bool):
            fail("behavior.add_gitkeep_to_empty_folders must be boolean.")
        normalized["add_gitkeep_to_empty_folders"] = value

    return normalized


def normalize_configuration_payload(raw_payload):
    payload = dict(raw_payload)
    payload["id"] = normalize_config_id(str(payload.get("id", "")).strip())
    if not payload["id"]:
        fail("Configuration id is required.")

    payload["name"] = str(payload.get("name", payload["id"])).strip() or payload["id"]
    payload["description"] = str(payload.get("description", "")).strip()
    payload["folders"] = normalize_folders(payload.get("folders", []))
    payload["files"] = normalize_files(payload.get("files", []))
    payload["runtime"] = normalize_runtime(payload.get("runtime"))
    payload["behavior"] = normalize_behavior(payload.get("behavior"))
    return payload


def load_registry():
    data = load_json_file(INDEX_FILE, "configuration index")
    entries = data.get("configurations")
    if not isinstance(entries, list):
        fail(f"'configurations' in {INDEX_FILE} must be a list.")
    return data, entries


def load_configurations_from_registry(entries):
    configs = []
    for entry in entries:
        if not isinstance(entry, dict):
            fail("Index entry must be an object.")
        config_id = str(entry.get("id", "")).strip()
        rel_path = str(entry.get("path", "")).strip()
        scope = str(entry.get("scope", "owner")).strip() or "owner"
        if not config_id or not rel_path:
            fail("Each index entry requires 'id' and 'path'.")
        if scope not in ("owner", "user_generated"):
            fail(f"Unsupported configuration scope '{scope}'.")

        config_path = (CONFIGURATIONS_DIR / rel_path).resolve()
        if not str(config_path).startswith(str(CONFIGURATIONS_DIR.resolve())):
            fail(f"Configuration path escapes configurations/: {rel_path}")
        if not config_path.exists():
            fail(f"Missing configuration file from index: {config_path}")

        data = load_json_file(config_path, f"configuration '{config_id}'")
        normalized = normalize_configuration_payload(data)
        if normalized["id"] != config_id:
            fail(
                f"Configuration id mismatch: index has '{config_id}', file has '{normalized['id']}'."
            )
        normalized["_scope"] = scope
        normalized["_path"] = rel_path
        configs.append(normalized)
    return configs


def prompt_yes_no(question: str, default: bool) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{question} {suffix}: ").strip().lower()
    if not raw:
        return default
    if raw in {"y", "yes"}:
        return True
    if raw in {"n", "no"}:
        return False
    print("Invalid answer. Please enter y or n.")
    return prompt_yes_no(question, default)


def prompt_choice(question: str, options, default_index: int = 0) -> int:
    for index, option in enumerate(options, start=1):
        marker = " (default)" if index - 1 == default_index else ""
        print(f" {index}) {option}{marker}")
    raw = input(f"{question} [default {default_index + 1}]: ").strip()
    if not raw:
        return default_index
    try:
        picked = int(raw) - 1
    except ValueError:
        print("Invalid input. Enter a number.")
        return prompt_choice(question, options, default_index)
    if picked < 0 or picked >= len(options):
        print("Choice out of range.")
        return prompt_choice(question, options, default_index)
    return picked


def print_folder_list(folders):
    if not folders:
        print("No folders defined.")
        return
    print("Folders:")
    for index, folder in enumerate(folders, start=1):
        print(f" {index}. {folder}")


def print_file_rules(file_rules):
    if not file_rules:
        print("No file rules defined.")
        return
    print("File rules:")
    for index, rule in enumerate(file_rules, start=1):
        enabled = "on" if rule["enabled"] else "off"
        executable = "x" if rule["executable"] else "-"
        print(
            f" {index}. [{enabled}] {rule['id']} ({executable}) {rule['source']} -> {rule['target']} "
            f"[{rule['post_process']}]"
        )


def pick_index(item_count: int, label: str):
    if item_count <= 0:
        print(f"No {label} available.")
        return None
    raw = input(f"Choose {label} index (1-{item_count}): ").strip()
    try:
        index = int(raw) - 1
    except ValueError:
        print("Invalid index.")
        return None
    if index < 0 or index >= item_count:
        print("Index out of range.")
        return None
    return index


def edit_folders_interactive(payload):
    while True:
        print("\nFolder editor:")
        options = [
            "List folders",
            "Add folder",
            "Rename folder",
            "Remove folder",
            "Back",
        ]
        action = prompt_choice("Choose action", options, 0)

        if action == 0:
            print_folder_list(payload["folders"])
            continue
        if action == 1:
            raw = input("New folder path: ").strip()
            if not raw:
                print("Skipped.")
                continue
            folder = normalize_relative_path(raw, "Folder path")
            if folder not in payload["folders"]:
                payload["folders"].append(folder)
                print(f"Added folder '{folder}'.")
            else:
                print("Folder already exists.")
            continue
        if action == 2:
            print_folder_list(payload["folders"])
            index = pick_index(len(payload["folders"]), "folder")
            if index is None:
                continue
            raw = input(f"New path for '{payload['folders'][index]}': ").strip()
            if not raw:
                print("Skipped.")
                continue
            folder = normalize_relative_path(raw, "Folder path")
            payload["folders"][index] = folder
            payload["folders"] = normalize_folders(payload["folders"])
            print("Folder updated.")
            continue
        if action == 3:
            print_folder_list(payload["folders"])
            index = pick_index(len(payload["folders"]), "folder")
            if index is None:
                continue
            removed = payload["folders"].pop(index)
            print(f"Removed folder '{removed}'.")
            continue
        if action == 4:
            break


def add_file_rule(payload):
    print("\nAdd file rule")
    raw_id = input("Rule id (example: config_json): ").strip()
    rule_id = normalize_config_id(raw_id) if raw_id else f"rule_{len(payload['files']) + 1}"
    if any(rule["id"] == rule_id for rule in payload["files"]):
        print(f"Rule id '{rule_id}' already exists.")
        return

    source = input("Artifact source (relative to artifacts/, placeholders allowed): ").strip()
    target = input("Target path in generated project: ").strip()
    if not source or not target:
        print("Source and target are required.")
        return

    enabled = prompt_yes_no("Enable this rule", True)
    executable = prompt_yes_no("Mark target file executable", False)
    post_options = ["none", "replace_first_heading_with_project_name"]
    post_choice = prompt_choice("Choose post-process", post_options, 0)
    post_process = post_options[post_choice]

    rule = normalize_file_rule(
        {
            "id": rule_id,
            "source": source,
            "target": target,
            "enabled": enabled,
            "executable": executable,
            "post_process": post_process,
        },
        len(payload["files"]),
    )
    payload["files"].append(rule)
    print(f"Added file rule '{rule['id']}'.")


def edit_file_rule(payload):
    print_file_rules(payload["files"])
    index = pick_index(len(payload["files"]), "file rule")
    if index is None:
        return

    rule = dict(payload["files"][index])
    print(f"Editing rule '{rule['id']}'")
    new_source = input(f"Source [{rule['source']}]: ").strip()
    if new_source:
        rule["source"] = new_source
    new_target = input(f"Target [{rule['target']}]: ").strip()
    if new_target:
        rule["target"] = new_target

    if prompt_yes_no("Change enabled flag", False):
        rule["enabled"] = prompt_yes_no("Enable this rule", rule["enabled"])
    if prompt_yes_no("Change executable flag", False):
        rule["executable"] = prompt_yes_no("Mark target executable", rule["executable"])
    if prompt_yes_no("Change post-process", False):
        post_options = ["none", "replace_first_heading_with_project_name"]
        current = post_options.index(rule["post_process"]) if rule["post_process"] in post_options else 0
        post_choice = prompt_choice("Choose post-process", post_options, current)
        rule["post_process"] = post_options[post_choice]

    rule = normalize_file_rule(rule, index)
    payload["files"][index] = rule
    payload["files"] = normalize_files(payload["files"])
    print("File rule updated.")


def toggle_file_rule(payload):
    print_file_rules(payload["files"])
    index = pick_index(len(payload["files"]), "file rule")
    if index is None:
        return
    payload["files"][index]["enabled"] = not payload["files"][index]["enabled"]
    state = "enabled" if payload["files"][index]["enabled"] else "disabled"
    print(f"Rule '{payload['files'][index]['id']}' is now {state}.")


def remove_file_rule(payload):
    print_file_rules(payload["files"])
    index = pick_index(len(payload["files"]), "file rule")
    if index is None:
        return
    removed = payload["files"].pop(index)
    print(f"Removed file rule '{removed['id']}'.")


def edit_runtime(payload):
    runtime = payload["runtime"]
    while True:
        print("\nRuntime settings:")
        print(f" setup_docs_venv: {runtime['setup_docs_venv']}")
        print(f" docs_venv_path: {runtime['docs_venv_path']}")
        print(f" docs_packages: {', '.join(runtime['docs_packages']) if runtime['docs_packages'] else '(none)'}")

        options = [
            "Toggle setup_docs_venv",
            "Change docs_venv_path",
            "Change docs_packages",
            "Back",
        ]
        action = prompt_choice("Choose action", options, 3)
        if action == 0:
            runtime["setup_docs_venv"] = not runtime["setup_docs_venv"]
            continue
        if action == 1:
            raw = input("New docs_venv_path: ").strip()
            if raw:
                runtime["docs_venv_path"] = normalize_relative_path(raw, "runtime.docs_venv_path")
            continue
        if action == 2:
            raw = input("Packages (comma-separated, empty for none): ").strip()
            if not raw:
                runtime["docs_packages"] = []
            else:
                runtime["docs_packages"] = [item.strip() for item in raw.split(",") if item.strip()]
            continue
        if action == 3:
            payload["runtime"] = normalize_runtime(runtime)
            break


def edit_behavior(payload):
    current = payload["behavior"]["add_gitkeep_to_empty_folders"]
    payload["behavior"]["add_gitkeep_to_empty_folders"] = prompt_yes_no(
        f"Add .gitkeep to empty folders (current: {current})",
        current,
    )


def print_payload_summary(payload):
    print("\nCurrent configuration summary:")
    print(f" id: {payload['id']}")
    print(f" name: {payload['name']}")
    print(f" description: {payload['description'] or '(none)'}")
    print(f" folders: {len(payload['folders'])}")
    print(f" files: {len(payload['files'])}")
    print(f" setup_docs_venv: {payload['runtime']['setup_docs_venv']}")


def edit_payload_interactive(payload):
    while True:
        print("\nConfiguration editor:")
        options = [
            "Show summary",
            "Edit folders",
            "List file rules",
            "Add file rule",
            "Edit file rule",
            "Toggle file rule enabled",
            "Remove file rule",
            "Edit runtime settings",
            "Edit behavior settings",
            "Finish editing",
        ]
        action = prompt_choice("Choose action", options, 0)
        if action == 0:
            print_payload_summary(payload)
            continue
        if action == 1:
            edit_folders_interactive(payload)
            continue
        if action == 2:
            print_file_rules(payload["files"])
            continue
        if action == 3:
            add_file_rule(payload)
            continue
        if action == 4:
            edit_file_rule(payload)
            continue
        if action == 5:
            toggle_file_rule(payload)
            continue
        if action == 6:
            remove_file_rule(payload)
            continue
        if action == 7:
            edit_runtime(payload)
            continue
        if action == 8:
            edit_behavior(payload)
            continue
        if action == 9:
            break


def pick_template_mode(owner_configs):
    print("\nCreation mode:")
    options = ["From scratch", "From owner template"]
    mode = prompt_choice("Choose mode", options, 1 if owner_configs else 0)
    if mode == 0:
        return "scratch", None
    if not owner_configs:
        print("No owner templates available. Falling back to scratch mode.")
        return "scratch", None

    print("\nOwner templates:")
    template_labels = [f"{item['name']} [{item['id']}]" for item in owner_configs]
    picked = prompt_choice("Choose template", template_labels, 0)
    return "template", owner_configs[picked]


def build_payload_from_mode(mode: str, template):
    if mode == "template":
        payload = copy.deepcopy(template)
        payload.pop("_scope", None)
        payload.pop("_path", None)
        payload["template"] = template["id"]
        return payload

    return {
        "id": "",
        "name": "",
        "description": "",
        "folders": default_folders(),
        "files": default_files(),
        "runtime": default_runtime(),
        "behavior": default_behavior(),
    }


def prompt_metadata(payload):
    raw_id = input("\nConfiguration id (example: mobile_app): ").strip()
    config_id = normalize_config_id(raw_id)
    if not config_id:
        fail("Configuration id is required.")
    payload["id"] = config_id

    default_name = payload.get("name") or config_id.replace("_", " ").title()
    payload["name"] = input(f"Display name [{default_name}]: ").strip() or default_name
    payload["description"] = input("Description (optional): ").strip()


def upsert_registry_entry(entries, config_id: str, scope: str, relative_path: str) -> None:
    existing_index = None
    for idx, entry in enumerate(entries):
        if str(entry.get("id", "")).strip() == config_id:
            existing_index = idx
            break

    payload = {"id": config_id, "scope": scope, "path": relative_path}
    if existing_index is None:
        entries.append(payload)
        return

    existing_scope = str(entries[existing_index].get("scope", "owner")).strip() or "owner"
    if existing_scope == "owner" and scope == "user_generated":
        fail(
            f"Configuration id '{config_id}' already belongs to an owner configuration. "
            "Use another id for user-generated configuration."
        )

    print(f"\nConfiguration id '{config_id}' already exists in index.")
    overwrite = prompt_yes_no("Overwrite existing registry entry", False)
    if not overwrite:
        fail("Cancelled by user.")
    entries[existing_index] = payload


def main() -> None:
    ensure_layout()
    registry_data, entries = load_registry()
    all_configs = load_configurations_from_registry(entries)
    owner_configs = [cfg for cfg in all_configs if cfg["_scope"] == "owner"]

    print("=== Configuration Creator ===")
    print("Tip: placeholders supported in file source/target: {lang}, {lang_folder}, {project_name}")
    print("User-created configurations are always stored in configurations/user_generated/.")

    scope = "user_generated"
    mode, template = pick_template_mode(owner_configs)
    payload = build_payload_from_mode(mode, template)
    prompt_metadata(payload)

    if mode == "template":
        keep_folders = prompt_yes_no("Keep template folders unchanged", True)
        if not keep_folders:
            edit_folders_interactive(payload)
        keep_files = prompt_yes_no("Keep template file rules unchanged", True)
        if not keep_files:
            edit_payload_interactive(payload)
    else:
        print("\nScratch mode starts from recommended defaults. You can edit everything now.")
        edit_payload_interactive(payload)

    if prompt_yes_no("Open editor for final adjustments", True):
        edit_payload_interactive(payload)

    payload = normalize_configuration_payload(payload)
    payload["created_at"] = datetime.now(timezone.utc).isoformat()

    target_dir = USER_GENERATED_DIR
    relative_prefix = "user_generated"
    output_path = target_dir / f"{payload['id']}.json"
    relative_path = f"{relative_prefix}/{payload['id']}.json"

    upsert_registry_entry(entries, payload["id"], scope, relative_path)
    write_json_file(output_path, payload)

    registry_data["configurations"] = sorted(
        entries,
        key=lambda entry: (
            0 if str(entry.get("scope", "owner")) == "owner" else 1,
            str(entry.get("id", "")).lower(),
        ),
    )
    write_json_file(INDEX_FILE, registry_data)

    print("\nConfiguration saved successfully.")
    print(f"- File: {output_path}")
    print("- Scope: user_generated")
    print(f"- Registered in: {INDEX_FILE}")
    print(f"- Folders: {len(payload['folders'])}")
    print(f"- File rules: {len(payload['files'])}")


if __name__ == "__main__":
    main()
