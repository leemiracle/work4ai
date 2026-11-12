# Backward Compatibility (bc) Layer

This folder contains backward compatibility mixins for maintaining v1/v2 SDK method support while implementing the modern v3 API.

## Purpose

- **Isolate legacy code**: Keep main endpoint files clean with v3 implementation
- **Maintain compatibility**: Ensure existing user code continues to work
- **Easy removal**: Can be removed in future major versions by just removing mixin inheritance

## Structure

```
bc/
├── __init__.py          # Exports all mixins
├── base.py              # Common patterns across all endpoints
├── simulation.py        # Simulation-specific v1/v2 methods
├── node.py              # Node-specific v1/v2 methods
├── interface.py         # Interface-specific v1/v2 methods
.
.
.
├── utils.py             # Shared utility functions
└── README.md            # This file
```

## Usage Pattern

### 1. Create Compat Mixin

**File**: `bc/your_endpoint.py`

```python
class YourEndpointCompatMixin:
    """v1/v2 compatibility for YourEndpoint."""
    
    def old_method_name(self, *args, **kwargs):
        """Legacy method from v1/v2. Use new_method_name() instead."""
        return self.new_method_name(*args, **kwargs)
```

### 2. Export from __init__.py

**File**: `bc/__init__.py`

```python
from .your_endpoint import YourEndpointCompatMixin

__all__ = [..., 'YourEndpointCompatMixin']
```

### 3. Inherit in Endpoint

**File**: `endpoints/your_endpoint.py`

```python
from air_sdk.bc import BaseCompatMixin, YourEndpointCompatMixin

@dataclass(eq=False)
class YourEndpoint(BaseCompatMixin, YourEndpointCompatMixin, AirModel):
    # Modern v3 implementation
    def new_method_name(self):
        """v3 method."""
        pass
```

## Example: Simulation

See `simulation.py` for a complete example:

**v1/v2 Methods** (in bc/simulation.py):
- `load()` → calls `start()`
- `stop()` → calls `shutdown()`
- `store()` → calls `shutdown()`
- `control(action='load')` → calls `start()`
- `control(action='store')` → calls `shutdown()`

**v3 Methods** (in endpoints/simulations.py):
- `start()` - modern method
- `shutdown()` - modern method

## Guidelines

### DO ✅

- Create one mixin per endpoint
- Document what v1/v2 method maps to in v3
- Add type: ignore comments for methods from parent class
- Keep bc code simple - just wrapper calls
- Test both v1/v2 and v3 patterns

### DON'T ❌

- Put v3 implementation in bc layer
- Mix v3 and legacy code in same file
- Remove legacy methods (breaks user code) if its not a must
- Add complex logic in bc mixins
- Include legacy methods in stub files

## Field Name Mappings (v1/v2 → v3)

The BC layer automatically handles field name changes between versions:

### Simulation Fields

#### Direct Field Mappings (Bidirectional)
- **`title` ↔ `name`** (v1/v2 ↔ v3)
  - v1/v2: `simulation.title` or `simulation.update(title='My Sim')`
  - v3: `simulation.name` or `simulation.update(name='My Sim')`
  - BC: Both work transparently

**Note:** `auto_oob_enabled` was NOT exposed in SDK v1/v2 (even though Manager API returned it), so no BC mapping is needed.

#### Computed Properties (Read-Only)
- **`sleep`** (v1/v2 computed from `sleep_at`)
  - Returns: `True` if `sleep_at` is set, `False` otherwise
  - Example: `if simulation.sleep: ...`

- **`expires`** (v1/v2 computed from `expires_at`)
  - Returns: `True` if `expires_at` is set, `False` otherwise
  - Example: `if simulation.expires: ...`

#### Method Parameter Mappings
- **`start` → `attempt_start`** in clone/duplicate (v1/v2 → v3)
  - v1/v2: `simulation.duplicate(start=True)`
  - v3: `simulation.clone(attempt_start=True)`
  - BC: `simulation.duplicate(start=True)` automatically maps to `attempt_start`

### New v3 Fields
- **`checkpoint`** in `start()` - Optional checkpoint ID to start from (v3 new field)
- **`create_checkpoint`** in `shutdown()` - Create checkpoint before shutdown (v3 new field)
- **`enable_dhcp`** in `enable_auto_oob()` - Enable/disable DHCP on OOB network (v3 new field)
  - BC: v2 `disable_auto_oob_dhcp` maps to `enable_dhcp` with inverted semantics
  - BC: `simulation.disable_auto_oob_dhcp` property provides read access (inverted from `enable_dhcp`)

## Methods NOT Migrated to v3

Some v1/v2 methods are **intentionally not supported** in v3 due to architectural changes:

### Simulation - NOT SUPPORTED
- `add_permission(email, **kwargs)` - **REMOVED**
  - Reason: NGC organization-level permission model replaces simulation-level permissions
  - Migration: Use NGC org permissions through NGC console

### Simulation - PENDING Implementation
- `create_service(name, interface, dest_port)` - **PENDING**
  - Will be available when Services endpoint is added
  - Currently raises `NotImplementedError` with clear message
  
- `preferences()` - **PENDING**
  - Will be available when UserPreferences endpoint is added
  - Preferences system may have been redesigned in v3
  - Currently raises `NotImplementedError`

## Testing

```python
def test_v1_v2_compatibility():
    """Test that legacy methods still work."""
    simulation = api.simulations.get('sim-id')
    
    # v1/v2 style (should work)
    simulation.load()
    simulation.stop()
    simulation.control(action='load')
    
def test_v3_recommended():
    """Test modern v3 methods."""
    simulation = api.simulations.get('sim-id')
    
    # v3 style (recommended)
    simulation.start()
    simulation.shutdown()
```