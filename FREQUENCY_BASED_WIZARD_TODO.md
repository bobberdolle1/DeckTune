# Frequency-Based Voltage Wizard - Implementation TODO

## Что это такое?

**Frequency-Based Voltage Wizard** - это расширенный режим автоматического подбора напряжения для CPU, который создает **кривую зависимости напряжения от частоты процессора**.

### Текущая реализация (Load-Based)
Сейчас DeckTune использует **load-based** подход:
- Подбирается 2 значения: минимальное напряжение (при низкой нагрузке) и максимальное (при высокой)
- Напряжение меняется в зависимости от **нагрузки CPU** (0-100%)
- Быстро (~5-10 минут тестирования)
- Простая настройка

### Новая реализация (Frequency-Based)
Frequency-based подход более точный:
- Подбирается **отдельное напряжение для каждого диапазона частот** (400, 500, 600... 3500 МГц)
- Напряжение меняется в зависимости от **текущей частоты CPU**
- Создается кривая из ~30 точек (каждые 100 МГц)
- Более долгое тестирование (~15-30 минут)
- Максимальная эффективность и стабильность

### Зачем это нужно?

1. **Точность:** На низких частотах (400-1000 МГц) можно применить более агрессивный undervolt, чем на высоких (3000+ МГц)
2. **Стабильность:** Каждая частота тестируется отдельно, исключая нестабильность
3. **Эффективность:** Оптимальное напряжение для каждой частоты = максимальная экономия энергии
4. **Гибкость:** Можно создавать профили для разных сценариев (игры, браузинг, простой)

### Как это работает?

```
Частота (МГц)  →  Напряжение (mV)
─────────────────────────────────
400            →  -50  (агрессивный undervolt)
800            →  -45
1200           →  -40
1600           →  -35
2000           →  -30
2400           →  -25
2800           →  -20
3200           →  -15
3500           →  -10  (консервативный undervolt)
```

Во время работы:
1. Система читает текущую частоту CPU (например, 2400 МГц)
2. Находит соответствующее напряжение в кривой (-25 mV)
3. Применяет это напряжение через ryzenadj
4. При изменении частоты напряжение автоматически обновляется

### Отличия от текущего режима

| Параметр | Load-Based (текущий) | Frequency-Based (новый) |
|----------|---------------------|------------------------|
| Основа | Нагрузка CPU (%) | Частота CPU (МГц) |
| Точек данных | 2 (min/max) | ~30 (каждые 100 МГц) |
| Время теста | 5-10 минут | 15-30 минут |
| Точность | Хорошая | Отличная |
| Сложность | Простая | Средняя |
| Применение | Универсальное | Продвинутое |

### Пример использования

**Сценарий 1: Игры**
- Частота часто меняется: 1500 → 3500 → 2000 МГц
- Frequency-based автоматически подстраивает напряжение под каждую частоту
- Стабильность + экономия энергии

**Сценарий 2: Браузинг**
- Частота низкая: 400-1200 МГц
- Можно применить агрессивный undervolt (-50 mV)
- Максимальное время работы от батареи

**Сценарий 3: Рендеринг**
- Частота постоянно высокая: 3000-3500 МГц
- Консервативный undervolt (-10 mV)
- Стабильность под нагрузкой

---

## Phase 1: Core Infrastructure (Backend)

### 1.1 Frequency Monitoring & Control
- [ ] `backend/platform/cpufreq.py` - CPU frequency control module
  - [ ] Read current CPU frequency per core (`/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`)
  - [ ] Set CPU governor to `userspace` for frequency locking
  - [ ] Lock CPU frequency to specific value during tests
  - [ ] Restore original governor after tests
  - [ ] Handle permission errors (requires root/sudo)

### 1.2 Frequency Curve Data Model
- [ ] `backend/tuning/frequency_curve.py` - Frequency curve data structures
  - [ ] `FrequencyPoint` dataclass: `(frequency_mhz: int, voltage_mv: int, stable: bool)`
  - [ ] `FrequencyCurve` class: List of FrequencyPoint with interpolation
  - [ ] `get_voltage_for_frequency(freq: int) -> int` - Linear interpolation
  - [ ] Serialize/deserialize to JSON
  - [ ] Validation: ensure voltages are in [-100, 0] range

### 1.3 Frequency-Based Test Runner
- [ ] `backend/tuning/runner.py` - Extend TestRunner
  - [ ] `run_frequency_locked_test(core_id: int, freq_mhz: int, voltage_mv: int, duration: int) -> TestResult`
  - [ ] Lock frequency before test
  - [ ] Apply voltage offset
  - [ ] Run stress test
  - [ ] Monitor for crashes/errors
  - [ ] Restore frequency after test

