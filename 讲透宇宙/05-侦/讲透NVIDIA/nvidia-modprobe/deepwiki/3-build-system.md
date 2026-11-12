<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-modprobe · page 3 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [utils.mk](utils.mk)
- [version.mk](version.mk)

</details>



The Build System is the foundation that manages compilation, linking, documentation generation, and distribution of the nvidia-modprobe utility. It provides cross-platform build capabilities, version management, and automated documentation generation. This system coordinates the compilation of the main executable, core libraries, and supporting utilities across different operating systems and architectures.

For information about the nvidia-modprobe runtime components, see [nvidia-modprobe System](#2). For details about the documentation generation process, see [Documentation System](#5).

## Architecture Overview

The build system follows a hierarchical structure with three primary components: version management, build configuration, and build orchestration. The system is designed to handle cross-platform compilation while maintaining consistent version information throughout the build process.

### Build System Component Hierarchy

```mermaid
graph TB
    subgraph "Version Management Layer"
        version_mk[version.mk]
        version_h["$(OUTPUTDIR)/version.h"]
        nvidia_version["NVIDIA_VERSION = 575.64"]
        
        version_mk --> version_h
        version_mk --> nvidia_version
    end
    
    subgraph "Build Configuration Layer"
        utils_mk[utils.mk]
        toolchain["CC, CXX, LD, AR"]
        target_detection["TARGET_OS, TARGET_ARCH"]
        cflags_config["CFLAGS, LDFLAGS"]
        
        utils_mk --> toolchain
        utils_mk --> target_detection
        utils_mk --> cflags_config
    end
    
    subgraph "Build Orchestration Layer"
        makefile[Makefile]
        source_lists["dist-files.mk, src.mk"]
        build_rules["DEFINE_OBJECT_RULE"]
        targets["$(NVIDIA_MODPROBE), $(MANPAGE)"]
        
        makefile --> source_lists
        makefile --> build_rules
        makefile --> targets
    end
    
    subgraph "Documentation Generation"
        gen_manpage_opts["$(GEN_MANPAGE_OPTS)"]
        options_inc["$(OPTIONS_1_INC)"]
        manpage_m4["nvidia-modprobe.1.m4"]
        
        gen_manpage_opts --> options_inc
        options_inc --> manpage_m4
    end
    
    version_mk --> makefile
    utils_mk --> makefile
    makefile --> gen_manpage_opts
```

Sources: [version.mk:1-12](), [utils.mk:1-619](), [Makefile:1-163]()

## Version Management System

The version management system is the most critical component of the build system, responsible for maintaining consistent version information across all build artifacts. It centers around the `version.mk` file and automated header generation.

### Version Management Flow

```mermaid
graph LR
    subgraph "Version Definition"
        version_mk_file["version.mk"]
        nvidia_version_var["NVIDIA_VERSION = 575.64"]
        nvidia_nvid_version["NVIDIA_NVID_VERSION = 575.64"]
        nvidia_nvid_extra["NVIDIA_NVID_EXTRA = "]
        
        version_mk_file --> nvidia_version_var
        version_mk_file --> nvidia_nvid_version
        version_mk_file --> nvidia_nvid_extra
    end
    
    subgraph "Header Generation"
        version_mk_list["$(lastword $(MAKEFILE_LIST))"]
        outputdir_version_h["$(OUTPUTDIR)/version.h"]
        define_nvidia_version["#define NVIDIA_VERSION \"575.64\""]
        
        version_mk_list --> outputdir_version_h
        outputdir_version_h --> define_nvidia_version
    end
    
    subgraph "Build Integration"
        nv_generated_headers["NV_GENERATED_HEADERS"]
        makefile_include["include $(VERSION_MK)"]
        version_validation["ifndef NVIDIA_VERSION"]
        
        outputdir_version_h --> nv_generated_headers
        version_mk_file --> makefile_include
        makefile_include --> version_validation
    end
    
    nvidia_version_var --> outputdir_version_h
```

The version system operates through several key mechanisms:

| Component | Purpose | Location |
|-----------|---------|----------|
| `NVIDIA_VERSION` | Primary version string | [version.mk:1]() |
| `NVIDIA_NVID_VERSION` | NVID-specific version | [version.mk:2]() |
| `NVIDIA_NVID_EXTRA` | Additional version info | [version.mk:3]() |
| `$(OUTPUTDIR)/version.h` | Generated header file | [version.mk:7-9]() |
| `NV_GENERATED_HEADERS` | Build dependency list | [version.mk:11]() |

The version header generation rule ensures that any changes to `version.mk` trigger regeneration of the version header, maintaining build consistency.

Sources: [version.mk:1-12](), [utils.mk:278-284]()

## Build Configuration System

The `utils.mk` file provides comprehensive cross-platform build configuration, toolchain detection, and compiler flag management. It serves as the foundation for all compilation operations across different operating systems and architectures.

### Toolchain and Platform Detection

```mermaid
graph TB
    subgraph "Toolchain Configuration"
        default_tools["CC ?= gcc, CXX ?= g++, LD ?= ld, AR ?= ar"]
        host_tools["HOST_CC, HOST_LD, HOST_CFLAGS"]
        tool_detection["TEST_CC_ARG, AS_HAS_INSTR"]
        
        default_tools --> host_tools
        default_tools --> tool_detection
    end
    
    subgraph "Platform Detection"
        target_os["TARGET_OS := $(shell uname)"]
        target_arch["TARGET_ARCH := $(shell uname -m)"]
        arch_mapping["x86, x86_64, aarch64, ppc64le"]
        
        target_os --> target_arch
        target_arch --> arch_mapping
    end
    
    subgraph "Compiler Flags"
        base_cflags["CFLAGS += -fno-strict-aliasing"]
        warning_flags["CC_ONLY_CFLAGS += -Wstrict-prototypes"]
        platform_flags["CFLAGS += -DNV_LINUX"]
        arch_flags["CFLAGS += -DNV_X86_64 -DNV_ARCH_BITS=64"]
        
        base_cflags --> warning_flags
        platform_flags --> arch_flags
    end
    
    target_os --> platform_flags
    target_arch --> arch_flags
```

The build configuration system handles multiple aspects:

**Platform-Specific Definitions:**
- Linux: `CFLAGS += -DNV_LINUX` [utils.mk:129-131]()
- FreeBSD: `CFLAGS += -DNV_BSD` [utils.mk:133-135]()
- SunOS: `CFLAGS += -DNV_SUNOS` [utils.mk:137-139]()

**Architecture-Specific Flags:**
- x86: `CFLAGS += -DNV_X86 -DNV_ARCH_BITS=32` [utils.mk:154-156]()
- x86_64: `CFLAGS += -DNV_X86_64 -DNV_ARCH_BITS=64` [utils.mk:158-160]()
- aarch64: `CFLAGS += -DNV_AARCH64 -DNV_ARCH_BITS=64` [utils.mk:166-168]()

**Build Mode Configuration:**
- Debug: `CFLAGS += -O0 -g -DDEBUG=1` [utils.mk:77-84]()
- Release: `CFLAGS += -O2` [utils.mk:83]()
- Development: `CFLAGS += -DDEVELOP=1` [utils.mk:86-90]()

Sources: [utils.mk:35-196](), [utils.mk:125-196]()

## Build Orchestration

The main `Makefile` coordinates the entire build process, integrating version management, build configuration, and source compilation into a cohesive build system.

### Build Target Dependencies

```mermaid
graph TB
    subgraph "Primary Targets"
        all_target["all: $(NVIDIA_MODPROBE) $(MANPAGE)"]
        nvidia_modprobe_target["$(NVIDIA_MODPROBE)"]
        manpage_target["$(MANPAGE)"]
        
        all_target --> nvidia_modprobe_target
        all_target --> manpage_target
    end
    
    subgraph "Source Organization"
        dist_files_mk["dist-files.mk"]
        common_utils_src["$(COMMON_UTILS_DIR)/src.mk"]
        modprobe_utils_src["$(MODPROBE_UTILS_DIR)/nvidia-modprobe-utils.mk"]
        src_list["SRC += $(addprefix ...)"]
        
        dist_files_mk --> src_list
        common_utils_src --> src_list
        modprobe_utils_src --> src_list
    end
    
    subgraph "Object Generation"
        build_object_list["$(call BUILD_OBJECT_LIST,$(SRC))"]
        define_object_rule["$(eval $(call DEFINE_OBJECT_RULE,TARGET,$(src)))"]
        objs_variable["OBJS = $(call BUILD_OBJECT_LIST,$(SRC))"]
        
        src_list --> build_object_list
        build_object_list --> define_object_rule
        build_object_list --> objs_variable
    end
    
    subgraph "Linking"
        unstripped_binary["$(NVIDIA_MODPROBE).unstripped"]
        debug_info_rules["$(eval $(call DEBUG_INFO_RULES, $(NVIDIA_MODPROBE)))"]
        final_binary["$(NVIDIA_MODPROBE)"]
        
        objs_variable --> unstripped_binary
        unstripped_binary --> debug_info_rules
        debug_info_rules --> final_binary
    end
    
    src_list --> objs_variable
    nvidia_modprobe_target --> final_binary
```

The build orchestration follows these key patterns:

**Source File Integration:**
- Main sources: `include dist-files.mk` [Makefile:73]()
- Common utilities: `SRC += $(addprefix $(COMMON_UTILS_DIR)/,$(COMMON_UTILS_SRC))` [Makefile:75-76]()
- Modprobe utilities: `SRC += $(addprefix $(MODPROBE_UTILS_DIR)/,$(MODPROBE_UTILS_SRC))` [Makefile:78-79]()

**Object File Generation:**
- Object list: `OBJS = $(call BUILD_OBJECT_LIST,$(SRC))` [Makefile:81]()
- Build rules: `$(foreach src,$(SRC),$(eval $(call DEFINE_OBJECT_RULE,TARGET,$(src))))` [Makefile:121]()

**Linking Process:**
- Unstripped binary: `$(NVIDIA_MODPROBE).unstripped: $(OBJS)` [Makefile:116]()
- Debug info processing: `$(eval $(call DEBUG_INFO_RULES, $(NVIDIA_MODPROBE)))` [Makefile:115]()

Sources: [Makefile:29-121](), [utils.mk:406-499]()

## Documentation Generation System

The build system includes a sophisticated documentation generation mechanism that creates man pages from command-line option definitions, ensuring synchronization between code and documentation.

### Documentation Build Flow

```mermaid
graph LR
    subgraph "Option Processing"
        gen_manpage_opts_src["gen-manpage-opts.c"]
        gen_manpage_opts_helper["gen-manpage-opts-helper.c"]
        gen_manpage_opts_binary["$(GEN_MANPAGE_OPTS)"]
        
        gen_manpage_opts_src --> gen_manpage_opts_binary
        gen_manpage_opts_helper --> gen_manpage_opts_binary
    end
    
    subgraph "Option Extraction"
        options_1_inc["$(OPTIONS_1_INC)"]
        gen_manpage_opts_execution["$< > $@"]
        
        gen_manpage_opts_binary --> options_1_inc
        gen_manpage_opts_binary --> gen_manpage_opts_execution
    end
    
    subgraph "Man Page Generation"
        nvidia_modprobe_1_m4["nvidia-modprobe.1.m4"]
        m4_processing["$(M4) -D__HEADER__ -D__VERSION__ -D__DATE__"]
        manpage_not_gzipped["$(MANPAGE_not_gzipped)"]
        
        options_1_inc --> nvidia_modprobe_1_m4
        nvidia_modprobe_1_m4 --> m4_processing
        m4_processing --> manpage_not_gzipped
    end
    
    subgraph "Final Processing"
        manpage_gzipped["$(MANPAGE_gzipped)"]
        gzip_compression["$(GZIP_CMD) -9nf"]
        
        manpage_not_gzipped --> gzip_compression
        gzip_compression --> manpage_gzipped
    end
```

The documentation generation system operates through these components:

**Option Extraction Tools:**
- Source generator: `GEN_MANPAGE_OPTS_SRC = gen-manpage-opts.c` [Makefile:139]()
- Helper functions: `GEN_MANPAGE_OPTS_SRC += $(COMMON_UTILS_DIR)/gen-manpage-opts-helper.c` [Makefile:140]()
- Binary target: `GEN_MANPAGE_OPTS = $(OUTPUTDIR_ABSOLUTE)/gen-manpage-opts` [Makefile:45]()

**M4 Template Processing:**
- Version substitution: `-D__VERSION__=$(NVIDIA_VERSION)` [Makefile:156]()
- Date substitution: `-D__DATE__="`$(DATE) +%F`"` [Makefile:157]()
- Build OS: `-D__BUILD_OS__=$(TARGET_OS)` [Makefile:158]()

**Compression Handling:**
- Conditional compression: `ifeq ($(MANPAGE_GZIP),1)` [Makefile:40-44]()
- Gzip processing: `$(GZIP_CMD) -9nf < $< > $@` [Makefile:162]()

Sources: [Makefile:134-163](), [utils.mk:103-117]()

## Build Utility Functions

The build system provides several utility functions and macros that handle complex build operations, dependency tracking, and cross-platform compilation.

### Object Rule Generation System

```mermaid
graph TB
    subgraph "Rule Definition Functions"
        define_object_rule["DEFINE_OBJECT_RULE"]
        define_object_rule_with_dir["DEFINE_OBJECT_RULE_WITH_DIR"]
        define_object_rule_with_object_name["DEFINE_OBJECT_RULE_WITH_OBJECT_NAME"]
        
        define_object_rule --> define_object_rule_with_dir
        define_object_rule_with_dir --> define_object_rule_with_object_name
    end
    
    subgraph "Dependency Tracking"
        auto_dep_suffix["AUTO_DEP_SUFFIX"]
        mmd_flag["-MMD -MF $(@:.o=.d.to_be_processed)"]
        mp_flag["-MP -MT $@"]
        sed_processing["$(SED) -e \"1,3s| $< | |\""]
        
        auto_dep_suffix --> mmd_flag
        auto_dep_suffix --> mp_flag
        auto_dep_suffix --> sed_processing
    end
    
    subgraph "Source Type Detection"
        nv_get_source_type["NV_GET_SOURCE_TYPE"]
        c_files["$(filter %.c, $(1))"]
        cpp_files["$(filter %.cpp, $(1))"]
        
        nv_get_source_type --> c_files
        nv_get_source_type --> cpp_files
    end
    
    subgraph "Build List Generation"
        build_object_list["BUILD_OBJECT_LIST"]
        build_dependency_list["BUILD_DEPENDENCY_LIST"]
        addprefix_outputdir["$(addprefix $(OUTPUTDIR)/,$(notdir ...))"]
        
        build_object_list --> addprefix_outputdir
        build_dependency_list --> addprefix_outputdir
    end
```

**Key Build Functions:**

| Function | Purpose | Usage |
|----------|---------|-------|
| `BUILD_OBJECT_LIST` | Generate object file list | [utils.mk:409-410]() |
| `DEFINE_OBJECT_RULE` | Create compilation rules | [utils.mk:497-499]() |
| `TEST_CC_ARG` | Test compiler arguments | [utils.mk:230-232]() |
| `DEBUG_INFO_RULES` | Handle debug information | [utils.mk:511-526]() |

**Dependency Tracking:**
- Automatic dependency generation: `AUTO_DEP_SUFFIX = -MMD -MF $(@:.o=.d.to_be_processed)` [utils.mk:338-342]()
- Dependency file processing: `$(SED) -e "1,3s| $< | |"` [utils.mk:339]()
- Include dependency files: `-include $(call BUILD_DEPENDENCY_LIST_WITH_DIR,$(3),$(4))` [utils.mk:477]()

**Cross-Platform Support:**
- Host vs. target compilation: `host_target = $(patsubst HOST,HOST_,$(patsubst TARGET,,$(1)))` [utils.mk:309]()
- Source type detection: `NV_GET_SOURCE_TYPE = $(strip $(if $(filter %.c, $(1)),CC, $(if $(filter %.cpp, $(1)),CXX, $(error ...))))` [utils.mk:292-295]()

Sources: [utils.mk:292-499](), [utils.mk:511-526]()

## Output Directory Structure

The build system uses a structured output directory layout that separates build artifacts by target platform and maintains organization across different build configurations.

### Output Directory Organization

```mermaid
graph TB
    subgraph "Base Directory Structure"
        curdir["$(CURDIR)"]
        outputdir["$(OUTPUTDIR) = _out/$(TARGET_OS)_$(TARGET_ARCH)"]
        outputdir_absolute["$(OUTPUTDIR_ABSOLUTE) = $(CURDIR)/$(OUTPUTDIR)"]
        
        curdir --> outputdir
        outputdir --> outputdir_absolute
    end
    
    subgraph "Platform-Specific Directories"
        linux_x86_64["_out/Linux_x86_64/"]
        linux_aarch64["_out/Linux_aarch64/"]
        freebsd_x86_64["_out/FreeBSD_x86_64/"]
        
        outputdir --> linux_x86_64
        outputdir --> linux_aarch64
        outputdir --> freebsd_x86_64
    end
    
    subgraph "Generated Files"
        version_h["$(OUTPUTDIR)/version.h"]
        object_files["$(OUTPUTDIR)/*.o"]
        dependency_files["$(OUTPUTDIR)/*.d"]
        nvidia_modprobe_binary["$(OUTPUTDIR)/nvidia-modprobe"]
        manpage_files["$(OUTPUTDIR)/nvidia-modprobe.1*"]
        
        outputdir_absolute --> version_h
        outputdir_absolute --> object_files
        outputdir_absolute --> dependency_files
        outputdir_absolute --> nvidia_modprobe_binary
        outputdir_absolute --> manpage_files
    end
```

The output directory structure provides:

**Platform Separation:**
- Linux x86_64: `_out/Linux_x86_64/` [utils.mk:197]()
- Linux aarch64: `_out/Linux_aarch64/` [utils.mk:197]()
- FreeBSD x86_64: `_out/FreeBSD_x86_64/` [utils.mk:197]()

**Generated Artifacts:**
- Version header: `$(OUTPUTDIR)/version.h` [version.mk:7]()
- Object files: `$(OUTPUTDIR)/*.o` [utils.mk:406-410]()
- Dependency files: `$(OUTPUTDIR)/*.d` [utils.mk:422-426]()
- Final binary: `$(OUTPUTDIR)/nvidia-modprobe` [Makefile:29]()

**Build Tool Outputs:**
- Option generator: `$(OUTPUTDIR_ABSOLUTE)/gen-manpage-opts` [Makefile:45]()
- Option includes: `$(OUTPUTDIR)/options.1.inc` [Makefile:46]()
- Manual pages: `$(OUTPUTDIR)/nvidia-modprobe.1[.gz]` [Makefile:37-38]()

Sources: [utils.mk:197-198](), [version.mk:7-11](), [Makefile:29-46]()

---

