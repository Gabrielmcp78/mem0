# FoundationModels Package

A modular, clean interface for FoundationModels operations on macOS with Apple Silicon.

## Architecture

The package is organized into focused modules with single responsibilities:

### Core Modules

- **`client.py`** - High-level client interface for end users
- **`factory.py`** - Factory pattern for creating components
- **`status.py`** - Availability checking and status management
- **`__init__.py`** - Package interface and exports

### Design Principles

- **Single Responsibility** - Each module has one clear purpose
- **Factory Pattern** - Clean object creation with error handling
- **Caching** - Status checks are cached for performance
- **Error Handling** - Proper exception hierarchy and propagation
- **Backward Compatibility** - Maintains existing API contracts

## Usage Examples

### Simple Usage (Recommended)

```python
from apple_intelligence import AppleIntelligenceClient

# Create client (auto-initializes)
client = AppleIntelligenceClient()

if client.is_ready:
    # Analyze text
    result = client.analyze_text("Your text here")
    
    # Create session
    session = client.create_session("Custom instructions")
    
    # Get status
    status = client.get_status()
```

### Quick Checks

```python
from apple_intelligence import is_apple_intelligence_ready, get_apple_intelligence_status

# Simple boolean check
if is_apple_intelligence_ready():
    print("FoundationModels is available!")

# Get detailed status
status = get_apple_intelligence_status()
print(f"Status: {status}")
```

### Factory Pattern

```python
from apple_intelligence import create_semantic_analyzer, create_model

# Create components directly
analyzer = create_semantic_analyzer()
if analyzer:
    result = analyzer.analyze("Text to analyze")

# Create model for custom usage
model = create_model()
if model:
    session = model.create_session()
```

### Advanced Usage

```python
from apple_intelligence import (
    AppleIntelligenceFactory,
    StatusChecker,
    FoundationModelsFramework,
    AppleIntelligenceModel
)

# Custom factory usage
factory = AppleIntelligenceFactory()
framework, model, analyzer = factory.create_complete_stack()

# Custom status checking
status_checker = StatusChecker()
status_checker.clear_cache()  # Force fresh check
availability = status_checker.check_availability(use_cache=False)
```

## Benefits of Modular Design

### 1. **Separation of Concerns**
- Status checking isolated from component creation
- Client interface separated from low-level operations
- Factory pattern centralizes object creation logic

### 2. **Better Testing**
- Each module can be tested independently
- Mock objects easier to create for specific modules
- Clear interfaces make unit testing straightforward

### 3. **Improved Maintainability**
- Changes localized to specific modules
- Clear dependencies between components
- Easy to extend without modifying existing code

### 4. **Performance Optimizations**
- Status caching reduces redundant system calls
- Lazy initialization only when needed
- Factory pattern enables object pooling if needed

### 5. **Clean Error Handling**
- Consistent error propagation across modules
- Proper exception hierarchy
- Graceful degradation when components fail

### 6. **Backward Compatibility**
- Existing code continues to work unchanged
- Gradual migration path to new interfaces
- No breaking changes to public APIs

## Migration Guide

### From `apple_intelligence_utils.py`

**Old way:**
```python
from apple_intelligence_utils import SimpleAppleIntelligence, is_apple_intelligence_ready

ai = SimpleAppleIntelligence()
if ai.initialize():
    result = ai.analyze_text("text")
```

**New way (same functionality):**
```python
from apple_intelligence import AppleIntelligenceClient, is_apple_intelligence_ready

client = AppleIntelligenceClient()  # Auto-initializes
if client.is_ready:
    result = client.analyze_text("text")
```

**Or keep using the old interface:**
```python
# This still works exactly the same
from apple_intelligence_utils import SimpleAppleIntelligence
```

## File Structure

```
apple_intelligence/
├── __init__.py          # Package interface
├── client.py            # High-level client
├── factory.py           # Component factory
├── status.py            # Status checking
└── README.md           # This file

# Backward compatibility
apple_intelligence_utils.py  # Wrapper for old interface
```

## Requirements

- macOS 15.1+
- Apple Silicon (M1/M2/M3/M4)
- PyObjC for Foundation Models access
- Python 3.9+

## Error Handling

All modules use the same `AppleIntelligenceError` exception hierarchy:

```python
from apple_intelligence import AppleIntelligenceError

try:
    client = AppleIntelligenceClient()
    result = client.analyze_text("text")
except AppleIntelligenceError as e:
    print(f"FoundationModels error: {e}")
```

## Performance Notes

- Status checks are cached by default (use `clear_status_cache()` to refresh)
- Factory creates components on-demand
- Client auto-initializes but can be controlled with `auto_initialize=False`
- All operations are synchronous (FoundationModels is local/fast)

This modular design provides a clean, maintainable foundation for FoundationModels integration while preserving all existing functionality.