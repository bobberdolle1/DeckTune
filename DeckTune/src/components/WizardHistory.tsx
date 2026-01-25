/**
 * Wizard History Browser Component
 * 
 * CRITICAL FIX #5: UI for browsing, viewing, and managing wizard presets
 * 
 * Features:
 * - List all wizard presets with chip grades
 * - Detailed view with curve visualization
 * - Apply/Delete actions
 * - Apply on Startup and Game Only Mode toggles
 */

import { useState, useEffect, FC } from "react";
import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  Focusable,
  ToggleField,
} from "@decky/ui";
import { call } from "@decky/api";
import {
  FaTrophy,
  FaMedal,
  FaAward,
  FaCertificate,
  FaTrash,
  FaCheck,
  FaChevronRight,
  FaChevronLeft,
  FaSpinner,
} from "react-icons/fa";

interface WizardPreset {
  id: string;
  name: string;
  chip_grade: string;
  offsets: { cpu: number };
  curve_data: Array<{ offset: number; result: string; temp: number; timestamp: string }>;
  duration: number;
  iterations: number;
  timestamp: string;
  apply_on_startup: boolean;
  game_only_mode: boolean;
  wizard_generated: boolean;
}

// ==================== Chip Grade Icon ====================

const ChipGradeIcon: FC<{ grade: string; size?: number }> = ({ grade, size = 16 }) => {
  const getGradeConfig = () => {
    switch (grade) {
      case "Platinum":
        return { icon: FaTrophy, color: "#e5e4e2" };
      case "Gold":
        return { icon: FaMedal, color: "#ffd700" };
      case "Silver":
        return { icon: FaAward, color: "#c0c0c0" };
      default:
        return { icon: FaCertificate, color: "#cd7f32" };
    }
  };

  const config = getGradeConfig();
  const Icon = config.icon;

  return <Icon style={{ color: config.color, fontSize: size }} />;
};

// ==================== Mini Curve Chart ====================

const MiniCurveChart: FC<{ data: any[] }> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const width = 120;
  const height = 60;
  const padding = 10;

  const offsets = data.map((d) => d.offset);
  const temps = data.map((d) => d.temp);

  const xMin = Math.min(...offsets);
  const xMax = Math.max(...offsets);
  const yMin = 0;
  const yMax = Math.max(...temps, 100);

  const xScale = (x: number) =>
    padding + ((x - xMin) / (xMax - xMin)) * (width - 2 * padding);

  const yScale = (y: number) =>
    height - padding - ((y - yMin) / (yMax - yMin)) * (height - 2 * padding);

  return (
    <svg width={width} height={height} style={{ backgroundColor: "#0d0f12", borderRadius: "4px" }}>
      <polyline
        points={data.map((d) => `${xScale(d.offset)},${yScale(d.temp)}`).join(" ")}
        fill="none"
        stroke="#1a9fff"
        strokeWidth={1.5}
      />
      {data.map((point, i) => {
        const color =
          point.result === "pass" ? "#4caf50" :
          point.result === "fail" ? "#ff9800" :
          "#f44336";
        
        return (
          <circle
            key={i}
            cx={xScale(point.offset)}
            cy={yScale(point.temp)}
            r={2}
            fill={color}
          />
        );
      })}
    </svg>
  );
};

// ==================== Preset List Item ====================