### 1.4 Frequency Wizard Session
- [ ] `backend/tuning/frequency_wizard.py` - New wizard implementation
  - [ ] `FrequencyWizardConfig` dataclass
    - [ ] `freq_start: int = 400` (MHz)
    - [ ] `freq_end: int = 3500` (MHz)
    - [ ] `freq_step: int = 100` (MHz)
    - [ ] `test_duration: int = 30` (seconds per frequency)
    - [ ] `voltage_start: int = -30` (mV, starting point)
    - [ ] `voltage_step: int = 2` (mV, step size)
    - [ ] `safety_margin: int = 5` (mV)
  - [ ] `_run_frequency_sweep(core_id: int) -> FrequencyCurve`
    - [ ] For each frequency (400, 500, 600, ..., 3500 MHz):
      - [ ] Binary search for max stable voltage at this frequency
      - [ ] Start at voltage_start, step down by voltage_step
      - [ ] Test until failure, then step back
      - [ ] Record stable voltage for this frequency
  - [ ] `_verify_frequency_curve(curve: FrequencyCurve) -> bool`
    - [ ] Run verification tests at 3-5 random frequencies
    - [ ] Ensure curve is stable across frequency range
  - [ ] Progress reporting (current frequency, voltage, % complete)
  - [ ] Cancellation support
  - [ ] Error recovery

## Phase 2: Rust Dynamic Controller

### 2.1 Frequency Curve Storage
- [ ] `gymdeck3/src/dynamic/frequency_curve.rs`
  - [ ] `FrequencyPoint` struct
  - [ ] `FrequencyCurve` struct with interpolation
  - [ ] `get_voltage_at_frequency(freq_mhz: u32) -> i32`
  - [ ] Linear interpolation between points
  - [ ] Clamp to curve bounds

### 2.2 Frequency-Based Voltage Controller
- [ ] `gymdeck3/src/dynamic/frequency_controller.rs`
  - [ ] `FrequencyVoltageController` struct
  - [ ] Store per-core frequency curves
  - [ ] `update_voltage_for_frequency(core_id: usize, freq_mhz: u32) -> i32`
  - [ ] Read current CPU frequency from sysfs
  - [ ] Calculate voltage from curve
  - [ ] Apply voltage via ryzenadj

### 2.3 Metrics Monitor Extension
- [ ] `gymdeck3/src/dynamic/metrics_monitor.rs` - Extend existing
  - [ ] Add frequency reading to `CoreMetrics`
  - [ ] Read from `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`
  - [ ] Include in telemetry samples

## Phase 3: Frontend UI

### 3.1 Frequency Wizard UI
- [ ] `src/components/FrequencyWizard.tsx`
  - [ ] Wizard configuration form
    - [ ] Frequency range selector (start/end/step)
    - [ ] Test duration slider
    - [ ] Starting voltage selector
    - [ ] Safety margin selector
  - [ ] Progress display
    - [ ] Current frequency being tested
    - [ ] Current voltage being tested
    - [ ] Progress bar (frequency sweep progress)
    - [ ] Estimated time remaining
  - [ ] Results visualization
    - [ ] Frequency vs Voltage curve chart (Recharts)
    - [ ] Show stable points
    - [ ] Show failed points
    - [ ] Highlight safety margin
  - [ ] Start/Cancel/Apply buttons

### 3.2 Frequency Curve Visualization
- [ ] `src/components/FrequencyCurveChart.tsx`
  - [ ] Line chart: X-axis = Frequency (MHz), Y-axis = Voltage (mV)
  - [ ] Plot stable voltage points
  - [ ] Show interpolated curve
  - [ ] Highlight current operating point
  - [ ] Interactive tooltips

### 3.3 Mode Selector Extension
- [ ] `src/components/DeckTuneApp.tsx` - Add frequency mode
  - [ ] Add "Frequency-Based" mode to mode selector
  - [ ] Route to FrequencyWizard component
  - [ ] Store mode preference in localStorage

## Phase 4: RPC Integration

### 4.1 Backend RPC Methods
- [ ] `backend/api/rpc.py` - Add frequency wizard methods
  - [ ] `start_frequency_wizard(config: dict) -> dict`
  - [ ] `get_frequency_wizard_progress() -> dict`
  - [ ] `cancel_frequency_wizard() -> dict`
  - [ ] `get_frequency_curve(core_id: int) -> dict`
  - [ ] `apply_frequency_curve(curves: dict) -> dict`
  - [ ] `enable_frequency_mode() -> dict`
  - [ ] `disable_frequency_mode() -> dict`

