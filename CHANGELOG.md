# Changelog

All notable changes to DeckTune will be documented in this file.

## [2.0.0] - 2026-01-15

### Major Changes - Dynamic Mode Refactor (gymdeck3)

#### New Rust Daemon (gymdeck3)
- **Complete rewrite** of dynamic mode in Rust for memory safety and performance
- **Static binary** (905KB) with zero runtime dependencies
- **Advanced load monitoring** from /proc/stat with per-core tracking
- **Adaptive strategies**: Conservative (5s ramp), Balanced (2s ramp), Aggressive (500ms ramp), Custom
- **Hysteresis control** prevents value hunting with configurable dead-band (1-20%)
- **Smooth transitions** with 1mV linear interpolation
- **Safety features**: watchdog, panic hook, automatic rollback, signal handling
- **JSON IPC protocol** (NDJSON) for status updates

#### Python Integration
- **DynamicController** manages gymdeck3 subprocess lifecycle
- **DynamicConfig** with validation and serialization
- **Profile management** with default profiles (Battery Saver, Balanced, Performance, Silent)
- **Settings migration** from old gymdeck2 format with automatic conversion
- **Event system** for real-time frontend updates

#### UI Enhancements
- **Expert Overclocker Mode** removes safety limits (-100mV range) with warning dialog
- **Simple Mode** single slider controls all cores simultaneously
- **Real-time load graph** displays CPU load when dynamic mode active
- **Profile switching** quick access to saved configurations

#### Testing & Quality
- **Property-based testing** for correctness verification
  - 8 Rust properties (proptest) - 244 tests
  - 7 Python properties (hypothesis) - 127 tests
- **Manual integration tests** comprehensive end-to-end validation
- **100% test coverage** for critical components

### Removed
- **gymdeck2** (C daemon) replaced by gymdeck3 (Rust)

### Technical Improvements
- Rust 1.70+ with musl static linking
- Comprehensive inline documentation
- Updated README with gymdeck3 build instructions
- Improved error handling and diagnostics

## [1.0.0] - 2026-01-15

### Added
- **Autotune Engine** — автоматический поиск оптимальных значений андервольта
  - Quick mode: быстрый поиск с шагом 5 и 30-секундными тестами
  - Thorough mode: точный поиск с бинарным уточнением и 2-минутными тестами
- **Platform Detection** — автоматическое определение модели Steam Deck
  - LCD (Jupiter): лимит -30
  - OLED (Galileo): лимит -35
  - Unknown: консервативный лимит -25
- **Safety System** — многоуровневая система безопасности
  - Watchdog с heartbeat мониторингом
  - Автоматический откат при зависании
  - Boot recovery при перезагрузке во время тюнинга
  - LKG (Last Known Good) persistence
  - Panic Disable кнопка
- **Stress Test Suite** — встроенные стресс-тесты
  - CPU Quick/Long (stress-ng)
  - RAM Quick/Thorough (memtester)
  - Combo (CPU + RAM)
- **Preset Management** — управление пресетами
  - Глобальные и per-game пресеты
  - Автоприменение при запуске игры
  - Экспорт/импорт в JSON
- **Wizard Mode** — простой интерфейс для новичков
  - 3-шаговый мастер настройки
  - Выбор цели (Quiet, Balanced, Max Battery, Max Performance)
- **Expert Mode** — расширенный интерфейс
  - Manual: ручная настройка ядер
  - Presets: управление пресетами
  - Tests: запуск тестов
  - Diagnostics: логи и экспорт
- **Diagnostics Export** — экспорт диагностики одной кнопкой
  - Логи плагина
  - Конфигурация и LKG
  - Системная информация
  - dmesg
- **Dynamic Mode** — интеграция с gymdeck3
  - Автоматическая подстройка под нагрузку
  - Стратегии: Default, Aggressive, Manual

### Technical
- Модульная архитектура backend (core, platform, tuning, api)
- Property-based testing с hypothesis (16 свойств, 91 тест)
- TypeScript/React frontend с Decky UI
- Python 3.10+ backend с type hints

## [0.x] - Previous Versions

Based on [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt)
