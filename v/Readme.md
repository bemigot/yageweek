[All "problems" index](https://new.contest.yandex.ru/contests/90998/problems)

## Agents Week Jupyter 1-3

In this homework you will build agents for a small online electronics store
(headphones, earbuds, keyboards, mice, and e-readers).

There are three tasks [i.e. notebooks], each introducing a new architecture:

1. Tool-Calling Agent (*ReAct* loop) - the model searches products and manages
   a shopping cart by calling tools in an iterative ReAct loop. You will write
   docstrings for the tool functions, generate a tool schema with
   `convert_to_openai_tool`, and implement run_shopping_agent - the ReActloop
   that sends messages to the LLM, executes tool calls,
   and returns the final text response.

2. Memory Agent - the agent gains long-term memory (a user profile saved to disk)
   and short-term memory (conversation history), so it remembers preferences
   across sessions and past search results within a session. You will implement
   `load_profile` / `save_profile` for reading and writing a JSON profile,
   define the update_profile tool schema, and implement `run_memory_agent`
   that injects the profile into the system prompt and carries
   conversation history between turns.

3. Multi-Agent System: four specialized agents - Retriever, Pros Analyst,
   Cons Analyst, and Ranker - coordinated by an Orchestrator that delegates work,
   collects results, and produces a final recommendation with honest pros & cons.
   You will implement all four agent classes and the CoordinatorAgent that runs
   them in a chain, passing data through a shared AgentContext.

Detailed instructions, starter code, and open test cases are in the notebook.

Important: all submissions are graded using the `gpt-oss-20b` model.
Use the same model when developing and testing your solutions - this way
the agent's behavior during grading will match what you observe locally.

Look for problem statement and instructions inside the notebook.
Notebook you can find inside Jupyter server in the first task.
