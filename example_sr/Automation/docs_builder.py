#!/usr/bin/env python3
"""
Documentation Builder Script

This script generates HTML pages from the Docs folder content for easy browsing.
It creates a build folder with index.html and linked pages for requirements and architecture.
"""

import os
import sys
from pathlib import Path

# Check if running in docs_venv, if not, restart in venv
venv_python = Path(__file__).parent / 'docs_venv' / 'bin' / 'python'
if venv_python.exists() and sys.executable != str(venv_python):
    import subprocess
    result = subprocess.run([str(venv_python), __file__], check=False)
    sys.exit(result.returncode)

import yaml
import requests
import shutil
import zlib


def log_warning(message: str):
    print(f"WARNING: {message}")


def log_error(message: str):
    print(f"ERROR: {message}")


def validate_requirement_list(data, label, required_keys, add_error):
    """Validate a requirement YAML list; returns a cleaned list (invalid entries skipped)."""
    if data is None:
        return []
    if not isinstance(data, list):
        add_error(f"{label} YAML must be a list of items.")
        return []

    cleaned = []
    seen_ids = set()
    allowed_status = {"draft", "in progress", "in review", "finished"}

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            add_error(f"{label}[{idx}] must be a mapping/dict.")
            continue

        missing = [k for k in required_keys if k not in item or item[k] in (None, "")]
        if missing:
            add_error(f"{label}[{idx}] missing required fields: {', '.join(missing)}.")
            continue

        item_id = item.get("id")
        if item_id in seen_ids:
            add_error(f"{label} duplicate id '{item_id}'.")
            continue
        seen_ids.add(item_id)

        status = str(item.get("status", "")).lower()
        if status and status not in allowed_status:
            add_error(f"{label} '{item_id}' has unknown status '{item['status']}'.")

        cleaned.append(item)

    return cleaned


def load_yaml(file_path):
    """Load YAML file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        log_error(f"Failed to load YAML '{file_path}': {e}")
        return None


def load_puml(file_path):
    """Load PUML file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log_error(f"Failed to load PUML '{file_path}': {e}")
        return None


def _plantuml_encode(puml_text: str) -> str:
    """Encode PlantUML text using the official deflate + 6-bit algorithm."""
    # Raw DEFLATE (no zlib header) is required; wbits=-15 turns off headers/checksums
    compressor = zlib.compressobj(level=9, wbits=-zlib.MAX_WBITS)
    compressed = compressor.compress(puml_text.encode("utf-8")) + compressor.flush()

    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    encoded_chars = []

    for i in range(0, len(compressed), 3):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0

        encoded_chars.append(alphabet[(b1 >> 2) & 0x3F])
        encoded_chars.append(alphabet[((b1 & 0x03) << 4) | ((b2 >> 4) & 0x0F)])

        if i + 1 < len(compressed):
            encoded_chars.append(alphabet[((b2 & 0x0F) << 2) | ((b3 >> 6) & 0x03)])
        if i + 2 < len(compressed):
            encoded_chars.append(alphabet[b3 & 0x3F])

    return "".join(encoded_chars)


def render_puml_to_svg(puml_text):
    """Render PUML text to SVG using PlantUML server."""
    try:
        if not isinstance(puml_text, str) or not puml_text.strip():
            raise ValueError("PUML source is empty or invalid.")

        encoded = _plantuml_encode(puml_text)
        url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200 and '<svg' in response.text:
            return response.text

        log_warning(
            f"PlantUML render fallback (status={response.status_code}, content-type={response.headers.get('Content-Type')})"
        )

        # Fallback to text view
        return (
            "<div class='puml-fallback'><h4>PlantUML Diagram (Text View)</h4>"
            f"<pre>{puml_text}</pre>"
            "<p>Unable to render. Copy to <a href='https://www.plantuml.com/plantuml/uml' target='_blank'>PlantUML Online Editor</a> to visualize.</p></div>"
        )

    except Exception as e:
        log_warning(f"PlantUML render failed: {e}")
        return (
            "<div class='puml-fallback'><h4>PlantUML Diagram (Text View)</h4>"
            f"<pre>{puml_text}</pre>"
            f"<p>Error: {e}</p></div>"
        )


