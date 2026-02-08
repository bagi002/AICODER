#!/usr/bin/env python3
"""
Project setup script driven by static templates in artifacts/.

The script creates a project skeleton and copies all template content from
artifacts instead of generating large file contents inline.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"
LANG_TO_FOLDER = {"en": "eng", "sr": "sr"}


def fail(message: str) -> None:
    """Print an error and exit."""
    print(f"ERROR: {message}")
    sys.exit(1)


def resolve_artifact(relative_path: str) -> Path:
    """Resolve an artifact path and fail if missing."""
    source = ARTIFACTS_DIR / relative_path
    if not source.exists():
        fail(f"Required artifact is missing: {source}")
    return source


def copy_artifact(relative_source: str, destination: Path, executable: bool = False) -> None:
    """Copy one artifact file to destination."""
    source = resolve_artifact(relative_source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if executable:
        destination.chmod(destination.stat().st_mode | 0o111)


def lang_folder(language: str) -> str:
    """Map CLI language option to artifacts folder name."""
    return LANG_TO_FOLDER.get(language, "eng")


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
    except Exception as exc:
        fail(f"Cannot use target directory '{target_dir}': {exc}")

    lang = input("Choose language (en/sr) [en]: ").strip().lower() or "en"
    if lang not in ("en", "sr"):
        lang = "en"

    project_name = input("Enter project name: ").strip()
    if not project_name:
        fail("Project name cannot be empty.")

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
        components = [component.strip() for component in custom.split(",") if component.strip()]
        if not components:
            components = project_types["1"][1]

    create_venv = input("Create Python virtual environment? (y/n): ").strip().lower() == "y"
    use_git = input("Initialize Git repository? (y/n): ").strip().lower() == "y"
    install_deps = (
        input("Install basic dependencies (Python pip, Node.js npm)? (y/n): ").strip().lower() == "y"
    )

    return {
        "project_name": project_name,
        "target_dir": target_dir,
        "language": lang,
        "components": components,
        "project_type": label,
        "create_venv": create_venv,
        "use_git": use_git,
        "install_deps": install_deps,
    }


def create_base_structure(project_path: Path, components) -> None:
    """Create base folders and copy core automation script."""
    folders = [
        ".vscode",
        "Automation",
        "Docs",
        "Docs/requirements",
        "Docs/architecture",
    ] + components

    for folder in folders:
        folder_path = project_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

    copy_artifact("scripts/docs_builder.py", project_path / "Automation" / "docs_builder.py", executable=True)


def add_gitkeep_for_empty_folders(project_path: Path, components) -> None:
    """Add .gitkeep only to folders that remained empty."""
    folders = [
        ".vscode",
        "Automation",
        "Docs",
        "Docs/requirements",
        "Docs/architecture",
    ] + components

    for folder in folders:
        folder_path = project_path / folder
        if folder_path.exists() and folder_path.is_dir() and not any(folder_path.iterdir()):
            (folder_path / ".gitkeep").touch()


def create_vscode_settings(project_path: Path) -> None:
    """Copy editor settings template."""
    copy_artifact(".vscode/settings.json", project_path / ".vscode" / "settings.json")


def create_docs_files(project_path: Path) -> None:
    """Copy requirements and architecture templates."""
    copy_artifact(
        "docs/requirements/high_level_requirements.yaml",
        project_path / "Docs" / "requirements" / "high_level_requirements.yaml",
    )
    copy_artifact(
        "docs/requirements/software_requirements.yaml",
        project_path / "Docs" / "requirements" / "software_requirements.yaml",
    )
    copy_artifact(
        "docs/architecture/runtime_diagram.puml",
        project_path / "Docs" / "architecture" / "runtime_diagram.puml",
    )
    copy_artifact(
        "docs/architecture/class_diagram.puml",
        project_path / "Docs" / "architecture" / "class_diagram.puml",
    )
    copy_artifact(
        "docs/architecture/block_diagram.puml",
        project_path / "Docs" / "architecture" / "block_diagram.puml",
    )


def create_agents_md(project_path: Path, language: str) -> None:
    """Copy AGENTS.md in selected language."""
    folder = lang_folder(language)
    copy_artifact(f"readmes/{folder}/AGENTS.md", project_path / "AGENTS.md")


def create_gitignore(project_path: Path) -> None:
    """Copy .gitignore template."""
    copy_artifact(".gitignore", project_path / ".gitignore")


def create_scripts(project_path: Path) -> None:
    """Copy shell scripts."""
    copy_artifact("scripts/setup.sh", project_path / "setup.sh", executable=True)
    copy_artifact("scripts/start.sh", project_path / "start.sh", executable=True)


def create_automation_readme(project_path: Path, language: str) -> None:
    """Copy Automation/README.md in selected language."""
    folder = lang_folder(language)
    copy_artifact(f"readmes/{folder}/README_Automation.md", project_path / "Automation" / "README.md")


def create_readme(project_path: Path, config) -> None:
    """Copy root README template and set project title."""
    folder = lang_folder(config["language"])
    readme_path = project_path / "README.md"
    copy_artifact(f"readmes/{folder}/README_root.md", readme_path)

    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    title = f"# {config['project_name']}"
    if lines and lines[0].startswith("# "):
        lines[0] = title
        readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        readme_path.write_text(f"{title}\n\n{content}", encoding="utf-8")


def create_virtual_env(project_path: Path, create_venv: bool) -> None:
    """Create root Python virtual environment when requested."""
    if not create_venv:
        return
    result = subprocess.run(["python3", "-m", "venv", "venv"], cwd=project_path, check=False)
    if result.returncode != 0:
        print("WARNING: Failed to create venv in project root.")


def install_dependencies(project_path: Path, install_deps: bool) -> None:
    """Install baseline dependencies when requested."""
    if not install_deps:
        return

    subprocess.run(["python3", "-m", "ensurepip", "--upgrade"], cwd=project_path, check=False)
    print("Basic dependency installation requested.")
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


def create_env_bootstrap_script(project_path: Path) -> None:
    """Copy helper for rebuilding local venvs after clone."""
    copy_artifact(
        "scripts/bootstrap_envs.sh",
        project_path / "Automation" / "bootstrap_envs.sh",
        executable=True,
    )


def setup_docs_venv(project_path: Path) -> None:
    """Create docs_venv and install docs builder dependencies."""
    print("Setting up documentation build environment...")
    venv_path = project_path / "Automation" / "docs_venv"
    create = subprocess.run(["python3", "-m", "venv", str(venv_path)], check=False)
    if create.returncode != 0:
        print("WARNING: Failed to create Automation/docs_venv.")
        return

    pip_path = venv_path / "bin" / "pip"
    if not pip_path.exists():
        print("WARNING: docs_venv created without pip executable.")
        return

    for package in ("pyyaml", "requests"):
        print(f"Installing {package} in docs_venv...")
        install = subprocess.run([str(pip_path), "install", package], check=False)
        if install.returncode != 0:
            print(f"WARNING: Failed to install {package} in docs_venv.")


def validate_artifacts() -> None:
    """Fail fast if mandatory artifacts are missing."""
    required = [
        ".gitignore",
        ".vscode/settings.json",
        "scripts/docs_builder.py",
        "scripts/setup.sh",
        "scripts/start.sh",
        "scripts/bootstrap_envs.sh",
        "docs/requirements/high_level_requirements.yaml",
        "docs/requirements/software_requirements.yaml",
        "docs/architecture/runtime_diagram.puml",
        "docs/architecture/class_diagram.puml",
        "docs/architecture/block_diagram.puml",
        "readmes/eng/AGENTS.md",
        "readmes/eng/README_Automation.md",
        "readmes/eng/README_root.md",
        "readmes/sr/AGENTS.md",
        "readmes/sr/README_Automation.md",
        "readmes/sr/README_root.md",
    ]
    for item in required:
        resolve_artifact(item)


def main() -> None:
    validate_artifacts()
    config = get_user_input()

    base_path = Path(config["target_dir"]).expanduser()
    base_path.mkdir(parents=True, exist_ok=True)

    project_path = base_path / config["project_name"]
    if project_path.exists():
        fail(f"Directory '{config['project_name']}' already exists. Choose another project name.")
    project_path.mkdir()

    create_base_structure(project_path, config["components"])
    create_vscode_settings(project_path)
    create_docs_files(project_path)
    create_agents_md(project_path, config["language"])
    create_gitignore(project_path)
    create_scripts(project_path)
    create_automation_readme(project_path, config["language"])
    create_readme(project_path, config)
    create_env_bootstrap_script(project_path)
    setup_docs_venv(project_path)
    add_gitkeep_for_empty_folders(project_path, config["components"])

    create_virtual_env(project_path, config["create_venv"])
    install_dependencies(project_path, config["install_deps"])
    initialize_git(project_path, config["use_git"])

    print(f"\nProject '{config['project_name']}' created successfully!")
    print(f"Navigate to '{config['project_name']}' to get started.")
    if config["create_venv"]:
        print("Root virtual environment created in venv/.")
    if config["use_git"]:
        print("Git repository initialized.")


if __name__ == "__main__":
    main()
