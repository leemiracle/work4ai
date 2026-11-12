<!-- source: DeepWiki mcp.deepwiki.com · repo openai/shap-e · page 5 Utility Functions · fetched 2026-10-26 -->

# Utility Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [shap_e/examples/sample_image_to_3d.ipynb](shap_e/examples/sample_image_to_3d.ipynb)
- [shap_e/examples/sample_text_to_3d.ipynb](shap_e/examples/sample_text_to_3d.ipynb)
- [shap_e/util/notebooks.py](shap_e/util/notebooks.py)

</details>



This page documents the utility functions used throughout the Shap-E system for rendering 3D models, setting up cameras, processing images, and visualizing results. These utilities serve as the supporting infrastructure that enables the main text-to-3D and image-to-3D generation workflows.

## Overview of Utility Functions

Shap-E provides several utility functions that handle common tasks required across different components of the system. These include camera positioning, latent space conversion, mesh processing, and visualization tools.

```mermaid
flowchart TD
    subgraph "Utility Functions"
        direction TB
        cameraUtils["Camera Utilities"]
        renderUtils["Rendering Utilities"]
        visualizationUtils["Visualization Utilities"]
        meshUtils["Mesh Utilities"]
        imageUtils["Image Utilities"]
    end
    
    subgraph "Main Components"
        textDiff["Text-conditional Diffusion"]
        imgDiff["Image-conditional Diffusion"]
        projLayer["Projection Layer"]
    end
    
    subgraph "User Interfaces"
        notebooks["Example Notebooks"]
    end
    
    cameraUtils --> renderUtils
    textDiff --> projLayer
    imgDiff --> projLayer
    projLayer --> renderUtils
    renderUtils --> meshUtils
    renderUtils --> visualizationUtils
    imageUtils --> imgDiff
    notebooks --> cameraUtils
    notebooks --> renderUtils
    notebooks --> visualizationUtils
    notebooks --> imageUtils
```

Sources: [shap_e/util/notebooks.py:1-87]()

## Camera Utilities

The camera utilities provide functionality for creating camera positions that can be used to render 3D models from different viewpoints.

### create_pan_cameras Function

The `create_pan_cameras` function creates a batch of cameras arranged in a circle around the 3D model. These cameras are used to generate multi-view renders of the model.

```mermaid
graph TD
    subgraph "create_pan_cameras Function"
        direction TB
        input["Input: size, device"]
        process["Create cameras in circle around origin"]
        output["Output: DifferentiableCameraBatch"]
    end
    
    input --> process
    process --> output

    subgraph "Camera Properties"
        position["Origin positions"]
        orientation["X, Y, Z axes"]
        params["Width, Height, FOV"]
    end

    process --> position
    process --> orientation
    process --> params
```

Example usage:
```python
cameras = create_pan_cameras(size=64, device=torch.device('cuda'))
```

The function:
1. Creates a series of camera positions in a circle around the origin
2. Defines the orientation vectors (x, y, z) for each camera
3. Returns a `DifferentiableCameraBatch` object that can be used with the renderer

Sources: [shap_e/util/notebooks.py:16-43](), [shap_e/examples/sample_text_to_3d.ipynb:78-78](), [shap_e/examples/sample_image_to_3d.ipynb:81-81]()

## Rendering and Visualization Utilities

These utilities convert latent representations into visual outputs, either as images or 3D meshes.

### decode_latent_images Function

The `decode_latent_images` function renders multiple views of a 3D model represented by a latent vector.

```mermaid
flowchart LR
    subgraph "decode_latent_images Function"
        latent["Latent Vector"] --> bottleneck["Bottleneck to Params"]
        bottleneck --> renderer["Render Views"]
        renderer --> images["PIL Images"]
        
        cameras["Camera Batch"] --> renderer
        renderMode["Rendering Mode (STF/NeRF)"] --> renderer
    end
```

This function:
1. Takes a latent vector and converts it to model parameters
2. Renders the model from multiple camera angles
3. Returns a list of PIL images

Example:
```python
images = decode_latent_images(xm, latent, cameras, rendering_mode='nerf')
```

Sources: [shap_e/util/notebooks.py:46-61](), [shap_e/examples/sample_text_to_3d.ipynb:80-80](), [shap_e/examples/sample_image_to_3d.ipynb:83-83]()

### decode_latent_mesh Function

The `decode_latent_mesh` function converts a latent vector into a triangular mesh representation.

```mermaid
flowchart LR
    subgraph "decode_latent_mesh Function"
        latent["Latent Vector"] --> bottleneck["Bottleneck to Params"]
        bottleneck --> renderer["STF Renderer"]
        renderer --> mesh["TorchMesh Object"]
    end
```

This function:
1. Takes a latent vector and converts it to model parameters
2. Uses the STF renderer to generate a mesh
3. Returns a `TorchMesh` object

Example:
```python
mesh = decode_latent_mesh(xm, latent)
```

Sources: [shap_e/util/notebooks.py:64-76](), [shap_e/examples/sample_text_to_3d.ipynb:95-95]()

### gif_widget Function

The `gif_widget` function creates an animated GIF widget for displaying a sequence of images in Jupyter notebooks.

