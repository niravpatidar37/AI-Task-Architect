import os
import json
import logging
from typing import Any, Dict, List, Set
from openai import OpenAI
from dotenv import load_dotenv

# ====================================================
# Environment Setup
# ====================================================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ====================================================
# Function Schema Definition
# ====================================================
n8n_workflow_function: Dict[str, Any] = {
    "name": "generate_n8n_workflow",
    "description": (
        "Convert natural language automation instructions into a valid n8n workflow JSON "
        "that can be directly imported and executed in n8n. "
        "Output must include top-level keys: 'name', 'nodes', and 'connections'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "nodes": {"type": "array", "items": {"type": "object"}},
            "connections": {"type": "object"},
        },
        "required": ["name", "nodes"],
    },
}

# ====================================================
# Helper: JSON Repair via AI
# ====================================================
def repair_json_with_ai(broken_json: str) -> Dict[str, Any]:
    """Attempt to repair malformed JSON output using GPT."""
    try:
        logging.warning("Attempting AI-assisted JSON repair...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a JSON repair engine. "
                        "Return valid, parsable JSON strictly matching n8n workflow format. "
                        "No commentary, no markdown — JSON only."
                    ),
                },
                {"role": "user", "content": broken_json},
            ],
        )
        content = getattr(response.choices[0].message, "content", None)
        if not content or not content.strip():
            raise ValueError("No content returned during JSON repair.")
        return json.loads(content.strip())
    except Exception as e:
        logging.error(f"JSON repair failed: {e}")
        # last-resort minimal scaffold
        return {"name": "AI Generated Workflow", "nodes": [], "connections": {}}

# ====================================================
# Node Ordering (Triggers First)
# ====================================================
def reorder_nodes_for_triggers(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure trigger nodes appear first in the workflow sequence."""
    triggers = [
        n
        for n in nodes
        if any(x in n.get("type", "").lower() for x in ["cron", "webhook", "schedule", "trigger"])
    ]
    others = [n for n in nodes if n not in triggers]
    return triggers + others

# ====================================================
# Connection Inference via AI
# ====================================================
def generate_connections_with_ai(prompt: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ask GPT to infer logical node connections."""
    try:
        logging.info("Inferring node connections with AI...")
        node_names = [n["name"] for n in nodes]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an n8n architect. "
                        "Create a valid 'connections' object linking the provided node list logically. "
                        "Follow the JSON schema from https://docs.n8n.io. "
                        "Return JSON only."
                    ),
                },
                {"role": "user", "content": json.dumps({"prompt": prompt, "nodes": node_names}, indent=2)},
            ],
        )
        content = getattr(response.choices[0].message, "content", None)
        return json.loads(content.strip()) if content and content.strip() else {}
    except Exception as e:
        logging.warning(f"AI connection reasoning failed: {e}")
        return {}

# ====================================================
# AI Self-Validation Layer
# ====================================================
def validate_with_ai(prompt: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
    """Ask GPT to inspect, modernize, and correct unsafe or incomplete workflow logic."""
    try:
        logging.info("Running AI validation and best-practice correction...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior n8n engineer and code reviewer. "
                        "Inspect this workflow JSON for correctness and safety. "
                        "Ensure it follows latest n8n v1+ schema and best practices:\n"
                        "- Code nodes must iterate over `$input.all()` safely and always `return items`.\n"
                        "- Never reference deprecated variables like `$item`, `$node`, or `$input.item`.\n"
                        "- Never assume fixed array indexes or shapes without checking.\n"
                        "- All nodes must have valid `parameters`, `typeVersion`, and `position`.\n"
                        "- Do not hardcode example data or placeholder URLs.\n"
                        "Return only corrected JSON, no explanations."
                    ),
                },
                {"role": "user", "content": json.dumps({"prompt": prompt, "workflow": workflow_json}, indent=2)},
            ],
        )
        content = getattr(response.choices[0].message, "content", "") or ""
        content = content.strip()
        if not content:
            raise ValueError("Validation model returned empty content.")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logging.warning("AI validation returned non-JSON. Attempting repair...")
            return repair_json_with_ai(content)
    except Exception as e:
        logging.warning(f"AI validation failed: {e}")
        return workflow_json