const PresetListItem: FC<{
  preset: WizardPreset;
  onSelect: () => void;
  isSelected: boolean;
}> = ({ preset, onSelect, isSelected }) => {
  const cpuOffset = preset.offsets?.cpu || 0;
  const date = new Date(preset.timestamp).toLocaleDateString();

  return (
    <div
      onClick={onSelect}
      style={{
        padding: "10px",
        backgroundColor: isSelected ? "#1a9fff20" : "#1a1d24",
        borderRadius: "4px",
        border: isSelected ? "1px solid #1a9fff" : "1px solid #2a2d34",
        cursor: "pointer",
        marginBottom: "8px",
        transition: "all 0.2s",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <ChipGradeIcon grade={preset.chip_grade} size={20} />
          <div>
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#fff" }}>
              {preset.chip_grade} • {cpuOffset}mV
            </div>
            <div style={{ fontSize: "10px", color: "#8b929a" }}>
              {date} • {preset.iterations} iterations
            </div>
          </div>
        </div>
        <FaChevronRight style={{ color: "#8b929a", fontSize: "12px" }} />
      </div>
      
      {preset.apply_on_startup && (
        <div style={{ fontSize: "9px", color: "#4caf50", marginTop: "4px" }}>
          ● Apply on Startup
        </div>
      )}
      {preset.game_only_mode && (
        <div style={{ fontSize: "9px", color: "#ff9800", marginTop: "4px" }}>
          ● Game Only Mode
        </div>
      )}
    </div>
  );
};

// ==================== Preset Detail View ====================

const PresetDetailView: FC<{
  preset: WizardPreset;
  onBack: () => void;
  onApply: () => void;
  onDelete: () => void;
  onUpdateOptions: (applyOnStartup: boolean, gameOnlyMode: boolean) => void;
}> = ({ preset, onBack, onApply, onDelete, onUpdateOptions }) => {
  const [applyOnStartup, setApplyOnStartup] = useState(preset.apply_on_startup);
  const [gameOnlyMode, setGameOnlyMode] = useState(preset.game_only_mode);
  const [isApplying, setIsApplying] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const cpuOffset = preset.offsets?.cpu || 0;

  const handleApply = async () => {
    setIsApplying(true);
    try {
      await onApply();
    } finally {
      setIsApplying(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete();
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleStartup = async (value: boolean) => {
    setApplyOnStartup(value);
    await onUpdateOptions(value, gameOnlyMode);
  };

  const handleToggleGameOnly = async (value: boolean) => {
    setGameOnlyMode(value);
    await onUpdateOptions(applyOnStartup, value);
  };

  return (
    <Focusable style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onBack}>
          <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <FaChevronLeft size={10} />
            <span>Back to List</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            padding: "12px",
            backgroundColor: "#1a1d24",
            borderRadius: "8px",
          }}
        >
          <ChipGradeIcon grade={preset.chip_grade} size={32} />
          <div>
            <div style={{ fontSize: "16px", fontWeight: "bold", color: "#fff" }}>
              {preset.chip_grade} Grade
            </div>
            <div style={{ fontSize: "20px", fontWeight: "bold", color: "#1a9fff" }}>
              {cpuOffset}mV
            </div>
          </div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <MiniCurveChart data={preset.curve_data || []} />
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontSize: "10px",
            color: "#8b929a",
            padding: "8px",
            backgroundColor: "#1a1d24",
            borderRadius: "4px",
          }}
        >
          <div>Date: {new Date(preset.timestamp).toLocaleString()}</div>
          <div>Duration: {Math.round(preset.duration)}s</div>
          <div>Iterations: {preset.iterations}</div>
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Apply on Startup"
          description="Automatically apply when DeckTune starts"
          checked={applyOnStartup}
          onChange={handleToggleStartup}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Game Only Mode"
          description="Only apply when a game is running"
          checked={gameOnlyMode}
          onChange={handleToggleGameOnly}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleApply} disabled={isApplying}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "5px",
              color: isApplying ? "#8b929a" : "#4caf50",
            }}
          >
            {isApplying ? <FaSpinner className="spin" size={12} /> : <FaCheck size={12} />}
            <span>{isApplying ? "Applying..." : "Apply Preset"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleDelete} disabled={isDeleting}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "5px",
              color: isDeleting ? "#8b929a" : "#f44336",
            }}
          >
            {isDeleting ? <FaSpinner className="spin" size={12} /> : <FaTrash size={12} />}
            <span>{isDeleting ? "Deleting..." : "Delete Preset"}</span>
          </div>
        </ButtonItem>
      </PanelSectionRow>

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
    </Focusable>
  );
};

// ==================== Main Component ====================

export const WizardHistory: FC = () => {
  const [presets, setPresets] = useState<WizardPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<WizardPreset | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadPresets = async () => {
    setIsLoading(true);
    try {
      const result = await call("get_wizard_presets") as WizardPreset[];
      setPresets(result || []);
    } catch (err) {
      console.error("Failed to load wizard presets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPresets();
  }, []);

  const handleApply = async () => {
    if (!selectedPreset) return;
    try {
      await call("apply_wizard_result", selectedPreset.id, true, selectedPreset.apply_on_startup, selectedPreset.game_only_mode);
      console.log("Applied wizard preset:", selectedPreset.id);
    } catch (err) {
      console.error("Failed to apply preset:", err);
    }
  };

  const handleDelete = async () => {
    if (!selectedPreset) return;
    try {
      await call("delete_wizard_preset", selectedPreset.id);
      console.log("Deleted wizard preset:", selectedPreset.id);
      setSelectedPreset(null);
      await loadPresets();
    } catch (err) {
      console.error("Failed to delete preset:", err);
    }
  };

  const handleUpdateOptions = async (applyOnStartup: boolean, gameOnlyMode: boolean) => {
    if (!selectedPreset) return;
    try {
      await call("update_wizard_preset_options", selectedPreset.id, applyOnStartup, gameOnlyMode);
      console.log("Updated wizard preset options:", selectedPreset.id);
      await loadPresets();
    } catch (err) {
      console.error("Failed to update preset options:", err);
    }
  };

  if (isLoading) {
    return (
      <PanelSection title="Wizard History">
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "20px" }}>
            <FaSpinner className="spin" style={{ fontSize: "24px", color: "#1a9fff" }} />
            <div style={{ fontSize: "12px", color: "#8b929a", marginTop: "10px" }}>
              Loading presets...
            </div>
          </div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  if (selectedPreset) {
    return (
      <PanelSection title="Wizard Preset Details">
        <PresetDetailView
          preset={selectedPreset}
          onBack={() => setSelectedPreset(null)}
          onApply={handleApply}
          onDelete={handleDelete}
          onUpdateOptions={handleUpdateOptions}
        />
      </PanelSection>
    );
  }

  return (
    <PanelSection title="Wizard History">
      {presets.length === 0 ? (
        <PanelSectionRow>
          <div style={{ textAlign: "center", padding: "20px", color: "#8b929a", fontSize: "12px" }}>
            No wizard presets found. Run the wizard to create your first preset.
          </div>
        </PanelSectionRow>
      ) : (
        <Focusable style={{ display: "flex", flexDirection: "column", gap: "0" }}>
          {presets.map((preset) => (
            <PresetListItem
              key={preset.id}
              preset={preset}
              onSelect={() => setSelectedPreset(preset)}
              isSelected={false}
            />
          ))}
        </Focusable>
      )}
    </PanelSection>
  );
};
