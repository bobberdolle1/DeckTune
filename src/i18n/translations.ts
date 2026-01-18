/**
 * Translations for DeckTune UI
 */

export type Language = "en" | "ru";

export interface Translations {
  // Settings Tab
  settingsTitle: string;
  languageSection: string;
  interfaceLanguage: string;
  selectLanguage: string;
  localizationComingSoon: string;
  expertModeSection: string;
  enableExpertMode: string;
  expertModeDescription: string;
  expertModeActiveGlobally: string;
  expertModeWarningTitle: string;
  expertModeWarningText: string;
  expertModeWarningAffects: string;
  expertModeWarningRisk: string;
  iUnderstand: string;
  cancel: string;
  aboutSettingsSection: string;
  aboutExpertMode: string;
  aboutControlMode: string;
  aboutLanguage: string;
  
  // Expert Mode Tabs
  manualTab: string;
  presetsTab: string;
  testsTab: string;
  fanTab: string;
  diagnosticsTab: string;
  
  // Manual Tab
  simpleMode: string;
  perCoreMode: string;
  dynamicMode: string;
  expertMode: string;
  expertModeActive: string;
  expertModeRange: string;
  allCores: string;
  core: string;
  apply: string;
  disable: string;
  reset: string;
  currentValues: string;
  controlMode: string;
  single: string;
  perCore: string;
  dynamic: string;
  
  // Dynamic Mode
  dynamicModeTitle: string;
  dynamicModeDescription: string;
  dynamicModeDescriptionActive: string;
  active: string;
  off: string;
  start: string;
  stop: string;
  settings: string;
  strategy: string;
  conservative: string;
  balanced: string;
  aggressive: string;
  simpleModeDynamic: string;
  simpleModeDescription: string;
  undervoltValue: string;
  sampleInterval: string;
  sampleIntervalDescription: string;
  hysteresis: string;
  hysteresisDescription: string;
  save: string;
  saving: string;
  howItWorks: string;
  
  // Presets Tab
  gameProfiles: string;
  globalPresets: string;
  saveFor: string;
  noGameProfiles: string;
  clickToCreate: string;
  deleteProfile: string;
  noGlobalPresets: string;
  saveCurrentValues: string;
  tested: string;
  delete: string;
  
  // Fan Tab
  fanControl: string;
  enableFanControl: string;
  enableFanControlDescription: string;
  fanMode: string;
  fanModeDefault: string;
  fanModeCustom: string;
  fanModeFixed: string;
  fanStatus: string;
  temperature: string;
  fanSpeed: string;
  mode: string;
  safetyOverride: string;
  safetyOverrideDescription: string;
  quickPresets: string;
  stock: string;
  stockDescription: string;
  silent: string;
  silentDescription: string;
  cool: string;
  coolDescription: string;
  gaming: string;
  gamingDescription: string;
  eco: string;
  ecoDescription: string;
  zeroRPM: string;
  zeroRPMDescription: string;
  temperatureHysteresis: string;
  temperatureHysteresisDescription: string;
  fixedFanSpeed: string;
  balancedDescription: string;
  aggressiveDescription: string;
  
  // Tests Tab
  runStressTest: string;
  selectTest: string;
  runTest: string;
  running: string;
  testInProgress: string;
  testHistory: string;
  noTests: string;
  optionalPackages: string;
  notInstalled: string;
  packagesNeeded: string;
  otherFeaturesWork: string;
  install: string;
  installing: string;
  
  // Diagnostics Tab
  systemInformation: string;
  platform: string;
  safeLimit: string;
  detection: string;
  successful: string;
  failed: string;
  currentConfiguration: string;
  activeCores: string;
  lkgCores: string;
  status: string;
  presetsCount: string;
  recentLogs: string;
  noLogs: string;
  exportDiagnostics: string;
  exporting: string;
  exportSuccessful: string;
  exportFailed: string;
  savedTo: string;
  
  // Common
  english: string;
  russian: string;
  loading: string;
  error: string;
  panicDisable: string;
  disabling: string;
  
