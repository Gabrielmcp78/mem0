# FoundationModels Test Suite

A clean, modular test suite for FoundationModels functionality on macOS with Apple Silicon.

## Quick Start

### Simple Usage
```python
from tests.foundation_models import run_foundation_models_tests

# Run all tests
success = run_foundation_models_tests()
```

### Command Line
```bash
# Run all tests
python -m tests.foundation_models.cli

# Quick availability check
python -m tests.foundation_models.cli --quick

# List available tests
python -m tests.foundation_models.cli --list
```

## Architecture

The test suite is organized into focused modules:

- **`test_runner.py`** - Test orchestration and execution
- **`test_cases.py`** - Individual test implementations  
- **`test_reporter.py`** - Output formatting and reporting
- **`config.py`** - Configuration and constants
- **`cli.py`** - Command-line interface

## Available Tests

### Core Tests
- `framework_loading` - Load Foundation Models framework
- `model_initialization` - Initialize FoundationModels model
- `availability_check` - Check model availability

### Advanced Tests  
- `session_creation` - Create language model session
- `semantic_analysis_setup` - Setup semantic analyzer
- `semantic_analysis` - Test semantic analysis functionality

## Usage Examples

### Run Specific Tests
```python
from tests.foundation_models import FoundationModelsTestRunner

runner = FoundationModelsTestRunner()
results = runner.run_specific_tests(['framework_loading', 'availability_check'])
success = runner.print_summary()
```

### Get Test Results
```python
runner = FoundationModelsTestRunner()
runner.run_all_tests()

failed_tests = runner.get_failed_tests()
passed_tests = runner.get_passed_tests()
```

### Command Line Options
```bash
# Core tests only
python -m tests.foundation_models.cli --core

# Advanced tests only  
python -m tests.foundation_models.cli --advanced

# Specific tests
python -m tests.foundation_models.cli --tests framework_loading model_initialization

# Verbose output
python -m tests.foundation_models.cli --verbose
```

## Configuration

Test settings are centralized in `config.py`:

```python
from tests.foundation_models import TestConfig

# Test categories
TestConfig.CORE_TESTS
TestConfig.ADVANCED_TESTS
TestConfig.ALL_TESTS

# Sample text for analysis
TestConfig.SAMPLE_TEXT

# Timeouts
TestConfig.FRAMEWORK_LOAD_TIMEOUT
TestConfig.MODEL_INIT_TIMEOUT
```

## Requirements

- macOS 15.1+
- Apple Silicon (M1/M2/M3/M4)
- PyObjC for Foundation Models access
- Python 3.9+

## Backward Compatibility

The original `test_apple_intelligence_modular.py` interface is maintained:

```python
# This still works
from test_apple_intelligence_modular import AppleIntelligenceTestSuite

test_suite = AppleIntelligenceTestSuite()
test_suite.run_all_tests()
test_suite.print_summary()
```

## Benefits

- **Modular Design** - Each component has a single responsibility
- **Easy Testing** - Components can be tested independently
- **Flexible Usage** - Multiple ways to run tests
- **Clean Output** - Consistent, formatted reporting
- **CLI Interface** - Command-line options for different scenarios
- **Backward Compatible** - Existing code continues to work

## Troubleshooting

If tests fail, check:
- Running on macOS 15.1+ with Apple Silicon
- FoundationModels framework is available
- PyObjC is properly installed
- System resources and memory availability

Use `--verbose` flag for detailed output during debugging.