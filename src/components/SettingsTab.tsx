/**
 * Settings tab for Expert Mode - global plugin settings.
 * Modern card-based design with animations and icons.
 */

import { useState, useEffect, FC } from "react";
import { DropdownItem, Focusable } from "@decky/ui";
import { 
  FaExclamationTriangle, 
  FaCheck, 
  FaTimes, 
  FaFlask, 
  FaInfoCircle,
  FaCheckCircle,
  FaLanguage
} from "react-icons/fa";
import { useDeckTune } from "../context";
import { getTranslation, Language } from "../i18n/translations";

export const SettingsTab: FC = () => {
  const { state, api } = useDeckTune();
  
  // Load language from localStorage first, then from state
  const [language, setLanguage] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('decktune_language');
      return (saved === "en" || saved === "ru") ? saved : (state.settings.language || "en");
    } catch {
      return state.settings.language || "en";
    }
  });
  
  const [expertModeEnabled, setExpertModeEnabled] = useState<boolean>(state.settings.expertMode || false);
  const [showExpertWarning, setShowExpertWarning] = useState<boolean>(false);

  const t = getTranslation(language);

  // Sync with state
  useEffect(() => {
    const stateLanguage = state.settings.language || "en";
    // Only update if different from localStorage
    try {
      const savedLanguage = localStorage.getItem('decktune_language');
      if (!savedLanguage || savedLanguage !== stateLanguage) {
        setLanguage(stateLanguage);
        localStorage.setItem('decktune_language', stateLanguage);
      }
    } catch (e) {
      console.error("Failed to sync language:", e);
    }
    setExpertModeEnabled(state.settings.expertMode || false);
  }, [state.settings]);

  const handleLanguageChange = async (newLang: Language) => {
    setLanguage(newLang);
    
    // Save to localStorage immediately
    try {
      localStorage.setItem('decktune_language', newLang);
    } catch (e) {
      console.error("Failed to save language to localStorage:", e);
    }
    
    // Save to backend settings
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
          backgroundColor: "rgba(0, 0, 0, 0.95)", zIndex: 9999,
          display: "flex", alignItems: "center", justifyContent: "center", 
          padding: "20px",
          animation: "fadeIn 0.2s ease-out"
        }}>
          <div style={{
            backgroundColor: "#1a1d23", 
            borderRadius: "12px", 
            padding: "20px",
            maxWidth: "400px", 
            border: "2px solid #ff6b6b",
            boxShadow: "0 8px 32px rgba(255, 107, 107, 0.3)",
            animation: "slideUp 0.3s ease-out"
          }}>
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              gap: "10px", 
              marginBottom: "16px",
              paddingBottom: "12px",
              borderBottom: "1px solid rgba(255, 107, 107, 0.3)"
            }}>
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                backgroundColor: "rgba(255, 107, 107, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}>
                <FaExclamationTriangle style={{ color: "#ff6b6b", fontSize: "18px" }} />
              </div>
              <div style={{ fontSize: "15px", fontWeight: "bold", color: "#ff6b6b" }}>
                {t.expertModeWarningTitle}
              </div>
            </div>
            <div style={{ fontSize: "11px", lineHeight: "1.6", marginBottom: "16px", color: "#e0e0e0" }}>
              <p style={{ marginBottom: "10px" }}>{t.expertModeWarningText}</p>
              <p style={{ 
                marginBottom: "10px", 
                color: "#ff9800",
                padding: "8px",
                backgroundColor: "rgba(255, 152, 0, 0.1)",
                borderRadius: "6px",
                borderLeft: "3px solid #ff9800"
              }}>
                <strong>{t.expertModeWarningAffects}</strong>
              </p>
              <p style={{ 
                color: "#f44336", 
                fontWeight: "bold", 
                fontSize: "10px",
                padding: "8px",
                backgroundColor: "rgba(244, 67, 54, 0.1)",
                borderRadius: "6px",
                textAlign: "center"
              }}>
                ⚠️ {t.expertModeWarningRisk}
              </p>
            </div>
            <Focusable style={{ display: "flex", gap: "10px" }} flow-children="horizontal">
              <Focusable 
                style={{ flex: 1 }} 
                focusClassName="gpfocus-danger" 
                onActivate={handleExpertModeConfirm} 
                onClick={handleExpertModeConfirm}
              >
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  gap: "6px",
                  padding: "10px", 
                  background: "linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%)",
                  borderRadius: "6px", 
                  cursor: "pointer",
                  fontSize: "11px", 
                  fontWeight: "bold",
                  transition: "all 0.2s ease",
                  boxShadow: "0 2px 8px rgba(183, 28, 28, 0.4)"
                }}>
                  <FaCheck size={11} />
                  <span>{t.iUnderstand}</span>
                </div>
              </Focusable>
              <Focusable 
                style={{ flex: 1 }} 
                focusClassName="gpfocus" 
                onActivate={handleExpertModeCancel} 
                onClick={handleExpertModeCancel}
              >
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center", 
                  gap: "6px",
                  padding: "10px", 
                  backgroundColor: "#3d4450",
                  borderRadius: "6px", 
                  cursor: "pointer",
                  fontSize: "11px", 
                  fontWeight: "bold",
                  transition: "all 0.2s ease"
                }}>
                  <FaTimes size={11} />
                  <span>{t.cancel}</span>
                </div>
              </Focusable>
            </Focusable>
          </div>
        </div>
      )}

      <Focusable style={{ display: "flex", flexDirection: "column", gap: "12px" }} flow-children="vertical">
        {/* Language Card */}
        <Focusable 
          onFocus={(e) => e.currentTarget.scrollIntoView({ behavior: "smooth", block: "nearest" })}
        >
        <div style={{
          background: "linear-gradient(135deg, #1a3a5c 0%, #1a2a4c 100%)",
          borderRadius: "10px",
          padding: "14px",
          border: "1px solid rgba(26, 159, 255, 0.2)",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          animation: "fadeInUp 0.4s ease-out"
        }}>
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "10px", 
            marginBottom: "12px" 
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #1a9fff 0%, #0d7fd8 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 2px 8px rgba(26, 159, 255, 0.4)"
            }}>
              <FaLanguage size={16} style={{ color: "#fff" }} />
            </div>
            <div>
              <div style={{ fontSize: "13px", fontWeight: "bold", color: "#fff" }}>
                {t.languageSection}
              </div>
              <div style={{ fontSize: "9px", color: "#8b929a", marginTop: "2px" }}>
                Interface Language / Язык интерфейса
              </div>
            </div>
          </div>
          
          {/* Current Language Display */}
          <div style={{
            padding: "10px 12px",
            backgroundColor: "rgba(26, 159, 255, 0.1)",
            borderRadius: "6px",
            marginBottom: "8px",
            border: "1px solid rgba(26, 159, 255, 0.2)"
          }}>
            <div style={{ fontSize: "9px", color: "#8b929a", marginBottom: "4px" }}>
              {language === "ru" ? "Текущий язык:" : "Current Language:"}
            </div>
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#fff" }}>
              {language === "en" ? "🇬🇧 English" : "🇷🇺 Русский"}
            </div>
          </div>
          
          <DropdownItem 
            label={language === "ru" ? "Изменить язык" : "Change Language"}
            menuLabel={t.selectLanguage}
            rgOptions={[
              { data: "en", label: `🇬🇧 ${t.english}` }, 
              { data: "ru", label: `🇷🇺 ${t.russian}` }
            ]}
            selectedOption={language === "en" ? 0 : 1}
            onChange={(option: any) => handleLanguageChange(option.data)}
            bottomSeparator="none"
          />
          
          {/* Language saved indicator */}
          <div style={{
            marginTop: "8px",
            padding: "6px 10px",
            backgroundColor: "rgba(76, 175, 80, 0.15)",
            borderRadius: "6px",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "9px",
            color: "#81c784"
          }}>
            <FaCheckCircle size={9} />
            <span>
              {language === "ru" 
                ? "Язык сохранён автоматически" 
                : "Language saved automatically"}
            </span>
          </div>
        </div>
      </Focusable>

        {/* Expert Mode Card */}
        <Focusable 
          onFocus={(e) => e.currentTarget.scrollIntoView({ behavior: "smooth", block: "nearest" })}
        >
        <div style={{
          background: expertModeEnabled 
            ? "linear-gradient(135deg, #5c1313 0%, #7c1c1c 100%)"
            : "linear-gradient(135deg, #2a2d35 0%, #23262e 100%)",
          borderRadius: "10px",
          padding: "14px",
          marginBottom: "12px",
          border: expertModeEnabled 
            ? "1px solid rgba(255, 107, 107, 0.4)" 
            : "1px solid rgba(61, 68, 80, 0.4)",
          boxShadow: expertModeEnabled
            ? "0 4px 16px rgba(255, 107, 107, 0.3)"
            : "0 4px 12px rgba(0, 0, 0, 0.3)",
          animation: "fadeInUp 0.5s ease-out",
          transition: "all 0.3s ease"
        }}>
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "10px", 
            marginBottom: "12px" 
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: expertModeEnabled
                ? "linear-gradient(135deg, #ff6b6b 0%, #f44336 100%)"
                : "linear-gradient(135deg, #5c4813 0%, #7c6013 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: expertModeEnabled
                ? "0 2px 8px rgba(255, 107, 107, 0.4)"
                : "0 2px 8px rgba(92, 72, 19, 0.4)",
              animation: expertModeEnabled ? "pulse 2s ease-in-out infinite" : "none"
            }}>
              <FaFlask size={14} style={{ color: "#fff" }} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: "13px", fontWeight: "bold", color: "#fff" }}>
                {t.expertModeSection}
              </div>
              <div style={{ fontSize: "9px", color: "#8b929a", marginTop: "2px" }}>
                {expertModeEnabled 
                  ? (language === "ru" ? "⚠️ Активен (-100мВ)" : "⚠️ Active (-100mV)")
                  : (language === "ru" ? "Безопасный режим" : "Safe mode")}
              </div>
            </div>
          </div>
          
          {/* Custom Toggle for Expert Mode */}
          <Focusable
            onActivate={() => handleExpertModeToggle(!expertModeEnabled)}
            onClick={() => handleExpertModeToggle(!expertModeEnabled)}
          >
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "10px 12px",
              backgroundColor: "rgba(255, 255, 255, 0.05)",
              borderRadius: "6px",
              cursor: "pointer",
              transition: "all 0.2s ease"
            }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "11px", fontWeight: "bold", color: "#fff", marginBottom: "2px" }}>
                  {t.enableExpertMode}
                </div>
                <div style={{ fontSize: "9px", color: "#8b929a" }}>
                  {t.expertModeDescription}
                </div>
              </div>
              <div style={{
                width: "44px",
                height: "24px",
                borderRadius: "12px",
                backgroundColor: expertModeEnabled ? "#4caf50" : "#3d4450",
                position: "relative",
                transition: "all 0.3s ease",
                marginLeft: "12px"
              }}>
                <div style={{
                  width: "20px",
                  height: "20px",
                  borderRadius: "10px",
                  backgroundColor: "#fff",
                  position: "absolute",
                  top: "2px",
                  left: expertModeEnabled ? "22px" : "2px",
                  transition: "all 0.3s ease",
                  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.3)"
                }} />
              </div>
            </div>
          </Focusable>
          
          {expertModeEnabled && (
            <div style={{ 
              marginTop: "10px",
              padding: "10px", 
              backgroundColor: "rgba(255, 152, 0, 0.15)",
              borderRadius: "6px", 
              border: "1px solid rgba(255, 152, 0, 0.3)",
              animation: "slideDown 0.3s ease-out"
            }}>
              <div style={{ 
                fontSize: "10px", 
                color: "#ffb74d", 
                display: "flex", 
                alignItems: "center", 
                gap: "6px", 
                marginBottom: "6px",
                fontWeight: "bold"
              }}>
                <FaExclamationTriangle size={10} />
                <span>{t.expertModeActiveGlobally}</span>
              </div>
              <div style={{ fontSize: "9px", color: "#ff9800", lineHeight: "1.5" }}>
                • {t.expertModeRange}<br/>
                • {language === "ru" ? "Применяется к: Единый, По-ядерный, Динамический" : "Applies to: Single, Per-Core, Dynamic"}<br/>
                • {language === "ru" ? "Используйте с особой осторожностью!" : "Use with extreme caution!"}
              </div>
            </div>
          )}
        </div>
      </Focusable>

        {/* Info Card */}
        <Focusable
          onFocus={(e) => e.currentTarget.scrollIntoView({ behavior: "smooth", block: "nearest" })}
        >
        <div style={{
          background: "linear-gradient(135deg, #1a2a3a 0%, #1a1d23 100%)",
          borderRadius: "10px",
          padding: "14px",
          border: "1px solid rgba(139, 146, 154, 0.2)",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          animation: "fadeInUp 0.6s ease-out"
        }}>
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "10px", 
            marginBottom: "12px" 
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #4caf50 0%, #388e3c 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 2px 8px rgba(76, 175, 80, 0.4)"
            }}>
              <FaInfoCircle size={14} style={{ color: "#fff" }} />
            </div>
            <div style={{ fontSize: "13px", fontWeight: "bold", color: "#fff" }}>
              {t.aboutSettingsSection}
            </div>
          </div>
          
          <div style={{ 
            fontSize: "10px", 
            color: "#a0a0a0", 
            lineHeight: "1.6",
            padding: "10px",
            backgroundColor: "rgba(255, 255, 255, 0.03)",
            borderRadius: "6px"
          }}>
            <div style={{ marginBottom: "8px", display: "flex", gap: "6px" }}>
              <span style={{ color: "#1a9fff", minWidth: "4px" }}>•</span>
              <div>
                <strong style={{ color: "#1a9fff" }}>{t.expertModeSection}:</strong>{" "}
                <span style={{ color: "#c0c0c0" }}>{t.aboutExpertMode}</span>
              </div>
            </div>
            <div style={{ marginBottom: "8px", display: "flex", gap: "6px" }}>
              <span style={{ color: "#4caf50", minWidth: "4px" }}>•</span>
              <div>
                <strong style={{ color: "#4caf50" }}>
                  {language === "ru" ? "Режимы управления" : "Control Modes"}:
                </strong>{" "}
                <span style={{ color: "#c0c0c0" }}>{t.aboutControlMode}</span>
              </div>
            </div>
            <div style={{ display: "flex", gap: "6px" }}>
              <span style={{ color: "#ff9800", minWidth: "4px" }}>•</span>
              <div>
                <strong style={{ color: "#ff9800" }}>{t.languageSection}:</strong>{" "}
                <span style={{ color: "#c0c0c0" }}>{t.aboutLanguage}</span>
              </div>
            </div>
          </div>
        </div>
      </Focusable>
      </Focusable>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(20px);
          }
          to { 
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideDown {
          from {
            opacity: 0;
            max-height: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            max-height: 200px;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse { 
          0%, 100% { 
            box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); 
          } 
          50% { 
            box-shadow: 0 0 0 8px rgba(255, 107, 107, 0); 
          } 
        }
        
        .gpfocus {
          box-shadow: 0 0 12px rgba(26, 159, 255, 0.8) !important;
          transform: scale(1.03);
          transition: all 0.2s ease;
        }
        
        .gpfocus-danger {
          box-shadow: 0 0 12px rgba(255, 107, 107, 0.8) !important;
          transform: scale(1.03);
          transition: all 0.2s ease;
        }
      `}</style>
    </>
  );
};
