/**
 * useTranslation hook for accessing translations in components
 */

import { useMemo } from "react";
import { useDeckTune } from "../context";
import { getTranslation, Language } from "./translations";

export function useTranslation() {
  const { state } = useDeckTune();
  
  // Get language from state or localStorage, fallback to English
  const language: Language = useMemo(() => {
    try {
      const saved = localStorage.getItem('decktune_language');
      if (saved === "en" || saved === "ru") return saved;
    } catch {
      // Ignore localStorage errors
    }
    return (state.settings.language as Language) || "en";
  }, [state.settings.language]);
  
  const t = useMemo(() => getTranslation(language), [language]);
  
  return { t, language };
}
