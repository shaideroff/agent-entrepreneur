# Agent Entrepreneur — ChatGPT & Codex Plugin

A Skills-only companion to the Agent Entrepreneur open-source project.

## What it does

The Plugin packages four reusable founder workflows:

1. Business diagnosis
2. Market research
3. Decision evaluation
4. Execution planning and outcome review

It is designed for founders, operators and early-stage teams who need structured analysis rather than generic startup advice.

## Important product boundary

This package contains Skills only. It does not bundle or connect to a hosted MCP server. ChatGPT or Codex supplies model reasoning and any available web, file or data tools. The Plugin itself does not independently browse the web, run named entrepreneur agents, collect customer data or execute external actions.

The separate Python/MCP product remains available from the [main repository](https://github.com/shaideroff/agent-entrepreneur). Its current experience-agent directory includes Preview entries; those entries are not represented here as active autonomous agents.

## Install and test

Use the ChatGPT/Codex Plugin installation flow or add this folder to a local plugin marketplace for development. Review each Skill's trigger conditions and test the positive/negative cases in submission/reviewer-cases.json.

## Release status

This is a release candidate under validation. It is not yet submitted to, approved by, or published in the OpenAI public Plugin Directory. Public submission requires a verified individual or business publisher identity, the required organization submission permission, accurate listing metadata, successful package and Skill checks, required policy attestations, and OpenAI review. OpenAI requires at least five positive and three negative test cases for plugin submissions. This package includes that required 5/3 case set. Because this is Skills-only, it does not include an MCP server endpoint or MCP demo credentials.

## License

Apache-2.0. See the repository LICENSE.
