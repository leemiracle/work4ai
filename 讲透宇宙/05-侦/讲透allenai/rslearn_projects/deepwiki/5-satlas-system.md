<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/rslearn_projects · page 5 Satlas System · fetched 2026-10-26 -->

# Satlas System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/satlas/marine_infra/config.json](data/satlas/marine_infra/config.json)
- [data/satlas/marine_infra/config.yaml](data/satlas/marine_infra/config.yaml)
- [data/satlas/wind_turbine/config_azure.json](data/satlas/wind_turbine/config_azure.json)
- [rslp/common/__init__.py](rslp/common/__init__.py)
- [rslp/common/worker.py](rslp/common/worker.py)
- [rslp/satlas/README.md](rslp/satlas/README.md)
- [rslp/satlas/__init__.py](rslp/satlas/__init__.py)
- [rslp/satlas/data_sources.py](rslp/satlas/data_sources.py)
- [rslp/satlas/postprocess.py](rslp/satlas/postprocess.py)
- [rslp/satlas/predict_pipeline.py](rslp/satlas/predict_pipeline.py)
- [rslp/satlas/publish.py](rslp/satlas/publish.py)
- [rslp/satlas/scripts/smooth_point_labels_viterbi.go](rslp/satlas/scripts/smooth_point_labels_viterbi.go)
- [tests/integration_slow/satlas/test_predict_pipeline.py](tests/integration_slow/satlas/test_predict_pipeline.py)
- [tests/unit/satlas/__init__.py](tests/unit/satlas/__init__.py)
- [tests/unit/satlas/test_postprocess.py](tests/unit/satlas/test_postprocess.py)

</details>



The Satlas System is a large-scale geospatial model inference platform that applies deep learning models to satellite imagery for detecting and monitoring infrastructure worldwide. The system processes satellite data through distributed inference pipelines, performs temporal smoothing, and publishes results as vector tiles and GeoJSON files for web applications.