# ====================================================
# Structural Validation Layer
# ====================================================
def ensure_valid_workflow(workflow_json: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Ensure workflow has all mandatory fields and valid connections."""
    name = workflow_json.get("name")
    nodes: List[Dict[str, Any]] = workflow_json.get("nodes", [])

    if not name or not nodes:
        raise ValueError("Missing required workflow fields: 'name' or 'nodes'")

    nodes = reorder_nodes_for_triggers(nodes)

    for i, node in enumerate(nodes):
        node.setdefault("parameters", {})
        node.setdefault("typeVersion", 1)
        node.setdefault("position", [200 + (i * 220), 300])

        # Normalize HTTP Request basics (best practice: explicit responseFormat)
        if node.get("type") == "n8n-nodes-base.httpRequest":
            node["parameters"].setdefault("responseFormat", "json")

    workflow_json.update(
        {
            "nodes": nodes,
            "id": workflow_json.get("id") or f"AI-{abs(hash(prompt)) % 10**8}",
            "active": bool(workflow_json.get("active", False)),
            "tags": workflow_json.get("tags", ["ai-generated"]),
            "settings": {
                "timezone": workflow_json.get("settings", {}).get("timezone", "UTC"),
                "executionOrder": workflow_json.get("settings", {}).get("executionOrder", "sequential"),
                "saveManualExecutions": bool(
                    workflow_json.get("settings", {}).get("saveManualExecutions", True)
                ),
            },
        }
    )

    # Connections
    connections = workflow_json.get("connections", {})
    if not isinstance(connections, dict) or not connections:
        connections = generate_connections_with_ai(prompt, nodes)
        if not connections:
            node_names = [n["name"] for n in nodes]
            connections = {
                node_names[i]: {"main": [[{"node": node_names[i + 1], "type": "main", "index": 0}]]}
                for i in range(len(node_names) - 1)
            }
            logging.info(f"Fallback sequential connections: {' → '.join(node_names)}")

    # Sanitize connections (remove unknown nodes and simple cycles)
    connections = sanitize_connections(connections, nodes) # type: ignore
    workflow_json["connections"] = connections
    return workflow_json

def sanitize_connections(connections: Dict[str, Any], nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Remove edges pointing to unknown nodes and break simple back-edges (cycles)."""
    valid_names: Set[str] = {n["name"] for n in nodes}
    out: Dict[str, Any] = {}

    for src, edges in connections.items():
        if src not in valid_names:
            continue
        main = edges.get("main", [])
        clean_main = []
        for branch in main:
            clean_branch = []
            for link in branch:
                dst = link.get("node")
                if dst in valid_names and dst != src:
                    clean_branch.append(link) # type: ignore
            if clean_branch:
                clean_main.append(clean_branch) # type: ignore
        if clean_main:
            out[src] = {"main": clean_main}

    # break trivial cycles (A->B and B->A) by removing back edge
    for src, edges in list(out.items()):
        for branch in edges.get("main", []):
            for link in branch:
                dst = link.get("node")
                if dst in out:
                    # does dst link back to src?
                    for b2 in out[dst].get("main", []):
                        if any(l2.get("node") == src for l2 in b2):
                            logging.info(f"Removing back-edge {dst} -> {src} to avoid cycle")
                            # remove the back edge
                            out[dst]["main"] = [
                                [l2 for l2 in bb if l2.get("node") != src] for bb in out[dst]["main"]
                            ]

    return out

# ====================================================
# Dynamic JavaScript Generator for Code Nodes
# ====================================================
def generate_code_node_js(prompt: str, node: Dict[str, Any], prev_node: Dict[str, Any]) -> str:
    """Ask GPT to generate clean, context-aware JavaScript for Code nodes."""
    logging.info(f"Generating dynamic JS for Code node '{node.get('name')}' based on prior context...")
    try:
        prev_context = json.dumps(prev_node.get("parameters", {}), indent=2)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert n8n automation developer. "
                        "Generate only JavaScript code for a modern n8n Code node. "
                        "Best practices:\n"
                        "- Begin with `const items = $input.all();`\n"
                        "- Safely read/transform `items` based on prior node context\n"
                        "- Prefer functional patterns (map/filter) when appropriate\n"
                        "- Use optional chaining; avoid assumptions about shape\n"
                        "- End with `return <arrayOfItems>;`\n"
                        "- Do NOT output markdown or explanations — JS only."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Prompt: {prompt}\n\n"
                        f"Previous node parameters:\n{prev_context}\n\n"
                        "Write the JS for this Code node now."
                    ),
                },
            ],
        )
        js_code = getattr(response.choices[0].message, "content", "").strip()
        if not js_code:
            raise ValueError("Empty JS content generated.")

        # Minimal safety rails: ensure it returns items and uses $input.all()
        if "return" not in js_code or "$input.all()" not in js_code:
            js_code = (
                "const items = $input.all();\n"
                "// Generated fallback: pass-through\n"
                "return items;"
            )
        return js_code
    except Exception as e:
        logging.warning(f"Dynamic JS generation failed: {e}")
        return "const items = $input.all();\nreturn items;"

# ====================================================
# Code Node Normalization & Modernization
# ====================================================
def looks_like_json_string(s: str) -> bool:
    s2 = (s or "").strip()
    if not s2:
        return False
    if not ((s2.startswith("{") and s2.endswith("}")) or (s2.startswith("[") and s2.endswith("]"))):
        return False
    try:
        json.loads(s2)
        return True
    except Exception:
        return False

