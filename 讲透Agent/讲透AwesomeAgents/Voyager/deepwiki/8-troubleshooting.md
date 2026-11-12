<!-- source: DeepWiki mcp.deepwiki.com · repo MineDojo/Voyager · page 8 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [FAQ.md](FAQ.md)
- [installation/fabric_mods_install.md](installation/fabric_mods_install.md)
- [installation/minecraft_instance_install.md](installation/minecraft_instance_install.md)

</details>



This page provides solutions to common issues encountered when setting up and running Voyager. It covers installation problems, runtime errors, connection issues, and performance considerations. For information about general usage of Voyager, see [Usage and Examples](#7).

## Common Installation Issues

### Minecraft and Fabric Setup

```mermaid
flowchart TD
    A["Installation Problem"] --> B{"Problem Type"}
    B -->|"Fabric Installation"| C["Check Fabric Version"]
    B -->|"Mods Installation"| D["Check Mods Folder"]
    B -->|"Authentication"| E["Check Azure/Launcher Setup"]
    
    C --> C1["Ensure Using Fabric 0.14.18 for MC 1.19"]
    C --> C2["Verify Loader in MC Versions Folder"]
    
    D --> D1["Verify All 5 Required Mods Present"]
    D --> D2["Check Mod Versions Match MC 1.19"]
    
    E --> E1["Azure Login Issues"]
    E --> E2["Official Launcher Issues"]
    
    E1 --> F1["Check Client ID"]
    E1 --> F2["Try Different Redirect URI Type"]
    
    E2 --> G1["Verify LAN World Setup"]
    E2 --> G2["Check Port Configuration"]
```

#### Missing or Incorrect Fabric Version

**Issue**: Voyager fails to connect to Minecraft or cannot find the correct Fabric version.

**Solution**:
1. Ensure you've installed Fabric Loader 0.14.18 for Minecraft 1.19
2. Verify the Fabric version appears in your Minecraft launcher under "Installations"
3. Check that the `version` parameter in your configuration matches exactly: `fabric-loader-0.14.18-1.19`

#### Missing Required Mods

**Issue**: Voyager crashes or behaves unexpectedly due to missing mods.

**Solution**:
1. Verify all 5 required mods are installed in your Minecraft mods folder:
   - Fabric API
   - Mod Menu
   - Complete Config
   - Multi Server Pause
   - Better Respawn
2. Ensure all mods are compatible with Minecraft 1.19
3. For Better Respawn, verify you've compiled it correctly and updated the config file

Sources: [installation/fabric_mods_install.md:1-22]()

### Authentication Problems

#### Azure Login Connection Error

**Issue**: Connection error after clicking on the Azure login link and logging into Microsoft account.

**Solution**:
- This is normal behavior. You'll get a connection refused or 404 error after login
- Copy the new URL from your browser (containing `code=M.C....`) and use it as instructed

#### KeyError: 'access_token' After Copying Link

**Issue**: Error `KeyError: 'access_token'` appears after copying the authentication link.

**Solution**:
1. Try changing the Redirect URI Type from "Public client/native" to "Web" in your Azure app registration
2. If that doesn't work, refer to the [minecraft-launcher-lib tutorial](https://minecraft-launcher-lib.readthedocs.io/en/stable/tutorial/microsoft_login.html)
3. If problems persist, consider using the Minecraft Official Launcher method instead

Sources: [FAQ.md:10-18]()

## Runtime Issues

### Mineflayer Connection Problems

```mermaid
flowchart TD
    A["Mineflayer Connection Error"] --> B{"Error Type"}
    B -->|"Subprocess Mineflayer failed to start"| C["Verify Node.js Setup"]
    B -->|"Port Conflict"| D["Change Server Port"]
    B -->|"Minecraft Connection"| E["Check Minecraft Instance"]
    
    C --> C1["Test Node.js Installation"]
    C --> C2["Check Dependencies"]
    
    D --> D1["Use Different Port"]
    D --> D2["Kill Existing Processes"]
    
    E --> E1["Verify Fabric Running"]
    E --> E2["Check LAN World Settings"]
```

#### Subprocess Mineflayer Failed to Start

**Issue**: Error message `Subprocess Mineflayer failed to start` when launching Voyager.

**Solution**:
1. Verify Node.js installation:
   ```bash
   cd voyager/env/mineflayer
   node index.js
   ```
   You should see "Server started on port {PORT}"
2. Ensure Fabric is installed correctly and selectable in the Minecraft launcher
3. If running multiple Voyager instances, use different ports:
   ```python
   voyager = Voyager(
       server_port=3001,  # default is 3000
       ...
   )
   ```

Sources: [FAQ.md:19-37]()

### Bot Behavior Issues

#### Bot Leaving and Rejoining After Each Task

**Issue**: The bot leaves and rejoins the game after completing each task.

**Solution**:
- This is default behavior to synchronize Mineflayer with Minecraft
- If you want to prevent this, use:
  ```python
  voyager.learn(reset_env=False)
  ```
- Consider increasing `env_wait_ticks` value to give Mineflayer more time to sync

#### Unable to See Bot's First-Person View

**Issue**: Cannot see what the bot is seeing in first-person.

**Solution**:
- This is a limitation of Mineflayer
- For recording bot actions, use [replay-mod](https://www.replaymod.com/)
- Start recording before the bot plays, then come back to render the view later

Sources: [FAQ.md:38-45]()

## LLM Integration Issues

```mermaid
flowchart TD
    A["LLM Integration Issues"] --> B{"Problem Type"}
    B -->|"Performance Problems"| C["GPT-3.5 vs GPT-4"]
    B -->|"Cost Concerns"| D["Cost Management"]
    B -->|"Timeout Issues"| E["Handle API Timeouts"]
    
    C --> C1["Consider Using GPT-4"]
    C --> C2["Reduce Context Length"]
    
    D --> D1["Monitor API Usage"]
    D --> D2["Budget Planning"]
    
    E --> E1["Use Azure Login Method"]
    E --> E2["Check Network Stability"]
```

### Using GPT-3.5 Instead of GPT-4

**Issue**: Considering using GPT-3.5 for cost reasons but concerned about performance.

**Solution**:
- GPT-4 is highly recommended for Voyager
- GPT-3.5 has poorer code quality, reasoning ability, and a more limited context length
- If you must use GPT-3.5, configure with `skill_manager_retrieval_top_k` ≤ 2 to reduce context length

### API Costs and Budget Considerations

**Issue**: Concerns about the cost of running Voyager.

**Solution**:
- Approximately 160 iterations with GPT-4 costs around $50 USD
- Monitor your OpenAI API expenses closely
- When starting Voyager, observe the bot for a while to ensure it completes tasks successfully

Sources: [FAQ.md:48-54]()

## Environment Configuration Issues

```mermaid
flowchart TD
    A["Environment Configuration"] --> B{"Problem Area"}
    B -->|"Minecraft Settings"| C["Minecraft World Setup"]
    B -->|"System Performance"| D["System Requirements"]
    B -->|"Network Issues"| E["Network Configuration"]
    
    C --> C1["Game Mode: Creative"]
    C --> C2["Difficulty: Peaceful"]
    C --> C3["LAN: Allow Cheats ON"]
    
    D --> D1["Check CPU/Memory"]
    D --> D2["Java Version for Mods"]
    
    E --> E1["Firewall Settings"]
    E --> E2["Local Network Accessibility"]
```

### Minecraft World Setup

**Issue**: Voyager cannot interact properly with the Minecraft world.

**Solution**:
1. Ensure your world is set up correctly:
   - Game Mode: Creative
   - Difficulty: Peaceful
2. When using Official Launcher:
   - Ensure "Open to LAN" is enabled
   - "Allow cheats" must be ON
   - Note the port number from the chat log

### Java Version Issues for Mod Compilation

**Issue**: Errors when compiling Better Respawn mod.

**Solution**:
1. You need Java Runtime Environment v17+ to build the Better Respawn mod
2. Some newer JRE versions may cause errors during build
3. If encountering problems, download JRE v17 from the archive link provided in the installation instructions

Sources: [installation/fabric_mods_install.md:10-13](), [installation/minecraft_instance_install.md:35-42]()

## System Diagnosis Flowchart

```mermaid
flowchart TD
    A["Voyager Issue"] --> B{"Installation or Runtime?"}
    
    B -->|"Installation"| C{"Component?"}
    B -->|"Runtime"| D{"Component?"}
    
    C -->|"Minecraft"| C1["Check Minecraft Version (1.19)"]
    C -->|"Fabric"| C2["Verify Fabric Loader (0.14.18)"]
    C -->|"Mods"| C3["Check 5 Required Mods"]
    C -->|"Authentication"| C4["Azure or Official Launcher Setup"]
    
    D -->|"Mineflayer"| D1["Verify Node.js & Connection"]
    D -->|"Agent Behavior"| D2["Check Reset Settings"]
    D -->|"LLM Integration"| D3["API Key & Model Settings"]
    D -->|"Skill System"| D4["Check Skill Library Access"]
    
    C1 --> E["Reinstall/Update Minecraft"]
    C2 --> E
    C3 --> E
    C4 --> E

    D1 --> F["See Specific Error Solutions"]
    D2 --> F
    D3 --> F
    D4 --> F
```

## Component-Specific Troubleshooting

### Voyager Core System Issues

If the Voyager main system is not running correctly, check:

1. Python environment is properly set up with all dependencies
2. OpenAI API key is valid and has sufficient credits
3. Correct model is specified (GPT-4 recommended)
4. System paths are correctly configured

### Agent Subsystem Issues

If specific agents are not functioning properly:

1. **ActionAgent**: Verify JavaScript code generation is working
2. **CurriculumAgent**: Check task proposal and context gathering
3. **CriticAgent**: Ensure task success evaluation is running
4. **SkillManager**: Verify skill storage and retrieval functionality

Sources: [FAQ.md:1-54]()

## Voyager-Minecraft Communication Diagram

```mermaid
sequenceDiagram
    participant V as "Voyager System"
    participant M as "Mineflayer Bridge"
    participant MC as "Minecraft (Fabric)"
    
    Note over V,MC: Common Failure Points
    
    V->>M: Initialize Connection
    
    alt Connection Failure
        M->>V: "Subprocess Mineflayer failed to start"
        Note right of V: Check Node.js installation
        Note right of V: Verify port availability
    end
    
    M->>MC: Connect to Game
    
    alt Authentication Failure
        MC->>M: Authentication Error
        M->>V: Connection Failed
        Note right of V: Check Azure login settings
        Note right of V: Verify Minecraft account
    end
    
    V->>M: Send JavaScript Code
    M->>MC: Execute Commands
    
    alt Execution Failure
        MC->>M: Execution Error
        M->>V: Command Failed
        Note right of V: Check generated code
        Note right of V: Verify mod installation
    end
    
    MC->>M: Return Game Events
    M->>V: Return Observations
    
    alt Sync Issues
        Note over V,MC: Bot may need to rejoin
        V->>M: Reset Connection
        M->>MC: Rejoin Game
    end
```

Sources: [FAQ.md:19-37](), [FAQ.md:38-45]()