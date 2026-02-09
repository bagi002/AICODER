#!/usr/bin/env python3
"""
Project setup script driven by artifacts/ templates and configuration JSON files.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"
CONFIGURATIONS_DIR = SCRIPT_DIR / "configurations"
CONFIG_INDEX_FILE = CONFIGURATIONS_DIR / "index.json"
LANG_TO_FOLDER = {"en": "eng", "sr": "sr"}
PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")
ALLOWED_PLACEHOLDERS = {"lang", "lang_folder", "project_name"}
ALLOWED_POST_PROCESS = {"none", "replace_first_heading_with_project_name"}


def default_runtime_settings():
    """Default runtime settings for legacy configs."""
    return {
        "setup_docs_venv": True,
        "docs_venv_path": "Automation/docs_venv",
        "docs_packages": ["pyyaml", "requests"],
    }


def default_behavior_settings():
    """Default behavior settings for legacy configs."""
    return {
        "add_gitkeep_to_empty_folders": True,
    }


def fail(message: str) -> None:
    """Print an error and exit."""
    print(f"ERROR: {message}")
    sys.exit(1)


def load_json_file(path: Path, label: str):
    """Load JSON file with a useful error if malformed."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"Missing {label}: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {label} '{path}': {exc}")


def normalize_relative_path(raw_path: str, label: str) -> str:
    """Validate and normalize a relative path."""
    normalized = raw_path.strip().replace("\\", "/").strip("/")
    if not normalized:
        fail(f"{label} cannot be empty.")
    if normalized.startswith("/") or normalized.startswith("~"):
        fail(f"{label} must be relative, got '{raw_path}'.")
    parts = [part for part in normalized.split("/") if part]
    if any(part == ".." for part in parts):
        fail(f"{label} contains invalid relative traversal: '{raw_path}'.")
    return normalized


def validate_placeholders(value: str, label: str) -> None:
    """Validate placeholders used in a template string."""
    for placeholder in PLACEHOLDER_PATTERN.findall(value):
        if placeholder not in ALLOWED_PLACEHOLDERS:
            fail(
                f"{label} uses unsupported placeholder '{{{placeholder}}}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_PLACEHOLDERS))}"
            )


def render_template_string(template: str, context: dict, label: str) -> str:
    """Render known placeholders in template string."""
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))
    leftovers = PLACEHOLDER_PATTERN.findall(rendered)
    if leftovers:
        fail(
            f"{label} still contains unresolved placeholders: "
            + ", ".join(sorted({f'{{{item}}}' for item in leftovers}))
        )
    return rendered


def resolve_artifact(relative_path: str) -> Path:
    """Resolve artifact source path and fail if missing."""
    source = ARTIFACTS_DIR / relative_path
    if not source.exists():
        fail(f"Required artifact is missing: {source}")
    return source


def normalize_folder_list(raw_folders, config_id: str):
    """Validate and normalize folder definitions from configuration files."""
    if not isinstance(raw_folders, list):
        fail(f"Configuration '{config_id}' must define 'folders' as a list.")

    normalized = []
    seen = set()
    for item in raw_folders:
        if not isinstance(item, str):
            fail(f"Configuration '{config_id}' has a non-string folder entry.")
        folder = normalize_relative_path(item, f"Configuration '{config_id}' folder")
        if folder not in seen:
            seen.add(folder)
            normalized.append(folder)
    return normalized


def normalize_file_rule(raw_rule, index: int, config_id: str):
    """Validate and normalize one file generation rule."""
    if not isinstance(raw_rule, dict):
        fail(f"Configuration '{config_id}' file rule at index {index} must be an object.")

    rule_id = str(raw_rule.get("id", "")).strip() or f"rule_{index+1}"
    enabled = raw_rule.get("enabled", True)
    if not isinstance(enabled, bool):
        fail(f"Configuration '{config_id}' file rule '{rule_id}' has non-boolean 'enabled'.")

    source = raw_rule.get("source")
    target = raw_rule.get("target")
    if not isinstance(source, str) or not source.strip():
        fail(f"Configuration '{config_id}' file rule '{rule_id}' requires string 'source'.")
    if not isinstance(target, str) or not target.strip():
        fail(f"Configuration '{config_id}' file rule '{rule_id}' requires string 'target'.")

    source_template = source.strip().replace("\\", "/")
    target_template = target.strip().replace("\\", "/")
    validate_placeholders(source_template, f"Configuration '{config_id}' file rule '{rule_id}' source")
    validate_placeholders(target_template, f"Configuration '{config_id}' file rule '{rule_id}' target")

    executable = raw_rule.get("executable", False)
    if not isinstance(executable, bool):
        fail(f"Configuration '{config_id}' file rule '{rule_id}' has non-boolean 'executable'.")

    post_process = str(raw_rule.get("post_process", "none")).strip() or "none"
    if post_process not in ALLOWED_POST_PROCESS:
        fail(
            f"Configuration '{config_id}' file rule '{rule_id}' uses unsupported post_process "
            f"'{post_process}'."
        )

    return {
        "id": rule_id,
        "enabled": enabled,
        "source_template": source_template,
        "target_template": target_template,
        "executable": executable,
        "post_process": post_process,
    }


