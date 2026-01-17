/**
 * Dynamic Mode Settings Tab - detailed configuration for gymdeck3.
 * 
 * Provides UI for configuring:
 * - Strategy selection (conservative, balanced, aggressive)
 * - Sample interval
 * - Per-core min/max/threshold settings
 * - Hysteresis
 * - Simple mode toggle
 */

import { useState, useEffect, FC } from "react";
import {
  PanelSectionRow,
  SliderField,
  DropdownItem,
  ToggleField,
  ButtonItem,
  Focusable,
} from "@decky/ui";
import { FaCheck, FaSave, FaUndo, FaInfoCircle } from "react-icons/fa";
import { useDeckTune } from "../context";

export const DynamicSettingsTab: FC = () => {
  const { state, api } = useDeckTune();
  
  // Local state for editing
  const [strategy, setStrategy] = useState<string>("balanced");
  const [sampleInterval, setSampleInterval] = useState<number>(100);
  const [hysteresis, setHysteresis] = useState<number>(5);
  const [simpleMode, setSimpleMode] = useState<boolean>(false);
  const [simpleValue, setSimpleValue] = useState<number>(-25);
  
  // Per-core settings (only visible in per-core mode)
  const [coreSettings, setCoreSettings] = useState<Array<{min: number, max: number, threshold: number}>>([
    { min: -20, max: -30, threshold: 50 },
    { min: -20, max: -30, threshold: 50 },
    { min: -20, max: -30, threshold: 50 },
    { min: -20, max: -30, threshold: 50 },
  ]);
  
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Get expert mode from settings
  const expertMode = state.settings.expertMode || false;
  const minLimit = expertMode ? -100 : -35;

  // Load current config from backend on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await api.getDynamicConfig();
        if (config) {
          setStrategy(config.strategy || "balanced");
          setSampleInterval(config.sample_interval_ms || 100);
          setHysteresis(config.hysteresis_percent || 5);
          setSimpleMode(config.simple_mode || false);
          setSimpleValue(config.simple_value || -25);
          
          if (config.cores && config.cores.length === 4) {
            setCoreSettings(config.cores.map((c: any) => ({
              min: c.min_mv || -20,
              max: c.max_mv || -30,
              threshold: c.threshold || 50,
            })));
          }
        }
      } catch (e) {
        console.error("Failed to load dynamic config:", e);
      }
    };
    
    loadConfig();
  }, [api]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const config = {
        strategy,
        sample_interval_ms: sampleInterval,
        hysteresis_percent: hysteresis,
        simple_mode: simpleMode,
        simple_value: simpleValue,
        cores: coreSettings.map((c, i) => ({
          min_mv: c.min,
          max_mv: c.max,
          threshold: c.threshold,
        })),
        expert_mode: expertMode,
      };
      
      await api.saveDynamicConfig(config);
      setHasChanges(false);
    } catch (e) {
      console.error("Failed to save dynamic config:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setStrategy("balanced");
    setSampleInterval(100);
    setHysteresis(5);
    setSimpleMode(false);
    setSimpleValue(-25);
    setCoreSettings([
      { min: -20, max: -30, threshold: 50 },
      { min: -20, max: -30, threshold: 50 },
      { min: -20, max: -30, threshold: 50 },
      { min: -20, max: -30, threshold: 50 },
    ]);
    setHasChanges(true);
  };

  const handleCoreChange = (coreIndex: number, field: 'min' | 'max' | 'threshold', value: number) => {
    const newSettings = [...coreSettings];
    newSettings[coreIndex][field] = value;
    setCoreSettings(newSettings);
    setHasChanges(true);
  };

  return (
    <>
      {/* Info banner */}
      <PanelSectionRow>
        <div style={{
          padding: "8px",
          backgroundColor: "#1a3a5c",
          borderRadius: "6px",
          marginBottom: "12px",
          fontSize: "10px",
          display: "flex",
          gap: "8px",
          alignItems: "flex-start"
        }}>
          <FaInfoCircle style={{ color: "#1a9fff", fontSize: "12px", marginTop: "2px", flexShrink: 0 }} />
          <div style={{ color: "#8b929a", lineHeight: "1.4" }}>
            Настройки применяются при следующем запуске динамического режима. 
            Если режим уже запущен, остановите и запустите заново.
          </div>
        </div>
      </PanelSectionRow>

      {/* Strategy Selection */}
      <PanelSectionRow>
        <div style={{ fontSize: "12px", fontWeight: "bold", marginBottom: "6px" }}>
          Стратегия / Strategy
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <DropdownItem
          label="Режим адаптации"
          menuLabel="Выбрать стратегию"
          rgOptions={[
            { data: "conservative", label: "Conservative (Осторожный)" },
            { data: "balanced", label: "Balanced (Сбалансированный)" },
            { data: "aggressive", label: "Aggressive (Агрессивный)" },
          ]}
          selectedOption={
            strategy === "conservative" ? 0 :
            strategy === "balanced" ? 1 : 2
          }
          onChange={(option: any) => {
            setStrategy(option.data);
            setHasChanges(true);
          }}
          bottomSeparator="none"
        />
      </PanelSectionRow>

      {/* Simple Mode Toggle */}
      <PanelSectionRow>
        <div style={{ fontSize: "12px", fontWeight: "bold", marginTop: "12px", marginBottom: "6px" }}>
          Режим управления / Control Mode
        </div>
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField
          label="Простой режим / Simple Mode"
          description="Одно значение для всех ядер"
          checked={simpleMode}
          onChange={(value) => {
            setSimpleMode(value);
            setHasChanges(true);
          }}
          bottomSeparator="none"
        />
      </PanelSectionRow>

      {/* Simple Mode Value */}
      {simpleMode && (
        <PanelSectionRow>
          <SliderField
            label="Значение / Value"
            value={simpleValue}
            min={minLimit}
            max={0}
            step={1}
            showValue={true}
            onChange={(value: number) => {
              setSimpleValue(value);
              setHasChanges(true);
            }}
            valueSuffix=" mV"
            bottomSeparator="none"
          />
        </PanelSectionRow>
      )}

      {/* Per-Core Settings */}
      {!simpleMode && (
        <>
          <PanelSectionRow>
            <div style={{ fontSize: "12px", fontWeight: "bold", marginTop: "12px", marginBottom: "6px" }}>
              Настройки по ядрам / Per-Core Settings
            </div>
          </PanelSectionRow>
          
          {coreSettings.map((core, index) => (
            <div key={index}>
              <PanelSectionRow>
                <div style={{ fontSize: "11px", color: "#1a9fff", marginTop: "8px", marginBottom: "4px" }}>
                  Ядро / Core {index}
                </div>
              </PanelSectionRow>
              
              <PanelSectionRow>
                <SliderField
                  label="Min (легкая нагрузка)"
                  value={core.min}
                  min={minLimit}
                  max={0}
                  step={1}
                  showValue={true}
                  onChange={(value: number) => handleCoreChange(index, 'min', value)}
                  valueSuffix=" mV"
                  bottomSeparator="none"
                />
              </PanelSectionRow>
              
              <PanelSectionRow>
                <SliderField
                  label="Max (высокая нагрузка)"
                  value={core.max}
                  min={minLimit}
                  max={0}
                  step={1}
                  showValue={true}
                  onChange={(value: number) => handleCoreChange(index, 'max', value)}
                  valueSuffix=" mV"
                  bottomSeparator="none"
                />
              </PanelSectionRow>
              
              <PanelSectionRow>
                <SliderField
                  label="Порог / Threshold"
                  value={core.threshold}
                  min={0}
                  max={100}
                  step={5}
                  showValue={true}
                  onChange={(value: number) => handleCoreChange(index, 'threshold', value)}
                  valueSuffix=" %"
                  bottomSeparator="none"
                />
              </PanelSectionRow>
            </div>
          ))}
        </>
      )}

      {/* Advanced Settings */}
      <PanelSectionRow>
        <div style={{ fontSize: "12px", fontWeight: "bold", marginTop: "12px", marginBottom: "6px" }}>
          Дополнительно / Advanced
        </div>
      </PanelSectionRow>
      
      <PanelSectionRow>
        <SliderField
          label="Интервал опроса / Sample Interval"
          value={sampleInterval}
          min={50}
          max={500}
          step={10}
          showValue={true}
          onChange={(value: number) => {
            setSampleInterval(value);
            setHasChanges(true);
          }}
          valueSuffix=" ms"
          bottomSeparator="none"
        />
      </PanelSectionRow>
      
      <PanelSectionRow>
        <SliderField
          label="Гистерезис / Hysteresis"
          value={hysteresis}
          min={1}
          max={20}
          step={1}
          showValue={true}
          onChange={(value: number) => {
            setHysteresis(value);
            setHasChanges(true);
          }}
          valueSuffix=" %"
          bottomSeparator="none"
        />
      </PanelSectionRow>

      {/* Action Buttons */}
      <PanelSectionRow>
        <Focusable style={{ display: "flex", gap: "6px", marginTop: "16px" }} flow-children="horizontal">
          <Focusable
            style={{ flex: 1 }}
            focusClassName="gpfocus"
            onActivate={handleSave}
            onClick={handleSave}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              padding: "10px",
              backgroundColor: hasChanges ? "#4caf50" : "#3d4450",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "11px",
              fontWeight: "bold",
              opacity: isSaving ? 0.5 : 1
            }}>
              {isSaving ? <FaSave className="spin" size={11} /> : <FaCheck size={11} />}
              <span>Сохранить / Save</span>
            </div>
          </Focusable>

          <Focusable
            style={{ flex: 1 }}
            focusClassName="gpfocus"
            onActivate={handleReset}
            onClick={handleReset}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              padding: "10px",
              backgroundColor: "#5c4813",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "11px",
              fontWeight: "bold"
            }}>
              <FaUndo size={11} />
              <span>Сброс / Reset</span>
            </div>
          </Focusable>
        </Focusable>
      </PanelSectionRow>

      <style>{`
        .gpfocus {
          box-shadow: 0 0 8px rgba(26, 159, 255, 0.8) !important;
          transform: scale(1.02);
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};
