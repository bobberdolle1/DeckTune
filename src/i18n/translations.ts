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
  
  // Manual Tab
  manualTab: string;
  simpleMode: string;
  perCoreMode: string;
  expertMode: string;
  expertModeActive: string;
  expertModeRange: string;
  allCores: string;
  core: string;
  apply: string;
  disable: string;
  reset: string;
  
  // Common
  english: string;
  russian: string;
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
    
    // Manual Tab
    manualTab: "Manual",
    simpleMode: "Simple Mode",
    perCoreMode: "Per-Core Mode",
    expertMode: "Expert Mode",
    expertModeActive: "Expert mode active",
    expertModeRange: "Range: -100mV",
    allCores: "All Cores",
    core: "Core",
    apply: "Apply",
    disable: "Disable",
    reset: "Reset",
    
    // Common
    english: "English",
    russian: "Русский",
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
    
    // Manual Tab
    manualTab: "Ручной",
    simpleMode: "Простой режим",
    perCoreMode: "По-ядерный режим",
    expertMode: "Экспертный режим",
    expertModeActive: "Экспертный режим активен",
    expertModeRange: "Диапазон: -100мВ",
    allCores: "Все ядра",
    core: "Ядро",
    apply: "Применить",
    disable: "Отключить",
    reset: "Сброс",
    
    // Common
    english: "English",
    russian: "Русский",
  },
};

export function getTranslation(lang: Language): Translations {
  return translations[lang] || translations.en;
}
