from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _decode_tool_payload(result):
    payload = json.loads(result.content[0].text)
    if isinstance(payload, dict) and "result" in payload:
        return payload["result"]
    return payload


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_stdio_transport_exposes_protocol_and_serves_tool_calls(
    tmp_path: Path,
) -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_entrepreneur.server"],
        env={
            **os.environ,
            "AGENT_ENTREPRENEUR_TRANSPORT": "stdio",
            "AGENT_ENTREPRENEUR_DB": str(tmp_path / "stdio-protocol.sqlite3"),
        },
    )
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            assert initialized.serverInfo.name == "Agent Entrepreneur"

            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "understand_business",
                "research_market",
                "analyse_business",
                "evaluate_decision",
                "create_execution_plan",
                "review_outcomes",
                "plan_specialist_workflow",
                "complete_specialist_workflow",
                "resume_specialist_workflow",
                "discover_experience_agents",
                "get_experience_agent_profile",
                "recommend_experience_agent_council",
                "prepare_experience_agent_council_work",
                "synthesize_experience_agent_council",
                "prepare_experience_agent_work_packet",
                "search_entrepreneurs",
                "save_memory",
                "search_memory",
                "delete_memory",
            }

            discovered = await session.call_tool(
                "discover_experience_agents", {"query": "Built from Zero"}
            )
            assert discovered.isError is False
            directory_payload = _decode_tool_payload(discovered)
            assert directory_payload[0]["agent_id"] == "built_from_zero"

            founder_profile = await session.call_tool(
                "get_experience_agent_profile", {"agent_id": "built_from_zero"}
            )
            assert founder_profile.isError is False
            founder_payload = _decode_tool_payload(founder_profile)
            assert founder_payload["dossier"]["agent_id"] == "built_from_zero"

            lead_route = await session.call_tool(
                "recommend_experience_agent_council",
                {"objective": "Evaluate a hyperlocal mobility marketplace."},
            )
            assert lead_route.isError is False
            lead_payload = _decode_tool_payload(lead_route)
            assert "markus_villig" in {
                item["agent_id"] for item in lead_payload["selected_agents"]
            }

            lead_council = await session.call_tool(
                "prepare_experience_agent_council_work",
                {"objective": "Evaluate a hyperlocal mobility marketplace."},
            )
            assert lead_council.isError is False
            lead_council_payload = _decode_tool_payload(lead_council)
            assert "brian_chesky" in lead_council_payload["ready_agent_ids"]
            assert "markus_villig" in lead_council_payload["not_ready_agent_ids"]
            assert lead_council_payload["council_protocol"]

            work_packet = await session.call_tool(
                "prepare_experience_agent_work_packet",
                {"agent_id": "jeff_bezos", "objective": "Assess customer-led scale."},
            )
            assert work_packet.isError is False
            assert _decode_tool_payload(work_packet)["status"] == "preview_work_packet"

            council = await session.call_tool(
                "synthesize_experience_agent_council",
                {
                    "objective": "Should we scale now?",
                    "contributions": [
                        {"agent_id": "built_from_zero", "recommendations": ["Validate demand first."]},
                        {"agent_id": "jeff_bezos", "recommendations": ["Build scalable mechanisms."]},
                    ],
                    "recommendation": "Run a bounded pilot with explicit scale gates.",
                    "challenges": [{
                        "challenger_agent_id": "built_from_zero",
                        "target_agent_id": "jeff_bezos",
                        "challenged_statement": "Build scalable mechanisms.",
                        "rationale": "Repeatable demand has not yet been demonstrated.",
                        "severity": "high",
                    }],
                },
            )
            assert council.isError is False
            council_payload = _decode_tool_payload(council)
            assert council_payload["challenges"][0]["severity"] == "high"

            resources = await session.list_resources()
            assert {str(resource.uri) for resource in resources.resources} == {
                "agent-entrepreneur://knowledge/specialists",
                "agent-entrepreneur://knowledge/entrepreneurs",
            }

            prompts = await session.list_prompts()
            assert {prompt.name for prompt in prompts.prompts} == {
                "business_diagnosis",
                "market_entry_assessment",
                "founder_execution_review",
            }

            invalid_result = await session.call_tool(
                "understand_business",
                {"industry": "software", "geography": "global"},
            )
            assert invalid_result.isError is True

            result = await session.call_tool(
                "understand_business",
                {"name": "Protocol Test Co", "industry": "software", "geography": "global"},
            )
            assert result.isError is False
            assert result.content
            payload = json.loads(result.content[0].text)
            assert payload["business"]["name"] == "Protocol Test Co"
            market_result = await session.call_tool(
                "research_market",
                {
                    "market": "digital banking",
                    "geography": "Brazil",
                    "research_questions": ["What is the competitive structure?"],
                    "supplied_sources": [
                        {
                            "title": "Nubank investor relations",
                            "url": "https://nu.com/en/investors/governance/management-team/",
                            "source_type": "primary",
                            "accessed_at": "2026-11-09",
                        }
                    ],
                },
            )
            assert market_result.isError is False
            market_brief = json.loads(market_result.content[0].text)
            assert len(market_brief["evidence"]) == 1
            assert "not been independently verified" in " ".join(market_brief["findings"])

            plan_result = await session.call_tool(
                "plan_specialist_workflow",
                {"objective": "evaluate pricing", "domains": ["finance"], "max_specialists": 1},
            )
            assert plan_result.isError is False
            plan = json.loads(plan_result.content[0].text)
            assert len(plan["specialists"]) == 1
            specialist_id = plan["specialists"][0]["specialist_id"]

            mismatched_plan = await session.call_tool(
                "complete_specialist_workflow",
                {
                    "workflow_id": plan["workflow_id"],
                    "objective": "evaluate pricing",
                    "domains": ["finance"],
                    "context": "A different context supplied after planning",
                    "max_specialists": 1,
                    "specialist_responses": [
                        {
                            "specialist_id": specialist_id,
                            "findings": [
                                {
                                    "statement": "This must not reuse the original plan.",
                                    "evidence_status": "unverified",
                                }
                            ],
                        }
                    ],
                },
            )
            assert mismatched_plan.isError is True

            completed = await session.call_tool(
                "complete_specialist_workflow",
                {
                    "workflow_id": plan["workflow_id"],
                    "objective": "evaluate pricing",
                    "domains": ["finance"],
                    "max_specialists": 1,
                    "specialist_responses": [
                        {
                            "specialist_id": specialist_id,
                            "findings": [
                                {
                                    "statement": "Pricing needs a paid validation test.",
                                    "evidence_status": "unverified",
                                }
                            ],
                            "recommendations": ["Run a bounded paid pilot."],
                        }
                    ],
                },
            )
            assert completed.isError is False
            workflow = json.loads(completed.content[0].text)
            assert workflow["status"] == "completed"
            assert workflow["steps_completed"] == 1

            interrupted_plan_result = await session.call_tool(
                "plan_specialist_workflow",
                {
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "untrusted_material": ["Supplier brochure: unverified capacity claim"],
                    "max_specialists": 2,
                },
            )
            interrupted_plan = json.loads(interrupted_plan_result.content[0].text)
            assert interrupted_plan["untrusted_material"] == [
                "Supplier brochure: unverified capacity claim"
            ]
            first_specialist, second_specialist = interrupted_plan["specialists"]
            partial = await session.call_tool(
                "complete_specialist_workflow",
                {
                    "workflow_id": interrupted_plan["workflow_id"],
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "untrusted_material": ["Supplier brochure: unverified capacity claim"],
                    "max_specialists": 2,
                    "specialist_responses": [
                        {
                            "specialist_id": first_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "The pilot budget needs a capped downside.",
                                    "evidence_status": "unverified",
                                }
                            ],
                        },
                        {
                            "specialist_id": second_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "Operations capacity is ready.",
                                    "evidence_status": "supported",
                                }
                            ],
                        },
                    ],
                },
            )
            partial_workflow = json.loads(partial.content[0].text)
            assert partial_workflow["status"] == "partial"
            resumed = await session.call_tool(
                "resume_specialist_workflow",
                {
                    "workflow_id": interrupted_plan["workflow_id"],
                    "objective": "validate market entry",
                    "domains": ["finance", "operations"],
                    "context": "A small pilot with limited capital",
                    "untrusted_material": ["Supplier brochure: unverified capacity claim"],
                    "max_specialists": 2,
                    "specialist_responses": [
                        {
                            "specialist_id": second_specialist["specialist_id"],
                            "findings": [
                                {
                                    "statement": "Operations capacity still needs a measured pilot.",
                                    "evidence_status": "unverified",
                                }
                            ],
                        }
                    ],
                },
            )
            assert resumed.isError is False
            assert json.loads(resumed.content[0].text)["status"] == "completed"

            profile_result = await session.call_tool(
                "search_entrepreneurs", {"query": "Canva", "region": "Oceania"}
            )
            assert profile_result.isError is False
            profiles_payload = json.loads(profile_result.content[0].text)
            # MCP SDK versions expose list results as arrays, envelopes, or individual blocks.
            if isinstance(profiles_payload, dict) and "name" in profiles_payload:
                first_profile = profiles_payload
            else:
                profiles = (
                    profiles_payload.get("result", profiles_payload)
                    if isinstance(profiles_payload, dict)
                    else profiles_payload
                )
                assert isinstance(profiles, list)
                assert profiles
                first_profile = profiles[0]
            assert first_profile["name"] == "Melanie Perkins"

            denied_memory = await session.call_tool(
                "save_memory", {"content": "pricing notes", "consent": False}
            )
            assert denied_memory.isError is True
            saved_memory = await session.call_tool(
                "save_memory", {"content": "pricing notes", "consent": True}
            )
            assert saved_memory.isError is False
            memory = json.loads(saved_memory.content[0].text)
            searched_memory = await session.call_tool(
                "search_memory", {"query": "pricing"}
            )
            assert searched_memory.isError is False
            memory_payload = json.loads(searched_memory.content[0].text)
            if isinstance(memory_payload, dict) and "id" in memory_payload:
                first_memory = memory_payload
            else:
                memory_results = (
                    memory_payload.get("result", memory_payload)
                    if isinstance(memory_payload, dict)
                    else memory_payload
                )
                assert isinstance(memory_results, list)
                assert memory_results
                first_memory = memory_results[0]
            assert first_memory["id"] == memory["record_id"]
            deleted_memory = await session.call_tool(
                "delete_memory", {"record_id": memory["record_id"]}
            )
            assert deleted_memory.isError is False
