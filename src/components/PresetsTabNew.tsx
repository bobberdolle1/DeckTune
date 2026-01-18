/**
 * Redesigned Presets tab - compact and gamepad-friendly.
 * 
 * Two sections:
 * 1. Game Profiles - auto-switching profiles per game
 * 2. Global Presets - manual presets you can apply anytime
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSectionRow,
  Focusable,
  showModal,
  ConfirmModal,
} from "@decky/ui";
import { call } from "@decky/api";
import {
  FaGamepad,
  FaGlobe,
  FaPlus,
  FaCheck,
  FaTrash,
  FaSpinner,
} from "react-icons/fa";
import { useDeckTune, useProfiles } from "../context";
import { Preset, GameProfile } from "../api/types";
import { useTranslation } from "../i18n/translations";

export const PresetsTabNew: FC = () => {
  const { state, api } = useDeckTune();
  const { t } = useTranslation();
  const profilesHook = useProfiles();
  
  // Extra safety: ensure profiles is always an array
  const profiles = Array.isArray(profilesHook.profiles) ? profilesHook.profiles : [];
  const { activeProfile, runningAppId, runningAppName } = profilesHook;
  
  const [activeSection, setActiveSection] = useState<"profiles" | "presets">("profiles");

  // Load profiles on mount
  useEffect(() => {
    const loadProfiles = async () => {
      try {
        await api.getProfiles();
      } catch (e) {
        console.error("Failed to load profiles:", e);
      }
    };
    loadProfiles();
  }, [api]);

  return (
    <>
      {/* Section switcher */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            gap: "4px",
            marginBottom: "12px",
            backgroundColor: "#23262e",
            borderRadius: "4px",
            padding: "2px",
          }}
          flow-children="horizontal"
        >
          <Focusable
            className={`section-button ${activeSection === "profiles" ? "active" : ""}`}
            focusClassName="gpfocus"
            onActivate={() => setActiveSection("profiles")}
            onClick={() => setActiveSection("profiles")}
            style={{ flex: 1 }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", padding: "6px", fontSize: "10px" }}>
              <FaGamepad size={10} />
              <span>{t.gameProfiles}</span>
            </div>
          </Focusable>
          
          <Focusable
            className={`section-button ${activeSection === "presets" ? "active" : ""}`}
            focusClassName="gpfocus"
            onActivate={() => setActiveSection("presets")}
            onClick={() => setActiveSection("presets")}
            style={{ flex: 1 }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "4px", padding: "6px", fontSize: "10px" }}>
              <FaGlobe size={10} />
              <span>{t.globalPresets}</span>
            </div>
          </Focusable>
        </Focusable>
      </PanelSectionRow>

      {/* Content */}
      {activeSection === "profiles" ? (
        <GameProfilesSection profiles={profiles} activeProfile={activeProfile} runningAppId={runningAppId} runningAppName={runningAppName} api={api} />
      ) : (
        <GlobalPresetsSection presets={state.presets} api={api} />
      )}

      <style>
        {`
          .section-button {
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            background-color: transparent;
            color: #8b929a;
          }
          .section-button.active {
            background-color: #1a9fff;
            color: #fff;
          }
          .section-button.gpfocus {
            border: 2px solid #1a9fff;
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
          }
          .section-button:hover {
            background-color: rgba(26, 159, 255, 0.2);
          }
          
          .preset-action-btn {
            border-radius: 4px;
            transition: all 0.2s ease;
          }
          .preset-action-btn.gpfocus {
            transform: scale(1.05);
            box-shadow: 0 0 8px rgba(26, 159, 255, 0.6);
          }
          .preset-apply.gpfocus > div {
            background-color: #1585d8 !important;
          }
          .preset-delete.gpfocus > div {
            background-color: #3a3d45 !important;
          }
          
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </>
  );
};

/**
 * Game Profiles Section
 */
interface GameProfilesSectionProps {
  profiles: GameProfile[];
  activeProfile: GameProfile | null;
  runningAppId: number | null;
  runningAppName: string | null;
  api: any;
}

const GameProfilesSection: FC<GameProfilesSectionProps> = ({ profiles, activeProfile, runningAppId, runningAppName, api }) => {
  const { t } = useTranslation();
  const [isCreating, setIsCreating] = useState(false);

  const handleQuickCreate = async () => {
    if (!runningAppId || !runningAppName) return;
    
    setIsCreating(true);
    try {
      const result = await api.createProfileForCurrentGame();
      if (!result.success) {
        alert(`Failed: ${result.error}`);
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (appId: number, name: string) => {
    showModal(
      <ConfirmModal
        strTitle={t.deleteProfile}
        strDescription={`${t.deleteProfile} ${name}?`}
        strOKButtonText={t.delete}
        strCancelButtonText={t.cancel}
        onOK={async () => {
          await api.deleteProfile(appId);
        }}
      />
    );
  };

  const formatCores = (cores: number[]): string => {
    const allSame = cores.every(v => v === cores[0]);
    return allSame ? `${cores[0]}mV` : cores.map(v => `${v}`).join("/");
  };

  return (
    <>
      {/* Quick create button */}
      {runningAppId && runningAppName && (
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleQuickCreate}
            disabled={isCreating}
            style={{ backgroundColor: "#1a9fff", marginBottom: "8px", minHeight: "32px" }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "6px", fontSize: "10px" }}>
              {isCreating ? <FaSpinner className="spin" size={10} /> : <FaPlus size={10} />}
              <span>{t.saveFor} {runningAppName}</span>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      )}

      {/* Profile list */}
      {profiles.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" }}>
            {t.noGameProfiles}
            {runningAppId && <div style={{ marginTop: "4px" }}>{t.clickToCreate}</div>}
          </div>
        </PanelSectionRow>
      ) : (
        profiles.map((profile) => {
          const isActive = activeProfile?.app_id === profile.app_id || runningAppId === profile.app_id;
          return (
            <PanelSectionRow key={profile.app_id}>
              <div style={{ marginBottom: "6px" }}>
                {/* Profile info */}
                <div style={{ 
                  padding: "6px 8px", 
                  backgroundColor: isActive ? "#1a3a5c" : "#23262e", 
                  borderRadius: "6px 6px 0 0",
                  border: isActive ? "2px solid #1a9fff" : "none",
                  borderBottom: "1px solid #3d4450"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ fontSize: "11px", fontWeight: "bold", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {profile.name}
                    </span>
                    {isActive && (
                      <span style={{ fontSize: "8px", padding: "1px 4px", backgroundColor: "#4caf50", borderRadius: "2px", fontWeight: "bold" }}>
                        {t.active}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: "9px", color: "#8b929a", marginTop: "2px" }}>
                    {formatCores(profile.cores)}
                    {profile.dynamic_enabled && <span style={{ marginLeft: "6px", color: "#4caf50" }}>⚡ Dynamic</span>}
                  </div>
                </div>
                
                {/* Action button */}
                <Focusable
                  style={{
                    backgroundColor: "#1a1d24",
                    borderRadius: "0 0 6px 6px",
                    padding: "6px",
                  }}
                >
                  <Focusable
                    className="preset-action-btn preset-delete"
                    focusClassName="gpfocus"
                    onActivate={() => handleDelete(profile.app_id, profile.name)}
                    onClick={() => handleDelete(profile.app_id, profile.name)}
                  >
                    <div style={{ 
                      display: "flex", 
                      alignItems: "center", 
                      justifyContent: "center", 
                      gap: "4px", 
                      padding: "6px 8px",
                      fontSize: "9px",
                      fontWeight: "600",
                      borderRadius: "4px",
                      backgroundColor: "#2a2d35",
                      color: "#f44336",
                      cursor: "pointer",
                      transition: "all 0.2s ease"
                    }}>
                      <FaTrash size={8} />
                      <span>{t.deleteProfile}</span>
                    </div>
                  </Focusable>
                </Focusable>
              </div>
            </PanelSectionRow>
          );
        })
      )}

      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </>
  );
};

/**
 * Global Presets Section
 */
interface GlobalPresetsSectionProps {
  presets: Preset[];
  api: any;
}

const GlobalPresetsSection: FC<GlobalPresetsSectionProps> = ({ presets, api }) => {
  const { t } = useTranslation();
  const [isApplying, setIsApplying] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleApply = async (preset: Preset) => {
    setIsApplying(preset.app_id);
    try {
      await api.applyUndervolt(preset.value);
    } finally {
      setIsApplying(null);
    }
  };

  const handleDelete = async (appId: number, label: string) => {
    showModal(
      <ConfirmModal
        strTitle={t.delete}
        strDescription={`${t.delete} "${label}"?`}
        strOKButtonText={t.delete}
        strCancelButtonText={t.cancel}
        onOK={async () => {
          await api.deletePreset(appId);
        }}
      />
    );
  };

  const handleQuickSave = async () => {
    setIsSaving(true);
    try {
      const timestamp = new Date().toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
      const label = `Preset ${timestamp}`;
      
      // Get current cores from API state
      const cores = api.state.cores || [0, 0, 0, 0];
      
      // Create preset object
      const preset = {
        app_id: Date.now(), // Use timestamp as unique ID
        label: label,
        value: cores,
        timeout: 0,
        use_timeout: false,
        tested: false,
      };
      
      console.log("Saving preset:", preset);
      
      // Call backend to save preset
      const result = await call("save_preset", preset);
      
      console.log("Save result:", result);
      
      if (result.success) {
        // Reload presets directly
        const updatedPresets = await call("get_presets");
        console.log("Updated presets:", updatedPresets);
        
        // Use setState to properly trigger React re-render
        api.setState({ presets: updatedPresets });
      }
    } catch (e) {
      console.error("Failed to save preset:", e);
      alert(`Failed to save: ${e}`);
    } finally {
      setIsSaving(false);
    }
  };

  const formatCores = (cores: number[]): string => {
    const allSame = cores.every(v => v === cores[0]);
    return allSame ? `${cores[0]}mV` : cores.map(v => `${v}`).join("/");
  };

  return (
    <>
      {/* Quick save button */}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={handleQuickSave}
          disabled={isSaving}
          style={{ backgroundColor: "#1a9fff", marginBottom: "8px", minHeight: "32px" }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "6px", fontSize: "10px" }}>
            {isSaving ? <FaSpinner className="spin" size={10} /> : <FaPlus size={10} />}
            <span>{t.saveCurrentValues}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {/* Preset list */}
      {presets.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" }}>
            {t.noGlobalPresets}
            <div style={{ marginTop: "4px" }}>{t.clickToCreate}</div>
          </div>
        </PanelSectionRow>
      ) : (
        presets.map((preset) => {
          const isApplyingThis = isApplying === preset.app_id;
          return (
            <PanelSectionRow key={preset.app_id}>
              <div style={{ marginBottom: "6px" }}>
                {/* Preset info */}
                <div style={{ padding: "6px 8px", backgroundColor: "#23262e", borderRadius: "6px 6px 0 0", borderBottom: "1px solid #3d4450" }}>
                  <div style={{ fontSize: "11px", fontWeight: "bold", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {preset.label}
                  </div>
                  <div style={{ fontSize: "9px", color: "#8b929a", marginTop: "2px" }}>
                    {formatCores(preset.value)}
                    {preset.tested && <span style={{ marginLeft: "6px", color: "#4caf50" }}>✓ {t.tested}</span>}
                  </div>
                </div>
                
                {/* Action buttons */}
                <Focusable
                  style={{
                    display: "flex",
                    gap: "4px",
                    backgroundColor: "#1a1d24",
                    borderRadius: "0 0 6px 6px",
                    padding: "6px",
                  }}
                  flow-children="horizontal"
                >
                  <Focusable
                    style={{ flex: 1 }}
                    className="preset-action-btn preset-apply"
                    focusClassName="gpfocus"
                    onActivate={() => handleApply(preset)}
                    onClick={() => handleApply(preset)}
                  >
                    <div style={{ 
                      display: "flex", 
                      alignItems: "center", 
                      justifyContent: "center", 
                      gap: "4px", 
                      padding: "6px 8px",
                      fontSize: "9px",
                      fontWeight: "600",
                      borderRadius: "4px",
                      backgroundColor: "#1a9fff",
                      color: "#fff",
                      cursor: "pointer",
                      transition: "all 0.2s ease"
                    }}>
                      {isApplyingThis ? <FaSpinner className="spin" size={9} /> : <FaCheck size={9} />}
                      <span>{t.apply}</span>
                    </div>
                  </Focusable>
                  
                  <Focusable
                    style={{ flex: 1 }}
                    className="preset-action-btn preset-delete"
                    focusClassName="gpfocus"
                    onActivate={() => handleDelete(preset.app_id, preset.label)}
                    onClick={() => handleDelete(preset.app_id, preset.label)}
                  >
                    <div style={{ 
                      display: "flex", 
                      alignItems: "center", 
                      justifyContent: "center", 
                      gap: "4px", 
                      padding: "6px 8px",
                      fontSize: "9px",
                      fontWeight: "600",
                      borderRadius: "4px",
                      backgroundColor: "#2a2d35",
                      color: "#f44336",
                      cursor: "pointer",
                      transition: "all 0.2s ease"
                    }}>
                      <FaTrash size={8} />
                      <span>{t.delete}</span>
                    </div>
                  </Focusable>
                </Focusable>
              </div>
            </PanelSectionRow>
          );
        })
      )}

      <style>
        {`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </>
  );
};
