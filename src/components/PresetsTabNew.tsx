/**
 * Updated Presets tab component with Game Profile management.
 * Requirements: 3.2, 5.1, 5.4, 7.3, 9.1, 9.2
 * 
 * Features:
 * - Game profile list with edit/delete
 * - Quick-create button when game is running
 * - Import/export profile buttons
 * - Legacy preset list with edit/delete/export
 * - Import preset button
 */

import React, { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSectionRow,
  SliderField,
  DropdownItem,
  Focusable,
  TextField,
  ToggleField,
} from "@decky/ui";
import {
  FaDownload,
  FaUpload,
  FaTrash,
  FaEdit,
  FaSpinner,
  FaRocket,
} from "react-icons/fa";
import { useDeckTune, useProfiles } from "../context";
import { Preset, GameProfile } from "../api/types";

export const PresetsTabNew: FC = () => {
  const { state, api } = useDeckTune();
  const { profiles, activeProfile, runningAppId, runningAppName, createProfileForCurrentGame, deleteProfile, exportProfiles, importProfiles } = useProfiles();
  const [editingPreset, setEditingPreset] = useState<Preset | null>(null);
  const [editingProfile, setEditingProfile] = useState<GameProfile | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [isImportingProfiles, setIsImportingProfiles] = useState(false);
  const [importJson, setImportJson] = useState("");
  const [importProfileJson, setImportProfileJson] = useState("");
  const [importError, setImportError] = useState<string | null>(null);
  const [importProfileError, setImportProfileError] = useState<string | null>(null);
  const [mergeStrategy, setMergeStrategy] = useState<"skip" | "overwrite" | "rename">("skip");
  const [isCreatingProfile, setIsCreatingProfile] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newProfileData, setNewProfileData] = useState<{
    app_id: number;
    name: string;
    cores: number[];
    dynamic_enabled: boolean;
  }>({
    app_id: 0,
    name: "",
    cores: [...state.cores],
    dynamic_enabled: false,
  });

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

  /**
   * Handle quick-create profile for current game.
   * Requirements: 5.1, 5.3, 5.4
   */
  const handleQuickCreate = async () => {
    setIsCreatingProfile(true);
    try {
      const result = await createProfileForCurrentGame();
      if (result.success) {
        alert(`Profile created for ${runningAppName}`);
      } else {
        alert(`Failed to create profile: ${result.error}`);
      }
    } catch (e) {
      alert(`Error creating profile: ${String(e)}`);
    } finally {
      setIsCreatingProfile(false);
    }
  };

  /**
   * Handle profile deletion.
   * Requirements: 3.4
   */
  const handleDeleteProfile = async (appId: number) => {
    if (confirm("Are you sure you want to delete this profile?")) {
      try {
        const result = await deleteProfile(appId);
        if (!result.success) {
          alert(`Failed to delete profile: ${result.error}`);
        }
      } catch (e) {
        alert(`Error deleting profile: ${String(e)}`);
      }
    }
  };

  /**
   * Handle profile export (all profiles).
   * Requirements: 9.1
   */
  const handleExportProfiles = async () => {
    try {
      const result = await exportProfiles();
      if (result.success && result.json) {
        console.log("Export profiles:", result.json);
        alert(`Profiles exported successfully!\n\nPath: ${result.path || "clipboard"}`);
      } else {
        alert(`Failed to export profiles: ${result.error}`);
      }
    } catch (e) {
      alert(`Error exporting profiles: ${String(e)}`);
    }
  };

  /**
   * Handle profile import.
   * Requirements: 9.2, 9.3, 9.4
   */
  const handleImportProfiles = async () => {
    setImportProfileError(null);
    try {
      const result = await importProfiles(importProfileJson, mergeStrategy);
      if (result.success) {
        setIsImportingProfiles(false);
        setImportProfileJson("");
        alert(`Successfully imported ${result.imported_count} profile(s)${result.conflicts.length > 0 ? `\nConflicts: ${result.conflicts.length}` : ""}`);
      } else {
        setImportProfileError(result.error || "Import failed");
      }
    } catch (e) {
      setImportProfileError("Invalid JSON format");
    }
  };

  /**
   * Handle preset deletion.
   */
  const handleDelete = async (appId: number) => {
    await api.deletePreset(appId);
  };

  /**
   * Handle preset export (single preset).
   */
  const handleExportSingle = async (preset: Preset) => {
    const json = JSON.stringify([preset], null, 2);
    console.log("Export preset:", json);
    alert(`Preset exported:\n${json}`);
  };

  /**
   * Handle export all presets.
   */
  const handleExportAll = async () => {
    const json = await api.exportPresets();
    console.log("Export all presets:", json);
    alert(`All presets exported:\n${json}`);
  };

  /**
   * Handle import presets.
   */
  const handleImport = async () => {
    setImportError(null);
    try {
      const result = await api.importPresets(importJson);
      if (result.success) {
        setIsImporting(false);
        setImportJson("");
        alert(`Successfully imported ${result.imported_count} preset(s)`);
      } else {
        setImportError(result.error || "Import failed");
      }
    } catch (e) {
      setImportError("Invalid JSON format");
    }
  };

  /**
   * Handle preset edit save.
   */
  const handleSaveEdit = async () => {
    if (editingPreset) {
      await api.updatePreset(editingPreset);
      setEditingPreset(null);
    }
  };

  /**
   * Handle profile edit save.
   * Requirements: 3.3
   */
  const handleSaveProfileEdit = async () => {
    if (editingProfile) {
      try {
        const result = await api.updateProfile(editingProfile.app_id, {
          name: editingProfile.name,
          cores: editingProfile.cores,
          dynamic_enabled: editingProfile.dynamic_enabled,
        });
        if (result.success) {
          setEditingProfile(null);
        } else {
          alert(`Failed to update profile: ${result.error}`);
        }
      } catch (e) {
        alert(`Error updating profile: ${String(e)}`);
      }
    }
  };

  /**
   * Handle create profile dialog.
   * Requirements: 3.1, 5.1
   */
  const handleCreateProfile = async () => {
    if (!newProfileData.name || newProfileData.app_id === 0) {
      alert("Please enter a game name and AppID");
      return;
    }

    try {
      const result = await api.createProfile({
        app_id: newProfileData.app_id,
        name: newProfileData.name,
        cores: newProfileData.cores,
        dynamic_enabled: newProfileData.dynamic_enabled,
        dynamic_config: newProfileData.dynamic_enabled ? state.dynamicSettings : null,
      });

      if (result.success) {
        setShowCreateDialog(false);
        setNewProfileData({
          app_id: 0,
          name: "",
          cores: [...state.cores],
          dynamic_enabled: false,
        });
        alert(`Profile created for ${newProfileData.name}`);
      } else {
        alert(`Failed to create profile: ${result.error}`);
      }
    } catch (e) {
      alert(`Error creating profile: ${String(e)}`);
    }
  };

  /**
   * Format core values for display.
   */
  const formatCoreValues = (values: number[]): string => {
    return values.map((v, i) => `C${i}:${v}`).join(" ");
  };

  // Check if a game is currently running
  const isGameRunning = runningAppId !== null && runningAppName !== null;

  return (
    <>
      {/* ==================== GAME PROFILES SECTION ==================== */}
      <PanelSectionRow>
        <div style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "12px", marginTop: "8px" }}>
          Game Profiles
        </div>
      </PanelSectionRow>

      {/* Quick-create button - Requirements: 5.1, 5.3, 5.4 */}
      {isGameRunning && (
        <PanelSectionRow>
          <ButtonItem
            layout="below"
            onClick={handleQuickCreate}
            disabled={isCreatingProfile}
            style={{
              backgroundColor: "#1a9fff",
              marginBottom: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              {isCreatingProfile ? (
                <>
                  <FaSpinner className="spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <FaRocket />
                  <span>Save as Profile for {runningAppName}</span>
                </>
              )}
            </div>
          </ButtonItem>
        </PanelSectionRow>
      )}

      {/* Profile management buttons */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            gap: "8px",
            marginBottom: "16px",
          }}
        >
          <ButtonItem layout="below" onClick={() => setShowCreateDialog(true)} style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              <FaEdit />
              <span>Create Profile</span>
            </div>
          </ButtonItem>

          <ButtonItem layout="below" onClick={handleExportProfiles} style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              <FaDownload />
              <span>Export All</span>
            </div>
          </ButtonItem>

          <ButtonItem layout="below" onClick={() => setIsImportingProfiles(true)} style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              <FaUpload />
              <span>Import</span>
            </div>
          </ButtonItem>
        </Focusable>
      </PanelSectionRow>

      {/* Create profile dialog - Requirements: 3.1, 5.1 */}
      {showCreateDialog && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Create New Profile
            </div>
            <TextField
              label="Game Name"
              value={newProfileData.name}
              onChange={(e: any) => setNewProfileData({ ...newProfileData, name: e.target.value })}
              style={{ marginBottom: "8px" }}
            />
            <TextField
              label="Steam AppID"
              value={String(newProfileData.app_id)}
              onChange={(e: any) => setNewProfileData({ ...newProfileData, app_id: parseInt(e.target.value) || 0 })}
              style={{ marginBottom: "8px" }}
            />
            <div style={{ fontSize: "12px", color: "#8b929a", marginBottom: "8px" }}>
              Cores: {formatCoreValues(newProfileData.cores)}
            </div>
            <ToggleField
              label="Enable Dynamic Mode"
              checked={newProfileData.dynamic_enabled}
              onChange={(checked: boolean) => setNewProfileData({ ...newProfileData, dynamic_enabled: checked })}
            />
            <Focusable style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <ButtonItem layout="below" onClick={handleCreateProfile}>
                <span>Create</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => setShowCreateDialog(false)}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Import profiles dialog - Requirements: 9.2, 9.3, 9.4 */}
      {isImportingProfiles && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Import Profiles
            </div>
            <TextField
              label="JSON Data"
              value={importProfileJson}
              onChange={(e: any) => setImportProfileJson(e.target.value)}
              style={{ marginBottom: "8px" }}
            />
            <DropdownItem
              label="Merge Strategy"
              menuLabel="Merge Strategy"
              rgOptions={[
                { data: "skip", label: "Skip conflicts (keep existing)" },
                { data: "overwrite", label: "Overwrite conflicts" },
                { data: "rename", label: "Rename conflicts" },
              ]}
              selectedOption={mergeStrategy}
              onChange={(option: any) => setMergeStrategy(option.data)}
            />
            {importProfileError && (
              <div style={{ color: "#f44336", fontSize: "12px", marginBottom: "8px", marginTop: "8px" }}>
                {importProfileError}
              </div>
            )}
            <Focusable style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <ButtonItem layout="below" onClick={handleImportProfiles}>
                <span>Import</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => { setIsImportingProfiles(false); setImportProfileJson(""); setImportProfileError(null); }}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Edit profile dialog - Requirements: 3.3 */}
      {editingProfile && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Edit Profile: {editingProfile.name}
            </div>
            <TextField
              label="Game Name"
              value={editingProfile.name}
              onChange={(e: any) => setEditingProfile({ ...editingProfile, name: e.target.value })}
              style={{ marginBottom: "8px" }}
            />
            <div style={{ fontSize: "12px", color: "#8b929a", marginBottom: "8px" }}>
              Cores: {formatCoreValues(editingProfile.cores)}
            </div>
            <ToggleField
              label="Enable Dynamic Mode"
              checked={editingProfile.dynamic_enabled}
              onChange={(checked: boolean) => setEditingProfile({ ...editingProfile, dynamic_enabled: checked })}
            />
            <Focusable style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <ButtonItem layout="below" onClick={handleSaveProfileEdit}>
                <span>Save</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => setEditingProfile(null)}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Profile list - Requirements: 3.2 */}
      {profiles.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "12px" }}>
            No game profiles yet. {isGameRunning ? "Click the button above to create one!" : "Launch a game and create a profile."}
          </div>
        </PanelSectionRow>
      ) : (
        profiles.map((profile) => {
          const isActive = activeProfile?.app_id === profile.app_id || runningAppId === profile.app_id;
          return (
            <PanelSectionRow key={profile.app_id}>
              <div
                style={{
                  padding: "12px",
                  backgroundColor: isActive ? "#1a3a5c" : "#23262e",
                  borderRadius: "8px",
                  marginBottom: "8px",
                  border: isActive ? "2px solid #1a9fff" : "none",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div style={{ fontWeight: "bold", fontSize: "14px" }}>{profile.name}</div>
                      {isActive && (
                        <div
                          style={{
                            fontSize: "10px",
                            padding: "2px 6px",
                            backgroundColor: "#1a9fff",
                            borderRadius: "4px",
                            fontWeight: "bold",
                          }}
                        >
                          ACTIVE
                        </div>
                      )}
                    </div>
                    <div style={{ fontSize: "11px", color: "#8b929a", marginTop: "2px" }}>
                      AppID: {profile.app_id}
                    </div>
                    <div style={{ fontSize: "12px", color: "#8b929a", marginTop: "4px" }}>
                      {formatCoreValues(profile.cores)}
                    </div>
                    {profile.dynamic_enabled && (
                      <div style={{ fontSize: "10px", color: "#4caf50", marginTop: "2px" }}>
                        ⚡ Dynamic Mode Enabled
                      </div>
                    )}
                  </div>
                  <Focusable style={{ display: "flex", gap: "8px" }}>
                    <button
                      onClick={() => setEditingProfile(profile)}
                      style={{
                        padding: "8px",
                        backgroundColor: "transparent",
                        border: "none",
                        color: "#1a9fff",
                        cursor: "pointer",
                      }}
                      title="Edit profile"
                    >
                      <FaEdit />
                    </button>
                    <button
                      onClick={() => handleDeleteProfile(profile.app_id)}
                      style={{
                        padding: "8px",
                        backgroundColor: "transparent",
                        border: "none",
                        color: "#f44336",
                        cursor: "pointer",
                      }}
                      title="Delete profile"
                    >
                      <FaTrash />
                    </button>
                  </Focusable>
                </div>
              </div>
            </PanelSectionRow>
          );
        })
      )}

      {/* Divider */}
      <PanelSectionRow>
        <div style={{ borderTop: "1px solid #3d4450", margin: "16px 0" }} />
      </PanelSectionRow>

      {/* ==================== LEGACY PRESETS SECTION ==================== */}
      <PanelSectionRow>
        <div style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "12px" }}>
          Legacy Presets
        </div>
      </PanelSectionRow>

      {/* Header with export all and import buttons */}
      <PanelSectionRow>
        <Focusable
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "16px",
          }}
        >
          <ButtonItem layout="below" onClick={handleExportAll}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaDownload />
              <span>Export All</span>
            </div>
          </ButtonItem>

          <ButtonItem layout="below" onClick={() => setIsImporting(true)}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaUpload />
              <span>Import</span>
            </div>
          </ButtonItem>
        </Focusable>
      </PanelSectionRow>

      {/* Import dialog */}
      {isImporting && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Import Presets
            </div>
            <TextField
              label="JSON Data"
              value={importJson}
              onChange={(e: any) => setImportJson(e.target.value)}
              style={{ marginBottom: "8px" }}
            />
            {importError && (
              <div style={{ color: "#f44336", fontSize: "12px", marginBottom: "8px" }}>
                {importError}
              </div>
            )}
            <Focusable style={{ display: "flex", gap: "8px" }}>
              <ButtonItem layout="below" onClick={handleImport}>
                <span>Import</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => { setIsImporting(false); setImportJson(""); setImportError(null); }}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Edit dialog */}
      {editingPreset && (
        <PanelSectionRow>
          <div
            style={{
              padding: "12px",
              backgroundColor: "#23262e",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: "bold", marginBottom: "8px" }}>
              Edit Preset: {editingPreset.label}
            </div>
            <TextField
              label="Label"
              value={editingPreset.label}
              onChange={(e: any) => setEditingPreset({ ...editingPreset, label: e.target.value })}
              style={{ marginBottom: "8px" }}
            />
            <ToggleField
              label="Use Timeout"
              checked={editingPreset.use_timeout}
              onChange={(checked: boolean) => setEditingPreset({ ...editingPreset, use_timeout: checked })}
            />
            {editingPreset.use_timeout && (
              <SliderField
                label="Timeout (seconds)"
                value={editingPreset.timeout}
                min={0}
                max={60}
                step={5}
                showValue={true}
                onChange={(value: number) => setEditingPreset({ ...editingPreset, timeout: value })}
              />
            )}
            <Focusable style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <ButtonItem layout="below" onClick={handleSaveEdit}>
                <span>Save</span>
              </ButtonItem>
              <ButtonItem layout="below" onClick={() => setEditingPreset(null)}>
                <span>Cancel</span>
              </ButtonItem>
            </Focusable>
          </div>
        </PanelSectionRow>
      )}

      {/* Preset list */}
      {state.presets.length === 0 ? (
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "12px" }}>
            No legacy presets saved.
          </div>
        </PanelSectionRow>
      ) : (
        state.presets.map((preset) => (
          <PanelSectionRow key={preset.app_id}>
            <div
              style={{
                padding: "12px",
                backgroundColor: "#23262e",
                borderRadius: "8px",
                marginBottom: "8px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: "bold", fontSize: "14px" }}>{preset.label}</div>
                  <div style={{ fontSize: "12px", color: "#8b929a" }}>
                    {formatCoreValues(preset.value)}
                  </div>
                  {preset.use_timeout && (
                    <div style={{ fontSize: "10px", color: "#ff9800" }}>
                      Timeout: {preset.timeout}s
                    </div>
                  )}
                  {preset.tested && (
                    <div style={{ fontSize: "10px", color: "#4caf50" }}>
                      ✓ Tested
                    </div>
                  )}
                </div>
                <Focusable style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => setEditingPreset(preset)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#1a9fff",
                      cursor: "pointer",
                    }}
                  >
                    <FaEdit />
                  </button>
                  <button
                    onClick={() => handleExportSingle(preset)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#8b929a",
                      cursor: "pointer",
                    }}
                  >
                    <FaDownload />
                  </button>
                  <button
                    onClick={() => handleDelete(preset.app_id)}
                    style={{
                      padding: "8px",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#f44336",
                      cursor: "pointer",
                    }}
                  >
                    <FaTrash />
                  </button>
                </Focusable>
              </div>
            </div>
          </PanelSectionRow>
        ))
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