def generate_html_head(title):
    """Generate HTML head section with improved styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Project Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #000;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        nav {{
            background-color: #f8f9fa;
            padding: 1rem 0;
            border-bottom: 1px solid #e9ecef;
        }}
        nav .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }}
        nav a {{
            margin: 0 1rem;
            text-decoration: none;
            color: #495057;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }}
        nav a:hover {{
            background-color: #007bff;
            color: white;
        }}
        nav .active {{
            background-color: #007bff;
            color: white;
        }}
        main {{
            padding: 2rem;
        }}
        h1, h2, h3 {{
            color: #000;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 2rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
        }}
        h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
        }}
        .requirement {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 5px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .requirement:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .status-draft {{ border-left-color: #ffc107; }}
        .status-in-progress {{ border-left-color: #17a2b8; }}
        .status-in-review {{ border-left-color: #6c757d; }}
        .status-finished {{ border-left-color: #28a745; }}
        
        .status-badge {{
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-left: 0.5rem;
        }}
        .badge-draft {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .badge-in-progress {{ background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .badge-in-review {{ background-color: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; }}
        .badge-finished {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .requirement h3 {{
            color: #495057;
            margin-bottom: 0.5rem;
        }}
        .requirement p {{
            margin-bottom: 0.5rem;
        }}
        .diagram {{
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .diagram svg {{
            max-width: 100%;
            height: auto;
        }}
        .puml-fallback {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 1rem;
            border-radius: 5px;
        }}
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 1rem;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 2rem;
        }}
        .btn {{
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }}
        .btn:hover {{
            background-color: #0056b3;
        }}
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2rem;
            }}
            nav .nav-container {{
                flex-direction: column;
            }}
            nav a {{
                margin: 0.25rem 0;
            }}
            main {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Project Documentation</h1>
            <p>Comprehensive project overview and requirements</p>
        </header>
"""


def generate_html_footer():
    """Generate HTML footer section."""
    return """
        <footer>
            <p>&copy; 2026 Project Documentation. Generated automatically.</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_navigation(current_page):
    """Generate navigation menu."""
    pages = {
        'index': 'Home',
        'architecture': 'Architecture',
        'high_level': 'High-Level Requirements',
        'software': 'Software Requirements'
    }
    nav = '<nav><div class="nav-container">'
    for page, title in pages.items():
        active_class = ' active' if page == current_page else ''
        nav += f'<a href="{page}.html" class="{active_class}">{title}</a>'
    nav += '</div></nav>'
    return nav


def generate_index_html():
    """Generate index.html page."""
    content = f"""
{generate_html_head("Home")}
{generate_navigation('index')}
<main>
    <h1>Welcome to Project Documentation</h1>
    <p>This documentation provides a comprehensive overview of the project, including architecture diagrams, requirements, and implementation details. Use the navigation above to explore different sections.</p>

    <h2>Documentation Sections</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div class="requirement">
            <h3>🏗️ Architecture</h3>
            <p>View system architecture diagrams including runtime, class, and block diagrams.</p>
            <a href="architecture.html" class="btn">View Architecture</a>
        </div>
        <div class="requirement">
            <h3>📋 High-Level Requirements</h3>
            <p>Browse high-level requirements that define the overall project scope.</p>
            <a href="high_level.html" class="btn">View Requirements</a>
        </div>
        <div class="requirement">
            <h3>⚙️ Software Requirements</h3>
            <p>Explore detailed software requirements with implementation status.</p>
            <a href="software.html" class="btn">View Requirements</a>
        </div>
    </div>
