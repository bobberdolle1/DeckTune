# gymdeck3 Fuzzing

This directory contains fuzz targets for testing gymdeck3's config parsing robustness.

## Requirements

- Rust nightly toolchain
- cargo-fuzz: `cargo install cargo-fuzz`

## Fuzz Targets

### fuzz_config_parser
Tests string parsing functions with arbitrary UTF-8 input:
- `parse_core_config()`
- `validate_sample_interval()`
- `validate_hysteresis()`
- `parse_fan_curve_point()`
- `validate_fan_hysteresis()`
- `parse_acoustic_profile()`

### fuzz_core_config
Tests `validate_core_config_values()` with arbitrary numeric values.

### fuzz_fan_curve
Tests `validate_fan_curve_point()` with arbitrary numeric values.

## Running Fuzz Tests

```bash
# Install cargo-fuzz (one-time)
cargo install cargo-fuzz

# Run a specific fuzz target
cd gymdeck3
cargo +nightly fuzz run fuzz_config_parser

# Run with dictionary for better coverage
cargo +nightly fuzz run fuzz_config_parser -- -dict=fuzz/dict/config.dict

# Run for a specific duration (e.g., 60 seconds)
cargo +nightly fuzz run fuzz_config_parser -- -max_total_time=60

# List all fuzz targets
cargo +nightly fuzz list
```

## Crash Artifacts

When a crash is found, the crashing input is saved to:
- `fuzz/artifacts/fuzz_config_parser/crash-<hash>`

To reproduce a crash:
```bash
cargo +nightly fuzz run fuzz_config_parser fuzz/artifacts/fuzz_config_parser/crash-<hash>
```

## Coverage

To generate coverage report:
```bash
cargo +nightly fuzz coverage fuzz_config_parser
```

## Property Being Tested

**Feature: decktune-3.1-reliability-ux, Property 12: Fuzzing no-panic guarantee**
**Validates: Requirements 6.1, 6.2**

*For any* byte sequence input to the config parser, the parser SHALL not panic and SHALL return either a valid config or an error.
