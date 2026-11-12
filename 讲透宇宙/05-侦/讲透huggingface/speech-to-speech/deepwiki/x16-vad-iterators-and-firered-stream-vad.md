<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/speech-to-speech · extra page VAD Iterators and FireRed Stream-VAD · fetched 2026-10-26 -->

# VAD Iterators and FireRed Stream-VAD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/speech_to_speech/VAD/README.md](src/speech_to_speech/VAD/README.md)
- [src/speech_to_speech/VAD/firered_vad_iterator.py](src/speech_to_speech/VAD/firered_vad_iterator.py)
- [src/speech_to_speech/VAD/vad_iterator.py](src/speech_to_speech/VAD/vad_iterator.py)
- [tests/test_firered_vad_iterator.py](tests/test_firered_vad_iterator.py)
- [tests/test_vad_iterator.py](tests/test_vad_iterator.py)

</details>



## Purpose and Scope

This document details the Voice Activity Detection (VAD) iterator backends implemented in the codebase: the Silero VAD v5 iterator (`VADIterator`) and the FireRed streaming VAD alternative (`FireRedVadIterator`) [src/speech_to_speech/VAD/vad_iterator.py:6-170](), [src/speech_to_speech/VAD/firered_vad_iterator.py:28-171](). It covers frame handling, state machine logic, pre-speech padding, PCM audio transformations, and operational guidance for choosing between backends based on `src/speech_to_speech/VAD/README.md` [src/speech_to_speech/VAD/README.md:1-33]().

---

## 1. Silero VADIterator Implementation

The Silero VAD iterator (`VADIterator`) provides stream imitation using preloaded ONNX or JIT Silero VAD models [src/speech_to_speech/VAD/vad_iterator.py:6-36](). It processes incoming audio chunks, tracks speech probabilities against a configured threshold, manages pre-speech padding buffers, and applies hysteresis to determine utterance boundaries [src/speech_to_speech/VAD/vad_iterator.py:38-170]().

### Core Parameters and State Machine

`VADIterator` is initialized with a VAD model, a detection `threshold` (default `0.5`), `sampling_rate` (`8000` or `16000` Hz), `min_silence_duration_ms` (default `300` ms), and `speech_pad_ms` (default `30` ms) [src/speech_to_speech/VAD/vad_iterator.py:7-54](). 

The internal state machine operates across three primary phases:
1. **Pre-Speech Buffering**: While `triggered` is `false`, incoming chunks are passed to `_remember_pre_speech()` [src/speech_to_speech/VAD/vad_iterator.py:141-143](). This maintains a rolling `_pre_speech_buffer` capped at `speech_pad_samples` via `_trim_pre_speech_buffer()` [src/speech_to_speech/VAD/vad_iterator.py:71-101]().
2. **Triggering**: When `speech_prob >= self.threshold` and `triggered` is `false`, the iterator sets `triggered = True`, copies the pre-speech buffer into `prefix_buffer`, records the triggering chunk, and initializes `active_speech_samples` [src/speech_to_speech/VAD/vad_iterator.py:131-139]().
3. **Active Speech and Hangover**: While `triggered` is `true`, chunks are appended to `buffer` [src/speech_to_speech/VAD/vad_iterator.py:145-146](). A hysteresis band (`threshold - 0.15`) prevents premature chunking during momentary dips in speech probability [src/speech_to_speech/VAD/vad_iterator.py:147-151](). If speech probability drops below `threshold - 0.15`, a silence timer (`temp_end`) starts [src/speech_to_speech/VAD/vad_iterator.py:153-157](). If the silence persists longer than `min_silence_samples`, the utterance is finalized, returning a combined list of tensors via `_speech_buffer()` and resetting internal states [src/speech_to_speech/VAD/vad_iterator.py:159-168]().

```mermaid
title "Silero VAD State Machine and Data Flow"
graph TD
    Input["IncomingAudioChunk (torch.Tensor)"] --> Call["VADIterator.__call__(x)"]
    Call --> Model["SileroModel(x, sampling_rate)"]
    Model --> ProbCheck{"speech_prob >= threshold?"}

    ProbCheck -- "No (Not Triggered)" --> PreSpeech["_remember_pre_speech(x)"]
    PreSpeech --> Trim["_trim_pre_speech_buffer()"]
    Trim --> ReturnNone1["Return None"]

    ProbCheck -- "Yes (Triggered False)" --> Trigger["triggered = True, prefix_buffer = _pre_speech_buffer"]
    Trigger --> Append1["buffer.append(x)"]
    Append1 --> ReturnNone2["Return None"]

    ProbCheck -- "Already Triggered" --> Append2["buffer.append(x)"]
    Append2 --> Hysteresis{"speech_prob >= threshold - 0.15?"}

    Hysteresis -- "Yes" --> ResetTemp["temp_end = 0, active_speech_samples += N"]
    Hysteresis -- "No" --> CheckSilence{"temp_end elapsed >= min_silence_samples?"}

    CheckSilence -- "No" --> ReturnNone3["Return None"]
    CheckSilence -- "Yes" --> Finalize["_speech_buffer() -> list[torch.Tensor]"]
    Finalize --> ResetState["Reset triggered = False, buffer = []"]
```

