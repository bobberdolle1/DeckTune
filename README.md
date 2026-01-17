# DeckTune

**English** | [Русский](#russian)

---

## English

**DeckTune** — an automated undervolting tool for Steam Deck (LCD/OLED) with safety guarantees. Transforms the complex tuning process into a one-button procedure with automatic optimal value discovery.

### Features

- **Auto Platform Detection** — LCD (Jupiter) or OLED (Galileo) with appropriate limits
- **Autotune** — automatic discovery of optimal values for your specific chip
- **Automated Silicon Binning** — discover your chip's maximum stable undervolt automatically
- **Per-Game Profiles** — automatic profile switching based on running game
- **Low-Level Fan Control** — custom fan curves with visual editor and safety overrides
- **Dynamic Mode** — real-time CPU load-based adjustment with configurable strategies (gymdeck3)
- **Safety System** — watchdog, automatic rollback on freeze, LKG (Last Known Good)
- **Built-in Stress Tests** — CPU, RAM, Combo for stability verification
- **Benchmarking** — quick performance testing with before/after comparison
- **Presets** — global and per-game settings with auto-apply
- **Diagnostics** — one-click export of logs and system info
- **Modern UI** — card-based design with smooth animations, gamepad-friendly
- **Multi-language** — English and Russian with persistent language selection

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
- **Adaptive Strategies**: Conservative (5s ramp), Balanced (2s ramp), Aggressive (500ms ramp)
- **Per-Core Control**: Independent load monitoring and value adjustment for each CPU core
- **Hysteresis**: Prevents value hunting with configurable dead-band (1-20%)
- **Smooth Transitions**: Linear interpolation with 1mV steps for stability
- **Safety**: Watchdog, automatic rollback, respects platform limits

**Configuration (Expert Mode → Manual → Dynamic Settings):**
1. Select Dynamic mode in Manual tab
2. Click "Dynamic Settings" button
3. Choose strategy (Conservative/Balanced/Aggressive)
4. Enable Simple Mode for unified control or use per-core settings
5. Adjust value slider (if Simple Mode enabled)
6. Click "Save Settings"
7. Settings apply on next Dynamic mode start

**How it works:**
1. Monitors CPU load from `/proc/stat` in real-time
2. Calculates optimal undervolt based on current load and strategy
3. Applies values smoothly via ryzenadj
4. Higher load → safer (less aggressive) values
5. Lower load → more aggressive values for better efficiency

#### Panic Disable Button

The red "Panic Disable" button is always available — instantly resets all values to 0.

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

### Modern UI Design

DeckTune features a completely redesigned interface optimized for Steam Deck's Quick Access Menu (QAM).

**Settings Tab:**
- 🌐 **Language Card**: Persistent language selection (English/Russian) with save indicator
- 🧪 **Expert Mode Card**: Extended range (-100mV) with pulsing animation when active
- ℹ️ **Info Card**: Structured information with color-coded sections
- ✨ **Smooth Animations**: fadeIn, slideUp, fadeInUp, slideDown, pulse effects
- 🎨 **Modern Design**: Gradient backgrounds, shadows, icon badges in circles

**Dynamic Settings:**
- Inline configuration panel in Manual tab
- Expandable settings with "Dynamic Settings" button
- Strategy selection (Conservative/Balanced/Aggressive)
- Simple Mode toggle for unified control
- Value slider with real-time preview
- Save button with loading indicator

**Gamepad Support:**
- Full navigation with D-Pad and analog stick
- A button to activate/select
- B button to go back
- L1/R1 for quick tab switching
- All interactive elements use `Focusable` components
- Visual feedback with focus indicators

**Compact Design:**
- Optimized for 310px QAM width
- Responsive layouts with flex containers
- Compact fonts (8-13px) and spacing
- Collapsible sections to save space
- Card-based organization for clarity

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

MIT License — see [LICENSE](LICENSE)

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

MIT License — см. [LICENSE](LICENSE)

---

## Acknowledgements / Благодарности

- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj) — AMD APU control utility
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — plugin framework
- [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt) — original project