  // Fan Tab - Loading/Error states
  loadingFanConfig: string;
  tryAgain: string;
  fanConfigUnavailable: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    // Settings Tab
    settingsTitle: "Settings",
    languageSection: "Language",
    interfaceLanguage: "Interface Language",
    selectLanguage: "Select Language",
    localizationComingSoon: "Localization coming soon! Currently English only.",
    expertModeSection: "Expert Undervolter Mode",
    enableExpertMode: "Enable Expert Mode",
    expertModeDescription: "Unlock extended range (-100mV) for all control modes",
    expertModeActiveGlobally: "Expert Mode Active Globally",
    expertModeWarningTitle: "Enable Expert Mode",
    expertModeWarningText: "⚠️ WARNING: Expert mode removes safety limits globally.",
    expertModeWarningAffects: "Affects: Manual, Per-Core, and Dynamic modes (-100mV range).",
    expertModeWarningRisk: "Use at your own risk!",
    iUnderstand: "I Understand",
    cancel: "Cancel",
    aboutSettingsSection: "About Settings",
    aboutExpertMode: "Expert Mode: Removes safety limits (-100mV). Applies globally to all control modes (Single, Per-Core, Dynamic).",
    aboutControlMode: "Control Mode Selection: Choose your preferred voltage control method in the Manual tab.",
    aboutLanguage: "Language: Interface localization.",
    
    // Expert Mode Tabs
    manualTab: "Manual",
    presetsTab: "Presets",
    testsTab: "Tests",
    fanTab: "Fan",
    diagnosticsTab: "Diagnostics",
    
    // Manual Tab
    simpleMode: "Simple Mode",
    perCoreMode: "Per-Core Mode",
    dynamicMode: "Dynamic Mode",
    expertMode: "Expert Mode",
    expertModeActive: "Expert mode active",
    expertModeRange: "Range: -100mV",
    allCores: "All Cores",
    core: "Core",
    apply: "Apply",
    disable: "Disable",
    reset: "Reset",
    currentValues: "Current Values",
    controlMode: "Control Mode",
    single: "Single",
    perCore: "Per-Core",
    dynamic: "Dynamic",
    
    // Dynamic Mode
    dynamicModeTitle: "Dynamic Mode",
    dynamicModeDescription: "Enable for automatic undervolt adaptation based on CPU load",
    dynamicModeDescriptionActive: "Automatic voltage adjustment based on real-time CPU load",
    active: "ACTIVE",
    off: "OFF",
    start: "Start",
    stop: "Stop",
    settings: "Settings",
    strategy: "Strategy",
    conservative: "Conservative",
    balanced: "Balanced",
    aggressive: "Aggressive",
    simpleModeDynamic: "Simple Mode",
    simpleModeDescription: "One value for all cores",
    undervoltValue: "Undervolt Value",
    sampleInterval: "Sample Interval",
    sampleIntervalDescription: "How often to check CPU load",
    hysteresis: "Hysteresis",
    hysteresisDescription: "Prevents frequent value switching",
    save: "Save",
    saving: "Saving...",
    howItWorks: "How it works:",
    
    // Presets Tab
    gameProfiles: "Game Profiles",
    globalPresets: "Global Presets",
    saveFor: "Save for",
    noGameProfiles: "No game profiles yet.",
    clickToCreate: "Click above to create one!",
    deleteProfile: "Delete Profile",
    noGlobalPresets: "No global presets saved.",
    saveCurrentValues: "Save Current Values",
    tested: "Tested",
    delete: "Delete",
    
    // Fan Tab
    fanControl: "Fan Control",
    enableFanControl: "Enable Fan Control",
    enableFanControlDescription: "Take manual control of the fan",
    fanMode: "Fan Mode",
    fanModeDefault: "Default (BIOS)",
    fanModeCustom: "Custom Curve",
    fanModeFixed: "Fixed Speed",
    fanStatus: "Fan Status",
    temperature: "Temperature",
    fanSpeed: "Fan Speed",
    mode: "Mode",
    safetyOverride: "SAFETY OVERRIDE",
    safetyOverrideDescription: "Safety override active: Fan running at maximum speed due to high temperature",
    quickPresets: "Quick Presets",
    stock: "Stock",
    stockDescription: "Factory BIOS curve",
    silent: "Silent",
    silentDescription: "Minimal noise, higher temps",
    cool: "Cool",
    coolDescription: "Low temps, more noise",
    gaming: "Gaming",
    gamingDescription: "Optimized for gaming",
    eco: "Eco",
    ecoDescription: "Power saving",
    zeroRPM: "Zero RPM Mode",
    zeroRPMDescription: "Allow fan to stop below 45°C (risky!)",
    temperatureHysteresis: "Temperature Hysteresis",
    temperatureHysteresisDescription: "Prevents rapid speed changes",
    fixedFanSpeed: "Fixed Fan Speed",
    balancedDescription: "Balance of noise and temps",
    aggressiveDescription: "Maximum cooling",
    
