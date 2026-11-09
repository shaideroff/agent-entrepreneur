import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";

const dbPath = process.env.AGENT_ENTREPRENEUR_DB;
assert.ok(dbPath, "AGENT_ENTREPRENEUR_DB must point to an isolated test database");

const client = new Client({ name: "agent-entrepreneur-interop-test", version: "1.0.0" });
const transport = new StdioClientTransport({
  command: process.env.PYTHON ?? "python",
  args: ["-m", "agent_entrepreneur.server"],
  env: {
    ...process.env,
    AGENT_ENTREPRENEUR_TRANSPORT: "stdio",
    AGENT_ENTREPRENEUR_DB: dbPath,
  },
});

const requiredTools = [
  "discover_experience_agents",
  "get_experience_agent_profile",
  "recommend_experience_agent_council",
  "prepare_experience_agent_council_work",
  "prepare_experience_agent_work_packet",
  "synthesize_experience_agent_council",
];

try {
  await client.connect(transport);
  const { tools } = await client.listTools();
  const exposed = new Set(tools.map((tool) => tool.name));
  for (const name of requiredTools) assert.ok(exposed.has(name), `Missing MCP tool: ${name}`);

  const calls = [
    ["discover_experience_agents", { query: "Built from Zero" }],
    ["get_experience_agent_profile", { agent_id: "built_from_zero" }],
    ["recommend_experience_agent_council", { objective: "Evaluate a hyperlocal mobility marketplace." }],
    ["prepare_experience_agent_council_work", { objective: "Compare founder-led validation and capital allocation." }],
    ["prepare_experience_agent_work_packet", { agent_id: "jeff_bezos", objective: "Assess customer-led scale." }],
    ["synthesize_experience_agent_council", {
      objective: "Should a founder scale now?",
      contributions: [
        { agent_id: "built_from_zero", recommendations: ["Validate demand first."] },
        { agent_id: "jeff_bezos", recommendations: ["Build scalable mechanisms."] },
      ],
      recommendation: "Run a bounded pilot with explicit scale gates.",
      disagreements: ["The timing of scale remains contested."],
    }],
  ];

  for (const [name, args] of calls) {
    const result = await client.callTool({ name, arguments: args });
    assert.equal(result.isError, false, `${name} returned an MCP tool error`);
    assert.ok(Array.isArray(result.content) && result.content.length > 0, `${name} returned no content`);
  }

  const invalid = await client.callTool({
    name: "discover_experience_agents",
    arguments: { status: "not-a-valid-status" },
  });
  assert.equal(invalid.isError, true, "Invalid status must be returned as a tool error");

  console.log(JSON.stringify({
    client: "@modelcontextprotocol/client",
    clientVersion: "2.4.0",
    transport: "stdio",
    requiredToolsDiscovered: requiredTools.length,
    validToolCalls: calls.length,
    invalidInputRejected: true,
    cleanShutdown: "pending",
  }));
} finally {
  await client.close();
}