Sources:
- `src/speech_to_speech/VAD/vad_iterator.py`

---

## 2. FireRed Stream-VAD Iterator Implementation

The FireRed streaming VAD backend (`FireRedVadIterator`) interfaces with `FireRedStreamVad` start and end events [src/speech_to_speech/VAD/firered_vad_iterator.py:1-29](). Unlike Silero, FireRed relies on discrete frame-level indicators (`is_speech_start`, `is_speech_end`, `is_speech`) produced by a streaming feature extractor and detection network [src/speech_to_speech/VAD/firered_vad_iterator.py:15-26]().

### Frame Handling and PCM Transformation

`FireRedVadIterator` enforces a strict `16000` Hz sampling rate [src/speech_to_speech/VAD/firered_vad_iterator.py:40-41](). Incoming audio tensors (scaled to Silero range `[-1, 1]`) are converted to `int16` PCM range by multiplying by `32768.0` and concatenated with any residual waveform `_tail` [src/speech_to_speech/VAD/firered_vad_iterator.py:146-148](). 

The processor feeds fixed-size `400`-sample windows (`_FIRERED_WINDOW_SAMPLES`) with a `160`-sample hop (`_FIRERED_HOP_SAMPLES`) into the `FireRedStreamer` backend via `_detect_frames()` [src/speech_to_speech/VAD/firered_vad_iterator.py:11-12, 145-157](). Unconsumed trailing samples are preserved in `self._tail` for subsequent calls [src/speech_to_speech/VAD/firered_vad_iterator.py:156]().

```mermaid
title "FireRed Stream-VAD Frame Processing and Event Flow"
graph TD
    InputChunk["Incoming Audio Chunk (torch.Tensor)"] --> DetFrames["_detect_frames(x)"]
    DetFrames --> Scale["Convert [-1, 1] to int16 PCM (* 32768.0)"]
    Scale --> TailMerge["Concatenate with self._tail"]
    TailMerge --> WindowCheck{"Audio Length >= 400 samples?"}

    WindowCheck -- "No" --> StoreTail["Update self._tail and Return []"]
    WindowCheck -- "Yes" --> ExtractWindows["Slide 400-sample windows at 160-sample hop"]
    ExtractWindows --> StreamerCall["FireRedStreamer.detect_chunk(audio)"]
    StreamerCall --> SaveTail["Update self._tail with remaining samples"]
    SaveTail --> ReturnResults["Return list[FireRedFrameResult]"]
```

Sources:
- `src/speech_to_speech/VAD/firered_vad_iterator.py`

---

## 3. Backend Selection and Operational Guidance

The pipeline supports selecting the VAD backend via the `--vad` command-line argument [src/speech_to_speech/VAD/README.md:5-9](). 

| Backend Flag (`--vad`) | Implementation Class | Description & Characteristics |
| :--- | :--- | :--- |
| `silero` (default) | `VADIterator` [src/speech_to_speech/VAD/vad_iterator.py:6]() | Silero VAD v5 model with standard thresholding, hysteresis band, and min-silence hangover logic [src/speech_to_speech/VAD/README.md:7](). |
| `firered` | `FireRedVadIterator` [src/speech_to_speech/VAD/firered_vad_iterator.py:28]() | FireRed streaming VAD using explicit start and end events from `FireRedStreamVad` [src/speech_to_speech/VAD/README.md:8](). Bypasses Silero trigger/min-silence hangover logic [src/speech_to_speech/VAD/README.md:10](). |

### Installation and Configuration for FireRed VAD

Using the FireRed VAD backend requires installing optional project extras and downloading model weights locally [src/speech_to_speech/VAD/README.md:16-21]():

```bash
pip install "speech-to-speech[fireredvad]"
hf download FireRedTeam/FireRedVAD --local-dir ./pretrained_models/FireRedVAD
```

To run the local pipeline with FireRed VAD [src/speech_to_speech/VAD/README.md:25-29]():

```bash
speech-to-speech local \
  --vad firered \
  --vad_firered_model_dir ./pretrained_models/FireRedVAD/Stream-VAD
```

The `--vad_firered_use_gpu` flag executes the detector on CUDA [src/speech_to_speech/VAD/README.md:31](). If the optional extra is missing or `--vad_firered_model_dir` is invalid, the handler fails during setup before accepting any client sessions [src/speech_to_speech/VAD/README.md:33]().

Sources:
- `src/speech_to_speech/VAD/README.md`

---

