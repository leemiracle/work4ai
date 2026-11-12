# 🌊 Streaming Voice Agent

A real-time voice interaction example using the OpenAI Agents SDK with continuous audio streaming. This demonstrates advanced voice pipeline capabilities with live speech detection, real-time processing, and turn-based conversation management.

## 🎯 What This Demonstrates

- **Real-Time Audio Processing**: Continuous audio input and output streaming
- **Activity Detection**: Automatic detection of speech start/stop
- **Turn Management**: Intelligent conversation turn handling
- **Live Agent Processing**: Real-time agent responses during conversation
- **Interruption Handling**: Lifecycle events for managing conversation flow
- **Streaming Callbacks**: Real-time monitoring and debugging

## 🧠 Core Concept: Streaming Voice Pipeline

The streaming voice pipeline processes audio continuously in real-time. Think of it as a **live conversation assistant** that:

- Continuously listens for audio input
- Automatically detects when you start and stop speaking
- Processes speech in real-time with AI agents
- Streams responses back as they're generated
- Manages conversation turns automatically

```
┌─────────────────────────────────────────────────────────────┐
│                   STREAMING VOICE WORKFLOW                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎤 CONTINUOUS AUDIO INPUT                                  │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    1. REAL-TIME CAPTURE                    │
│  │  STREAMING  │    ◦ Continuous microphone input           │
│  │   AUDIO     │    ◦ Chunk-based processing                │
│  │  RECORDER   │    ◦ Activity detection                    │
│  └─────────────┘                                            │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    2. LIVE TRANSCRIPTION                   │
│  │ STREAMING   │    ◦ Real-time speech-to-text              │
│  │TRANSCRIPTION│    ◦ Turn boundary detection               │
│  └─────────────┘                                            │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    3. CONCURRENT PROCESSING                │
│  │  PARALLEL   │    ◦ Agent workflow execution              │
│  │ AGENT EXEC  │    ◦ Tool calls & handoffs                 │
│  └─────────────┘    ◦ Multiple turns in session             │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    4. STREAMING RESPONSE                   │
│  │  LIVE TTS   │    ◦ Real-time text-to-speech              │
│  │  PLAYBACK   │    ◦ Chunked audio output                  │
│  └─────────────┘    ◦ Immediate response playback           │
│       │                                                     │
│       ▼                                                     │
│  🔊 CONTINUOUS AUDIO OUTPUT                                 │
│                                                             │
│  ↺ LOOP FOR MULTIPLE TURNS                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

1. **Install voice dependencies**:
   ```bash
   pip install 'openai-agents[voice]'
   pip install sounddevice numpy soundfile librosa
   ```

2. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the streaming voice agent**:
   ```bash
   python agent.py
   ```

4. **Start talking**: The agent will automatically detect when you speak and respond in real-time!

## 🧪 What This Example Includes

### **Real-Time Audio Management**
- **StreamedAudioRecorder**: Continuous microphone input with threading
- **AudioPlayer**: Real-time audio playback with stream management
- **Activity Detection**: Automatic speech start/stop detection
- **Turn-Based Processing**: Intelligent conversation management

### **Advanced Agent Capabilities**
- **Multi-Language Support**: English, Spanish, and French agents
- **Enhanced Tools**: Weather, time, reminders, and news
- **Real-Time Handoffs**: Language detection during streaming
- **Session Management**: Multi-turn conversation tracking

### **Streaming Tools**
- `get_weather(city)`: Real-time weather information
- `get_time()`: Current time with live updates
- `set_reminder(message, minutes)`: Demo reminder functionality
- `get_news_summary()`: Mock news updates

### **Advanced Monitoring**
- **StreamingWorkflowCallbacks**: Real-time event monitoring
- **VoiceSessionManager**: Session lifecycle management
- **Turn Tracking**: Conversation analytics and statistics
- **Lifecycle Events**: Turn start/end event handling

## 🎯 Example Interactions

### **Natural Conversation Flow**
- Start speaking → Agent automatically detects speech
- Pause → Agent processes and responds immediately  
- Continue talking → New turn begins automatically
- Multiple turns in single session

### **Real-Time Tool Usage**
- "What's the weather in New York?" → Immediate weather response
- "What time is it?" → Live time information
- "Set a reminder to call Sarah in 15 minutes" → Reminder confirmation
- "Give me a news summary" → Current news update

### **Live Language Switching**
- Speak in English → English agent responds
- Switch to "¿Qué tiempo hace en Madrid?" → Spanish agent takes over
- Switch to "Quelle heure est-il?" → French agent responds
- Seamless language detection and handoffs

## 🔧 Key Implementation Patterns

### **1. Streaming Pipeline Setup**
```python
pipeline = VoicePipeline(
    workflow=SingleAgentVoiceWorkflow(agent, callbacks=StreamingWorkflowCallbacks())
)
```

### **2. Continuous Audio Input**
```python
with StreamedAudioRecorder() as recorder:
    streamed_input = StreamedAudioInput()
    
    while session_active:
        if recorder.has_audio():
            audio_chunk = recorder.get_audio_chunk()
            streamed_input.push_audio(audio_chunk)