</main>
{generate_html_footer()}
"""
    return content


def generate_architecture_html(docs_path):
    """Generate a hub page for architecture diagrams with links to per-diagram pages."""
    content = f"""
{generate_html_head("Architecture")}
{generate_navigation('architecture')}
<main>
    <h1>System Architecture Diagrams</h1>
    <p>Select a diagram to view it on its dedicated page.</p>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div class="requirement">
            <h3>Runtime Diagram</h3>
            <p>Sequence of runtime interactions.</p>
            <a class="btn" href="runtime.html">Open runtime diagram</a>
        </div>
        <div class="requirement">
            <h3>Class Diagram</h3>
            <p>Class structure and relationships.</p>
            <a class="btn" href="class.html">Open class diagram</a>
        </div>
        <div class="requirement">
            <h3>Block Diagram</h3>
            <p>High-level blocks and data flows.</p>
            <a class="btn" href="block.html">Open block diagram</a>
        </div>
    </div>
</main>
{generate_html_footer()}
"""
    return content


def generate_single_diagram_page(docs_path, filename, title, page_slug):
    """Generate a dedicated page for one PlantUML diagram."""
    puml_path = docs_path / 'architecture' / filename
    puml_source = load_puml(puml_path)

    if puml_source is None:
        svg = f"<div class='puml-fallback'><p>Missing or unreadable file: {puml_path.name}</p></div>"
        log_warning(f"Skipping render for missing/invalid PUML: {puml_path}")
    else:
        if "@startuml" not in puml_source or "@enduml" not in puml_source:
            log_warning(f"PUML file may be invalid (missing @startuml/@enduml): {puml_path}")
        svg = render_puml_to_svg(puml_source)

    content = f"""
{generate_html_head(title)}
{generate_navigation('architecture')}
<main>
    <h1>{title}</h1>
    <p>Rendered from {filename}. Edit the PUML file and rebuild docs to refresh.</p>
    <div class="diagram">
        {svg}
    </div>
    <p style="text-align:center; margin-top:1rem;"><a class="btn" href="architecture.html">⬅ Back to Architecture Hub</a></p>
</main>
{generate_html_footer()}
"""
    return content


def generate_requirements_html(requirements_data, title, page_name, links=None):
    """Generate requirements HTML page."""
    if links is None:
        links = {}
    
    if isinstance(requirements_data, str):
        # Error message
        content = f"""
{generate_html_head(title)}
{generate_navigation(page_name)}
<main>
    <h1>{title}</h1>
    <p>{requirements_data}</p>
</main>
{generate_html_footer()}
"""
        return content

    content = f"""
{generate_html_head(title)}
{generate_navigation(page_name)}
<main>
    <h1>{title}</h1>
    <p>This section contains all {title.lower()} with their current status and details.</p>
"""

    for req in requirements_data:
        status = req.get('status', 'draft')
        status_slug = status.lower().replace(' ', '-')
        status_class = f"status-{status_slug}"
        req_id = req['id']
        
        if page_name == 'software':
            refines = req.get('refines', 'N/A')
            refines_link = links.get(f"sw_{req_id}", "#")
            if refines_link != "#":
                refines = f'<a href="{refines_link}">{refines}</a>'
        else:
            refines = req.get('refines', 'N/A')
        
        content += f"""
    <div class="requirement {status_class}" id="{req_id}">
        <h3>{req_id}: {req['name']}</h3>
        <p><strong>Status:</strong> <span class="status-badge badge-{status_slug}">{status}</span></p>
        <p><strong>Refines:</strong> {refines}</p>
        <p><strong>Description:</strong></p>
        <p>{req.get('description', 'N/A').replace('> ', '').strip()}</p>
"""
        
        # For high-level, add list of refining software requirements
        if page_name == 'high_level':
            refining_links = links.get(f"hl_{req_id}", [])
            if refining_links:
                content += "<p><strong>Refined by:</strong></p><ul>"
                for link in refining_links:
                    sw_id = link.split('#')[1]
                    content += f'<li><a href="{link}">{sw_id}</a></li>'
                content += "</ul>"
        
        content += "</div>"

    content += """
