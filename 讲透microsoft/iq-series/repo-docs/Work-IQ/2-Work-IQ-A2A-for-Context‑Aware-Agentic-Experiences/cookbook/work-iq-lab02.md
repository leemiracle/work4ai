# Lab 02: A2A for Context‑Aware, Agentic Experiences

## Understanding A2A

A2A (Agent2Agent) is an open protocol that gives AI agents a common language to discover each other, exchange messages, and collaborate across different frameworks and vendors. Instead of treating another agent like a simple tool call, A2A allows true agent-to-agent interaction, including multi-turn conversations, delegation, and bidirectional workflows.

In practice, the flow is: discover an agent through its agent card, authenticate, send a request, and optionally stream task updates/results for long-running work. A2A is designed to be secure and enterprise-ready (HTTPS, standard auth patterns, opaque execution), while supporting rich modalities beyond plain text.

A2A and MCP are complementary:

- MCP standardizes how an agent connects to tools, APIs, and data sources (agent-to-tool).
- A2A standardizes how agents communicate with other agents (agent-to-agent).

Think of MCP as how an agent uses capabilities, and A2A as how agents collaborate with each other to solve more complex end-to-end tasks.

In this lab you are going to learn how to leverage Work IQ via A2A.

## Start Work IQ CLI in A2A Server mode

You can run the following scripts directly from a terminal session, for example using the PowerShell terminal or the Bash terminal, depending on the platform where you are running this cookbook.

Run the following command, to accept the end user license agreement, if you haven't done it yet:

```
workiq accept-eula
```

Now run the following command to start the A2A Server mode:

```
workiq a2aserver
```

You can see a message informing you that the "Work IQ A2A Server started at http://localhost:5100".
There is also a message like "Agent card available at: http://localhost:5100/.well-known/agent-card.json".
Copy the URL of the agent card into your clipboard.

## Consume Work IQ via A2A

Check that the A2A Inspector tool is up and running, accordingly to the prerequisites described in the [Episode 2 README](../README.md).
Open a browser and navigate to the URL of the A2A Inspector. The A2A Inspector URL should be [http://127.0.0.1:5001](http://127.0.0.1:5001) when running A2A Inspector locally, or [http://127.0.0.1:8080](http://127.0.0.1:8080) when running it from a Docker container.


Once the A2A Inspector tool renders in your browser, paste the agent card URL into the text field at the top of the inspector page and select the **Connect** button.

![The user interface of the A2A Inspector. At the top there is a textbox to paste the URL of the agent card.](../../../images/work-iq/a2a-inspector-ui.png)

The A2A Inspector will connect to your locally running Work IQ A2A Server. In the terminal window where you are running the Work IQ CLI, you can see the tracing of the requests made by the A2A Inspector. In the interface of the A2A Inspector you can see the agent card downloaded and validated in the **Agent Card** section.

The agent card looks like the following JSON.

```JSON
{
  "additionalInterfaces": [],
  "capabilities": {
    "extensions": [],
    "pushNotifications": false,
    "stateTransitionHistory": false,
    "streaming": true
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "description": "Relays messages to Microsoft 365 Copilot via REST or A2A protocol",
  "name": "Work IQ Relay Agent",
  "preferredTransport": "JSONRPC",
  "protocolVersion": "0.3.0",
  "skills": [
    {
      "description": "Ask a question to Microsoft 365 Copilot for information about emails, meetings, files, and other M365 data.",
      "examples": [
        "What meetings do I have today?",
        "Summarize my recent emails from my manager",
        "Find documents about the quarterly report"
      ],
      "id": "ask_work_iq",
      "inputModes": [
        "text/plain"
      ],
      "name": "Ask Work IQ",
      "outputModes": [
        "text/plain"
      ],
      "tags": [
        "m365",
        "copilot",
        "email",
        "meetings",
        "files"
      ]
    }
  ],
  "supportsAuthenticatedExtendedCard": false,
  "url": "http://localhost:5100/",
  "version": "1.0.0"
}
```

The agent card document describes the A2A server and provides the following information:

- **Identity**: name, description, and version of the agent
- **Service Endpoint**: the URL of the agent endpoint as well as the protocol type and version supported by the remote agent 
- **A2A Capabilities**: the list of supported A2A features like streaming, state transition history, etc.
- **Authentication**: the authentication requirements to consume the agent
- **Skills**: what the agent can do for you as well as what kind of media types the agent supports like natural language, typed responses, etc.

Now scroll down in the A2A Inspector page and type the following prompt in the last textbox of the page and select the **Send** command to send the prompt to the target agent. 

```
Who am I? What is my role in the company?
```

Notice that, since the Work IQ A2A server supports streaming, you will see streaming response at first. Then, when the response is ready you will get back information about who you are in your own Microsoft 365 tenant.

Now let's try with the following prompt:

```
When is my next meeting?
```

You will get back detailed information about your next and upcoming meeting, based on your personal agenda in Microsoft 365.
You can also expand the **Session Details** panel and inspect the transport protocol, the input and output modalities of the conversation and the unique ID of the current conversation context.

## Wrap up

As you can see, you can consume Work IQ as a remote agent from any other agent, as long as you have support for the A2A protocol. This option opens plenty of possibilities like consuming Work IQ from almost any agentic platform, getting access to the intelligent layer of Work IQ from any AI solution.

## Where to go next

- **Explore the IQ Series** — Learn about Foundry IQ with [Episode 1: Foundry IQ: Unlocking Knowledge for your Agents](../../../Foundry-IQ/1-Foundry-IQ-Unlocking-Knowledge-for-Agents/).