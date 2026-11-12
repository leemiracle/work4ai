# molmo-utils

Molmo Utils contains a set of helper functions for processing and integrating visual inputs with **Molmo**, Ai2’s state-of-the-art multimodal open language models.

## Installation

```bash
pip install molmo-utils          # basic usage
pip install molmo-utils[torchcodec]  # recommended for video inputs
```

## Usage

### Molmo2

```python
from transformers import AutoProcessor, AutoModelForImageTextToText
from molmo_utils import process_vision_info

model_path = "allenai/Molmo2-8B"

model = AutoModelForImageTextToText.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto",
    trust_remote_code=True,
)

processor = AutoProcessor.from_pretrained(
    model_path,
    trust_remote_code=True,
    dtype="auto",
    device_map="auto",
)

# You can directly use a local file path, a URL, or a base64-encoded image.
# The processed visual tokens will always be inserted at the beginning of the input sequence.

messages = [
    # Image
    ## Local file path
    [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": "file:///path/to/your/image.jpg"},
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
    ## Image URL
    [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": "http://path/to/your/image.jpg"},
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
    ## Base64-encoded image
    [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": "data:image;base64,/9j/..."},
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
    ## PIL.Image.Image
    [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": pil_image},
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
    # Video
    ## Local video path
    [
        {
            "role": "user",
            "content": [
                {"type": "video", "video": "file:///path/to/video1.mp4"},
                {"type": "text", "text": "Describe this video."},
            ],
        }
    ],
    ## Local video frames (timestamps must be provided)
    [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": [
                        "file:///path/to/extracted_frame1.jpg",
                        "file:///path/to/extracted_frame2.jpg",
                        "file:///path/to/extracted_frame3.jpg",
                    ],
                    "timestamps": [0.0, 0.5, 1.0],
                },
                {"type": "text", "text": "Describe this video."},
            ],
        }
    ],
    ## The model dynamically adjusts the frame sampling mode, maximum number of frames,
    ## maximum sampling FPS, etc.
    [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": "file:///path/to/video1.mp4",
                    "frame_sampling_mode": "uniform_last_frame",
                    "num_frames": 384,
                    "max_fps": 8.0,
                },
                {"type": "text", "text": "Describe this video."},
            ],
        }
    ],
]


text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

images, videos, video_kwargs = process_vision_info(messages)

if videos is not None:
    videos, video_metadatas = zip(*videos)
    videos = list(videos)
    video_metadatas = list(video_metadatas)
else:
    video_metadatas = None

inputs = processor(
    text=text,
    images=images,
    videos=videos,
    video_metadata=video_metadatas,
    return_tensors="pt",
    **video_kwargs,
)
inputs = inputs.to(model.device)

generated_ids = model.generate(**inputs, max_new_tokens=2048)
generated_text = processor.post_process_image_text_to_text(
    generated_ids[:, inputs["input_ids"].size(1):],
    skip_special_tokens=True,
)
print(generated_text)
```