</main>
"""
    content += generate_html_footer()
    return content


def build_docs(docs_path):
    """Build HTML documentation from Docs folder."""
    build_path = docs_path / 'build'
    build_path.mkdir(exist_ok=True)

    errors = []

    def add_error(msg):
        errors.append(msg)
        log_error(msg)

    # Load requirements
    hl_req_path = docs_path / 'requirements/high_level_requirements.yaml'
    sw_req_path = docs_path / 'requirements/software_requirements.yaml'

    hl_req_data = load_yaml(hl_req_path)
    sw_req_data = load_yaml(sw_req_path)

    # Validate YAML load results
    if hl_req_data is None:
        add_error(f"Could not load {hl_req_path}")
    if sw_req_data is None:
        add_error(f"Could not load {sw_req_path}")

    # Validate requirement schema
    hl_req_data = validate_requirement_list(
        hl_req_data, "High-level", ["id", "name", "status", "description"], add_error
    )
    sw_req_data = validate_requirement_list(
        sw_req_data, "Software", ["id", "name", "status", "refines", "description"], add_error
    )

    # Build links and detect dangling software requirements
    links = {}
    dangling_sw = []

    if isinstance(hl_req_data, list) and isinstance(sw_req_data, list):
        # Map high-level IDs
        hl_ids = {req['id']: req for req in hl_req_data}
        # For each software req, add link to high-level
        for sw_req in sw_req_data:
            refines = sw_req.get('refines')
            if refines and refines in hl_ids:
                links[f"sw_{sw_req['id']}"] = f"high_level.html#{refines}"
            else:
                dangling_sw.append(sw_req.get('id', '<unknown>'))

        # For each high-level, find software that refines it
        for hl_req in hl_req_data:
            hl_id = hl_req['id']
            refining_sw = [sw['id'] for sw in sw_req_data if sw.get('refines') == hl_id]
            if refining_sw:
                links[f"hl_{hl_id}"] = [f"software.html#{sw_id}" for sw_id in refining_sw]
    else:
        if not isinstance(hl_req_data, list):
            add_error("High-level requirements YAML must be a list of entries.")
        if not isinstance(sw_req_data, list):
            add_error("Software requirements YAML must be a list of entries.")

    # Generate pages
    index_html = generate_index_html()
    architecture_html = generate_architecture_html(docs_path)
    runtime_html = generate_single_diagram_page(docs_path, 'runtime_diagram.puml', 'Runtime Diagram', 'runtime')
    class_html = generate_single_diagram_page(docs_path, 'class_diagram.puml', 'Class Diagram', 'class')
    block_html = generate_single_diagram_page(docs_path, 'block_diagram.puml', 'Block Diagram', 'block')

    high_level_html = generate_requirements_html(hl_req_data, "High-Level Requirements", 'high_level', links)
    software_html = generate_requirements_html(sw_req_data, "Software Requirements", 'software', links)

    # Write files
    (build_path / 'index.html').write_text(index_html, encoding='utf-8')
    (build_path / 'architecture.html').write_text(architecture_html, encoding='utf-8')
    (build_path / 'runtime.html').write_text(runtime_html, encoding='utf-8')
    (build_path / 'class.html').write_text(class_html, encoding='utf-8')
    (build_path / 'block.html').write_text(block_html, encoding='utf-8')
    (build_path / 'high_level.html').write_text(high_level_html, encoding='utf-8')
    (build_path / 'software.html').write_text(software_html, encoding='utf-8')

    if dangling_sw:
        add_error(f"Dangling software requirements (no matching high-level refines): {', '.join(dangling_sw)}")

    if errors:
        print("\nBuild completed with issues:")
        for err in errors:
            print(f" - {err}")
    else:
        print(f"Documentation built successfully in {build_path}")
    print(f"Open {build_path / 'index.html'} in your browser to view the documentation.")


def main():
    # Script is run from Automation folder
    automation_path = Path.cwd()
    project_root = automation_path.parent
    docs_path = project_root / 'Docs'

    if not docs_path.exists():
        print("Docs folder not found. Please run this script from the Automation folder within the project.")
        return

    build_docs(docs_path)


if __name__ == "__main__":
    main()
