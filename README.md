# DeckTune

<p align="center">
  <img src="./assets/preview.jpg" alt="DeckTune Preview" width="600"/>
</p>

<p align="center">
  <a href="#english">English</a> | <a href="#russian">Русский</a>
</p>

---

<a name="english"></a>
## �🇧 English

**DeckTune** — an automated undervolting tool for Steam Deck (LCD/OLED) with safety guarantees. Transforms the complex tuning process into a one-button procedure with automatic optimal value discovery.

### ✨ Features

- 🔍 **Auto Platform Detection** — LCD (Jupiter) or OLED (Galileo) with appropriate limits
- 🎯 **Autotune** — automatic discovery of optimal values for your specific chip
- �️ **Safety System** — watchdog, automatic rollback on freeze, LKG (Last Known Good)
- 🧪 **Built-in Stress Tests** — CPU, RAM, Combo for stability verification
- 💾 **Presets** — global and per-game settings with auto-apply
- 📊 **Diagnostics** — one-click export of logs and system info
- ⚡ **Dynamic Mode** — automatic adjustment based on load (gymdeck2)

### 🚀 Installation

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

### 📖 Usage

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

#### Panic Disable Button

The red "Panic Disable" button is always available — instantly resets all values to 0.

### 🔧 Architecture

```
DeckTune/
├── backend/           # Python backend
│   ├── core/          # ryzenadj wrapper, safety manager
│   ├── platform/      # model detection, limits
│   ├── tuning/        # autotune engine, test runner
│   ├── api/           # RPC methods, events
│   └── watchdog.py    # heartbeat monitoring
├── src/               # TypeScript frontend
│   ├── api/           # API client
│   ├── components/    # UI components
│   └── context/       # React context
├── bin/               # ryzenadj binary, gymdeck2
└── tests/             # Property-based tests (pytest + hypothesis)
```

### 🧪 Testing

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/ -v
```

The project uses property-based testing (hypothesis) for correctness verification:
- 16 correctness properties
- 91 tests
- Coverage of all critical components

### ⚠️ Safety

DeckTune includes multi-level protection:

1. **Platform Limits** — automatic limits for each model
2. **Watchdog** — rollback on freeze (heartbeat every 5 sec, timeout 30 sec)
3. **Boot Recovery** — automatic rollback on reboot during tuning
4. **LKG Values** — persistence of last stable values
5. **Panic Disable** — instant reset with one button

### 📋 Recommendations

- For global use, don't set values below -20/-25
- Configure undervolt individually for each game
- Use Thorough autotune mode for maximum accuracy
- If freezing occurs, reduce values

### 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

### 📄 License

MIT License — see [LICENSE](LICENSE)

---

<a name="russian"></a>
## 🇷🇺 Русский

**DeckTune** — автоматизированный инструмент для андервольтинга Steam Deck (LCD/OLED) с гарантией безопасности. Превращает сложный процесс настройки в однокнопочную процедуру с автоматическим поиском оптимальных значений.

### ✨ Возможности

- 🔍 **Автоматическое определение модели** — LCD (Jupiter) или OLED (Galileo) с соответствующими лимитами
- 🎯 **Autotune** — автоматический поиск оптимальных значений для вашего конкретного чипа
- 🛡️ **Система безопасности** — watchdog, автоматический откат при зависании, LKG (Last Known Good)
- 🧪 **Встроенные стресс-тесты** — CPU, RAM, Combo для проверки стабильности
- 💾 **Пресеты** — глобальные и per-game настройки с автоприменением
- 📊 **Диагностика** — экспорт логов и системной информации одной кнопкой
- ⚡ **Динамический режим** — автоматическая подстройка под нагрузку (gymdeck2)

### 🚀 Установка

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

### 📖 Использование

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

#### Кнопка Panic Disable

Красная кнопка "Panic Disable" всегда доступна — мгновенно сбрасывает все значения в 0.

### 🔧 Архитектура

```
DeckTune/
├── backend/           # Python backend
│   ├── core/          # ryzenadj wrapper, safety manager
│   ├── platform/      # определение модели, лимиты
│   ├── tuning/        # autotune engine, test runner
│   ├── api/           # RPC методы, события
│   └── watchdog.py    # мониторинг heartbeat
├── src/               # TypeScript frontend
│   ├── api/           # API клиент
│   ├── components/    # UI компоненты
│   └── context/       # React context
├── bin/               # ryzenadj binary, gymdeck2
└── tests/             # Property-based тесты (pytest + hypothesis)
```

### 🧪 Тестирование

```bash
# Установка зависимостей
pip install -r requirements-test.txt

# Запуск тестов
pytest tests/ -v
```

Проект использует property-based testing (hypothesis) для проверки корректности:
- 16 свойств корректности
- 91 тест
- Покрытие всех критических компонентов

### ⚠️ Безопасность

DeckTune включает многоуровневую систему защиты:

1. **Platform Limits** — автоматические лимиты для каждой модели
2. **Watchdog** — откат при зависании (heartbeat каждые 5 сек, таймаут 30 сек)
3. **Boot Recovery** — автоматический откат при перезагрузке во время тюнинга
4. **LKG Values** — сохранение последних стабильных значений
5. **Panic Disable** — мгновенный сброс одной кнопкой

### 📋 Рекомендации

- Для глобального использования не ставьте значения ниже -20/-25
- Настраивайте андервольт индивидуально для каждой игры
- Используйте Thorough режим autotune для максимальной точности
- При зависаниях уменьшайте значения

### 🤝 Contributing

Pull requests приветствуются! Для крупных изменений сначала откройте issue.

### 📄 Лицензия

MIT License — см. [LICENSE](LICENSE)

---

## 🙏 Acknowledgements / Благодарности

- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj) — AMD APU control utility
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — plugin framework
- [Decky-Undervolt](https://github.com/totallynotbakadestroyer/Decky-Undervolt) — original project
