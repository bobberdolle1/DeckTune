# Requirements Document

## Introduction

DeckTune 3.1 focuses on reliability improvements, performance optimizations, and UX enhancements. This release adds crash recovery metrics, real-time telemetry graphs, improved communication between frontend and backend, and a guided setup wizard for new users.

## Glossary

- **DeckTune**: The Steam Deck undervolting plugin
- **gymdeck3**: Rust daemon for dynamic undervolt mode
- **Crash Recovery**: System that restores safe values after system freeze/reboot
- **LKG (Last Known Good)**: Last stable undervolt values before a crash
- **Telemetry**: Real-time temperature, power, and load data
- **NDJSON**: Newline-delimited JSON format used by gymdeck3 output
- **Platform Detection**: Automatic identification of Steam Deck model (LCD/OLED)

## Requirements

### Requirement 1: Crash Recovery Metrics

**User Story:** As a user, I want to see how many times crash recovery has saved my system, so that I can understand the stability of my undervolt settings.

#### Acceptance Criteria

1. WHEN the system boots after a crash during tuning THEN DeckTune SHALL increment a persistent crash counter and record the timestamp
2. WHEN a user opens the Diagnostics tab THEN DeckTune SHALL display total crash recovery count, last crash date, and the values that caused the crash
3. WHEN crash recovery activates THEN DeckTune SHALL log the crashed values, restored LKG values, and recovery reason to a persistent crash history
4. WHEN a user exports diagnostics THEN DeckTune SHALL include the complete crash recovery history in the archive
5. WHEN the crash history exceeds 50 entries THEN DeckTune SHALL remove the oldest entries to maintain the limit

### Requirement 2: Real-Time Telemetry Graphs

**User Story:** As a user, I want to see live graphs of temperature and power consumption, so that I can monitor the impact of my undervolt settings.

#### Acceptance Criteria

1. WHEN gymdeck3 is running THEN DeckTune SHALL collect temperature readings from hwmon sensors at 1-second intervals
2. WHEN gymdeck3 is running THEN DeckTune SHALL collect power consumption data from ryzenadj at 1-second intervals
3. WHEN a user views the monitoring panel THEN DeckTune SHALL display a scrolling line graph showing the last 60 seconds of temperature data
4. WHEN a user views the monitoring panel THEN DeckTune SHALL display a scrolling line graph showing the last 60 seconds of power consumption data
5. WHEN telemetry data is collected THEN DeckTune SHALL store the data in a circular buffer limited to 300 samples (5 minutes)
6. WHEN the user hovers over a graph point THEN DeckTune SHALL display the exact value and timestamp

### Requirement 3: Platform Detection Caching

**User Story:** As a user, I want the plugin to start faster, so that I can access settings without delay.

#### Acceptance Criteria

1. WHEN DeckTune detects the platform for the first time THEN DeckTune SHALL cache the detection result to persistent storage
2. WHEN DeckTune starts and a valid cache exists THEN DeckTune SHALL use the cached platform data instead of re-detecting
3. WHEN the cached platform data is older than 30 days THEN DeckTune SHALL re-detect the platform and update the cache
4. WHEN a user manually triggers platform re-detection THEN DeckTune SHALL clear the cache and perform fresh detection
5. WHEN the cache file is corrupted or invalid THEN DeckTune SHALL fall back to fresh detection without error

### Requirement 4: Streaming Status Updates

**User Story:** As a user, I want to see real-time status updates without lag, so that I can monitor dynamic mode responsively.

#### Acceptance Criteria

1. WHEN gymdeck3 emits a status update THEN DeckTune backend SHALL forward it to the frontend within 100ms
2. WHEN the frontend subscribes to status updates THEN DeckTune SHALL use server-sent events instead of polling
3. WHEN gymdeck3 is not running THEN DeckTune SHALL not send unnecessary status updates to the frontend
4. WHEN the frontend reconnects after disconnect THEN DeckTune SHALL resume status streaming without requiring page reload
5. WHEN status updates fail to deliver THEN DeckTune SHALL buffer up to 10 updates and retry delivery