    // Tests Tab
    runStressTest: "Run Stress Test",
    selectTest: "Select Test",
    runTest: "Run Test",
    running: "Running",
    testInProgress: "Test in progress...",
    testHistory: "Test History (Last 10)",
    noTests: "No tests run yet.",
    optionalPackages: "Optional Packages",
    notInstalled: "Not installed:",
    packagesNeeded: "These packages are only needed for stress tests.",
    otherFeaturesWork: "All other plugin features work without them.",
    install: "Install",
    installing: "Installing...",
    
    // Diagnostics Tab
    systemInformation: "System Information",
    platform: "Platform",
    safeLimit: "Safe Limit",
    detection: "Detection",
    successful: "Successful",
    failed: "Failed",
    currentConfiguration: "Current Configuration",
    activeCores: "Active Cores",
    lkgCores: "LKG Cores",
    status: "Status",
    presetsCount: "Presets Count",
    recentLogs: "Recent Logs",
    noLogs: "No logs available",
    exportDiagnostics: "Export Diagnostics",
    exporting: "Exporting...",
    exportSuccessful: "Export Successful",
    exportFailed: "Export Failed",
    savedTo: "Saved to:",
    
    // Common
    english: "English",
    russian: "Русский",
    loading: "Loading...",
    error: "Error",
    panicDisable: "PANIC DISABLE",
    disabling: "Disabling...",
    
