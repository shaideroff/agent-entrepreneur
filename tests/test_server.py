import importlib
import sys
import types

def test_server_registers_tools_resources_and_prompts(monkeypatch):
    registered = {"tools": [], "resources": [], "prompts": []}
    class FakeFastMCP:
        def __init__(self, *args, **kwargs): self.args, self.kwargs = args, kwargs
        def tool(self): return lambda fn: registered["tools"].append(fn.__name__) or fn
        def resource(self, uri): return lambda fn: registered["resources"].append(uri) or fn
        def prompt(self): return lambda fn: registered["prompts"].append(fn.__name__) or fn
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    fastmcp_module = types.ModuleType("mcp.server.fastmcp")
    fastmcp_module.FastMCP = FakeFastMCP
    monkeypatch.setitem(sys.modules, "mcp", mcp_module)
    monkeypatch.setitem(sys.modules, "mcp.server", server_module)
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fastmcp_module)
    sys.modules.pop("agent_entrepreneur.server", None)
    module = importlib.import_module("agent_entrepreneur.server")
    from pathlib import Path
    from agent_entrepreneur.config import Settings
    module.create_server(Settings(database_path=Path("/tmp/agent-entrepreneur-test.db")))
    assert registered["tools"] == ["understand_business", "research_market", "analyse_business", "evaluate_decision", "create_execution_plan", "review_outcomes", "plan_specialist_workflow", "complete_specialist_workflow", "resume_specialist_workflow", "discover_experience_agents", "get_experience_agent_profile", "recommend_experience_agent_council", "prepare_experience_agent_council_work", "synthesize_experience_agent_council", "prepare_experience_agent_work_packet", "search_entrepreneurs", "save_memory", "search_memory", "delete_memory"]
    assert len(registered["resources"]) == 2
    assert len(registered["prompts"]) == 3
