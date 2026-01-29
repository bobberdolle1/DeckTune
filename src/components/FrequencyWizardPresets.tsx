/**
 * FrequencyWizardPresets - Manage frequency wizard presets.
 * 
 * Displays saved frequency wizard results as presets with:
 * - Per-core frequency curves visualization
 * - Chip quality grading
 * - Apply on Startup toggle
 * - Apply/Delete actions
 */

import { useState, useEffect, FC } from "react";
import {
  PanelSection,
  PanelSectionRow,
  ToggleField,
  Focusable,
  showModal,
  ConfirmModal,
} from "@decky/ui";
import {
  FaPlay,
  FaTrash,
  FaTrophy,
  FaMedal,
  FaAward,
  FaCertificate,
  FaStar,
  FaChartLine,
} from "react-icons/fa";
import { useDeckTune } from "../context";

interface FrequencyWizardPreset {
  id: string;
  name: string;
  type: string;
  created_at: string;
  chip_grade: string;
  frequency_curves: Record<string, any>;
  per_core_stats: Array<{
    core_id: number;
    total_points: number;
    stable_points: number;
    avg_voltage: number;
    min_voltage: number;
    max_voltage: number;
  }>;
  wizard_config: any;
  apply_on_startup: boolean;
  game_only_mode: boolean;
  enabled: boolean;
}

const GRADE_ICONS: Record<string, any> = {
  Platinum: FaTrophy,
  Gold: FaMedal,
  Silver: FaAward,
  Bronze: FaCertificate,
  Standard: FaStar,
};

const GRADE_COLORS: Record<string, string> = {
  Platinum: "#E5E4E2",
  Gold: "#FFD700",
  Silver: "#C0C0C0",
  Bronze: "#CD7F32",
  Standard: "#808080",
};