def normalize_file_rules(raw_rules, config_id: str):
    """Validate and normalize file generation rules."""
    if raw_rules is None:
        fail(f"Configuration '{config_id}' must define explicit 'files' rules.")
    if not isinstance(raw_rules, list):
        fail(f"Configuration '{config_id}' must define 'files' as a list.")

    normalized = []
    seen_ids = set()
    for index, rule in enumerate(raw_rules):
        normalized_rule = normalize_file_rule(rule, index, config_id)
        if normalized_rule["id"] in seen_ids:
            fail(f"Configuration '{config_id}' has duplicate file rule id '{normalized_rule['id']}'.")
        seen_ids.add(normalized_rule["id"])
        normalized.append(normalized_rule)
    return normalized


def normalize_runtime_settings(raw_runtime, config_id: str):
    """Normalize runtime settings from configuration."""
    baseline = default_runtime_settings()
    if raw_runtime is None:
        return baseline
    if not isinstance(raw_runtime, dict):
        fail(f"Configuration '{config_id}' 'runtime' must be an object.")

    normalized = dict(baseline)
    if "setup_docs_venv" in raw_runtime:
        if not isinstance(raw_runtime["setup_docs_venv"], bool):
            fail(f"Configuration '{config_id}' runtime.setup_docs_venv must be boolean.")
        normalized["setup_docs_venv"] = raw_runtime["setup_docs_venv"]

    if "docs_venv_path" in raw_runtime:
        if not isinstance(raw_runtime["docs_venv_path"], str):
            fail(f"Configuration '{config_id}' runtime.docs_venv_path must be string.")
        normalized["docs_venv_path"] = normalize_relative_path(
            raw_runtime["docs_venv_path"], f"Configuration '{config_id}' runtime.docs_venv_path"
        )

    if "docs_packages" in raw_runtime:
        raw_packages = raw_runtime["docs_packages"]
        if not isinstance(raw_packages, list) or any(not isinstance(item, str) for item in raw_packages):
            fail(f"Configuration '{config_id}' runtime.docs_packages must be a list of strings.")
        packages = [item.strip() for item in raw_packages if item.strip()]
        normalized["docs_packages"] = packages
    return normalized


def normalize_behavior_settings(raw_behavior, config_id: str):
    """Normalize behavior settings from configuration."""
    baseline = default_behavior_settings()
    if raw_behavior is None:
        return baseline
    if not isinstance(raw_behavior, dict):
        fail(f"Configuration '{config_id}' 'behavior' must be an object.")

    normalized = dict(baseline)
    if "add_gitkeep_to_empty_folders" in raw_behavior:
        value = raw_behavior["add_gitkeep_to_empty_folders"]
        if not isinstance(value, bool):
            fail(f"Configuration '{config_id}' behavior.add_gitkeep_to_empty_folders must be boolean.")
        normalized["add_gitkeep_to_empty_folders"] = value
    return normalized


def normalize_configuration_data(config_data: dict, config_id: str):
    """Normalize a full configuration document."""
    folders = normalize_folder_list(config_data.get("folders", []), config_id)
    files = normalize_file_rules(config_data.get("files"), config_id)
    runtime = normalize_runtime_settings(config_data.get("runtime"), config_id)
    behavior = normalize_behavior_settings(config_data.get("behavior"), config_id)

    return {
        "id": config_id,
        "name": str(config_data.get("name", config_id)).strip() or config_id,
        "description": str(config_data.get("description", "")).strip(),
        "folders": folders,
        "files": files,
        "runtime": runtime,
        "behavior": behavior,
    }