This document covers the prediction pipeline, custom data sources, distributed processing architecture, and post-processing workflows. For information about the underlying ML framework, see [Core Infrastructure](#2). For details about training these models, see the rslearn framework documentation.

## System Architecture

The Satlas System consists of four main components that work together to process satellite imagery at global scale:

```mermaid
graph TB
    subgraph "Applications"
        marine_infra[Application.MARINE_INFRA]
        wind_turbine[Application.WIND_TURBINE] 
        solar_farm[Application.SOLAR_FARM]
        tree_cover[Application.TREE_COVER]
    end
    
    subgraph "Data Sources"
        monthly_s2[MonthlySentinel2]
        monthly_azure_s2[MonthlyAzureSentinel2]
        monthly_s1[MonthlySentinel1]
    end
    
    subgraph "Prediction Pipeline"
        predict_pipeline[predict_pipeline]
        predict_multi[predict_multi]
        get_output_fname[get_output_fname]
        merge_and_upload_points[merge_and_upload_points]
    end
    
    subgraph "Distributed Processing"
        worker_pipeline[worker_pipeline]
        launch_workers[launch_workers]
        write_jobs[write_jobs_for_year_months]
        pubsub[Google Cloud Pub/Sub]
    end
    
    subgraph "Post-processing"
        merge_points[merge_points]
        smooth_points[smooth_points]
        viterbi_go[smooth_point_labels_viterbi.go]
        publish_points[publish_points]
    end
    
    subgraph "Output Storage"
        r2[Cloudflare R2]
        gcs[Google Cloud Storage]
        vector_tiles[Vector Tiles]
    end
    
    marine_infra --> predict_pipeline
    wind_turbine --> predict_pipeline
    solar_farm --> predict_pipeline
    tree_cover --> predict_pipeline
    
    monthly_s2 --> predict_pipeline
    monthly_azure_s2 --> predict_pipeline
    monthly_s1 --> predict_pipeline
    
    predict_pipeline --> worker_pipeline
    write_jobs --> pubsub
    pubsub --> worker_pipeline
    
    predict_pipeline --> merge_points
    merge_points --> smooth_points
    smooth_points --> viterbi_go
    smooth_points --> publish_points
    
    publish_points --> r2
    publish_points --> gcs
    publish_points --> vector_tiles
```

Sources: [rslp/satlas/predict_pipeline.py:62-68](), [rslp/satlas/data_sources.py:86-437](), [rslp/common/worker.py:67-220](), [rslp/satlas/postprocess.py:51-218](), [rslp/satlas/publish.py:104-195]()

## Applications and Models

The system supports four distinct applications, each with specialized models and configurations:

| Application | Enum Value | Purpose | Model Type | Output Format |
|-------------|------------|---------|------------|---------------|
| Marine Infrastructure | `Application.MARINE_INFRA` | Offshore platforms and wind turbines | Object Detection | Point GeoJSON |
| Wind Turbines | `Application.WIND_TURBINE` | Onshore wind turbines | Object Detection | Point GeoJSON |
| Solar Farms | `Application.SOLAR_FARM` | Solar installations | Segmentation | Raster GeoTIFF |
| Tree Cover | `Application.TREE_COVER` | Forest coverage mapping | Segmentation | Raster GeoTIFF |

The application type determines model configuration paths and output processing:

```mermaid
graph LR
    subgraph "Configuration Files"
        app_enum[Application enum] --> dataset_config["data/satlas/{application}/config.json"]
        app_enum --> model_config["data/satlas/{application}/config.yaml"]
    end
    
    subgraph "Output Determination"
        app_enum --> app_is_raster[APP_IS_RASTER dict]
        app_is_raster --> point_output[Point GeoJSON]
        app_is_raster --> raster_output[Raster GeoTIFF]
    end
    
    subgraph "Processing Pipeline"
        point_output --> merge_and_upload_points[merge_and_upload_points]
        raster_output --> raster_copy[Direct file copy]
    end
```

Sources: [rslp/satlas/predict_pipeline.py:62-76](), [rslp/satlas/predict_pipeline.py:27-28](), [rslp/satlas/predict_pipeline.py:315-325]()

## Custom Data Sources

The system uses specialized data sources that create monthly mosaics from satellite imagery, ensuring temporal diversity in model inputs:

### MonthlySentinel2

The `MonthlySentinel2` class wraps the standard Sentinel-2 data source to create mosaics from different 30-day periods within the query time range:

```mermaid
graph TB
    subgraph "Monthly Mosaic Creation"
        geometry[STGeometry with time range]
        find_monthly_matches[_find_monthly_matches]
        period_groups[Period-based item groups]
        
        geometry --> find_monthly_matches
        find_monthly_matches --> period_groups
    end
    
    subgraph "Selection Logic"
        most_recent[Most recent periods preferred]
        cloud_filter[max_cloud_cover filter]
        fallback[Older periods as fallback]
        
        period_groups --> most_recent
        cloud_filter --> most_recent
        most_recent --> fallback
    end
    
    subgraph "Configuration"
        period_days[period_days: 30]
        max_matches[max_matches from query_config]
        max_cloud_cover[max_cloud_cover limit]
    end
```

The `_find_monthly_matches` function divides the time range into periods and selects the most recent periods with available imagery, falling back to older periods when necessary.

Sources: [rslp/satlas/data_sources.py:21-83](), [rslp/satlas/data_sources.py:86-191]()

### Azure and Sentinel-1 Sources

The system also provides `MonthlyAzureSentinel2` and `MonthlySentinel1` classes that follow the same monthly mosaic pattern but use different underlying data sources and query mechanisms.

Sources: [rslp/satlas/data_sources.py:194-437]()

## Prediction Pipeline

### Core Pipeline Function

The `predict_pipeline` function orchestrates the complete inference process for a single geographic tile:

```mermaid
graph TB
    subgraph "Input Processing"
        application[Application type]
        projection_json[UTM projection JSON]
        bounds[PixelBounds]
        time_range[datetime range]
    end
    
    subgraph "Dataset Setup"
        ds_config[Load dataset config]
        set_time_range[Set rtree time range]
        create_windows[Create PATCH_SIZE windows]
        
        ds_config --> set_time_range
        set_time_range --> create_windows
    end
    
    subgraph "Processing"
        materialize_dataset[materialize_dataset]
        run_model_predict[run_model_predict]
        merge_upload[merge_and_upload_points]
        
        create_windows --> materialize_dataset
        materialize_dataset --> run_model_predict
        run_model_predict --> merge_upload
    end
    
    subgraph "Output"
        check_exists[Check if output exists]
        output_fname[get_output_fname]
        
        merge_upload --> output_fname
    end
    
    application --> ds_config
    projection_json --> create_windows
    bounds --> create_windows
    time_range --> set_time_range
    check_exists --> output_fname
```

Sources: [rslp/satlas/predict_pipeline.py:176-326]()

### Window Creation and Tiling

The pipeline divides large geographic areas into manageable `PATCH_SIZE` (2048x2048 pixel) windows to enable parallel processing and reduce memory usage:

```mermaid
graph LR
    subgraph "Tiling Logic"
        bounds[Input bounds] --> validate[Validate multiples of PATCH_SIZE]
        validate --> tile_loop[Create tile_col, tile_row loops]
        tile_loop --> window_bounds[Calculate window bounds]
        window_bounds --> boundary_check[Check WGS84 boundaries]
        boundary_check --> window_creation[Create Window objects]
    end
    
    subgraph "Boundary Filtering"
        longitude_check[Skip if near ±180°]
        crossing_check[Skip if crosses 0° longitude]
        
        boundary_check --> longitude_check
        boundary_check --> crossing_check
    end
```

The system skips windows near longitude boundaries to avoid projection artifacts.

Sources: [rslp/satlas/predict_pipeline.py:251-297]()

## Distributed Processing and Job Management

### Worker System Architecture

The Satlas system uses Google Cloud Pub/Sub for distributed job queuing, allowing horizontal scaling across Beaker clusters:

```mermaid
graph TB
    subgraph "Job Creation"
        write_jobs_for_year_months[write_jobs_for_year_months]
        write_jobs[write_jobs]
        publisher[PublisherClient]
        topic[Pub/Sub Topic]
        
        write_jobs_for_year_months --> write_jobs
        write_jobs --> publisher
        publisher --> topic
    end
    
    subgraph "Worker Execution"
        launch_workers[launch_workers]
        beaker_spec[ExperimentSpec.new]
        worker_pipeline[worker_pipeline]
        subscriber[SubscriberClient]
        
        launch_workers --> beaker_spec
        beaker_spec --> worker_pipeline
        worker_pipeline --> subscriber
        subscriber --> topic
    end
    
    subgraph "Job Processing"
        process_message[process_message]
        run_workflow[run_workflow]
        predict_multi[predict_multi]
        
        subscriber --> process_message
        process_message --> run_workflow
        run_workflow --> predict_multi
    end
    
    subgraph "Error Handling"
        retry_logic[Retry with sleep]
        consecutive_errors[Track consecutive errors]
        idle_timeout[Idle timeout termination]
        
        process_message --> retry_logic
        retry_logic --> consecutive_errors
        worker_pipeline --> idle_timeout
    end
```

Sources: [rslp/common/worker.py:67-220](), [rslp/common/worker.py:222-284](), [rslp/common/worker.py:287-312]()

### Task Distribution

Jobs are distributed by creating prediction tasks for different UTM zones and time periods:

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `year_months` | Time periods to process | `[[2024, 7]]` |
| `application` | Model application type | `MARINE_INFRA` |
| `out_path` | Output storage path | `gs://rslearn-eai/projects/satlas/marine_infra/version-20241212/{year:04d}-{month:02d}/` |
| `days_before` | Historical imagery range | `120` |
| `days_after` | Future imagery range | `90` |

Sources: [rslp/satlas/README.md:45-65]()

## Post-processing and Publishing

### Point Merging

The `merge_points` function consolidates prediction outputs from distributed tasks into timestep-specific GeoJSON files:

```mermaid
graph TB
    subgraph "Input Processing"
        predict_path[Individual task outputs]
        get_fc[_get_fc multiprocessing]
        category_map[APP_CATEGORY_MAPS remapping]
    end
    
    subgraph "Feature Processing"
        iterate_files[Iterate prediction files]
        src_projection[Extract source projection]
        convert_coords[Convert to WGS84 coordinates]
        store_pixel_coords[Store pixel coords as properties]
    end
    
    subgraph "Patch Tracking"
        valid_patches[Track valid patches]
        merge_patches[Merge valid_patches by CRS]
        patch_dict[valid_patches dict by projection]
    end
    
    subgraph "Output Generation"
        merged_features[Consolidated features list]
        feature_collection[Final FeatureCollection]
        write_geojson[Write {label}.geojson]
    end
    
    predict_path --> get_fc
    get_fc --> iterate_files
    iterate_files --> src_projection
    src_projection --> convert_coords
    convert_coords --> store_pixel_coords
    
    iterate_files --> valid_patches
    valid_patches --> merge_patches
    merge_patches --> patch_dict
    
    store_pixel_coords --> merged_features
    patch_dict --> feature_collection
    merged_features --> feature_collection
    feature_collection --> write_geojson
```

Sources: [rslp/satlas/postprocess.py:51-133]()

### Viterbi Smoothing

The `smooth_points` function applies temporal smoothing using a Go implementation of the Viterbi algorithm:

```mermaid
graph TB
    subgraph "Input Preparation"
        merged_path[Merged timestep files]
        download_history[Download all timesteps]
        sort_labels[Sort by YYYY-MM]
    end
    
    subgraph "Viterbi Processing"
        go_script[smooth_point_labels_viterbi.go]
        hmm_params[HMM transition probabilities]
        nms_filtering[Non-maximal suppression]
        temporal_smoothing[Temporal state tracking]
    end
    
    subgraph "Output Generation"
        per_timestep[Smoothed per-timestep files]
        history_geojson[history.geojson with start/end times]
        upload_results[Upload to smoothed_path]
    end
    
    merged_path --> download_history
    download_history --> sort_labels
    sort_labels --> go_script
    
    go_script --> hmm_params
    hmm_params --> nms_filtering
    nms_filtering --> temporal_smoothing
    
    temporal_smoothing --> per_timestep
    temporal_smoothing --> history_geojson
    per_timestep --> upload_results
    history_geojson --> upload_results
```

The Go implementation uses Hidden Markov Model parameters to determine when infrastructure appears and disappears over time, handling cases where detection gaps occur due to cloud cover or sensor issues.

Sources: [rslp/satlas/postprocess.py:136-218](), [rslp/satlas/scripts/smooth_point_labels_viterbi.go:1-497]()

### Publishing Pipeline

The `publish_points` function uploads results to multiple destinations:

```mermaid
graph TB
    subgraph "Cloudflare R2 Upload"
        r2_bucket[get_cloudflare_r2_bucket]
        history_upload[Upload history.geojson]
        timestep_upload[Upload recent timesteps]
        latest_symlink[Create latest.geojson]
        update_index[Update index.txt]
    end
    
    subgraph "Vector Tile Generation"
        tippecanoe_prep[Add tippecanoe layer properties]
        run_tippecanoe[Run tippecanoe command]
        bkt_conversion[make_bkt for tile format]
        gcs_upload[Upload to GCS]
    end
    
    r2_bucket --> history_upload
    history_upload --> timestep_upload
    timestep_upload --> latest_symlink
    latest_symlink --> update_index
    
    tippecanoe_prep --> run_tippecanoe
    run_tippecanoe --> bkt_conversion
    bkt_conversion --> gcs_upload
```

The publishing process creates both downloadable GeoJSON files on Cloudflare R2 and vector tiles on Google Cloud Storage for web map display.

Sources: [rslp/satlas/publish.py:104-195]()

---

