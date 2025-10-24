import os
import json
import logging
from typing import Any, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# --- Function schema for OpenAI ---
n8n_workflow_function: Dict[str, Any] = {
    "name": "generate_n8n_workflow",
    "description": (
        "Convert natural language automation instructions into a valid n8n workflow JSON "
        "that can be directly imported into n8n. "
        "The output must include top-level keys: 'name', 'nodes', and 'connections'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "nodes": {"type": "array", "items": {"type": "object"}},
            "connections": {"type": "object"}
        },
        "required": ["name", "nodes"]
    }
}

def repair_json_with_ai(broken_json: str) -> Dict[str, Any]:
    try:
        logging.warning("Attempting AI-assisted JSON repair...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Fix and return only valid JSON. Do not explain anything."
                },
                {"role": "user", "content": broken_json},
            ],
        )
        content = getattr(response.choices[0].message, "content", None)
        if not content:
            raise ValueError("No content returned during JSON repair.")
        return json.loads(content.strip())
    except Exception as e:
        logging.error(f"JSON repair failed: {e}")
        raise


# --- Utility: Identify trigger nodes (to reorder workflow correctly) ---
def reorder_nodes_for_triggers(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    triggers = [n for n in nodes if "cron" in n["type"] or "webhook" in n["type"]]
    others = [n for n in nodes if n not in triggers]
    return triggers + others


# --- AI fallback: infer logical connections ---
def generate_connections_with_ai(prompt: str, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        logging.info("🧠 Asking AI to infer logical connections...")
        node_names = [n["name"] for n in nodes]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an n8n workflow architect. "
                        "Return a JSON object defining logical 'connections' between nodes "
                        "based on their order and task purpose. Use n8n's connection format. "
                        "Example: { 'Cron': { 'main': [[{ 'node': 'Google Sheets', 'type': 'main', 'index': 0 }]] } }"
                    ),
                },
                {"role": "user", "content": json.dumps({"prompt": prompt, "nodes": node_names}, indent=2)},
            ],
        )
        content = getattr(response.choices[0].message, "content", None)
        if not content:
            raise ValueError("Empty connection data.")
        return json.loads(content.strip())
    except Exception as e:
        logging.warning(f"AI connection reasoning failed: {e}")
        return {}


# --- Core validation & enrichment ---
def ensure_valid_workflow(workflow_json: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    name = workflow_json.get("name")
    nodes: List[Dict[str, Any]] = workflow_json.get("nodes", [])

    if not name or not nodes:
        raise ValueError("Missing required workflow fields: 'name' or 'nodes'")

    # Sort nodes: triggers first
    nodes = reorder_nodes_for_triggers(nodes)

    # Enrich nodes with realistic defaults if not provided
    for i, node in enumerate(nodes):
        node.setdefault("parameters", {})
        node.setdefault("typeVersion", 1)
        node.setdefault("position", [200 + (i * 220), 300])

        # Intelligent enrichment
        if "cron" in node["type"]:
            node["parameters"].setdefault("triggerTimes", [{"mode": "everyDay", "hour": 9, "minute": 0}])
        elif "googleSheets" in node["type"]:
            node["parameters"].setdefault("operation", "read")
            node["parameters"].setdefault("sheetName", "Team Updates")
            node["parameters"].setdefault("range", "A:B")
        elif "openai" in node["type"]:
            node["parameters"].setdefault("operation", "chat")
            node["parameters"].setdefault("model", "gpt-4o-mini")
            node["parameters"].setdefault(
                "text",
                "={{'Summarize the following updates: ' + JSON.stringify($json)}}"
            )
        elif "slack" in node["type"]:
            node["parameters"].setdefault("operation", "post")
            node["parameters"].setdefault("channel", "#daily-summary")
            node["parameters"].setdefault("text", "={{$json.text || 'Summary generated successfully.'}}")

    # Add metadata
    workflow_json["nodes"] = nodes
    workflow_json.setdefault("id", f"AI-Generated-{abs(hash(prompt)) % 10**8}")
    workflow_json.setdefault("active", False)
    workflow_json.setdefault("tags", ["ai-generated", "auto"])
    workflow_json.setdefault(
        "settings",
        {"timezone": "UTC", "executionOrder": "sequential", "saveManualExecutions": True},
    )

    # --- Handle connections ---
    connections = workflow_json.get("connections", {})
    if not isinstance(connections, dict) or not connections:
        connections = generate_connections_with_ai(prompt, nodes)

    # Fallback: linear connections
    if not connections:
        node_names = [n["name"] for n in nodes]
        connections = {
            node_names[i]: {
                "main": [[{"node": node_names[i + 1], "type": "main", "index": 0}]]
            }
            for i in range(len(node_names) - 1)
        }
        logging.info(f"🔗 Fallback sequential connections: {' → '.join(node_names)}")

    workflow_json["connections"] = connections
    return workflow_json


# --- Workflow generator entrypoint ---
def generate_workflow(prompt: str) -> Dict[str, Any]:
    """
    Generate a fully structured, importable n8n workflow JSON.
    Falls back to a plain JSON generation prompt if function_call fails.
    """
    try:
        logging.info(f"🤖 Generating workflow for: {prompt[:100]}...")

        # --- Primary structured call using function schema ---
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert automation architect. "
                        "Generate a valid n8n workflow JSON that includes "
                        "the following top-level keys: name, nodes, connections. "
                        "Ensure the workflow is valid for import into n8n."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            functions=[n8n_workflow_function], # type: ignore
            function_call={"name": "generate_n8n_workflow"},
        )

        fc = getattr(response.choices[0].message, "function_call", None)
        raw_args = getattr(fc, "arguments", "").strip() if fc else ""

        if not raw_args:
            logging.warning("⚠️ No structured arguments returned. Falling back to natural JSON.")
            raw_args = getattr(response.choices[0].message, "content", "").strip()

        # --- Step 2: Parse JSON output ---
        try:
            if not raw_args:
                raise ValueError("Empty response from OpenAI.")
            workflow_json = json.loads(raw_args)
        except (json.JSONDecodeError, ValueError) as e:
            logging.warning(f"⚠️ JSON parsing failed ({e}). Attempting AI repair...")
            workflow_json = repair_json_with_ai(raw_args)

        # --- Step 3: Validate structure ---
        if "name" not in workflow_json or "nodes" not in workflow_json:
            logging.warning("⚠️ Incomplete workflow returned. Retrying with fallback...")

            response2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an n8n workflow generator. "
                            "Always output valid JSON with fields: name, nodes, connections. "
                            "Ensure nodes have parameters, name, type, typeVersion, position. "
                            "Return only the JSON, no explanation or markdown."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            fallback_content = getattr(response2.choices[0].message, "content", "").strip()
            logging.debug(f"[Fallback] Raw content: {fallback_content!r}")

            if not fallback_content:
                raise ValueError("Fallback OpenAI response was empty.")

            workflow_json = json.loads(fallback_content)

        # --- Step 4: Final validation and enrichment ---
        validated = ensure_valid_workflow(workflow_json, prompt)
        logging.info(f"✅ Workflow generated successfully: {validated['name']}")
        return validated

    except Exception as e:
        logging.error(f"❌ Workflow generation failed: {str(e)}")
        raise RuntimeError(f"Workflow generation failed: {str(e)}") from e

