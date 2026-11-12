<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-reflect · page 2 Audio System · fetched 2026-10-26 -->

# Audio System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main/audio.cpp](main/audio.cpp)

</details>



The Audio System implements real-time audio processing for the Reflect hardware AI assistant, providing Opus-encoded audio streaming between the ESP32-S3 device and WebRTC peer connections. This system handles microphone input capture, speaker output playback, codec initialization, and feedback prevention mechanisms.

For information about WebRTC communication that transports the audio data, see [WebRTC Communication](#3). For details about the hardware platform and codec devices, see [Hardware Platform](#6).

## Audio Configuration and Constants

The audio system operates with specific configuration parameters optimized for voice communication with the OpenAI Realtime API:

| Parameter | Value | Purpose |
|-----------|--------|---------|
| Sample Rate | 16kHz | Voice-optimized sampling frequency |
| Channels | Mono (1) | Single-channel voice communication |
| Bit Depth | 16-bit | Standard PCM audio depth |
| PCM Buffer Size | 640 bytes | 20ms audio frames at 16kHz |
| Opus Bitrate | 30kbps | Low-bandwidth voice encoding |
| Opus Complexity | 0 | Minimum CPU usage for real-time processing |

The system defines these constants in [main/audio.cpp:7-17]() and configures the ESP codec sample format in [main/audio.cpp:19-25]().

**Audio Configuration Diagram**
```mermaid
graph TB
    subgraph "Audio Constants"
        SAMPLE_RATE["SAMPLE_RATE: 16000"]
        CHANNELS["CHANNELS: 1"]
        PCM_BUFFER_SIZE["PCM_BUFFER_SIZE: 640"]
        OPUS_BUFFER_SIZE["OPUS_BUFFER_SIZE: 1276"]
        OPUS_ENCODER_BITRATE["OPUS_ENCODER_BITRATE: 30000"]
        GAIN["GAIN: 5.0"]
    end
    
    subgraph "Codec Configuration"
        fs["esp_codec_dev_sample_info_t fs"]
        mic_codec_dev["esp_codec_dev_handle_t mic_codec_dev"]
        spk_codec_dev["esp_codec_dev_handle_t spk_codec_dev"]
    end
    
    SAMPLE_RATE --> fs
    CHANNELS --> fs
    fs --> mic_codec_dev
    fs --> spk_codec_dev
```

Sources: [main/audio.cpp:7-28]()

## Codec and Buffer Initialization

The `reflect_audio()` function initializes all audio components in a specific sequence to ensure proper codec setup and memory allocation.

**Codec Initialization Process**
```mermaid
graph TD
    reflect_audio["reflect_audio()"]
    
    subgraph "Speaker Initialization"
        bsp_audio_codec_speaker_init["bsp_audio_codec_speaker_init()"]
        esp_codec_dev_open_spk["esp_codec_dev_open(spk_codec_dev, &fs)"]
        esp_codec_dev_set_out_vol["esp_codec_dev_set_out_vol(spk_codec_dev, 100)"]
    end
    
    subgraph "Microphone Initialization"
        bsp_audio_codec_microphone_init["bsp_audio_codec_microphone_init()"]
        esp_codec_dev_set_in_gain["esp_codec_dev_set_in_gain(mic_codec_dev, 42.0)"]
        esp_codec_dev_open_mic["esp_codec_dev_open(mic_codec_dev, &fs)"]
    end
    
    subgraph "Opus Decoder Setup"
        opus_decoder_create["opus_decoder_create(SAMPLE_RATE, 1, &opus_error)"]
        decoder_buffer_malloc["malloc(PCM_BUFFER_SIZE)"]
    end
    
    subgraph "Opus Encoder Setup"
        opus_encoder_create["opus_encoder_create(..., OPUS_APPLICATION_VOIP, ...)"]
        opus_encoder_init["opus_encoder_init(...)"]
        opus_encoder_ctl_bitrate["OPUS_SET_BITRATE(30000)"]
        opus_encoder_ctl_complexity["OPUS_SET_COMPLEXITY(0)"]
        opus_encoder_ctl_signal["OPUS_SET_SIGNAL(OPUS_SIGNAL_VOICE)"]
    end
    
    subgraph "Buffer Allocation"
        read_buffer_malloc["heap_caps_malloc(PCM_BUFFER_SIZE)"]
        encoder_output_buffer_malloc["malloc(OPUS_BUFFER_SIZE)"]
    end
    
    reflect_audio --> bsp_audio_codec_speaker_init
    bsp_audio_codec_speaker_init --> esp_codec_dev_open_spk
    esp_codec_dev_open_spk --> esp_codec_dev_set_out_vol
    
    esp_codec_dev_set_out_vol --> bsp_audio_codec_microphone_init
    bsp_audio_codec_microphone_init --> esp_codec_dev_set_in_gain
    esp_codec_dev_set_in_gain --> esp_codec_dev_open_mic
    
    esp_codec_dev_open_mic --> opus_decoder_create
    opus_decoder_create --> decoder_buffer_malloc
    
    decoder_buffer_malloc --> opus_encoder_create
    opus_encoder_create --> opus_encoder_init
    opus_encoder_init --> opus_encoder_ctl_bitrate
    opus_encoder_ctl_bitrate --> opus_encoder_ctl_complexity
    opus_encoder_ctl_complexity --> opus_encoder_ctl_signal
    
    opus_encoder_ctl_signal --> read_buffer_malloc
    read_buffer_malloc --> encoder_output_buffer_malloc
```

The initialization process configures the microphone gain to 42.0 and speaker volume to 100%, while setting up Opus encoding optimized for voice applications with minimal CPU complexity.

Sources: [main/audio.cpp:48-84]()

## Audio Input Pipeline

The `reflect_send_audio()` function captures microphone input and encodes it for transmission via WebRTC peer connections.

**Audio Input Processing Flow**
```mermaid
graph LR
    mic_input["Microphone Input"]
    is_playing_check["is_playing check"]
    esp_codec_dev_read["esp_codec_dev_read(mic_codec_dev, read_buffer, PCM_BUFFER_SIZE)"]
    memset_zero["memset(read_buffer, 0, PCM_BUFFER_SIZE)"]
    opus_encode["opus_encode(opus_encoder, read_buffer, ..., encoder_output_buffer, ...)"]
    peer_connection_send_audio["peer_connection_send_audio(peer_connection, encoder_output_buffer, encoded_size)"]
    
    mic_input --> is_playing_check
    is_playing_check -->|"false"| esp_codec_dev_read
    is_playing_check -->|"true"| memset_zero
    esp_codec_dev_read --> opus_encode
    memset_zero --> opus_encode
    opus_encode --> peer_connection_send_audio
```

The input pipeline implements feedback prevention by checking the `is_playing` atomic boolean. When audio is currently being played through the speaker, the microphone input is zeroed to prevent echo and feedback loops.

Sources: [main/audio.cpp:115-129]()

## Audio Output Pipeline

The `reflect_play_audio()` function receives Opus-encoded audio data, decodes it to PCM, and plays it through the device speaker with gain control.

**Audio Output Processing Flow**
```mermaid
graph LR
    opus_data["Opus Data Input"]
    opus_decode["opus_decode(opus_decoder, data, size, decoder_buffer, ...)"]
    display_check["reflect_display_pressed()"]
    memset_mute["memset(decoder_buffer, 0, PCM_BUFFER_SIZE)"]
    set_is_playing["set_is_playing(decoder_buffer)"]
    apply_gain["apply_gain((int16_t *)decoder_buffer)"]
    esp_codec_dev_write["esp_codec_dev_write(spk_codec_dev, decoder_buffer, PCM_BUFFER_SIZE)"]
    
    opus_data --> opus_decode
    opus_decode --> display_check
    display_check -->|"true"| memset_mute
    display_check -->|"false"| set_is_playing
    memset_mute --> set_is_playing
    set_is_playing --> apply_gain
    apply_gain --> esp_codec_dev_write
```

The output pipeline includes a manual mute function triggered by display touch input and automatic gain amplification of 5.0x to ensure adequate speaker volume.

Sources: [main/audio.cpp:100-113]()

## Feedback Prevention System

The system implements sophisticated feedback prevention using the `is_playing` atomic boolean and dynamic input muting.

**Feedback Prevention Logic**
```mermaid
graph TB
    subgraph "Audio Detection"
        set_is_playing["set_is_playing(int16_t *in_buf)"]
        sample_loop["for (i = 0; i < PCM_BUFFER_SIZE/2; i++)"]
        threshold_check["if (in_buf[i] != -1 && in_buf[i] != 0 && in_buf[i] != 1)"]
        any_set_true["any_set = true"]
        is_playing_update["is_playing = any_set"]
    end
    
    subgraph "Input Muting"
        reflect_send_audio["reflect_send_audio()"]
        is_playing_check["if (is_playing)"]
        memset_input["memset(read_buffer, 0, PCM_BUFFER_SIZE)"]
        normal_read["esp_codec_dev_read(mic_codec_dev, read_buffer, PCM_BUFFER_SIZE)"]
    end
    
    set_is_playing --> sample_loop
    sample_loop --> threshold_check
    threshold_check --> any_set_true
    any_set_true --> is_playing_update
    
    reflect_send_audio --> is_playing_check
    is_playing_check -->|"true"| memset_input
    is_playing_check -->|"false"| normal_read
    
    is_playing_update -.->|"atomic update"| is_playing_check
```

The `set_is_playing()` function analyzes PCM samples to detect active audio playback by checking if samples exceed noise floor thresholds (-1, 0, 1). When audio is detected, the microphone input is automatically muted to prevent acoustic feedback.

Sources: [main/audio.cpp:37-46](), [main/audio.cpp:115-121]()

## Gain Control and Audio Processing

The `apply_gain()` function amplifies decoded audio samples while preventing clipping through proper range limiting.

```mermaid
graph LR
    samples_input["int16_t *samples"]
    gain_multiply["scaled = (float)samples[i] * GAIN"]
    clamp_upper["if (scaled > 32767.0f) scaled = 32767.0f"]
    clamp_lower["if (scaled < -32768.0f) scaled = -32768.0f"]
    samples_output["samples[i] = (int16_t)scaled"]
    
    samples_input --> gain_multiply
    gain_multiply --> clamp_upper
    clamp_upper --> clamp_lower
    clamp_lower --> samples_output
```

The gain amplification uses a fixed multiplier of 5.0x defined by the `GAIN` constant, with proper saturation arithmetic to prevent 16-bit integer overflow and audio distortion.

Sources: [main/audio.cpp:86-98]()

## Integration with WebRTC and Task Management

The audio system integrates with the broader Reflect architecture through WebRTC peer connections and FreeRTOS task scheduling.

**Audio System Integration**
```mermaid
graph TB
    subgraph "FreeRTOS Task Layer"
        reflect_send_audio_task["reflect_send_audio_task"]
        task_priority["Priority: 7, Core: 0"]
    end
    
    subgraph "Audio Functions"
        reflect_send_audio["reflect_send_audio(PeerConnection *)"]
        reflect_play_audio["reflect_play_audio(uint8_t *data, size_t size)"]
    end
    
    subgraph "WebRTC Integration"
        peer_connection_send_audio["peer_connection_send_audio()"]
        webrtc_audio_callback["WebRTC Audio Callback"]
    end
    
    subgraph "Display Integration"
        reflect_display_pressed["reflect_display_pressed()"]
    end
    
    reflect_send_audio_task --> reflect_send_audio
    task_priority --> reflect_send_audio_task
    reflect_send_audio --> peer_connection_send_audio
    webrtc_audio_callback --> reflect_play_audio
    reflect_display_pressed --> reflect_play_audio
```

The audio system operates within a dedicated FreeRTOS task (`reflect_send_audio_task`) running at priority 7 on CPU core 0, ensuring real-time audio processing performance. Audio data flows bidirectionally through WebRTC peer connections to enable voice communication with the OpenAI Realtime API.

Sources: [main/audio.cpp:115-129](), [main/audio.cpp:100-113]()

---

