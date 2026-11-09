#!/usr/bin/env bash
set -euo pipefail

INSPECTOR="./node_modules/.bin/mcp-inspector"
SERVER_CMD=(python -m agent_entrepreneur.server)
OUTPUT_DIR="${RUNNER_TEMP:-/tmp}/agent-entrepreneur-inspector"
mkdir -p "$OUTPUT_DIR"

"$INSPECTOR" --cli "${SERVER_CMD[@]}" --method tools/list --strict --format json > "$OUTPUT_DIR/tools-list.json"

required_tools=(
  discover_experience_agents
  get_experience_agent_profile
  recommend_experience_agent_council
  prepare_experience_agent_council_work
  prepare_experience_agent_work_packet
  synthesize_experience_agent_council
)
for tool in "${required_tools[@]}"; do
  jq -e --arg name "$tool" '.result.tools | any(.name == $name)' "$OUTPUT_DIR/tools-list.json" > /dev/null
done

run_tool() {
  local name="$1"
  local args="$2"
  "$INSPECTOR" --cli "${SERVER_CMD[@]}" --method tools/call \
    --tool-name "$name" --tool-args-json "$args" --format json \
    > "$OUTPUT_DIR/$name.json"
  jq -e '.result.isError != true' "$OUTPUT_DIR/$name.json" > /dev/null
}

run_tool discover_experience_agents '{"query":"Built from Zero"}'
run_tool get_experience_agent_profile '{"agent_id":"built_from_zero"}'
run_tool recommend_experience_agent_council '{"objective":"Evaluate a constrained founder launch."}'
run_tool prepare_experience_agent_council_work '{"objective":"Evaluate a constrained founder launch."}'
run_tool prepare_experience_agent_work_packet '{"agent_id":"built_from_zero","objective":"Evaluate a constrained founder launch."}'
run_tool synthesize_experience_agent_council '{"objective":"Evaluate a constrained founder launch.","contributions":[{"agent_id":"built_from_zero","recommendations":["Test demand first."]},{"agent_id":"jeff_bezos","recommendations":["Build repeatable mechanisms."]}],"recommendation":"Run a bounded pilot with explicit decision gates."}'

set +e
"$INSPECTOR" --cli "${SERVER_CMD[@]}" --method tools/call \
  --tool-name discover_experience_agents \
  --tool-args-json '{"status":"not-a-valid-status"}' --format json \
  > "$OUTPUT_DIR/invalid-status.json"
invalid_exit=$?
set -e
if [ "$invalid_exit" -ne 5 ]; then
  echo "Expected Inspector tool_is_error exit code 5, received $invalid_exit"
  exit 1
fi
jq -e '.result.isError == true' "$OUTPUT_DIR/invalid-status.json" > /dev/null

echo "MCP Inspector CLI passed: strict tool schema, all six tools, invalid-input rejection."
