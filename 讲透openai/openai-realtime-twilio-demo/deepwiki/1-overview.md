<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-realtime-twilio-demo · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides an introduction to the OpenAI Realtime Twilio Demo, a system that integrates OpenAI's Realtime API with Twilio's phone calling capability to create an AI-powered phone calling assistant. For detailed architecture information, see [Architecture](#1.1), and for specific component details, see [System Components](#1.2).

## Purpose and Scope

The OpenAI Realtime Twilio Demo demonstrates how to build an AI calling assistant that can:

- Receive incoming phone calls through Twilio
- Process speech in real-time using OpenAI's Realtime API
- Generate AI responses that are spoken back to the caller
- Display call transcripts in a web interface
- Execute function calls in response to user requests

This overview covers the high-level architecture, component interactions, and call flow, without diving into implementation details that are covered in other sections.

Sources: [README.md:1-4](), [README.md:19-25]()

## System Components

The system consists of two primary applications:

| Component | Description | Purpose |
|-----------|-------------|---------|
| `webapp` | Next.js web application | Frontend for call configuration and transcript display |
| `websocket-server` | Express-based backend | Bridges communication between Twilio, OpenAI, and the frontend |

Additionally, the system relies on:

- **Twilio**: For phone call handling and audio streaming
- **OpenAI Realtime API**: For real-time speech processing and AI responses
- **ngrok**: For exposing the locally running server to the internet

Sources: [README.md:19-25](), [README.md:44-60]()

## System Architecture

### High-Level Architecture Diagram

```mermaid
graph TD
    User(("User")) -->|"Places call"| TwilioPhone["Twilio Phone Number"]
    Admin(("Admin")) -->|"Configures calls"| Webapp["webapp (NextJS)"]
    
    TwilioPhone -->|"Webhook request to /twiml"| WebsocketServer["websocket-server (Express)"]
    WebsocketServer -->|"TwiML response"| TwilioPhone
    
    TwilioPhone <-->|"Bi-directional stream to /call"| WebsocketServer
    WebsocketServer <-->|"Audio/Text"| RealtimeAPI["OpenAI Realtime API"]
    
    WebsocketServer -->|"Transcripts via /logs"| Webapp
    
    Ngrok["ngrok"] -.->|"Exposes"| WebsocketServer
    
    subgraph "LocalEnvironment"
        Webapp
        WebsocketServer
        Ngrok
    end
```

Sources: [README.md:19-44]()

### Code Entity Relationship Diagram

```mermaid
flowchart LR
    User(("User"))
    Admin(("Admin"))
    
    subgraph "TwilioServices"
        TwilioPhone["Phone Service"]
        TwiML["TwiML Handler"]
    end
    
    subgraph "LocalEnvironment"
        subgraph "webapp"
            Frontend["Frontend UI"]
            CallConfig["Call Configuration"]
            Transcripts["Transcripts Display"]
        end
        
        subgraph "websocket-server"
            TwiMLEndpoint["/twiml Endpoint"]
            CallWSEndpoint["/call WebSocket"]
            LogsWSEndpoint["/logs WebSocket"]
            MessageHandler["Message Handler"]
            FunctionCalling["Function Call Handler"]
        end
        
        Ngrok["ngrok Tunnel"]
    end
    
    subgraph "OpenAIServices"
        RealtimeAPI["Realtime API"]
    end
    
    User <-->|"Audio"| TwilioPhone
    Admin -->|"Configures"| CallConfig
    
    TwilioPhone -->|"Request"| Ngrok
    Ngrok -->|"Forward"| TwiMLEndpoint
    TwiMLEndpoint -->|"TwiML"| Ngrok
    Ngrok -->|"Forward"| TwilioPhone
    
    TwilioPhone <-->|"Bi-directional Audio"| Ngrok
    Ngrok <-->|"Forward"| CallWSEndpoint
    
    CallWSEndpoint <-->|"Audio/Text"| MessageHandler
    MessageHandler <-->|"API Calls"| RealtimeAPI
    MessageHandler -->|"Call Transcripts"| LogsWSEndpoint
    LogsWSEndpoint -->|"Transcripts"| Transcripts
```

Sources: [README.md:19-44]()

## Call Lifecycle

The following sequence diagram illustrates the typical flow of an AI-powered phone call:

```mermaid
sequenceDiagram
    participant User as "User"
    participant Twilio as "Twilio"
    participant WS as "websocket-server"
    participant OpenAI as "OpenAI"
    participant Frontend as "webapp"
    
    Frontend ->> WS: "Connect to /logs WebSocket"
    User ->> Twilio: "Place call to Twilio number"
    Twilio ->> WS: "Query /twiml for instructions"
    WS ->> Twilio: "Return TwiML with stream settings"
    Twilio ->> WS: "Open bi-directional stream to /call"
    WS ->> OpenAI: "Connect to Realtime API"
    
    loop "During Call"
        User ->> Twilio: "User speaks"
        Twilio ->> WS: "Forward audio"
        WS ->> OpenAI: "Forward audio"
        OpenAI ->> WS: "AI response"
        WS ->> Twilio: "Forward AI response"
        Twilio ->> User: "Play AI response audio"
        WS ->> Frontend: "Send transcript updates"
    end
    
    User ->> Twilio: "End call"
    Twilio ->> WS: "Close stream"
    WS ->> OpenAI: "Close connection"
```

Sources: [README.md:44-60]()

## Key Components

### WebSocket Server

The WebSocket server is the core of the system, handling bidirectional communication between all components:

| Endpoint | Purpose |
|----------|---------|
| `/twiml` | Returns TwiML instructions to Twilio for handling calls |
| `/call` | WebSocket endpoint for bi-directional audio streaming with Twilio |
| `/logs` | WebSocket endpoint for sending real-time transcripts to the frontend |

For more details on the WebSocket server implementation, see [WebSocket Server](#2).

Sources: [README.md:26-28]()

### Next.js Web Application

The frontend webapp provides a user interface for configuration and monitoring:

| Feature | Purpose |
|---------|---------|
| Call Configuration | Configure Twilio phone numbers and settings |
| Transcript Display | View real-time transcripts of ongoing calls |
| Connection Status | Monitor connection status with the WebSocket server |

For more details on the frontend application, see [Frontend Application](#3).

Sources: [README.md:23-24]()

## TwiML Integration

Twilio uses TwiML (a form of XML) to specify how to handle a phone call. When a call comes in, the system provides TwiML instructions that tell Twilio to start a bi-directional stream with the WebSocket server:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Connected</Say>
  <Connect>
    <Stream url="{{WS_URL}}" />
  </Connect>
  <Say>Disconnected</Say>
</Response>
```

The `{{WS_URL}}` placeholder is replaced with the WebSocket server's endpoint URL.

Sources: [README.md:27-40]()

## Function Calling Support

The system includes support for function calling, allowing the AI assistant to trigger actions during a call. The current implementation includes a mocking mechanism for testing and development purposes.

For more details on function calling, see [Function Calling](#2.4).

Sources: [README.md:61-64]()

## Getting Started

To run the system, you need:

1. OpenAI API key with access to the Realtime API
2. Twilio account with a phone number
3. ngrok account for exposing the local server

The typical setup involves running three separate processes:

| Terminal | Purpose | Command |
|----------|---------|---------|
| 1 | Run the webapp | `npm run dev` |
| 2 | Run the websocket-server | `npm run dev` |
| 3 | Run ngrok | `ngrok http 8081` |

For detailed setup instructions, see [Setup and Deployment](#4).

Sources: [README.md:9-16](), [README.md:66-105]()

## Security Considerations

The repository is provided as a reference implementation and demonstration. As noted in the README, the security practices may not be suitable for production use without additional review and hardening:

> This repo isn't polished, and the security practices leave some to be desired. Please only use this as reference, and make sure to audit your app with security and engineering before deploying!

Sources: [README.md:107-109]()

---

