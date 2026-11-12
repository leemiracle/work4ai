<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/CoCosNet · extra page Flickr Dataset · fetched 2026-10-26 -->

# Flickr Dataset

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/flickr_dataset.py](data/flickr_dataset.py)

</details>



## Purpose and Scope

The `FlickrDataset` class provides a general-purpose dataset implementation for processing Flickr image collections within the CoCosNet framework. This implementation supports image-to-image translation tasks using semantic masks and follows the standard dataset interface established by the framework's dataset management system.

For information about the broader dataset architecture, see [Dataset Architecture](#3.1). For other domain-specific implementations, see [ADE20K Dataset](#3.2.1), [CelebAHQ Datasets](#3.2.2), and [DeepFashion Dataset](#3.2.3).

## Class Architecture

The `FlickrDataset` follows the framework's inheritance hierarchy, extending the base `Pix2pixDataset` class with Flickr-specific configurations and path handling logic.

### Class Inheritance Diagram

```mermaid
graph TD
    BaseDataset["BaseDataset<br/>(Abstract Base)"]
    Pix2pixDataset["Pix2pixDataset<br/>(Core Implementation)"]
    FlickrDataset["FlickrDataset<br/>(Flickr-specific)"]
    
    BaseDataset --> Pix2pixDataset
    Pix2pixDataset --> FlickrDataset
    
    subgraph "Key Methods"
        modify_commandline_options["modify_commandline_options()"]
        get_paths["get_paths()"]
        get_ref["get_ref()"]
        imgpath_to_labelpath["imgpath_to_labelpath()"]
    end
    
    FlickrDataset --> modify_commandline_options
    FlickrDataset --> get_paths
    FlickrDataset --> get_ref
    FlickrDataset --> imgpath_to_labelpath
```

Sources: [data/flickr_dataset.py:1-67]()

### Class Definition

The `FlickrDataset` class is implemented as a minimal extension of `Pix2pixDataset`, overriding specific methods to handle Flickr dataset characteristics:

| Method | Purpose | Line Reference |
|--------|---------|----------------|
| `modify_commandline_options` | Sets dataset-specific configuration defaults | [data/flickr_dataset.py:10-23]() |
| `get_paths` | Discovers and organizes image and mask file paths | [data/flickr_dataset.py:25-34]() |
| `get_ref` | Loads reference mappings for training/testing | [data/flickr_dataset.py:36-50]() |
| `imgpath_to_labelpath` | Converts image paths to corresponding mask paths | [data/flickr_dataset.py:52-54]() |

Sources: [data/flickr_dataset.py:7-67]()

## Configuration and Options

The `FlickrDataset` establishes specific defaults through the `modify_commandline_options` static method, configuring the dataset for optimal Flickr image processing.

### Configuration Parameters

```mermaid
graph LR
    subgraph "Image Processing"
        preprocess_mode["preprocess_mode='resize_and_crop'"]
        load_size_train["load_size=286 (training)"]
        load_size_test["load_size=256 (testing)"]
        crop_size["crop_size=256"]
        display_winsize["display_winsize=256"]
    end
    
    subgraph "Label Configuration"
        label_nc["label_nc=150"]
        contain_dontcare["contain_dontcare_label=True"]
    end
    
    subgraph "Caching Settings"
        cache_read["cache_filelist_read=False"]
        cache_write["cache_filelist_write=False"]
    end
    
    FlickrDataset --> preprocess_mode
    FlickrDataset --> load_size_train
    FlickrDataset --> load_size_test
    FlickrDataset --> crop_size
    FlickrDataset --> display_winsize
    FlickrDataset --> label_nc
    FlickrDataset --> contain_dontcare
    FlickrDataset --> cache_read
    FlickrDataset --> cache_write
```

The configuration uses 150 label classes (`label_nc=150`), matching the semantic richness expected for general image datasets. Training uses a larger load size (286) than testing (256) to enable data augmentation during training phases.

Sources: [data/flickr_dataset.py:12-22]()

## Data Organization and File Paths

The `FlickrDataset` expects a specific directory structure that separates images from their corresponding semantic masks, with different organization for training and testing phases.

### File Structure and Path Resolution

```mermaid
graph TD
    subgraph "Training Phase"
        dataroot_train["opt.dataroot/"]
        images_train["images/"]
        mask_train["mask/"]
        
        dataroot_train --> images_train
        dataroot_train --> mask_train
    end
    
    subgraph "Testing Phase"
        dataroot_test["opt.dataroot/"]
        test_images["test/images/"]
        test_mask["test/mask/"]
        
        dataroot_test --> test_images
        dataroot_test --> test_mask
    end
    
    subgraph "Path Processing"
        get_paths["get_paths()"]
        os_listdir["os.listdir()"]
        path_sorting["sorted()"]
        path_joining["os.path.join()"]
        
        get_paths --> os_listdir
        os_listdir --> path_sorting
        path_sorting --> path_joining
    end
    
    images_train --> get_paths
    test_images --> get_paths
    mask_train --> get_paths
    test_mask --> get_paths
```

The `get_paths` method constructs file paths dynamically based on the training phase, using `root.replace('images', 'mask')` to derive mask paths from image paths.

Sources: [data/flickr_dataset.py:25-34]()

### Path Mapping Implementation

The dataset implements bidirectional path mapping between images and labels:

| Function | Input | Output | Implementation |
|----------|-------|--------|----------------|
| `get_paths` | `opt.dataroot`, `opt.phase` | `label_paths`, `image_paths` | [data/flickr_dataset.py:26-33]() |
| `imgpath_to_labelpath` | Image file path | Corresponding mask file path | [data/flickr_dataset.py:53]() |

Sources: [data/flickr_dataset.py:25-34](), [data/flickr_dataset.py:52-54]()

## Reference System

The `FlickrDataset` uses external reference files to manage training and testing splits, enabling controlled cross-validation and consistent evaluation.

### Reference File Processing

```mermaid
graph LR
    subgraph "Reference Files"
        flickr_ref["flickr_ref.txt<br/>(training)"]
        flickr_ref_test["flickr_ref_test_from_train.txt<br/>(testing)"]
    end
    
    subgraph "Processing Logic"
        get_ref["get_ref()"]
        file_reading["fd.readlines()"]
        line_parsing["items = lines[i].strip().split(',')"]
        dict_building["ref_dict[key] = val"]
    end
    
    subgraph "Output Structure"
        ref_dict["ref_dict<br/>(key-value mappings)"]
        train_test_folder["train_test_folder<br/>('', 'test')"]
    end
    
    flickr_ref --> get_ref
    flickr_ref_test --> get_ref
    get_ref --> file_reading
    file_reading --> line_parsing
    line_parsing --> dict_building
    dict_building --> ref_dict
    get_ref --> train_test_folder
```

The reference system processes comma-separated files where each line contains a key followed by reference values. Training phase uses the first and last reference (`[items[1], items[-1]]`), while testing uses all references (`items[1:]`).

Sources: [data/flickr_dataset.py:36-50]()

### Reference File Format

| Phase | File | Line Format | Value Selection |
|-------|------|-------------|-----------------|
| Training | `flickr_ref.txt` | `key,ref1,ref2,...,refN` | `[ref1, refN]` |
| Testing | `flickr_ref_test_from_train.txt` | `key,ref1,ref2,...,refN` | `[ref1,ref2,...,refN]` |

Sources: [data/flickr_dataset.py:42-47]()

## Integration with CoCosNet Framework

The `FlickrDataset` integrates seamlessly with the CoCosNet framework's dataset management system through the established factory pattern and dynamic loading mechanism.

### Framework Integration Flow

```mermaid
graph TD
    subgraph "Dataset Factory"
        find_dataset_using_name["find_dataset_using_name('flickr')"]
        import_module["importlib.import_module('data.flickr_dataset')"]
        class_instantiation["FlickrDataset()"]
    end
    
    subgraph "Initialization"
        modify_commandline_options["FlickrDataset.modify_commandline_options()"]
        dataset_initialize["dataset.initialize()"]
        get_paths["get_paths()"]
        get_ref["get_ref()"]
    end
    
    subgraph "Runtime Operations"
        getitem["__getitem__()"]
        imgpath_to_labelpath["imgpath_to_labelpath()"]
        data_loading["Data Loading Pipeline"]
    end
    
    find_dataset_using_name --> import_module
    import_module --> class_instantiation
    class_instantiation --> modify_commandline_options
    modify_commandline_options --> dataset_initialize
    dataset_initialize --> get_paths
    dataset_initialize --> get_ref
    
    get_paths --> getitem
    get_ref --> getitem
    getitem --> imgpath_to_labelpath
    imgpath_to_labelpath --> data_loading
```

The dataset follows the framework's naming convention (`flickr_dataset.py` containing `FlickrDataset` class) and implements the required interface methods inherited from `Pix2pixDataset`.

Sources: [data/flickr_dataset.py:7](), [data/flickr_dataset.py:10-23]()

---