def load_available_configurations():
    """Load and validate all configurations from configurations/index.json."""
    if not CONFIGURATIONS_DIR.exists():
        fail(f"Configurations directory does not exist: {CONFIGURATIONS_DIR}")

    index_data = load_json_file(CONFIG_INDEX_FILE, "configuration index")
    entries = index_data.get("configurations")
    if not isinstance(entries, list) or not entries:
        fail(f"{CONFIG_INDEX_FILE} must contain a non-empty 'configurations' list.")

    available = []
    seen_ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail(f"{CONFIG_INDEX_FILE} has an invalid entry that is not an object.")

        ref_id = str(entry.get("id", "")).strip()
        rel_path = str(entry.get("path", "")).strip()
        scope = str(entry.get("scope", "")).strip() or "owner"
        if not ref_id or not rel_path:
            fail(f"{CONFIG_INDEX_FILE} entries require 'id' and 'path'.")
        if scope not in ("owner", "user_generated"):
            fail(f"Configuration '{ref_id}' has unsupported scope '{scope}'.")

        config_path = (CONFIGURATIONS_DIR / rel_path).resolve()
        if not str(config_path).startswith(str(CONFIGURATIONS_DIR.resolve())):
            fail(f"Configuration '{ref_id}' points outside configurations/: {rel_path}")
        if not config_path.exists():
            fail(f"Configuration '{ref_id}' points to missing file: {config_path}")

        config_data = load_json_file(config_path, f"configuration '{ref_id}'")
        file_id = str(config_data.get("id", "")).strip()
        if not file_id:
            fail(f"Configuration file '{config_path}' is missing 'id'.")
        if file_id != ref_id:
            fail(f"ID mismatch for '{ref_id}': index uses '{ref_id}' but file defines '{file_id}'.")
        if file_id in seen_ids:
            fail(f"Duplicate configuration id in index: '{file_id}'.")
        seen_ids.add(file_id)

        normalized = normalize_configuration_data(config_data, file_id)
        normalized["scope"] = scope
        normalized["relative_path"] = rel_path
        available.append(normalized)

    available.sort(key=lambda item: (0 if item["scope"] == "owner" else 1, item["name"].lower()))
    return available


def choose_configuration(configurations):
    """Prompt user to pick one of the available configurations."""
    print("\nSelect project configuration:")
    for index, config in enumerate(configurations, start=1):
        scope_label = "owner" if config["scope"] == "owner" else "user"
        folder_count = len(config["folders"])
        file_count = len(config["files"])
        print(f" {index}) {config['name']} [{config['id']}] ({scope_label})")
        print(f"    folders={folder_count}, file_rules={file_count}")
        if config["description"]:
            print(f"    {config['description']}")

    choice_raw = input(f"Choose 1-{len(configurations)} [1]: ").strip() or "1"
    try:
        choice = int(choice_raw)
    except ValueError:
        fail(f"Invalid configuration choice '{choice_raw}'.")
    if choice < 1 or choice > len(configurations):
        fail(f"Configuration choice must be between 1 and {len(configurations)}.")
    return configurations[choice - 1]


def get_user_input(configurations):
    """Collect user input for project creation."""
    print("=== Project Setup Script ===")
    print("This script creates a project from artifacts and selected configuration.\n")

    target_dir = input("Target directory for the new project (default = current): ").strip()
    if not target_dir:
        target_dir = os.getcwd()
    target_dir = os.path.abspath(os.path.expanduser(target_dir))
    try:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        fail(f"Cannot use target directory '{target_dir}': {exc}")

    language = input("Choose language (en/sr) [en]: ").strip().lower() or "en"
    if language not in ("en", "sr"):
        language = "en"

    project_name = input("Enter project name: ").strip()
    if not project_name:
        fail("Project name cannot be empty.")

    selected_config = choose_configuration(configurations)

    create_venv = input("Create Python virtual environment? (y/n): ").strip().lower() == "y"
    use_git = input("Initialize Git repository? (y/n): ").strip().lower() == "y"
    install_deps = (
        input("Install basic dependencies (Python pip, Node.js npm)? (y/n): ").strip().lower() == "y"
    )

    return {
        "project_name": project_name,
        "target_dir": target_dir,
        "language": language,
        "selected_configuration": selected_config,
        "create_venv": create_venv,
        "use_git": use_git,
        "install_deps": install_deps,
    }


def create_folders(project_path: Path, folders) -> None:
    """Create folder structure from configuration."""
    for folder in folders:
        (project_path / folder).mkdir(parents=True, exist_ok=True)


def apply_post_process(target_path: Path, post_process: str, project_name: str) -> None:
    """Apply optional post-processing transformation after file copy."""
    if post_process == "none":
        return

    if post_process == "replace_first_heading_with_project_name":
        content = target_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = f"# {project_name}"
        if lines and lines[0].startswith("# "):
            lines[0] = title
            target_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            target_path.write_text(f"{title}\n\n{content}", encoding="utf-8")
        return

    fail(f"Unsupported post_process '{post_process}'.")


def apply_file_rules(project_path: Path, file_rules, context: dict):
    """Apply file generation rules from configuration."""
    generated_targets = []
    seen_targets = set()

    for rule in file_rules:
        if not rule["enabled"]:
            continue

        source_rel = render_template_string(
            rule["source_template"], context, f"source for file rule '{rule['id']}'"
        )
        target_rel = render_template_string(
            rule["target_template"], context, f"target for file rule '{rule['id']}'"
        )
        source_rel = normalize_relative_path(
            source_rel, f"source path for file rule '{rule['id']}'"
        )
        target_rel = normalize_relative_path(
            target_rel, f"target path for file rule '{rule['id']}'"
        )

        if target_rel in seen_targets:
            fail(f"Configuration has duplicate generated target path: '{target_rel}'.")
        seen_targets.add(target_rel)

        source = resolve_artifact(source_rel)
        target = project_path / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if rule["executable"]:
            target.chmod(target.stat().st_mode | 0o111)
        apply_post_process(target, rule["post_process"], context["project_name"])
        generated_targets.append(target_rel)

    return generated_targets