### 4.2 Frontend API Client
- [ ] `src/api/Api.ts` - Add frequency wizard methods
  - [ ] `startFrequencyWizard(config: FrequencyWizardConfig): Promise<void>`
  - [ ] `getFrequencyWizardProgress(): Promise<FrequencyWizardProgress>`
  - [ ] `cancelFrequencyWizard(): Promise<void>`
  - [ ] `getFrequencyCurve(coreId: number): Promise<FrequencyCurve>`
  - [ ] `applyFrequencyCurve(curves: FrequencyCurve[]): Promise<void>`

## Phase 5: Settings & Persistence

### 5.1 Configuration Storage
- [ ] `backend/core/settings_manager.py` - Extend settings
  - [ ] `frequency_curves: dict` - Store per-core frequency curves
  - [ ] `frequency_mode_enabled: bool`
  - [ ] `frequency_wizard_config: dict` - Last used wizard config
  - [ ] Save/load frequency curves to settings.json

### 5.2 Profile System Extension
- [ ] `backend/dynamic/profile_manager.py` - Add frequency profiles
  - [ ] Store frequency curves in game profiles
  - [ ] Apply frequency curve when profile activates
  - [ ] Export/import frequency profiles

## Phase 6: Testing

### 6.1 Unit Tests
- [ ] `tests/test_frequency_curve.py`
  - [ ] Test interpolation accuracy
  - [ ] Test boundary conditions
  - [ ] Test serialization/deserialization
- [ ] `tests/test_frequency_wizard.py`
  - [ ] Test frequency sweep logic
  - [ ] Test cancellation
  - [ ] Test error recovery
- [ ] `tests/test_frequency_controller.py`
  - [ ] Test voltage calculation
  - [ ] Test frequency reading
  - [ ] Test curve application

### 6.2 Integration Tests
- [ ] `tests/test_frequency_wizard_integration.py`
  - [ ] End-to-end wizard execution (mocked hardware)
  - [ ] RPC communication
  - [ ] Settings persistence
- [ ] `tests/test_frequency_mode_switching.py`
  - [ ] Switch between load-based and frequency-based modes
  - [ ] Verify correct controller is active

### 6.3 Hardware Tests
- [ ] Manual testing on Steam Deck
  - [ ] Verify frequency locking works
  - [ ] Verify voltage application at different frequencies
  - [ ] Verify stability under load
  - [ ] Verify no crashes or freezes

## Phase 7: Documentation

- [ ] `docs/FREQUENCY_WIZARD_GUIDE.md`
  - [ ] How frequency-based mode works
  - [ ] When to use vs load-based mode
  - [ ] Configuration recommendations
  - [ ] Troubleshooting
- [ ] `docs/FREQUENCY_WIZARD_API.md`
  - [ ] RPC API documentation
  - [ ] Data structures
  - [ ] Example usage
- [ ] Update `README.md` with frequency mode feature

## Phase 8: Optimization & Polish

### 8.1 Performance
- [ ] Optimize frequency sweep (skip redundant tests)
- [ ] Parallel testing (test multiple cores simultaneously)
- [ ] Adaptive step size (larger steps at stable regions)
- [ ] Cache frequency readings

### 8.2 UX Improvements
- [ ] Estimated time calculation
- [ ] Pause/resume wizard
- [ ] Save intermediate results
- [ ] Quick presets (conservative/balanced/aggressive)

### 8.3 Safety Features
- [ ] Temperature monitoring during tests
- [ ] Auto-abort on overheat
- [ ] Watchdog for frozen tests
- [ ] Automatic rollback on instability

## Estimated Effort

- **Phase 1-2 (Backend):** 3-4 days
- **Phase 3 (Frontend):** 2-3 days
- **Phase 4 (RPC):** 1 day
- **Phase 5 (Settings):** 1 day
- **Phase 6 (Testing):** 2-3 days
- **Phase 7 (Docs):** 1 day
- **Phase 8 (Polish):** 2-3 days

**Total:** ~12-18 days for full implementation

## Dependencies

- Root/sudo access for cpufreq control
- stress-ng for CPU stress testing
- Python 3.8+
- Rust 1.70+
- React 18+
- Recharts for visualization

## Risks & Mitigations

1. **Risk:** Frequency locking may not work on all kernels
   - **Mitigation:** Fallback to load-based mode if cpufreq unavailable

2. **Risk:** Long wizard duration (~30 frequencies × 30s = 15+ minutes)
   - **Mitigation:** Adaptive testing, skip stable regions, parallel cores

3. **Risk:** System instability during aggressive testing
   - **Mitigation:** Conservative starting points, temperature monitoring, watchdog

4. **Risk:** Frequency changes during normal use may not trigger voltage updates fast enough
   - **Mitigation:** High-frequency polling (10-50ms), predictive voltage application
