# DeckTune

**v3.3.4** | Automated CPU undervolting for Steam Deck with safety guarantees

[English](#english) | [Русский](#russian)

---

## English

### Features

- **Automated Undervolting** — One-click optimal value discovery for your chip
- **Frequency-Based Curves** — Voltage optimization across entire CPU frequency spectrum (400-3500 MHz)
- **Dynamic Manual Mode** — Per-core voltage curves with real-time load adaptation
- **Per-Game Profiles** — Automatic profile switching based on running game
- **Safety System** — Watchdog, automatic rollback, Last Known Good (LKG) recovery
- **Built-in Tests** — CPU/RAM stress tests with stability verification
- **Fan Control** — Custom fan curves with visual editor and safety overrides
- **QAM Optimized** — Compact UI designed for Steam Deck Quick Access Menu

### Installation

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

**Requirements:** Steam Deck (LCD/OLED), Decky Loader, SteamOS

### Quick Start

1. **Wizard Mode** (beginners): Select goal → Wait for autotune → Apply
2. **Expert Mode** (advanced): Manual per-core adjustment, presets, tests, diagnostics
3. **Panic Disable**: Red button instantly resets all values to 0

### Modes

#### Wizard Mode
- **Load-Based**: Automatic optimal value discovery with chip quality grading
- **Frequency-Based**: Generate voltage curves for specific CPU frequencies (10-30 min)

#### Expert Mode
- **Manual**: Static per-core voltage adjustment
- **Dynamic Manual**: Load-based voltage curves (min/max/threshold per core)
- **Presets**: Save/load configurations, per-game profiles
- **Tests**: Stress testing with duration control
- **Diagnostics**: System info, logs, export

### Documentation

- [User Guide](docs/USER_GUIDE.md) — Complete usage instructions
- [Frequency Wizard Guide](docs/FREQUENCY_WIZARD_GUIDE.md) — Frequency-based mode walkthrough
- [Dynamic Manual Mode Guide](docs/DYNAMIC_MANUAL_MODE_GUIDE.md) — Load-based curves setup
- [API Reference](docs/FREQUENCY_WIZARD_API.md) — RPC methods for developers

### Safety

- Platform-specific limits (LCD: -50mV, OLED: -60mV)
- Watchdog with 30s timeout
- Boot recovery on crash
- LKG value persistence
- Panic Disable button

### Architecture

```
DeckTune/
├── backend/          # Python: RPC, safety, platform detection
├── src/              # TypeScript/React: UI components
├── gymdeck3/         # Rust: Dynamic mode daemon
├── bin/              # Binaries: ryzenadj, gymdeck3
└── tests/            # Property-based tests (pytest, proptest)
```

### Building

```bash
# Python tests
pip install -r requirements-test.txt
pytest tests/ -v

# Rust daemon
cd gymdeck3
cargo build --release --target x86_64-unknown-linux-musl
```

### License

GPL-3.0 — see [LICENSE](LICENSE)

---

<a name="russian"></a>
## Русский

### Возможности

- **Автоматический андервольтинг** — Поиск оптимальных значений одной кнопкой
- **Частотные кривые** — Оптимизация напряжения для всех частот CPU (400-3500 МГц)
- **Динамический ручной режим** — Кривые напряжения по ядрам с адаптацией под нагрузку
- **Профили для игр** — Автопереключение профилей по запущенной игре
- **Система безопасности** — Watchdog, автооткат, восстановление LKG
- **Встроенные тесты** — Стресс-тесты CPU/RAM с проверкой стабильности
- **Управление кулером** — Кастомные кривые с визуальным редактором
- **Оптимизация для QAM** — Компактный UI для Quick Access Menu Steam Deck

### Установка

```bash
curl -L https://github.com/bobberdolle1/DeckTune/releases/latest/download/install.sh | sh
```

**Требования:** Steam Deck (LCD/OLED), Decky Loader, SteamOS

### Быстрый старт

1. **Wizard Mode** (новички): Выбор цели → Ожидание автотюна → Применение
2. **Expert Mode** (опытные): Ручная настройка по ядрам, пресеты, тесты, диагностика
3. **Panic Disable**: Красная кнопка мгновенно сбрасывает все значения в 0

### Режимы

#### Wizard Mode
- **Load-Based**: Автопоиск оптимальных значений с оценкой качества чипа
- **Frequency-Based**: Генерация кривых напряжения для частот CPU (10-30 мин)

#### Expert Mode
- **Manual**: Статическая настройка напряжения по ядрам
- **Dynamic Manual**: Кривые напряжения по нагрузке (min/max/threshold на ядро)
- **Presets**: Сохранение/загрузка конфигураций, профили для игр
- **Tests**: Стресс-тестирование с контролем длительности
- **Diagnostics**: Системная информация, логи, экспорт

### Документация

- [Руководство пользователя](docs/USER_GUIDE_RU.md) — Полная инструкция по использованию
- [Руководство по частотному мастеру](docs/FREQUENCY_WIZARD_GUIDE.md) — Настройка частотного режима
- [Руководство по динамическому режиму](docs/DYNAMIC_MANUAL_MODE_GUIDE.md) — Настройка кривых по нагрузке

### Безопасность

- Лимиты для платформы (LCD: -50mV, OLED: -60mV)
- Watchdog с таймаутом 30s
- Восстановление при загрузке после сбоя
- Сохранение LKG значений
- Кнопка Panic Disable

### Лицензия

GPL-3.0 — см. [LICENSE](LICENSE)

---

## Acknowledgements

- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj) — AMD APU control utility
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — Plugin framework
