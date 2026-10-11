# AI agents

[`agents.ipynb`](agents.ipynb) builds two LangChain agents and asks them the same questions about the conference:

- The **REST agent** can only use the four REST MCP servers, one for each service.
- The **GraphQL agent** can only use the GraphQL MCP server, which reads the schema and queries the Apollo Router.

Each run prints which tools the agent called. The notebook ends with a table that compares the tool calls,
model calls, tokens and time for every question, followed by both agents' answers.

## Run it

1. Start the main stack and the [MCP servers](../mcp/README.md).
2. Log in to AWS with a profile that has Amazon Bedrock access:

   ```sh
   aws sso login --profile <your AWS profile>
   ```

   The notebook's first cell asks for the profile name.
3. Install dependencies with `uv sync`.
4. Open the [agents.ipynb](./agents.ipynb) and set the kernel to the one located in your .venv created by `uv`.
5. Run the cells in order.

## Questions and saved results

The questions are in the `QUESTIONS` list. The notebook saves each run in `results/<question>/<agent>.json`,
which Git ignores. When you run the notebook again, it reuses the saved results for the same model,
so adding a question runs only the new question.

- To run one question again, delete its folder in `results/`.
- To run every question again, delete the `results/` folder.