    // Fan Tab - Loading/Error states
    loadingFanConfig: "Loading fan configuration...",
    tryAgain: "Try Again",
    fanConfigUnavailable: "Fan configuration unavailable",
  },
  
  ru: {
    // Settings Tab
    settingsTitle: "Настройки",
    languageSection: "Язык",
    interfaceLanguage: "Язык интерфейса",
    selectLanguage: "Выбрать язык",
    localizationComingSoon: "Локализация скоро! Пока доступен только английский.",
    expertModeSection: "Экспертный режим андервольта",
    enableExpertMode: "Включить экспертный режим",
    expertModeDescription: "Разблокировать расширенный диапазон (-100мВ) для всех режимов",
    expertModeActiveGlobally: "Экспертный режим активен глобально",
    expertModeWarningTitle: "Включить экспертный режим",
    expertModeWarningText: "⚠️ ВНИМАНИЕ: Экспертный режим снимает ограничения безопасности глобально.",
    expertModeWarningAffects: "Влияет на: Ручной, По-ядерный и Динамический режимы (диапазон -100мВ).",
    expertModeWarningRisk: "Используйте на свой риск!",
    iUnderstand: "Я понимаю",
    cancel: "Отмена",
    aboutSettingsSection: "О настройках",
    aboutExpertMode: "Экспертный режим: Снимает ограничения безопасности (-100мВ). Применяется глобально ко всем режимам управления (Единый, По-ядерный, Динамический).",
    aboutControlMode: "Выбор режима управления: Выберите предпочитаемый метод управления напряжением во вкладке Ручной.",
    aboutLanguage: "Язык: Локализация интерфейса.",
    
    // Expert Mode Tabs
    manualTab: "Ручной",
    presetsTab: "Пресеты",
    testsTab: "Тесты",
    fanTab: "Вентилятор",
    diagnosticsTab: "Диагностика",
    
    // Manual Tab
    simpleMode: "Простой режим",
    perCoreMode: "По-ядерный режим",
    dynamicMode: "Динамический режим",
    expertMode: "Экспертный режим",
    expertModeActive: "Экспертный режим активен",
    expertModeRange: "Диапазон: -100мВ",
    allCores: "Все ядра",
    core: "Ядро",
    apply: "Применить",
    disable: "Отключить",
    reset: "Сброс",
    currentValues: "Текущие значения",
    controlMode: "Режим управления",
    single: "Единый",
    perCore: "По-ядерный",
    dynamic: "Динамический",
    
    // Dynamic Mode
    dynamicModeTitle: "Динамический режим",
    dynamicModeDescription: "Включите для автоматической адаптации андервольта под нагрузку процессора",
    dynamicModeDescriptionActive: "Автоматическая подстройка напряжения на основе нагрузки CPU в реальном времени",
    active: "АКТИВЕН",
    off: "ВЫКЛ",
    start: "Запустить",
    stop: "Остановить",
    settings: "Настройки",
    strategy: "Стратегия",
    conservative: "Безопасная",
    balanced: "Сбалансированная",
    aggressive: "Агрессивная",
    simpleModeDynamic: "Простой режим",
    simpleModeDescription: "Одно значение для всех ядер",
    undervoltValue: "Значение андервольта",
    sampleInterval: "Интервал опроса",
    sampleIntervalDescription: "Как часто проверять нагрузку CPU",
    hysteresis: "Гистерезис",
    hysteresisDescription: "Предотвращает частые переключения значений",
    save: "Сохранить",
    saving: "Сохранение...",
    howItWorks: "Как работает:",
    
    // Presets Tab
    gameProfiles: "Игровые профили",
    globalPresets: "Глобальные пресеты",
    saveFor: "Сохранить для",
    noGameProfiles: "Нет игровых профилей.",
    clickToCreate: "Нажмите выше, чтобы создать!",
    deleteProfile: "Удалить профиль",
    noGlobalPresets: "Нет сохранённых пресетов.",
    saveCurrentValues: "Сохранить текущие значения",
    tested: "Протестировано",
    delete: "Удалить",
    
    // Fan Tab
    fanControl: "Управление вентилятором",
    enableFanControl: "Включить управление вентилятором",
    enableFanControlDescription: "Взять ручное управление вентилятором",
    fanMode: "Режим вентилятора",
    fanModeDefault: "По умолчанию (BIOS)",
    fanModeCustom: "Своя кривая",
    fanModeFixed: "Фиксированная скорость",
    fanStatus: "Статус вентилятора",
    temperature: "Температура",
    fanSpeed: "Скорость вентилятора",
    mode: "Режим",
    safetyOverride: "ЗАЩИТНОЕ ПЕРЕОПРЕДЕЛЕНИЕ",
    safetyOverrideDescription: "Защитное переопределение активно: Вентилятор работает на максимальной скорости из-за высокой температуры",
    quickPresets: "Быстрые пресеты",
    stock: "Заводской",
    stockDescription: "Заводская кривая BIOS",
    silent: "Тихий",
    silentDescription: "Минимальный шум, выше температура",
    cool: "Холодный",
    coolDescription: "Низкая температура, больше шума",
    gaming: "Игровой",
    gamingDescription: "Оптимально для игр",
    eco: "Эко",
    ecoDescription: "Экономия энергии",
    zeroRPM: "Режим Zero RPM",
    zeroRPMDescription: "Разрешить остановку вентилятора ниже 45°C (рискованно!)",
    temperatureHysteresis: "Гистерезис температуры",
    temperatureHysteresisDescription: "Предотвращает быстрые изменения скорости",
    fixedFanSpeed: "Фиксированная скорость вентилятора",
    balancedDescription: "Баланс шума и температуры",
    aggressiveDescription: "Максимальное охлаждение",
    
    // Tests Tab
    runStressTest: "Запустить стресс-тест",
    selectTest: "Выбрать тест",
    runTest: "Запустить тест",
    running: "Выполняется",
    testInProgress: "Тест выполняется...",
    testHistory: "История тестов (последние 10)",
    noTests: "Тесты ещё не запускались.",
    optionalPackages: "Опциональные пакеты",
    notInstalled: "Не установлены:",
    packagesNeeded: "Эти пакеты нужны только для стресс-тестов.",
    otherFeaturesWork: "Остальные функции плагина работают без них.",
    install: "Установить",
    installing: "Установка...",
    
    // Diagnostics Tab
    systemInformation: "Системная информация",
    platform: "Платформа",
    safeLimit: "Безопасный лимит",
    detection: "Определение",
    successful: "Успешно",
    failed: "Не удалось",
    currentConfiguration: "Текущая конфигурация",
    activeCores: "Активные ядра",
    lkgCores: "LKG ядра",
    status: "Статус",
    presetsCount: "Количество пресетов",
    recentLogs: "Последние логи",
    noLogs: "Логи недоступны",
    exportDiagnostics: "Экспорт диагностики",
    exporting: "Экспорт...",
    exportSuccessful: "Экспорт успешен",
    exportFailed: "Экспорт не удался",
    savedTo: "Сохранено в:",
    
    // Common
    english: "English",
    russian: "Русский",
    loading: "Загрузка...",
    error: "Ошибка",
    panicDisable: "АВАРИЙНОЕ ОТКЛЮЧЕНИЕ",
    disabling: "Отключение...",
    
    // Fan Tab - Loading/Error states
    loadingFanConfig: "Загрузка конфигурации вентилятора...",
    tryAgain: "Попробовать снова",
    fanConfigUnavailable: "Конфигурация вентилятора недоступна",
  },
};

export function getTranslation(lang: Language): Translations {
  return translations[lang] || translations.en;
}

export { useTranslation } from "./useTranslation";