### Requirement 5: Setup Wizard

**User Story:** As a new user, I want a guided setup process, so that I can configure DeckTune safely without reading documentation.

#### Acceptance Criteria

1. WHEN a user opens DeckTune for the first time THEN DeckTune SHALL display a welcome wizard with step-by-step guidance
2. WHEN the wizard starts THEN DeckTune SHALL explain what undervolting is and its benefits/risks in simple terms
3. WHEN the wizard reaches the goal selection step THEN DeckTune SHALL offer preset goals: Quiet/Cool, Balanced, Max Battery, Max Performance with explanations
4. WHEN the user selects a goal THEN DeckTune SHALL show estimated battery improvement and temperature reduction for that goal
5. WHEN the wizard completes THEN DeckTune SHALL save the user's preferences and mark first-run as complete
6. WHEN a user wants to re-run the wizard THEN DeckTune SHALL provide a "Run Setup Wizard" option in settings
7. WHEN the wizard is running THEN DeckTune SHALL allow the user to skip or cancel at any step without applying changes

### Requirement 6: Rust Config Fuzzing Infrastructure

**User Story:** As a developer, I want automated fuzzing for config parsing, so that I can catch edge cases and prevent crashes from malformed input.

#### Acceptance Criteria

1. WHEN the fuzzing suite runs THEN gymdeck3 config parser SHALL handle arbitrary byte sequences without panicking
2. WHEN the fuzzing suite runs THEN gymdeck3 CLI argument parser SHALL reject invalid inputs gracefully with error messages
3. WHEN a fuzz test discovers a crash THEN the fuzzing infrastructure SHALL save the crashing input for reproduction
4. WHEN fuzzing completes THEN the infrastructure SHALL report code coverage percentage for the config module
5. WHEN a new config field is added THEN the fuzzing dictionary SHALL be updated to include the new field name

### Requirement 7: Frontend-Backend Integration Tests

**User Story:** As a developer, I want automated tests for frontend-backend communication, so that I can catch RPC contract violations before release.

#### Acceptance Criteria

1. WHEN integration tests run THEN the test suite SHALL verify all RPC methods return expected response shapes
2. WHEN integration tests run THEN the test suite SHALL verify event payloads match TypeScript type definitions
3. WHEN an RPC method signature changes THEN integration tests SHALL fail if frontend types are not updated
4. WHEN integration tests run THEN the test suite SHALL verify error responses include proper error codes and messages
5. WHEN a new RPC method is added THEN the test suite SHALL require a corresponding integration test

### Requirement 8: Session History with Metrics

**User Story:** As a user, I want to see a history of my gaming sessions with performance metrics, so that I can track the effectiveness of my undervolt settings over time.

#### Acceptance Criteria

1. WHEN gymdeck3 starts THEN DeckTune SHALL create a new session record with start timestamp and initial settings
2. WHEN gymdeck3 stops THEN DeckTune SHALL finalize the session record with end timestamp and calculated metrics
3. WHEN a session ends THEN DeckTune SHALL calculate and store: total duration, average temperature, min/max temperature, average power consumption, and estimated battery savings
4. WHEN a user views the session history THEN DeckTune SHALL display the last 30 sessions with key metrics in a list view
5. WHEN a user selects a session THEN DeckTune SHALL display detailed metrics including temperature graph, power graph, and undervolt values used
6. WHEN a user wants to compare sessions THEN DeckTune SHALL allow selecting two sessions and display side-by-side metric comparison
7. WHEN session history exceeds 100 entries THEN DeckTune SHALL archive older sessions to a separate file and keep only the last 100 in active storage
8. WHEN a user exports diagnostics THEN DeckTune SHALL include session history summary in the archive