```mermaid
flowchart LR
    subgraph "gif_widget Function"
        images["List of PIL Images"] --> createGif["Create GIF in Memory"]
        createGif --> encode["Base64 Encode"]
        encode --> widget["HTML Widget"]
    end
```

This function:
1. Takes a list of PIL images
2. Creates an animated GIF
3. Encodes it as a base64 string
4. Returns an HTML widget that can be displayed in a Jupyter notebook

Example:
```python
display(gif_widget(images))
```

Sources: [shap_e/util/notebooks.py:79-86](), [shap_e/examples/sample_text_to_3d.ipynb:81-81](), [shap_e/examples/sample_image_to_3d.ipynb:84-84]()

## Image Utilities

### load_image Function

The `load_image` function loads and preprocesses images for use with the image-to-3D generation pipeline.

```mermaid
flowchart LR
    subgraph "load_image Function"
        path["Image Path"] --> load["Load Image"]
        load --> preprocess["Preprocess Image"]
        preprocess --> output["Processed Image"]
    end
```

Example:
```python
image = load_image("example_data/corgi.png")
```

Sources: [shap_e/examples/sample_image_to_3d.ipynb:52-52]()

## Integration with Main Workflows

The utility functions are integrated into the main Shap-E workflows as shown in the following diagram:

```mermaid
sequenceDiagram
    participant User
    participant Notebook as Example Notebook
    participant DiffModel as Diffusion Model
    participant Utils as Utility Functions
    participant Transmitter as Transmitter (xm)
    
    User->>Notebook: Provides text prompt or image
    Notebook->>DiffModel: Passes input to model
    DiffModel->>Notebook: Returns latent representation
    
    Notebook->>Utils: create_pan_cameras(size, device)
    Utils->>Notebook: Returns camera batch
    
    Notebook->>Utils: decode_latent_images(xm, latent, cameras, mode)
    Utils->>Transmitter: Convert latent to params
    Transmitter->>Utils: Render views with camera batch
    Utils->>Notebook: Returns rendered images
    
    Notebook->>Utils: gif_widget(images)
    Utils->>Notebook: Returns animated GIF widget
    Notebook->>User: Displays animated GIF
    
    alt Save as mesh
        Notebook->>Utils: decode_latent_mesh(xm, latent)
        Utils->>Transmitter: Convert latent to params
        Transmitter->>Utils: Generate mesh representation
        Utils->>Notebook: Returns TorchMesh object
        Notebook->>User: Saves mesh as PLY/OBJ file
    end
```

This diagram illustrates how the utility functions support the main text-to-3D and image-to-3D generation processes, handling the camera setup, rendering, and visualization aspects of the workflow.

Sources: [shap_e/examples/sample_text_to_3d.ipynb:75-99](), [shap_e/examples/sample_image_to_3d.ipynb:78-84]()

## Camera Model

The camera model used in Shap-E is based on the `DifferentiableCameraBatch` and `DifferentiableProjectiveCamera` classes.

```mermaid
classDiagram
    class DifferentiableCameraBatch {
        +shape
        +flat_camera
    }
    
    class DifferentiableProjectiveCamera {
        +origin
        +x
        +y
        +z
        +width
        +height
        +x_fov
        +y_fov
    }
    
    DifferentiableCameraBatch --> DifferentiableProjectiveCamera : contains
```

The `DifferentiableProjectiveCamera` defines:
- Camera position (origin)
- Camera orientation (x, y, z axes)
- View dimensions (width, height)
- Field of view angles (x_fov, y_fov)

The `create_pan_cameras` function creates a batch of these cameras positioned in a circle around the model, allowing for consistent multi-view rendering.

Sources: [shap_e/util/notebooks.py:10-10](), [shap_e/util/notebooks.py:16-43]()

## Relationship to Main Components

The utility functions bridge the gap between the diffusion models that generate latent representations and the final outputs that users interact with.

```mermaid
graph TD
    subgraph "Core Models"
        textModel["Text-conditional Diffusion Model"]
        imageModel["Image-conditional Diffusion Model"]
        transmitter["Transmitter (xm)"]
    end
    
    subgraph "Utility Functions"
        createCameras["create_pan_cameras"]
        decodeImages["decode_latent_images"]
        decodeMesh["decode_latent_mesh"]
        gifWidget["gif_widget"]
        loadImage["load_image"]
    end
    
    subgraph "User Outputs"
        renderedViews["Rendered Views (GIFs)"]
        meshFiles["Mesh Files (PLY/OBJ)"]
    end
    
    loadImage --> imageModel
    textModel --> latent["Latent Vector"]
    imageModel --> latent
    latent --> decodeImages
    latent --> decodeMesh
    createCameras --> decodeImages
    transmitter --> decodeImages
    transmitter --> decodeMesh
    decodeImages --> renderedViews
    decodeMesh --> meshFiles
    decodeImages --> images["Image Sequence"]
    images --> gifWidget
    gifWidget --> renderedViews
```

This diagram illustrates how the utility functions connect the core diffusion models to the outputs that users interact with, handling the conversion from latent representations to visual outputs.

Sources: [shap_e/examples/sample_text_to_3d.ipynb:10-100](), [shap_e/examples/sample_image_to_3d.ipynb:10-84](), [shap_e/util/notebooks.py:1-87]()