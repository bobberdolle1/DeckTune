/**
 * Settings tab for Expert Mode - global plugin settings.
 */

import { useState, useEffect, FC } from "react";
import { PanelSectionRow, ToggleField, DropdownItem, Focusable } from "@decky/ui";
import { FaExclamationTriangle, FaExclamationCircle, FaCheck, FaTimes } from "react-icons/fa";
import { useDeckTune } from "../context";
import { getTranslation, Language } from "../i18n/translations";

export const SettingsTab: FC = () => {
  const { state, api } = useDeckTune();
  const [language, setLanguage] = useState<Language>(state.settings.language || "en");
  const [expertModeEnabled, setExpertModeEnabled] = useState<boolean>(state.settings.expertMode || false);
  const [showExpertWarning, setShowExpertWarning] = useState<boolean>(false);

  const t = getTranslation(language);

  // Sync with state
  useEffect(() => {
    setLanguage(state.settings.language || "en");
    setExpertModeEnabled(state.settings.expertMode || false);
  }, [state.settings]);

  const handleLanguageChange = async (newLang: Language) => {
    setLanguage(newLang);
    await api.saveSettings({
      ...state.settings,
      language: newLang,
    });
  };

  const handleExpertModeToggle = (value: boolean) => {
    if (value && !expertModeEnabled) {
      setShowExpertWarning(true);
    } else {
      setExpertModeEnabled(value);
      api.saveSettings({
        ...state.settings,
        expertMode: value,
      });
    }
  };

  const handleExpertModeConfirm = () => {
    setExpertModeEnabled(true);
    setShowExpertWarning(false);
    api.saveSettings({
      ...state.settings,
      expertMode: true,
    });
  };

  const handleExpertModeCancel = () => {
    setShowExpertWarning(false);
  };

  return (
    <>
      {/* Expert Mode Warning Dialog */}
      {showExpertWarning && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.9)", zIndex: 9999,
          display: "flex", alignItems: "center", justifyContent: "center", padding: "20px"
        }}>
          <div style={{
            backgroundColor: "#1a1d23", borderRadius: "8px", padding: "16px",
            maxWidth: "400px", border: "2px solid #ff6b6b"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <FaExclamationTriangle style={{ color: "#ff6b6b", fontSize: "20px" }} />
              <div style={{ fontSize: "14px", fontWeight: "bold", color: "#ff6b6b" }}>
                {t.expertModeWarningTitle}
              </div>
            </div>
            <div style={{ fontSize: "11px", lineHeight: "1.5", marginBottom: "12px", color: "#e0e0e0" }}>
              <p style={{ marginBottom: "8px" }}>{t.expertModeWarningText}</p>
              <p style={{ marginBottom: "8px", color: "#ff9800" }}>
                <strong>{t.expertModeWarningAffects}</strong>
              </p>
              <p style={{ color: "#f44336", fontWeight: "bold", fontSize: "10px" }}>
                {t.expertModeWarningRisk}
              </p>
            </div>
            <Focusable style={{ display: "flex", gap: "8px" }} flow-children="horizontal">
              <Focusable style={{ flex: 1 }} focusClassName="gpfocus" onActivate={handleExpertModeConfirm} onClick={handleExpertModeConfirm}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px",
                  padding: "8px", backgroundColor: "#b71c1c", borderRadius: "4px", cursor: "pointer",
                  fontSize: "10px", fontWeight: "bold" }}>
                  <FaCheck size={10} /><span>{t.iUnderstand}</span>
                </div>
              </Focusable>
              <Focusable style={{ flex: 1 }} focusClassName="gpfocus" onActivate={handleExpertModeCancel} onClick={handleExpertModeCancel}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px",
                  padding: "8px", backgroundColor: "#3d4450", borderRadius: "4px", cursor: "pointer",
                  fontSize: "10px", fontWeight: "bold" }}>
                  <FaTimes size={10} /><span>{t.cancel}</span>
                </div>
              </Focusable>
            </Focusable>
          </div>
        </div>
      )}

      {/* Language Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
          {t.languageSection} / Language
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <DropdownItem 
          label={t.interfaceLanguage}
          menuLabel={t.selectLanguage}
          rgOptions={[
            { data: "en", label: t.english }, 
            { data: "ru", label: t.russian }
          ]}
          selectedOption={language === "en" ? 0 : 1}
          onChange={(option: any) => handleLanguageChange(option.data)}
        />
      </PanelSectionRow>

      {/* Expert Mode Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          {t.expertModeSection}
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField 
          label={t.enableExpertMode}
          description={t.expertModeDescription}
          checked={expertModeEnabled} 
          onChange={handleExpertModeToggle}
          bottomSeparator="none"
        />
      </PanelSectionRow>
      {expertModeEnabled && (
        <PanelSectionRow>
          <div style={{ 
            padding: "8px", 
            background: "linear-gradient(135deg, #5c1313 0%, #7c1c1c 100%)",
            borderRadius: "6px", 
            border: "1px solid #ff6b6b", 
            marginBottom: "12px",
            animation: "pulse 2s ease-in-out infinite"
          }}>
            <div style={{ fontSize: "10px", color: "#ffb74d", display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <FaExclamationTriangle size={10} />
              <span style={{ fontWeight: "bold" }}>{t.expertModeActiveGlobally}</span>
            </div>
            <div style={{ fontSize: "9px", color: "#ff9800" }}>
              • {t.expertModeRange}<br/>
              • {language === "ru" ? "Применяется к: Единый, По-ядерный, Динамический" : "Applies to: Single, Per-Core, Dynamic"}<br/>
              • {language === "ru" ? "Используйте с особой осторожностью!" : "Use with extreme caution!"}
            </div>
          </div>
        </PanelSectionRow>
      )}

      {/* About Settings Section */}
      <PanelSectionRow>
        <div style={{ fontSize: "14px", fontWeight: "bold", marginTop: "16px", marginBottom: "8px" }}>
          {t.aboutSettingsSection}
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <div style={{ padding: "12px", backgroundColor: "#23262e", borderRadius: "8px", fontSize: "10px", color: "#8b929a", lineHeight: "1.6" }}>
          <p style={{ marginBottom: "8px" }}>
            <strong style={{ color: "#1a9fff" }}>{t.expertModeSection}:</strong> {t.aboutExpertMode}
          </p>
          <p style={{ marginBottom: "8px" }}>
            <strong style={{ color: "#1a9fff" }}>
              {language === "ru" ? "Выбор режима управления" : "Control Mode Selection"}:
            </strong> {t.aboutControlMode}
          </p>
          <p>
            <strong style={{ color: "#1a9fff" }}>{t.languageSection}:</strong> {t.aboutLanguage}
          </p>
        </div>
      </PanelSectionRow>

      <style>{`
        @keyframes pulse { 
          0%, 100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); } 
          50% { box-shadow: 0 0 0 8px rgba(255, 107, 107, 0); } 
        }
        .gpfocus {
          box-shadow: 0 0 8px rgba(26, 159, 255, 0.8) !important;
          transform: scale(1.02);
        }
      `}</style>
    </>
  );
};