def add_gitkeep_for_empty_folders(project_path: Path, folders) -> None:
    """Add .gitkeep only to folders that remained empty."""
    for folder in folders:
        folder_path = project_path / folder
        if folder_path.exists() and folder_path.is_dir() and not any(folder_path.iterdir()):
            (folder_path / ".gitkeep").touch()


def create_virtual_env(project_path: Path, create_venv: bool) -> None:
    """Create root Python virtual environment when requested."""
    if not create_venv:
        return
    result = subprocess.run(["python3", "-m", "venv", "venv"], cwd=project_path, check=False)
    if result.returncode != 0:
        print("WARNING: Failed to create venv in project root.")


def install_dependencies(project_path: Path, install_deps: bool, generated_files) -> None:
    """Install baseline dependencies when requested."""
    if not install_deps:
        return

    subprocess.run(["python3", "-m", "ensurepip", "--upgrade"], cwd=project_path, check=False)
    print("Basic dependency installation requested.")
    if "setup.sh" in generated_files:
        print("Run './setup.sh' inside the new project to finish component-specific setup.")


def initialize_git(project_path: Path, use_git: bool) -> None:
    """Initialize git repository when requested."""
    if not use_git:
        return

    subprocess.run(["git", "init"], cwd=project_path, check=False)
    subprocess.run(["git", "add", "."], cwd=project_path, check=False)
    commit = subprocess.run(
        ["git", "commit", "-m", "Initial project structure"],
        cwd=project_path,
        check=False,
        capture_output=True,
        text=True,
    )
    if commit.returncode != 0:
        print("WARNING: Initial git commit was skipped (likely missing git user.name/user.email).")


def setup_docs_venv(project_path: Path, runtime_settings: dict) -> None:
    """Create docs venv if enabled in configuration runtime settings."""
    if not runtime_settings.get("setup_docs_venv", False):
        return

    venv_rel = runtime_settings.get("docs_venv_path", "Automation/docs_venv")
    venv_path = project_path / venv_rel
    print(f"Setting up documentation build environment at '{venv_rel}'...")

    create = subprocess.run(["python3", "-m", "venv", str(venv_path)], check=False)
    if create.returncode != 0:
        print(f"WARNING: Failed to create docs venv at '{venv_rel}'.")
        return

    pip_path = venv_path / "bin" / "pip"
    if not pip_path.exists():
        print("WARNING: docs venv created without pip executable.")
        return

    for package in runtime_settings.get("docs_packages", []):
        print(f"Installing {package} in docs venv...")
        install = subprocess.run([str(pip_path), "install", package], check=False)
        if install.returncode != 0:
            print(f"WARNING: Failed to install {package} in docs venv.")


def main() -> None:
    available_configurations = load_available_configurations()
    config = get_user_input(available_configurations)

    base_path = Path(config["target_dir"]).expanduser()
    base_path.mkdir(parents=True, exist_ok=True)

    project_path = base_path / config["project_name"]
    if project_path.exists():
        fail(f"Directory '{config['project_name']}' already exists. Choose another project name.")
    project_path.mkdir()

    selected = config["selected_configuration"]
    folders = selected["folders"]
    file_rules = selected["files"]
    runtime = selected["runtime"]
    behavior = selected["behavior"]

    create_folders(project_path, folders)

    context = {
        "lang": config["language"],
        "lang_folder": LANG_TO_FOLDER.get(config["language"], "eng"),
        "project_name": config["project_name"],
    }
    generated_files = apply_file_rules(project_path, file_rules, context)

    if behavior.get("add_gitkeep_to_empty_folders", True):
        add_gitkeep_for_empty_folders(project_path, folders)

    setup_docs_venv(project_path, runtime)
    create_virtual_env(project_path, config["create_venv"])
    install_dependencies(project_path, config["install_deps"], generated_files)
    initialize_git(project_path, config["use_git"])

    print(f"\nProject '{config['project_name']}' created successfully!")
    print(f"Configuration used: {selected['name']} ({selected['id']})")
    print(f"Configuration file: configurations/{selected['relative_path']}")
    print(f"Folders created: {len(folders)}")
    print(f"Files generated: {len(generated_files)}")
    print(f"Navigate to '{config['project_name']}' to get started.")
    if config["create_venv"]:
        print("Root virtual environment created in venv/.")
    if config["use_git"]:
        print("Git repository initialized.")


if __name__ == "__main__":
    main()