```

### **3. Real-Time Audio Output**
```python
with AudioPlayer() as player:
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            player.add_audio(event.data)
        elif event.type == "voice_stream_event_lifecycle":
            handle_turn_events(event)
```

### **4. Session Management**
```python
class VoiceSessionManager:
    async def start_session(self):
        # Concurrent input/output processing
        input_task = asyncio.create_task(self._process_audio_input())
        output_task = asyncio.create_task(self._process_audio_output())
        await asyncio.gather(input_task, output_task)
```

## 💡 Streaming Voice Best Practices

1. **Activity Detection**: Let the pipeline handle speech detection automatically
2. **Turn Management**: Use lifecycle events to manage conversation flow
3. **Concurrent Processing**: Handle input and output streams simultaneously
4. **Buffer Management**: Add silence buffers between turns for natural flow
5. **Error Recovery**: Implement robust error handling for streaming failures
6. **Resource Management**: Properly clean up audio streams and resources

## 📊 Performance Characteristics

### **Streaming Pipeline Benefits**
- **Real-Time Interaction**: Immediate response to user speech
- **Natural Conversation**: Continuous, flowing dialogue
- **Activity Detection**: Automatic turn boundary detection
- **Concurrent Processing**: Parallel input/output handling
- **Scalable**: Handles multiple turns efficiently

### **Technical Advantages**
- **Low Latency**: Minimal delay between speech and response
- **Adaptive**: Handles variable speech patterns
- **Robust**: Automatic error recovery and continuation
- **Efficient**: Chunk-based processing for optimal performance

## 🌊 Streaming Features

### **Automatic Turn Detection**
- **Speech Activity Detection**: Automatically detects when user starts speaking
- **Silence Detection**: Identifies when user finishes speaking
- **Turn Boundaries**: Intelligent conversation turn management
- **Continuous Listening**: Always ready for next input

### **Real-Time Processing**
- **Live Transcription**: Speech-to-text as you speak
- **Streaming Agent Response**: AI processing during speech
- **Immediate Audio Output**: Text-to-speech as response generates
- **Parallel Operations**: Multiple processes running simultaneously

### **Lifecycle Management**
- **Turn Events**: `turn_started` and `turn_ended` notifications
- **Session Tracking**: Multi-turn conversation analytics
- **State Management**: Proper resource allocation and cleanup
- **Interruption Handling**: Graceful handling of user interruptions

## 🚨 Requirements & Dependencies

### **Core Dependencies**
- `openai-agents[voice]`: OpenAI Agents SDK with voice support
- `sounddevice`: Real-time audio I/O
- `numpy`: Audio data processing
- `threading`: Concurrent audio processing
- `asyncio`: Asynchronous pipeline management

### **System Requirements**
- **Real-Time Audio**: Low-latency audio hardware
- **Microphone**: Good quality microphone for speech detection
- **Processing Power**: Sufficient CPU for real-time processing
- **Network**: Stable connection for streaming API calls

## 🔗 Related Examples

- **[Static Voice](../static/README.md)**: Turn-based voice interaction
- **[Voice Pipeline Documentation](https://openai.github.io/openai-agents-python/voice/pipeline)**: Official pipeline docs
- **[Streaming Events](https://openai.github.io/openai-agents-python/voice/quickstart)**: Voice event handling

## 🛠️ Advanced Customization

### **Custom Activity Detection**
- Implement custom speech detection algorithms
- Add voice activity thresholds
- Configure silence detection parameters

### **Enhanced Session Management**
- Add conversation memory across sessions
- Implement user authentication
- Add conversation logging and analytics

### **Real-Time Features**
- Add live transcription display
- Implement real-time sentiment analysis
- Add voice emotion detection

## 🚨 Streaming Considerations

### **Interruption Handling**
The SDK currently doesn't support built-in interruptions. Use lifecycle events to:
- Mute microphone during AI responses (`turn_started`)
- Unmute microphone after responses (`turn_ended`)
- Handle user interruptions gracefully

### **Performance Optimization**
- **Buffer Sizes**: Optimize audio chunk sizes for latency vs. quality
- **Concurrent Limits**: Balance processing threads for performance
- **Memory Management**: Clean up audio buffers regularly
- **Network Optimization**: Handle API call failures gracefully

## 💡 Pro Tips

- **Start Simple**: Begin with basic streaming, add features gradually
- **Monitor Lifecycle Events**: Use callbacks to understand turn flow
- **Test Audio Hardware**: Ensure low-latency audio setup
- **Handle Edge Cases**: Plan for network issues and audio failures
- **Optimize for Conversation**: Design agents for natural dialogue flow

## 🔗 Next Steps

After mastering streaming voice agents:
- **Production Deployment**: Scale streaming voice for real applications
- **Custom Voice Models**: Integrate specialized speech models
- **Multi-Modal Agents**: Combine voice with vision and text
- **Enterprise Voice Solutions**: Build robust voice applications

## 🎯 Troubleshooting

### **Common Issues**
- **Audio Latency**: Check audio hardware and buffer settings
- **Speech Detection**: Adjust microphone levels and sensitivity
- **Turn Management**: Monitor lifecycle events for debugging
- **Resource Usage**: Monitor CPU and memory during streaming
- **Network Issues**: Implement retry logic for API failures
