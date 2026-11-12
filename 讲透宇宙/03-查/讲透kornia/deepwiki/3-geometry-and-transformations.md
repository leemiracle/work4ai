<!-- source: DeepWiki mcp.deepwiki.com · repo kornia/kornia · page 3 Geometry and Transformations · fetched 2026-10-21 -->

# Geometry and Transformations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/geometry.conversions.rst](docs/source/geometry.conversions.rst)
- [docs/source/geometry.transform.rst](docs/source/geometry.transform.rst)
- [kornia/geometry/camera/pinhole.py](kornia/geometry/camera/pinhole.py)
- [kornia/geometry/conversions.py](kornia/geometry/conversions.py)
- [kornia/geometry/transform/affwarp.py](kornia/geometry/transform/affwarp.py)
- [kornia/geometry/transform/imgwarp.py](kornia/geometry/transform/imgwarp.py)

</details>



This document provides an overview of Kornia's geometry and transformation capabilities, which form a core pillar of the library's differentiable computer vision operations. The `kornia.geometry` module provides a comprehensive set of functions and classes for performing geometric transformations on 2D and 3D images, converting between different geometric representations, and working with camera models.

**Scope**: This page covers the overall architecture and organization of the geometry module. For detailed information on specific subsystems, see:
- Geometric representations and conversions between rotation matrices, quaternions, axis-angle, and Euler angles: [3.1](#3.1)
- Image warping operations and transformation matrix generation: [3.2](#3.2)
- Camera models, projection, and unprojection: [3.3](#3.3)
- Coordinate system normalization and homography operations: [3.4](#3.4)
- High-level geometric operations with module wrappers: [3.5](#3.5)

## Module Organization

The geometry module is organized into three main submodules that work together to provide a complete geometric transformation pipeline:

**Diagram: Kornia Geometry Module Structure**

```mermaid
graph TB
    subgraph "kornia.geometry"
        CONV["geometry.conversions<br/>Geometric Representations"]
        TRANS["geometry.transform<br/>Image Transformations"]
        CAM["geometry.camera<br/>Camera Models"]
        LINALG["geometry.linalg<br/>Linear Algebra Utilities"]
    end
    
    subgraph "conversions Functions"
        ROT_CONV["Rotation Conversions<br/>rotation_matrix_to_quaternion<br/>axis_angle_to_rotation_matrix<br/>quaternion_to_axis_angle"]
        COORD_CONV["Coordinate Conversions<br/>convert_points_to_homogeneous<br/>convert_points_from_homogeneous<br/>normalize_pixel_coordinates"]
        HOMO_CONV["Homography Operations<br/>normalize_homography<br/>denormalize_homography<br/>convert_affinematrix_to_homography"]
        ANGLE_CONV["Angle Conversions<br/>deg2rad<br/>rad2deg<br/>cart2pol<br/>pol2cart"]
    end
    
    subgraph "transform Functions"
        WARP["Warping Functions<br/>warp_perspective<br/>warp_affine<br/>warp_grid<br/>remap"]
        MATRIX["Matrix Generators<br/>get_perspective_transform<br/>get_rotation_matrix2d<br/>get_affine_matrix2d<br/>get_shear_matrix2d"]
        HIGHLEVEL["High-Level Operations<br/>rotate<br/>translate<br/>scale<br/>shear<br/>resize"]
        MODULES["nn.Module Wrappers<br/>Rotate<br/>Translate<br/>Scale<br/>Shear<br/>Resize<br/>Affine"]
    end
    
    subgraph "camera Classes"
        PINHOLE["PinholeCamera<br/>project<br/>unproject<br/>scale"]
        PINHOLELIST["PinholeCamerasList<br/>Multiple cameras"]
    end
    
    CONV --> ROT_CONV
    CONV --> COORD_CONV
    CONV --> HOMO_CONV
    CONV --> ANGLE_CONV
    
    TRANS --> WARP
    TRANS --> MATRIX
    TRANS --> HIGHLEVEL
    TRANS --> MODULES
    
    CAM --> PINHOLE
    CAM --> PINHOLELIST
    
    HIGHLEVEL -.uses.-> WARP
    HIGHLEVEL -.uses.-> MATRIX
    MATRIX -.uses.-> CONV
    WARP -.uses.-> CONV
    PINHOLE -.uses.-> CONV
    MODULES -.uses.-> HIGHLEVEL
```

**Sources**: [kornia/geometry/conversions.py:1-1932](), [kornia/geometry/transform/imgwarp.py:1-1350](), [kornia/geometry/transform/affwarp.py:1-937](), [kornia/geometry/camera/pinhole.py:1-787]()

## Core Concepts

### Geometric Representations

Kornia supports multiple representations of 3D rotations, each with specific advantages for different operations:

| Representation | Shape | Use Case | Key Functions |
|----------------|-------|----------|---------------|
| Rotation Matrix | `(*, 3, 3)` | Composing rotations, applying to points | `rotation_matrix_to_quaternion`, `rotation_matrix_to_axis_angle` |
| Quaternion (w,x,y,z) | `(*, 4)` | Interpolation, avoiding gimbal lock | `quaternion_to_rotation_matrix`, `quaternion_to_axis_angle` |
| Axis-Angle (Rodrigues) | `(*, 3)` | Compact rotation representation | `axis_angle_to_rotation_matrix`, `axis_angle_to_quaternion` |
| Euler Angles (roll,pitch,yaw) | `(*, 3)` | Human-readable angles | `euler_from_quaternion`, `quaternion_from_euler` |

All conversion functions in [kornia/geometry/conversions.py:292-889]() are differentiable, enabling gradient-based optimization of geometric parameters.

### Transformation Matrices

Kornia uses homogeneous coordinates and transformation matrices for geometric operations:

- **Affine transformations** (`2×3` or `3×4` matrices): Preserve parallel lines, used for rotation, scaling, translation, shearing
- **Perspective transformations** (`3×3` or `4×4` matrices): Allow projective distortions, used for homographies and camera projection

**Diagram: Transformation Matrix Hierarchy**

```mermaid
graph LR
    subgraph "2D Transformations"
        AFF2D["Affine 2x3<br/>Linear + Translation"]
        HOMO2D["Homography 3x3<br/>Projective Transform"]
    end
    
    subgraph "3D Transformations"
        AFF3D["Affine 3x4<br/>Linear + Translation"]
        HOMO3D["Homography 4x4<br/>Projective Transform"]
    end
    
    subgraph "Elementary Operations"
        ROT["Rotation<br/>get_rotation_matrix2d"]
        TRANS["Translation<br/>get_translation_matrix2d"]
        SCALE["Scaling<br/>get_affine_matrix2d"]
        SHEAR["Shearing<br/>get_shear_matrix2d"]
    end
    
    subgraph "Complex Operations"
        PERSP["Perspective<br/>get_perspective_transform"]
        PROJ["Projection<br/>get_projective_transform"]
    end
    
    ROT --> AFF2D
    TRANS --> AFF2D
    SCALE --> AFF2D
    SHEAR --> AFF2D
    
    AFF2D --> HOMO2D
    AFF3D --> HOMO3D
    
    PERSP --> HOMO2D
    PROJ --> HOMO3D
```

**Sources**: [kornia/geometry/transform/imgwarp.py:396-705](), [kornia/geometry/conversions.py:236-289]()

## Image Warping Pipeline

The image warping pipeline in Kornia follows a consistent pattern for applying geometric transformations to images:

**Diagram: Image Warping Data Flow**

```mermaid
graph LR
    INPUT["Input Image<br/>Tensor BCHW"]
    
    subgraph "Transformation Definition"
        POINTS["Control Points<br/>or Parameters"]
        MATRIX_GEN["Matrix Generation<br/>get_perspective_transform<br/>get_rotation_matrix2d<br/>get_affine_matrix2d"]
        MATRIX["Transformation Matrix<br/>Bx3x3 or Bx2x3"]
    end
    
    subgraph "Normalization"
        NORM["Coordinate Normalization<br/>normalize_homography<br/>Pixel → [-1, 1]"]
        NORM_MAT["Normalized Matrix"]
    end
    
    subgraph "Grid Generation"
        MESHGRID["Create Sampling Grid<br/>create_meshgrid"]
        TRANSFORM_GRID["Transform Grid Points<br/>transform_points"]
        GRID["Warped Grid<br/>BxHxWx2"]
    end
    
    subgraph "Sampling"
        SAMPLE["Grid Sampling<br/>F.grid_sample"]
        OUTPUT["Warped Image<br/>Tensor BCHW"]
    end
    
    INPUT --> SAMPLE
    
    POINTS --> MATRIX_GEN
    MATRIX_GEN --> MATRIX
    MATRIX --> NORM
    NORM --> NORM_MAT
    
    NORM_MAT --> MESHGRID
    MESHGRID --> TRANSFORM_GRID
    TRANSFORM_GRID --> GRID
    GRID --> SAMPLE
    
    SAMPLE --> OUTPUT
```

**Sources**: [kornia/geometry/transform/imgwarp.py:65-149](), [kornia/geometry/transform/imgwarp.py:255-303]()

### Warping Functions

The core warping functions follow a consistent interface:

```python
# From kornia/geometry/transform/imgwarp.py
warp_perspective(src, M, dsize, mode, padding_mode, align_corners, fill_value)
warp_affine(src, M, dsize, mode, padding_mode, align_corners, fill_value)
remap(image, map_x, map_y, mode, padding_mode, align_corners, normalized_coordinates)
```

All warping functions:
- Accept batched inputs `(B, C, H, W)`
- Support multiple interpolation modes: `'bilinear'`, `'nearest'`
- Support multiple padding modes: `'zeros'`, `'border'`, `'reflection'`, `'fill'`
- Use PyTorch's `grid_sample` internally for differentiable sampling
- Normalize coordinates to `[-1, 1]` range

**Sources**: [kornia/geometry/transform/imgwarp.py:65-225](), [kornia/geometry/transform/imgwarp.py:489-556]()

## Coordinate Systems and Normalization

Kornia operates in multiple coordinate systems depending on the context:

| Coordinate System | Range | Usage |
|-------------------|-------|-------|
| Pixel Coordinates | `[0, W-1]`, `[0, H-1]` | Image indexing, original data |
| Normalized Coordinates | `[-1, 1]` | PyTorch grid_sample, homographies |
| Homogeneous Coordinates | `(x, y, w)` or `(x, y, z, w)` | Projective transformations |
| Camera Coordinates | 3D space relative to camera | 3D geometry, depth |

**Diagram: Coordinate System Conversions**

```mermaid
graph TB
    PIXEL["Pixel Coordinates<br/>(u, v) ∈ [0, W-1] × [0, H-1]"]
    NORM["Normalized Coordinates<br/>(x, y) ∈ [-1, 1] × [-1, 1]"]
    HOMO["Homogeneous Coordinates<br/>(x, y, w)"]
    EUCLIDEAN["Euclidean Coordinates<br/>(x, y)"]
    CAM3D["3D Camera Coordinates<br/>(X, Y, Z)"]
    WORLD3D["3D World Coordinates<br/>(X_w, Y_w, Z_w)"]
    
    PIXEL -->|"normalize_pixel_coordinates<br/>factor = 2/(hw-1)"| NORM
    NORM -->|"denormalize_pixel_coordinates<br/>inverse factor"| PIXEL
    
    EUCLIDEAN -->|"convert_points_to_homogeneous<br/>append w=1"| HOMO
    HOMO -->|"convert_points_from_homogeneous<br/>divide by w"| EUCLIDEAN
    
    PIXEL -->|"pixel2cam<br/>multiply by depth<br/>apply K_inv"| CAM3D
    CAM3D -->|"cam2pixel<br/>project<br/>apply K"| PIXEL
    
    CAM3D -->|"apply extrinsics"| WORLD3D
    WORLD3D -->|"apply extrinsics_inv"| CAM3D
```

**Sources**: [kornia/geometry/conversions.py:896-1019](), [kornia/geometry/conversions.py:173-228](), [kornia/geometry/camera/pinhole.py:678-733]()

### Homography Normalization

Homographies in pixel space must be normalized before applying transformations to work with PyTorch's normalized coordinate system:

```python
# From kornia/geometry/conversions.py:1042-1076
normalize_homography(dst_pix_trans_src_pix, dsize_src, dsize_dst)
```

This function:
1. Computes normalization matrices for source and destination images
2. Chains transformations: `dst_norm → dst_pix → src_pix → src_norm`
3. Returns normalized homography operating in `[-1, 1]` space

**Sources**: [kornia/geometry/conversions.py:1042-1108]()

## Camera Model

The `PinholeCamera` class encapsulates the pinhole camera model with intrinsic and extrinsic parameters:

**Diagram: PinholeCamera Architecture**

```mermaid
graph TB
    subgraph "PinholeCamera State"
        INTRINSICS["intrinsics: Tensor<br/>Bx4x4 matrix<br/>fx, fy, cx, cy"]
        EXTRINSICS["extrinsics: Tensor<br/>Bx4x4 matrix<br/>R (3x3) + t (3x1)"]
        HEIGHT["height: Tensor<br/>Image height (B,)"]
        WIDTH["width: Tensor<br/>Image width (B,)"]
    end
    
    subgraph "Derived Properties"
        FX["fx, fy<br/>Focal lengths"]
        CXY["cx, cy<br/>Principal point"]
        TXY["tx, ty, tz<br/>Translation vector"]
        K["camera_matrix<br/>3x3 K matrix"]
        RT["rt_matrix<br/>3x4 [R|t] matrix"]
        ROTMAT["rotation_matrix<br/>3x3 R matrix"]
    end
    
    subgraph "Operations"
        PROJECT["project(point_3d)<br/>3D world → 2D pixel<br/>P = K @ [R|t]"]
        UNPROJECT["unproject(point_2d, depth)<br/>2D pixel → 3D world<br/>P_inv = [R|t]^-1 @ K^-1"]
        SCALE["scale(scale_factor)<br/>Adjust intrinsics + image size"]
        CLONE["clone()<br/>Deep copy"]
    end
    
    INTRINSICS --> FX
    INTRINSICS --> CXY
    INTRINSICS --> K
    
    EXTRINSICS --> TXY
    EXTRINSICS --> RT
    EXTRINSICS --> ROTMAT
    
    K --> PROJECT
    RT --> PROJECT
    K --> UNPROJECT
    RT --> UNPROJECT
    
    INTRINSICS --> SCALE
    HEIGHT --> SCALE
    WIDTH --> SCALE
```

**Sources**: [kornia/geometry/camera/pinhole.py:29-413]()

The camera projection follows standard computer vision conventions:

```
3D World Point (X_w, Y_w, Z_w)
    ↓ Apply extrinsics [R|t]
3D Camera Point (X_c, Y_c, Z_c)
    ↓ Apply intrinsics K
Homogeneous 2D (u*Z_c, v*Z_c, Z_c)
    ↓ Normalize by Z_c
2D Pixel Point (u, v)
```

**Sources**: [kornia/geometry/camera/pinhole.py:319-376]()

## High-Level Transform API

Kornia provides both functional and module-based APIs for common geometric transformations:

| Operation | Functional API | Module API | Description |
|-----------|---------------|------------|-------------|
| Rotation | `rotate(tensor, angle, center)` | `Rotate(angle)` | Rotate image around center |
| Translation | `translate(tensor, translation)` | `Translate(translation)` | Shift image by offset |
| Scaling | `scale(tensor, scale_factor, center)` | `Scale(scale_factor)` | Scale image around center |
| Shearing | `shear(tensor, shear)` | `Shear(shear)` | Shear transformation |
| Resize | `resize(input, size, interpolation)` | `Resize(size)` | Resize to target size |
| Affine | `affine(tensor, matrix)` | `Affine(angle, translation, scale_factor, shear)` | Composite affine transform |

**Diagram: High-Level Transform Implementation**

```mermaid
graph TB
    subgraph "User API"
        FUNC["Functional Interface<br/>rotate, translate, scale, shear"]
        MODULE["Module Interface<br/>Rotate, Translate, Scale, Shear"]
    end
    
    subgraph "Implementation Layer"
        COMPUTE_MAT["Matrix Computation<br/>_compute_rotation_matrix<br/>_compute_translation_matrix<br/>_compute_scaling_matrix<br/>_compute_shear_matrix"]
        AFFINE["affine(tensor, matrix)<br/>Universal warping function"]
    end
    
    subgraph "Core Warping"
        GET_MATRIX["Matrix Generators<br/>get_rotation_matrix2d<br/>get_affine_matrix2d"]
        WARP_AFFINE["warp_affine<br/>Low-level warping"]
        NORMALIZE["normalize_homography<br/>Coordinate normalization"]
        GRID_SAMPLE["F.grid_sample<br/>PyTorch sampling"]
    end
    
    FUNC --> COMPUTE_MAT
    MODULE --> FUNC
    
    COMPUTE_MAT --> AFFINE
    AFFINE --> WARP_AFFINE
    
    COMPUTE_MAT --> GET_MATRIX
    WARP_AFFINE --> GET_MATRIX
    WARP_AFFINE --> NORMALIZE
    WARP_AFFINE --> GRID_SAMPLE
```

**Sources**: [kornia/geometry/transform/affwarp.py:137-537](), [kornia/geometry/transform/affwarp.py:772-937]()

### Example Usage Pattern

The high-level API handles common use cases with minimal code:

```python
# Functional API - stateless, direct application
rotated = rotate(img, angle=torch.tensor([45.0]))

# Module API - stateful, reusable transforms
transform = Rotate(angle=torch.tensor([45.0]))
rotated = transform(img)

# Composite transformations with Affine
transform = Affine(
    angle=torch.tensor([45.0]),
    translation=torch.tensor([[10.0, 20.0]]),
    scale_factor=torch.tensor([[1.5, 1.5]]),
    shear=torch.tensor([[0.1, 0.2]])
)
transformed = transform(img)
```

**Sources**: [kornia/geometry/transform/affwarp.py:248-310](), [kornia/geometry/transform/affwarp.py:808-882]()

## Integration with Other Modules

The geometry module integrates with other Kornia components:

- **Augmentation System** ([4](#4)): Geometric augmentations use `geometry.transform` for warping operations and `geometry.conversions` for parameter generation
- **Feature Detection** ([5](#5)): LAF (Local Affine Frames) use rotation matrices and affine transforms from `geometry.conversions`
- **Deep Learning Models** ([6](#6)): Object detection and segmentation models use geometric transforms for preprocessing and post-processing

**Sources**: [kornia/geometry/transform/imgwarp.py:1-63](), [kornia/geometry/conversions.py:1-77]()

## Performance Considerations

All geometric operations in Kornia are designed for performance:

1. **Batched operations**: All functions support batch processing with shape `(B, ...)` for parallel execution
2. **GPU acceleration**: Operations run on CUDA when input tensors are on GPU
3. **Differentiability**: All operations maintain gradients for end-to-end training
4. **Anti-aliasing**: `resize` function supports Gaussian pre-filtering for high-quality downsampling

**Sources**: [kornia/geometry/transform/affwarp.py:553-635]()

---

