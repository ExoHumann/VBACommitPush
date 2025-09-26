# SPOT_VISO

SPOT_VISO bridge geometry and visualization system.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Check system integrity
spotviso check

# Run smoke tests
spotviso test -m smoke

# Run all tests  
spotviso test

# Visualize a case
spotviso viz --case <id>
```

## Development

```bash
pip install -e .[dev]
```