export const FrequencyWizardPresets: FC = () => {
  const { api } = useDeckTune();
  const [presets, setPresets] = useState<FrequencyWizardPreset[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedPreset, setExpandedPreset] = useState<string | null>(null);

  useEffect(() => {
    loadPresets();
  }, []);

  const loadPresets = async () => {
    try {
      setLoading(true);
      const result = await api.getFrequencyWizardPresets();
      if (result.success) {
        setPresets(result.presets || []);
      }
    } catch (err) {
      console.error("Failed to load frequency wizard presets:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (presetId: string) => {
    try {
      const result = await api.applyFrequencyWizardPreset(presetId);
      if (result.success) {
        await loadPresets();
      }
    } catch (err) {
      console.error("Failed to apply preset:", err);
    }
  };

  const handleDelete = async (presetId: string, presetName: string) => {
    showModal(
      <ConfirmModal
        strTitle="Delete Preset"
        strDescription={`Delete frequency wizard preset "${presetName}"?`}
        strOKButtonText="Delete"
        strCancelButtonText="Cancel"
        onOK={async () => {
          try {
            const result = await api.deleteFrequencyWizardPreset(presetId);
            if (result.success) {
              await loadPresets();
            }
          } catch (err) {
            console.error("Failed to delete preset:", err);
          }
        }}
      />
    );
  };

  const handleToggleStartup = async (presetId: string, value: boolean) => {
    try {
      await api.updateFrequencyWizardPreset(presetId, { apply_on_startup: value });
      await loadPresets();
    } catch (err) {
      console.error("Failed to update preset:", err);
    }
  };

  const handleToggleGameOnly = async (presetId: string, value: boolean) => {
    try {
      await api.updateFrequencyWizardPreset(presetId, { game_only_mode: value });
      await loadPresets();
    } catch (err) {
      console.error("Failed to update preset:", err);
    }
  };

  if (loading) {
    return (
      <PanelSection title="Frequency Wizard Presets">
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" }}>
            Loading...
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  if (presets.length === 0) {
    return (
      <PanelSection title="Frequency Wizard Presets">
        <PanelSectionRow>
          <div style={{ color: "#8b929a", textAlign: "center", padding: "16px", fontSize: "11px" }}>
            No presets yet. Run the Frequency Wizard to create one.
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <PanelSection title="Frequency Wizard Presets">
      {presets.map((preset) => {
        const GradeIcon = GRADE_ICONS[preset.chip_grade] || FaStar;
        const gradeColor = GRADE_COLORS[preset.chip_grade] || "#808080";
        const isExpanded = expandedPreset === preset.id;

        return (
          <div key={preset.id} style={{ marginBottom: "12px" }}>
            {/* Preset header */}
            <PanelSectionRow>
              <div style={{ 
                padding: "8px", 
                backgroundColor: preset.enabled ? "#1a3a5c" : "#23262e", 
                borderRadius: "6px 6px 0 0",
                border: preset.enabled ? "2px solid #1a9fff" : "none",
                borderBottom: "1px solid #3d4450"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <GradeIcon style={{ color: gradeColor }} size={14} />
                  <div style={{ fontWeight: "bold", color: gradeColor, fontSize: "11px" }}>
                    {preset.chip_grade}
                  </div>
                  {preset.enabled && (
                    <div style={{ fontSize: "8px", padding: "1px 4px", backgroundColor: "#4caf50", borderRadius: "2px", fontWeight: "bold" }}>
                      ACTIVE
                    </div>
                  )}
                  <div style={{ opacity: 0.7, fontSize: "9px", marginLeft: "auto" }}>
                    {new Date(preset.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{ fontSize: "10px", fontWeight: "bold" }}>
                  {preset.name}
                </div>
              </div>
            </PanelSectionRow>

            {/* Toggles */}
            <PanelSectionRow>
              <ToggleField
                label="Apply on Startup"
                description="Apply this preset when plugin starts"
                checked={preset.apply_on_startup || false}
                onChange={(value) => handleToggleStartup(preset.id, value)}
              />
            </PanelSectionRow>

            <PanelSectionRow>
              <ToggleField
                label="Game Only Mode"
                description="Apply only when a game is running"
                checked={preset.game_only_mode || false}
                onChange={(value) => handleToggleGameOnly(preset.id, value)}
              />
            </PanelSectionRow>

            {/* Action buttons */}
            <PanelSectionRow>
              <div
                style={{
                  display: "flex",
                  gap: "4px",
                  backgroundColor: "#1a1d24",
                  borderRadius: "0 0 6px 6px",
                  padding: "6px",
                }}
              >
                <Focusable
                  style={{ flex: 1 }}
                  onActivate={() => handleApply(preset.id)}
                  onClick={() => handleApply(preset.id)}
                >
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "center", 
                    gap: "4px", 
                    padding: "8px",
                    fontSize: "9px",
                    fontWeight: "600",
                    borderRadius: "4px",
                    backgroundColor: preset.enabled ? "#2a2d35" : "#1a9fff",
                    color: preset.enabled ? "#8b929a" : "#fff",
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}>
                    <FaPlay size={8} />
                    <div>{preset.enabled ? "Active" : "Apply"}</div>
                  </div>
                </Focusable>
                
                <Focusable
                  style={{ flex: 1 }}
                  onActivate={() => setExpandedPreset(isExpanded ? null : preset.id)}
                  onClick={() => setExpandedPreset(isExpanded ? null : preset.id)}
                >
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "center", 
                    gap: "4px", 
                    padding: "8px",
                    fontSize: "9px",
                    fontWeight: "600",
                    borderRadius: "4px",
                    backgroundColor: "#2a2d35",
                    color: "#fff",
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}>
                    <FaChartLine size={8} />
                    <div>{isExpanded ? "Hide" : "Show"}</div>
                  </div>
                </Focusable>

                <Focusable
                  style={{ flex: 1 }}
                  onActivate={() => handleDelete(preset.id, preset.name)}
                  onClick={() => handleDelete(preset.id, preset.name)}
                >
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "center", 
                    gap: "4px", 
                    padding: "8px",
                    fontSize: "9px",
                    fontWeight: "600",
                    borderRadius: "4px",
                    backgroundColor: "#2a2d35",
                    color: "#f44336",
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}>
                    <FaTrash size={8} />
                    <div>Delete</div>
                  </div>
                </Focusable>
              </div>
            </PanelSectionRow>

            {/* Expanded details */}
            {isExpanded && preset.per_core_stats && (
              <PanelSectionRow>
                <div style={{ fontSize: "9px", opacity: 0.8, padding: "8px", backgroundColor: "#1a1d24", borderRadius: "4px" }}>
                  {preset.per_core_stats.map((stat) => (
                    <div key={stat.core_id} style={{ marginBottom: "4px" }}>
                      Core {stat.core_id}: avg {stat.avg_voltage.toFixed(1)}mV, 
                      min {stat.min_voltage}mV ({stat.stable_points} pts)
                    </div>
                  ))}
                </div>
              </PanelSectionRow>
            )}
          </div>
        );
      })}
    </PanelSection>
  );
};
