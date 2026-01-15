# Changelog

All notable changes to DeckTune will be documented in this file.

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
- **Dynamic Mode** — интеграция с gymdeck2
  - Автоматическая подстройка под нагрузку
  - Стратегии: Default, Aggressive, Manual

### Technical
- Модульная архитектура backend (core, platform, tuning, api)
- Property-based testing с hypothesis (16 свойств, 91 тест)
- TypeScript/React frontend с Decky UI
- Python 3.10+ backend с type hints

## [0.x] - Previous Versions

Based on [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt)
