# DeckTune

**Current Stable Version**: v3.1.26 | [Branch Info](BRANCHES.md)

**English** | [Русский](#russian)

---

## English

**DeckTune** — an automated undervolting tool for Steam Deck (LCD/OLED) with safety guarantees. Transforms the complex tuning process into a one-button procedure with automatic optimal value discovery.

### Features

- **Auto Platform Detection** — LCD (Jupiter) or OLED (Galileo) with appropriate limits
- **Autotune** — automatic discovery of optimal values for your specific chip
- **Automated Silicon Binning** — discover your chip's maximum stable undervolt automatically
- **Per-Game Profiles** — automatic profile switching based on running game
- **Settings Management** — centralized settings with persistent storage and Game Only Mode
- **Low-Level Fan Control** — custom fan curves with visual editor and safety overrides
- **Safety System** — watchdog, automatic rollback on freeze, LKG (Last Known Good)
- **Built-in Stress Tests** — CPU, RAM, Combo for stability verification
- **Benchmarking** — quick performance testing with before/after comparison
- **Presets** — global and per-game settings with auto-apply
- **Diagnostics** — one-click export of logs and system info
- **Dynamic Mode** — automatic adjustment based on load (gymdeck3)

### Installation

#### Requirements

- Steam Deck (LCD or OLED)
- [Decky Loader](https://decky.xyz/)
- SteamOS

#### Quick Install

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

#### Manual Install

1. Download the latest release from [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Transfer the archive to your Steam Deck
3. Enable Developer Mode in Decky Loader settings
4. Install the plugin from the archive

### Usage

**📖 For detailed guides, see [User Guide](docs/USER_GUIDE.md)**

#### Wizard Mode (for beginners)

1. Open DeckTune in the Decky menu
2. Select your goal: Quiet/Cool, Balanced, Max Battery, Max Performance
3. Wait for autotune to complete
4. Click "Apply & Save"

#### Expert Mode (for power users)

- **Manual** — manual per-core value adjustment
- **Presets** — preset management (create, edit, export/import)
- **Tests** — run stress tests manually
- **Diagnostics** — view logs and export diagnostics

#### Dynamic Mode (gymdeck3)

Dynamic Mode automatically adjusts undervolt values based on real-time CPU load, providing optimal balance between performance and efficiency.

**Features:**
- **Adaptive Strategies**: Conservative (5s ramp), Balanced (2s ramp), Aggressive (500ms ramp), Custom
- **Per-Core Control**: Independent load monitoring and value adjustment for each CPU core
- **Hysteresis**: Prevents value hunting with configurable dead-band (1-20%)
- **Smooth Transitions**: Linear interpolation with 1mV steps for stability
- **Safety**: Watchdog, automatic rollback, respects platform limits

**How it works:**
1. Monitors CPU load from `/proc/stat` in real-time
2. Calculates optimal undervolt based on current load and strategy
3. Applies values smoothly via ryzenadj
4. Higher load → safer (less aggressive) values
5. Lower load → more aggressive values for better efficiency

**Configuration Profiles:**
- Battery Saver (conservative, max battery life)
- Balanced (moderate responsiveness)
- Performance (fast adaptation)
- Custom (user-defined load curves)

#### Dynamic Manual Mode (NEW in v3.2.0)

Dynamic Manual Mode provides granular per-core voltage curve control with real-time visualization, optimized for Steam Deck's QAM interface.

**Features:**
- **Per-Core Voltage Curves**: Configure independent voltage curves for each CPU core (0-3)
  - MinimalValue: Conservative voltage at low CPU load (-100 to 0 mV)
  - MaximumValue: Aggressive voltage at high CPU load (-100 to 0 mV)
  - Threshold: CPU load percentage where transition occurs (0-100%)
- **Simple Mode**: Apply identical settings to all cores simultaneously for quick configuration
- **Expert Mode**: Fine-tune each core individually for maximum optimization
- **Real-Time Visualization**: 
  - Live voltage curve graphs with threshold markers
  - Real-time metrics display (load, voltage, frequency, temperature)
  - Time-series graphs with 60-point FIFO buffer
  - Updates every 500ms when active
- **QAM Optimized**: Compact UI designed to fit perfectly in Decky Loader's Quick Access Menu
- **Gamepad Navigation**: Full Steam Deck controller support
  - D-pad Up/Down: Switch between cores
  - D-pad Left/Right: Navigate controls
  - L1/R1: Adjust slider values
  - A button: Activate buttons
- **Safety Features**:
  - Validation with min ≤ max enforcement
  - Platform limit clamping (-100 to 0 mV)
  - Dangerous configuration warnings
  - Last Known Good (LKG) configuration backup
  - Automatic rollback on errors
- **Configuration Persistence**: 
  - localStorage for instant loading
  - Backend storage for cross-session persistence
  - Safe defaults fallback

**How to Use:**
1. Open DeckTune → Expert Mode → Dynamic Manual tab
2. Choose Simple Mode (all cores) or Expert Mode (per-core)
3. Adjust voltage curve parameters with sliders
4. View real-time curve visualization
5. Click Apply to save configuration
6. Click Start to activate dynamic voltage control
7. Monitor real-time metrics and graphs

**Documentation:**
- [User Guide](docs/DYNAMIC_MANUAL_MODE_GUIDE.md) - Complete usage instructions
- [API Reference](docs/DYNAMIC_MANUAL_MODE_API.md) - RPC methods and data structures
- [Troubleshooting](docs/DYNAMIC_MANUAL_MODE_TROUBLESHOOTING.md) - Common issues and solutions
- [QAM Optimization](docs/QAM_OPTIMIZATION.md) - UI design for Quick Access Menu
- **Safety Validation**: Multi-layer validation prevents dangerous configurations
- **Persistent Storage**: Configurations saved to localStorage and backend settings

**How it works:**
1. Define a voltage curve for each core using three parameters:
   - **Minimal Value** (-100 to 0 mV): Voltage offset at low CPU load
   - **Maximum Value** (-100 to 0 mV): Voltage offset at high CPU load
   - **Threshold** (0-100%): CPU load percentage where transition occurs
2. Below threshold: Applies Minimal Value (more aggressive undervolt)
3. Above threshold: Linear interpolation from Minimal to Maximum Value
4. System monitors CPU load every 500ms and applies appropriate voltage

**Usage (Expert Mode → Dynamic Manual Tab):**

**Simple Mode (Recommended for beginners):**
1. Enable Simple Mode toggle
2. Adjust three sliders:
   - Minimal Value: Voltage at low load (e.g., -30mV)
   - Maximum Value: Voltage at high load (e.g., -15mV)
   - Threshold: Load transition point (e.g., 50%)
3. Click "Apply" to save configuration
4. Click "Start Dynamic Mode" to activate
5. Monitor real-time metrics and voltage curve graph

**Expert Mode (Per-core control):**
1. Disable Simple Mode toggle
2. Select a core using tabs (Core 0, Core 1, Core 2, Core 3)
3. Adjust sliders for selected core
4. Repeat for each core you want to configure
5. Click "Apply" to save all configurations
6. Click "Start Dynamic Mode" to activate
7. Switch between cores to monitor individual metrics

**Example Configuration:**

*Balanced Profile (Simple Mode):*
```
Minimal Value: -30mV  (aggressive at idle)
Maximum Value: -15mV  (safe under load)
Threshold: 50%        (transition at medium load)
```

*Performance Profile (Expert Mode):*
```
Core 0: -35mV → -20mV @ 60%  (primary core, aggressive)
Core 1: -30mV → -15mV @ 50%  (balanced)
Core 2: -25mV → -10mV @ 40%  (conservative)
Core 3: -25mV → -10mV @ 40%  (conservative)
```

**Gamepad Controls:**
- **D-pad Up/Down**: Switch between cores (Expert Mode)
- **D-pad Left/Right**: Navigate between sliders and buttons
- **L1/R1**: Adjust slider values (±1mV or ±1%)
- **A Button**: Activate focused button (Apply, Start, Stop)
- **B Button**: Cancel/Go back

**Safety Features:**
- **Validation**: Prevents min > max configurations
- **Clamping**: Enforces -100mV to 0mV voltage range
- **Platform Limits**: Respects hardware-specific safety limits
- **Warning Dialogs**: Alerts for potentially dangerous settings
- **Reset to Safe Defaults**: One-click restore to -30mV/-15mV/50%
- **Last Known Good**: Automatic recovery from unstable configurations

**Real-Time Monitoring:**
- **Voltage Curve Graph**: Visual representation of voltage vs. CPU load
- **Current Operating Point**: Live marker showing current load and voltage
- **Metrics Display**: 
  - CPU Load (0-100%)
  - Voltage Offset (mV)
  - Frequency (MHz)
  - Temperature (°C)
- **Time-Series Graph**: Last 60 data points (30 seconds of history)
- **Status Indicator**: Active/Inactive state with visual feedback

**Configuration Persistence:**
- Saved to localStorage for immediate access
- Backed up to backend settings for cross-session persistence
- Survives plugin reloads and system reboots
- Separate storage for Simple Mode and Expert Mode configurations

**Troubleshooting:**

*Dynamic mode won't start:*
- Verify all voltage values are between -100mV and 0mV
- Ensure Minimal Value ≤ Maximum Value for all cores
- Check that gymdeck3 daemon is running
- Review backend logs for RPC errors

*System becomes unstable:*
- Click "Stop Dynamic Mode" immediately
- Click "Reset to Safe Defaults" to restore conservative values
- Reduce voltage aggressiveness (increase Minimal/Maximum values toward 0)
- Increase Threshold to transition earlier under load

*Metrics not updating:*
- Verify Dynamic Mode status shows "Active"
- Check that polling interval is 500ms (automatic)
- Ensure gymdeck3 has permissions to read `/proc/stat` and hwmon
- Restart plugin if metrics remain frozen

*Configuration not persisting:*
- Check browser localStorage is enabled
- Verify backend settings file permissions: `~/homebrew/settings/decktune/settings.json`
- Review backend logs for write errors
- Try "Apply" button again to force save

**Best Practices:**
- Start with Simple Mode and safe defaults (-30mV/-15mV/50%)
- Test stability with stress tests before aggressive values
- Use Expert Mode only if you understand per-core behavior
- Monitor temperature and frequency during initial testing
- Create separate configurations for different workloads
- Keep Maximum Value more conservative (closer to 0) for stability under load

#### Panic Disable Button

The red "Panic Disable" button is always available — instantly resets all values to 0.

### Settings Management (NEW in v3.1.26)

DeckTune 3.1.26 introduces a comprehensive settings management system with persistent storage and advanced features.

**Features:**
- **Header Bar Navigation**: Compact icon-based access to Fan Control and Settings
- **Settings Menu**: Centralized modal for global plugin configuration
- **Expert Mode**: Advanced mode with confirmation dialog and safety warnings
- **Apply on Startup**: Automatically apply your last profile when Steam Deck boots
- **Game Only Mode**: Apply undervolt only during games, reset to default in Steam menu
- **Persistent Storage**: All settings survive plugin reloads and system reboots

**Usage (Settings Menu):**
1. Click the Settings icon (⚙️) in the header bar
2. Toggle Expert Mode (requires confirmation for safety)
3. Settings are saved automatically

**Usage (Manual Tab - Startup Behavior):**
1. Open Expert Mode → Manual tab
2. Enable "Apply on Startup" to auto-apply last profile on boot
3. Enable "Game Only Mode" to apply undervolt only during games
4. Settings persist across reboots

**Game Only Mode:**
- Monitors Steam game launches and exits
- Applies your saved undervolt profile when a game starts
- Resets undervolt to 0 (default) when you exit to Steam menu
- Transitions happen within 2 seconds
- Perfect for users who want performance during gaming but stability in menus

**Apply on Startup:**
- Automatically applies your last active profile during plugin initialization
- No need to manually apply settings after each reboot
- Skips application if no previous profile exists
- Logs all startup application results

**Technical Details:**
- Backend storage: `~/homebrew/settings/decktune/settings.json`
- Atomic writes with backup for data safety
- Game state monitoring via Steam events with polling fallback
- React Context API for unified settings access across components
- Graceful error handling with fallback to default values

### Automated Silicon Binning

Silicon Binning automatically discovers your chip's maximum stable undervolt through iterative testing with crash recovery.

**How it works:**
1. Starts at -10mV and tests progressively lower values in -5mV steps
2. Each iteration runs a 60-second stress test (CPU + memory)
3. State is persisted before each test for crash recovery
4. If system crashes, boot recovery detects it and restores last stable value
5. Recommends a safe value with 5mV safety margin

**Usage (Wizard Mode):**
1. Click "Find Max Undervolt" button
2. Wait for binning to complete (typically 5-15 minutes)
3. Review discovered maximum and recommended value
4. Click "Apply Recommended" to use the safe value

**Configuration (Advanced):**
- Test Duration: 30-300 seconds per iteration (default: 60s)
- Step Size: 1-10mV increments (default: 5mV)
- Start Value: 0 to -20mV starting point (default: -10mV)

**Safety Features:**
- Persistent state for crash recovery
- Maximum iteration limit (20 attempts)
- Platform limit enforcement
- Consecutive failure abort (3 failures)
- Cancellation with instant rollback

### Per-Game Profiles

Automatically switch undervolt settings based on the currently running Steam game.

**Features:**
- **Automatic Detection**: Monitors Steam's active game via AppID
- **Quick-Create**: Save current settings as profile for active game
- **Global Default**: Fallback settings when no game-specific profile exists
- **Import/Export**: Share profiles with other users or backup settings
- **Profile Switching**: Seamless transitions within 500ms

**Usage:**
1. Launch a game and tune settings to your preference
2. Click "Save as Profile for [Game Name]" in Expert Mode
3. Profile automatically applies whenever you launch that game
4. Create profiles for different games (performance vs battery life)

**Profile Management (Expert Mode → Presets Tab):**
- View all profiles with game names and settings
- Edit existing profiles
- Delete profiles (reverts to global default)
- Export all profiles to JSON file
- Import profiles with conflict resolution

**Detection Methods:**
- Primary: Steam appmanifest files (`~/.steam/steam/steamapps/`)
- Fallback: Process scanning (`/proc` for `-applaunch` argument)
- Polling: 2-second intervals with 5-second debouncing

### Benchmarking

Quick performance testing to measure the impact of your undervolt settings.

**Features:**
- **10-Second Tests**: Fast stress-ng matrix operations
- **Score Comparison**: Automatic before/after comparison
- **History Tracking**: Last 20 benchmark results saved
- **Undervolt Recording**: Tracks which settings were used for each test

**Usage:**
1. Run benchmark with current settings (baseline)
2. Adjust undervolt values
3. Run benchmark again
4. View percentage improvement/degradation
5. Compare any two results from history

**Benchmark Output:**
- Score: Operations per second (bogo ops/s)
- Duration: Actual test time
- Cores Used: Undervolt values during test
- Comparison: Score difference and percentage change

**Available in both Wizard and Expert modes.**

### Low-Level Fan Control

DeckTune 3.0 introduces direct fan control via hwmon sysfs, integrated into the gymdeck3 Rust daemon.

**Features:**
- **Custom Fan Curves**: Visual SVG editor with drag-and-drop points
- **Three Modes**: Default (BIOS), Custom (curve), Fixed (constant speed)
- **Temperature Interpolation**: Smooth transitions between curve points
- **Hysteresis Control**: Prevents rapid speed changes (1-10°C configurable)
- **Safety Overrides**: 90°C+ forces 100% PWM, 85°C+ enforces minimum 80%
- **Zero RPM Mode**: Allow fan to stop below 45°C (optional, with warning)
- **Fail-Safe**: Drop trait returns control to BIOS on daemon exit/crash

**Usage (Expert Mode → Fan Control):**
1. Enable "Fan Control" toggle
2. Select mode: Default, Custom, or Fixed
3. For Custom mode, edit the curve on the SVG graph:
   - Click to add points
   - Drag points to adjust
   - Double-click to remove points
4. Configure hysteresis (2-5°C recommended)
5. Optionally enable Zero RPM (use with caution!)
6. Save settings

**Example Curve:**
```
40°C → 20%   (quiet at idle)
50°C → 30%   (light load)
60°C → 45%   (medium load)
70°C → 60%   (gaming)
80°C → 80%   (heavy gaming)
85°C → 100%  (maximum cooling)
```

**Safety Features:**
- Temperature ≥ 90°C: Forces 100% PWM (ignores curve)
- Temperature ≥ 85°C: Minimum 80% PWM enforced
- Zero RPM only allowed below 45°C when explicitly enabled
- Drop trait automatically returns control to BIOS on exit

**CLI Arguments (gymdeck3):**
```bash
gymdeck3 balanced 100000 \
  --fan-control \
  --fan-mode custom \
  --fan-curve 40:20 --fan-curve 60:50 --fan-curve 80:100 \
  --fan-hysteresis 3 \
  --fan-zero-rpm  # optional, enables Zero RPM
```

### Architecture

```
DeckTune/
├── backend/           # Python backend
│   ├── core/          # ryzenadj wrapper, safety manager
│   ├── platform/      # model detection, limits
│   ├── tuning/        # autotune engine, test runner
│   ├── dynamic/       # gymdeck3 controller, profiles
│   ├── api/           # RPC methods, events
│   └── watchdog.py    # heartbeat monitoring
├── src/               # TypeScript frontend
│   ├── api/           # API client
│   ├── components/    # UI components
│   └── context/       # React context
├── gymdeck3/          # Rust dynamic mode daemon
│   ├── src/           # Load monitoring, adaptation strategies
│   └── tests/         # Property-based tests (proptest)
├── bin/               # ryzenadj binary, gymdeck3
└── tests/             # Property-based tests (pytest + hypothesis)
```

### Testing

```bash
# Install Python test dependencies
pip install -r requirements-test.txt

# Run Python tests
pytest tests/ -v

# Build and test gymdeck3 (Rust)
cd gymdeck3
cargo test
cargo build --release --target x86_64-unknown-linux-musl
```

The project uses property-based testing for correctness verification:
- **Python**: 16 correctness properties, 91 tests (hypothesis)
- **Rust**: 8 correctness properties for gymdeck3 (proptest)
- Coverage of all critical components

### Building gymdeck3

gymdeck3 is a standalone Rust daemon that powers Dynamic Mode. It's pre-built and included in releases, but you can rebuild it if needed.

**Requirements:**
- Rust toolchain (1.70+)
- musl target for static linking

**Build Instructions:**

```bash
# Install musl target (one-time setup)
rustup target add x86_64-unknown-linux-musl

# Build gymdeck3
cd gymdeck3
cargo build --release --target x86_64-unknown-linux-musl

# Verify static linking (should show "not a dynamic executable")
ldd target/x86_64-unknown-linux-musl/release/gymdeck3

# Copy to bin/ directory
cp target/x86_64-unknown-linux-musl/release/gymdeck3 ../bin/
```

**Binary Specifications:**
- Target: `x86_64-unknown-linux-musl` (static linking)
- Size: < 5MB (stripped, LTO enabled)
- Dependencies: None (self-contained)
- Optimization: `-Oz` (size-optimized)

**CLI Usage:**

```bash
# Basic usage
gymdeck3 <strategy> <sample_interval_us> [OPTIONS]

# Example: Balanced strategy, 100ms sampling, 4 cores
gymdeck3 balanced 100000 \
  --core 0:-20:-30:50.0 \
  --core 1:-20:-30:50.0 \
  --core 2:-20:-30:50.0 \
  --core 3:-20:-30:50.0 \
  --hysteresis 5.0 \
  --ryzenadj-path /path/to/ryzenadj \
  --status-interval 1000 \
  --verbose

# Strategies: conservative, balanced, aggressive, custom
# Sample interval: 10000-5000000 microseconds (10ms-5s)
# Core format: N:MIN:MAX:THRESHOLD (e.g., 0:-20:-35:50.0)
# Hysteresis: 1.0-20.0 percent
```

**Architecture:**

```
gymdeck3 (Rust)
├── LoadMonitor      → Reads /proc/stat, calculates per-core load
├── Strategy         → Maps load to target undervolt values
├── Hysteresis       → Prevents value hunting with dead-band
├── Interpolation    → Smooth transitions with 1mV steps
├── RyzenadjExecutor → Applies values via ryzenadj subprocess
├── Watchdog         → 10s timeout, auto-reset on stall
└── OutputWriter     → JSON status to stdout (NDJSON)
```

**Status Output (NDJSON):**

```json
{"type":"status","load":[45.2,52.1,38.7,41.0],"values":[-28,-25,-30,-29],"strategy":"balanced","uptime_ms":12500}
{"type":"transition","from":[-25,-25,-25,-25],"to":[-30,-30,-30,-30],"progress":0.5}
{"type":"error","code":"ryzenadj_failed","message":"Command returned exit code 1"}
```

**Signals:**
- `SIGTERM/SIGINT`: Graceful shutdown, reset values to 0
- `SIGUSR1`: Force immediate status output
- Panic: Automatic reset to 0 via panic hook

### Safety

DeckTune includes multi-level protection:

1. **Platform Limits** — automatic limits for each model
2. **Watchdog** — rollback on freeze (heartbeat every 5 sec, timeout 30 sec)
3. **Boot Recovery** — automatic rollback on reboot during tuning
4. **LKG Values** — persistence of last stable values
5. **Panic Disable** — instant reset with one button

### Recommendations

- For global use, don't set values below -20/-25
- Configure undervolt individually for each game
- Use Thorough autotune mode for maximum accuracy
- If freezing occurs, reduce values

### Contributing

Pull requests are welcome! For major changes, please open an issue first.

### License

GPL-3.0 License — see [LICENSE](LICENSE)

---

<a name="russian"></a>
## Русский

**DeckTune** — автоматизированный инструмент для андервольтинга Steam Deck (LCD/OLED) с гарантией безопасности. Превращает сложный процесс настройки в однокнопочную процедуру с автоматическим поиском оптимальных значений.

### Возможности

- **Автоматическое определение модели** — LCD (Jupiter) или OLED (Galileo) с соответствующими лимитами
- **Autotune** — автоматический поиск оптимальных значений для вашего конкретного чипа
- **Автоматический Silicon Binning** — автоматическое определение максимального стабильного андервольта
- **Профили для игр** — автоматическое переключение профилей в зависимости от запущенной игры
- **Низкоуровневое управление кулером** — кастомные кривые с визуальным редактором и защитой от перегрева
- **Система безопасности** — watchdog, автоматический откат при зависании, LKG (Last Known Good)
- **Встроенные стресс-тесты** — CPU, RAM, Combo для проверки стабильности
- **Бенчмаркинг** — быстрое тестирование производительности с сравнением до/после
- **Пресеты** — глобальные и per-game настройки с автоприменением
- **Диагностика** — экспорт логов и системной информации одной кнопкой
- **Динамический режим** — автоматическая подстройка под нагрузку (gymdeck3)

### Установка

#### Требования

- Steam Deck (LCD или OLED)
- [Decky Loader](https://decky.xyz/)
- SteamOS

#### Быстрая установка

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

#### Ручная установка

1. Скачайте последний релиз из [Releases](https://github.com/bobberdolle1/DeckTune/releases)
2. Перенесите архив на Steam Deck
3. В настройках Decky Loader включите Developer Mode
4. Установите плагин из архива

### Использование

**📖 Подробные руководства см. в [User Guide](docs/USER_GUIDE.md)**

#### Wizard Mode (для новичков)

1. Откройте DeckTune в меню Decky
2. Выберите цель: Quiet/Cool, Balanced, Max Battery, Max Performance
3. Дождитесь завершения автотюнинга
4. Нажмите "Apply & Save"

#### Expert Mode (для опытных)

- **Manual** — ручная настройка значений для каждого ядра
- **Presets** — управление пресетами (создание, редактирование, экспорт/импорт)
- **Tests** — запуск стресс-тестов вручную
- **Diagnostics** — просмотр логов и экспорт диагностики

#### Динамический режим (gymdeck3)

Динамический режим автоматически подстраивает значения андервольта на основе реальной нагрузки CPU, обеспечивая оптимальный баланс между производительностью и эффективностью.

**Возможности:**
- **Адаптивные стратегии**: Conservative (5s рампа), Balanced (2s рампа), Aggressive (500ms рампа), Custom
- **Управление по ядрам**: Независимый мониторинг нагрузки и настройка значений для каждого ядра CPU
- **Гистерезис**: Предотвращает колебания значений с настраиваемым dead-band (1-20%)
- **Плавные переходы**: Линейная интерполяция с шагом 1mV для стабильности
- **Безопасность**: Watchdog, автоматический откат, соблюдение лимитов платформы

**Как это работает:**
1. Мониторит нагрузку CPU из `/proc/stat` в реальном времени
2. Вычисляет оптимальный андервольт на основе текущей нагрузки и стратегии
3. Плавно применяет значения через ryzenadj
4. Высокая нагрузка → безопасные (менее агрессивные) значения
5. Низкая нагрузка → более агрессивные значения для лучшей эффективности

**Профили конфигурации:**
- Battery Saver (консервативный, максимальное время работы)
- Balanced (умеренная отзывчивость)
- Performance (быстрая адаптация)
- Custom (пользовательские кривые нагрузки)

#### Кнопка Panic Disable

Красная кнопка "Panic Disable" всегда доступна — мгновенно сбрасывает все значения в 0.

### Автоматический Silicon Binning

Silicon Binning автоматически определяет максимальный стабильный андервольт вашего чипа через итеративное тестирование с восстановлением после сбоев.

**Как это работает:**
1. Начинает с -10mV и тестирует постепенно более низкие значения с шагом -5mV
2. Каждая итерация запускает 60-секундный стресс-тест (CPU + память)
3. Состояние сохраняется перед каждым тестом для восстановления после сбоя
4. Если система зависает, восстановление при загрузке обнаруживает это и восстанавливает последнее стабильное значение
5. Рекомендует безопасное значение с запасом 5mV

**Использование (Wizard Mode):**
1. Нажмите кнопку "Find Max Undervolt"
2. Дождитесь завершения binning (обычно 5-15 минут)
3. Просмотрите обнаруженный максимум и рекомендуемое значение
4. Нажмите "Apply Recommended" для использования безопасного значения

**Конфигурация (Расширенные настройки):**
- Длительность теста: 30-300 секунд на итерацию (по умолчанию: 60s)
- Размер шага: 1-10mV приращения (по умолчанию: 5mV)
- Начальное значение: от 0 до -20mV (по умолчанию: -10mV)

**Функции безопасности:**
- Постоянное состояние для восстановления после сбоя
- Максимальный лимит итераций (20 попыток)
- Соблюдение лимитов платформы
- Прерывание при последовательных сбоях (3 сбоя)
- Отмена с мгновенным откатом

### Профили для игр

Автоматическое переключение настроек андервольта в зависимости от текущей запущенной игры Steam.

**Возможности:**
- **Автоматическое определение**: Мониторит активную игру Steam через AppID
- **Быстрое создание**: Сохранение текущих настроек как профиля для активной игры
- **Глобальный по умолчанию**: Резервные настройки, когда нет профиля для конкретной игры
- **Импорт/Экспорт**: Обмен профилями с другими пользователями или резервное копирование настроек
- **Переключение профилей**: Плавные переходы в течение 500ms

**Использование:**
1. Запустите игру и настройте параметры по своему усмотрению
2. Нажмите "Save as Profile for [Game Name]" в Expert Mode
3. Профиль автоматически применяется при каждом запуске этой игры
4. Создавайте профили для разных игр (производительность vs время работы)

**Управление профилями (Expert Mode → вкладка Presets):**
- Просмотр всех профилей с названиями игр и настройками
- Редактирование существующих профилей
- Удаление профилей (возврат к глобальному по умолчанию)
- Экспорт всех профилей в JSON файл
- Импорт профилей с разрешением конфликтов

**Методы определения:**
- Основной: Файлы appmanifest Steam (`~/.steam/steam/steamapps/`)
- Резервный: Сканирование процессов (`/proc` для аргумента `-applaunch`)
- Опрос: Интервалы 2 секунды с 5-секундным debouncing

### Бенчмаркинг

Быстрое тестирование производительности для измерения влияния настроек андервольта.

**Возможности:**
- **10-секундные тесты**: Быстрые матричные операции stress-ng
- **Сравнение результатов**: Автоматическое сравнение до/после
- **Отслеживание истории**: Сохранение последних 20 результатов бенчмарка
- **Запись андервольта**: Отслеживание настроек, использованных для каждого теста

**Использование:**
1. Запустите бенчмарк с текущими настройками (базовая линия)
2. Настройте значения андервольта
3. Запустите бенчмарк снова
4. Просмотрите процентное улучшение/ухудшение
5. Сравните любые два результата из истории

**Вывод бенчмарка:**
- Оценка: Операций в секунду (bogo ops/s)
- Длительность: Фактическое время теста
- Использованные ядра: Значения андервольта во время теста
- Сравнение: Разница в оценке и процентное изменение

**Доступно в режимах Wizard и Expert.**

### Архитектура

```
DeckTune/
├── backend/           # Python backend
│   ├── core/          # ryzenadj wrapper, safety manager
│   ├── platform/      # определение модели, лимиты
│   ├── tuning/        # autotune engine, test runner
│   ├── dynamic/       # gymdeck3 контроллер, профили
│   ├── api/           # RPC методы, события
│   └── watchdog.py    # мониторинг heartbeat
├── src/               # TypeScript frontend
│   ├── api/           # API клиент
│   ├── components/    # UI компоненты
│   └── context/       # React context
├── gymdeck3/          # Rust демон динамического режима
│   ├── src/           # Мониторинг нагрузки, стратегии адаптации
│   └── tests/         # Property-based тесты (proptest)
├── bin/               # ryzenadj binary, gymdeck3
└── tests/             # Property-based тесты (pytest + hypothesis)
```

### Тестирование

```bash
# Установка зависимостей для Python тестов
pip install -r requirements-test.txt

# Запуск Python тестов
pytest tests/ -v

# Сборка и тестирование gymdeck3 (Rust)
cd gymdeck3
cargo test
cargo build --release --target x86_64-unknown-linux-musl
```

Проект использует property-based testing для проверки корректности:
- **Python**: 16 свойств корректности, 91 тест (hypothesis)
- **Rust**: 8 свойств корректности для gymdeck3 (proptest)
- Покрытие всех критических компонентов

### Сборка gymdeck3

gymdeck3 — это автономный демон на Rust, обеспечивающий работу динамического режима. Он предсобран и включён в релизы, но вы можете пересобрать его при необходимости.

**Требования:**
- Rust toolchain (1.70+)
- musl target для статической линковки

**Инструкции по сборке:**

```bash
# Установка musl target (однократно)
rustup target add x86_64-unknown-linux-musl

# Сборка gymdeck3
cd gymdeck3
cargo build --release --target x86_64-unknown-linux-musl

# Проверка статической линковки (должно показать "not a dynamic executable")
ldd target/x86_64-unknown-linux-musl/release/gymdeck3

# Копирование в директорию bin/
cp target/x86_64-unknown-linux-musl/release/gymdeck3 ../bin/
```

**Спецификации бинарника:**
- Target: `x86_64-unknown-linux-musl` (статическая линковка)
- Размер: < 5MB (stripped, LTO включён)
- Зависимости: Нет (самодостаточный)
- Оптимизация: `-Oz` (оптимизация по размеру)

**Использование CLI:**

```bash
# Базовое использование
gymdeck3 <strategy> <sample_interval_us> [OPTIONS]

# Пример: Balanced стратегия, 100ms семплирование, 4 ядра
gymdeck3 balanced 100000 \
  --core 0:-20:-30:50.0 \
  --core 1:-20:-30:50.0 \
  --core 2:-20:-30:50.0 \
  --core 3:-20:-30:50.0 \
  --hysteresis 5.0 \
  --ryzenadj-path /path/to/ryzenadj \
  --status-interval 1000 \
  --verbose

# Стратегии: conservative, balanced, aggressive, custom
# Интервал семплирования: 10000-5000000 микросекунд (10ms-5s)
# Формат ядра: N:MIN:MAX:THRESHOLD (например, 0:-20:-35:50.0)
# Гистерезис: 1.0-20.0 процентов
```

**Архитектура:**

```
gymdeck3 (Rust)
├── LoadMonitor      → Читает /proc/stat, вычисляет нагрузку на ядро
├── Strategy         → Отображает нагрузку на целевые значения андервольта
├── Hysteresis       → Предотвращает колебания значений с dead-band
├── Interpolation    → Плавные переходы с шагом 1mV
├── RyzenadjExecutor → Применяет значения через ryzenadj subprocess
├── Watchdog         → 10s таймаут, авто-сброс при зависании
└── OutputWriter     → JSON статус в stdout (NDJSON)
```

**Вывод статуса (NDJSON):**

```json
{"type":"status","load":[45.2,52.1,38.7,41.0],"values":[-28,-25,-30,-29],"strategy":"balanced","uptime_ms":12500}
{"type":"transition","from":[-25,-25,-25,-25],"to":[-30,-30,-30,-30],"progress":0.5}
{"type":"error","code":"ryzenadj_failed","message":"Command returned exit code 1"}
```

**Сигналы:**
- `SIGTERM/SIGINT`: Корректное завершение, сброс значений в 0
- `SIGUSR1`: Принудительный немедленный вывод статуса
- Panic: Автоматический сброс в 0 через panic hook

### Безопасность

DeckTune включает многоуровневую систему защиты:

1. **Platform Limits** — автоматические лимиты для каждой модели
2. **Watchdog** — откат при зависании (heartbeat каждые 5 сек, таймаут 30 сек)
3. **Boot Recovery** — автоматический откат при перезагрузке во время тюнинга
4. **LKG Values** — сохранение последних стабильных значений
5. **Panic Disable** — мгновенный сброс одной кнопкой

### Рекомендации

- Для глобального использования не ставьте значения ниже -20/-25
- Настраивайте андервольт индивидуально для каждой игры
- Используйте Thorough режим autotune для максимальной точности
- При зависаниях уменьшайте значения

### Contributing

Pull requests приветствуются! Для крупных изменений сначала откройте issue.

### Лицензия

GPL-3.0 License — см. [LICENSE](LICENSE)

---

## Acknowledgements / Благодарности

- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj) — AMD APU control utility
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — plugin framework
- [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt) — original project