def modernize_code_nodes(workflow_json: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Ensure all Code nodes use modern API and AI-generated JavaScript logic."""
    nodes = workflow_json.get("nodes", [])
    updated = False

    for idx, node in enumerate(nodes):
        node_type = node.get("type", "").lower()
        if "function" in node_type or "code" in node_type:
            # Force modern Code node type
            if node_type != "n8n-nodes-base.code":
                node["type"] = "n8n-nodes-base.code"
                updated = True

            params = node.setdefault("parameters", {})
            # Normalize key name to jsCode; migrate from functionCode/code if present
            js_code = params.get("jsCode") or params.get("functionCode") or params.get("code") or ""
            if "functionCode" in params:
                del params["functionCode"]
            if "code" in params:
                del params["code"]

            # n8n best practice: set language explicitly
            params.setdefault("language", "JavaScript")

            # If jsCode accidentally contains JSON (e.g., whole workflow dumped), replace via GPT
            if looks_like_json_string(js_code):
                logging.info(f"Code node '{node.get('name')}' had JSON in jsCode — regenerating dynamically.")
                js_code = ""

            # If legacy tokens or empty, generate dynamic JS using context
            legacy = any(t in js_code for t in ["$json", "$input.item", "$item", "[0].json"])
            if legacy or not js_code.strip():
                prev_node = nodes[idx - 1] if idx > 0 else {}
                js_code = generate_code_node_js(prompt, node, prev_node) # type: ignore
                updated = True

            # Ensure it ends with returning an array
            if "return" not in js_code:
                js_code += "\nreturn $input.all();"

            params["jsCode"] = js_code
            node["parameters"] = params

    if updated:
        workflow_json["nodes"] = nodes
        logging.info("Code nodes dynamically updated using AI-generated, context-aware logic.")
    return workflow_json

# ====================================================
# Lint Pass for Code Nodes (optionally round-trip via AI)
# ====================================================
def lint_code_nodes(workflow_json: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Detect and auto-refactor legacy or unsafe Code node patterns."""
    bad_tokens = ("$input.item", "$item", "[0].json")
    nodes = workflow_json.get("nodes", [])

    for node in nodes:
        node_type = node.get("type", "")
        if node_type in ("n8n-nodes-base.code", "n8n-nodes-base.function"):
            code = node.get("parameters", {}).get("jsCode") or node.get("parameters", {}).get("code", "")
            if looks_like_json_string(code) or any(bad in code for bad in bad_tokens):
                logging.info("Legacy Code syntax or invalid jsCode detected — sending for AI refactor...")
                return validate_with_ai(prompt, workflow_json)
    return workflow_json

# ====================================================
# Main Workflow Generator
# ====================================================
def generate_workflow(prompt: str) -> Dict[str, Any]:
    """Generate an importable, executable n8n workflow dynamically via GPT-4o."""
    try:
        logging.info(f"🤖 Generating workflow for prompt: {prompt[:100]}")

        # Step 1: Generate base workflow
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an elite n8n automation engineer. "
                        "Generate a runnable, production-grade n8n workflow JSON. "
                        "Ensure full schema compliance and logical node order. "
                        "Code nodes must follow the modern API and be safe.\n"
                        "Return JSON only — no text."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            functions=[n8n_workflow_function],  # type: ignore
            function_call={"name": "generate_n8n_workflow"},
        )

        fc = getattr(response.choices[0].message, "function_call", None)
        raw_args = getattr(fc, "arguments", "").strip() if fc else ""
        if not raw_args:
            logging.warning("No structured arguments returned. Falling back to raw content.")
            raw_args = getattr(response.choices[0].message, "content", "").strip()

        # Step 2: Parse & repair JSON if needed
        try:
            workflow_json = json.loads(raw_args) if raw_args else {}
        except json.JSONDecodeError:
            logging.warning("Invalid JSON, invoking repair...")
            workflow_json = repair_json_with_ai(raw_args or "{}")

        # Step 3: Validate structure
        try:
            validated = ensure_valid_workflow(workflow_json, prompt)
        except ValueError as ve:
            logging.warning(f"Structure incomplete ({ve}). Rebuilding via AI...")
            repair_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an n8n architect. "
                            "Rebuild a valid workflow JSON including 'name', 'nodes', and 'connections'. "
                            "Each node must include name, type, parameters, typeVersion, and position. "
                            "Return JSON only."
                        ),
                    },
                    {"role": "user", "content": json.dumps({"prompt": prompt, "partial": workflow_json}, indent=2)},
                ],
            )
            repair_content = getattr(repair_response.choices[0].message, "content", "") or ""
            if not repair_content.strip():
                workflow_json = {"name": "AI Generated Workflow", "nodes": [], "connections": {}}
            else:
                try:
                    workflow_json = json.loads(repair_content.strip())
                except json.JSONDecodeError:
                    workflow_json = repair_json_with_ai(repair_content)
            validated = ensure_valid_workflow(workflow_json, prompt)  # type: ignore

        # Step 4: AI validation + modernization
        enhanced = validate_with_ai(prompt, validated)
        enhanced = lint_code_nodes(enhanced, prompt)
        enhanced = modernize_code_nodes(enhanced, prompt)

        logging.info(f"✅ Workflow generated successfully: {enhanced.get('name', 'Unnamed Workflow')}")
        return enhanced

    except Exception as e:
        logging.error(f"Workflow generation failed: {e}")
        raise RuntimeError(f"Workflow generation failed: {e}") from e
