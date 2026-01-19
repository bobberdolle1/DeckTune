# Wizard Mode Refactoring - Implementation Guide

## Overview

This document provides a comprehensive implementation plan for refactoring the DeckTune Wizard Mode into a robust, transparent, "one-click" solution for finding optimal undervolt values.

## Architecture

### Backend Components

#### 1. WizardSession Class (`backend/tuning/wizard_session.py`)

**Status**: ✅ Implemented

The core orchestrator that manages the complete wizard workflow:

**Key Features**:
- State management (IDLE, RUNNING, PAUSED, CRASHED, FINISHED, CANCELLED)
- Step-down iterative testing algorithm
- Crash recovery with dirty exit detection
- Real-time progress tracking (ETA, OTA, heartbeat)
- Curve data collection for visualization
- Chip quality grading (Bronze/Silver/Gold/Platinum)
- Automatic preset generation

**Configuration Options**:
```python
@dataclass
class WizardConfig:
    target_domains: List[str]  # ["cpu", "gpu", "soc"]
    aggressiveness: AggressivenessLevel  # SAFE, BALANCED, AGGRESSIVE
    test_duration: TestDuration  # SHORT (30s), LONG (120s)
    safety_limits: Dict[str, int]  # Platform-specific hard limits
```

**Aggressiveness Levels**:
- **SAFE**: 2mV steps, +10mV safety margin
- **BALANCED**: 5mV steps, +5mV safety margin  
- **AGGRESSIVE**: 10mV steps, +2mV safety margin

**Algorithm**:
1. Start at -10mV (safe starting point)
2. Test current offset with stress test
3. If PASS → Update last_stable, step down (more negative)
4. If FAIL → Increment failure counter
5. Stop conditions:
   - Reached platform safety limit
   - 3 consecutive failures
   - User cancellation

**Crash Recovery**:
- Sets crash flag before each risky operation
- Persists state to disk after each iteration
- On boot, checks for dirty exit flag
- Restores last known stable values
- Shows recovery UI with crash details

**Chip Grading Scale**:
- **Platinum**: ≥ -51mV (Top 1-5%)
- **Gold**: -36 to -50mV (Top 20%)
- **Silver**: -21 to -35mV (Top 40%)
- **Bronze**: -10 to -20mV (Bottom 60%)

#### 2. Event Emitter Updates (`backend/api/events.py`)

**Status**: ✅ Implemented

Added three new event types:

```python
async def emit_wizard_progress(progress_data: Dict)
async def emit_wizard_complete(result_data: Dict)
async def emit_wizard_error(error_message: str)
```

**Progress Data Structure**:
```python
{
    "state": "running",
    "current_stage": "Testing -25mV",
    "current_offset": -25,
    "progress_percent": 45.2,
    "eta_seconds": 180,
    "ota_seconds": 120,
    "heartbeat": 1705678900.123,
    "live_metrics": {
        "iterations": 5,
        "last_stable": -20
    }
}
```

#### 3. RPC Integration (`backend/api/rpc.py`)

**Status**: 🔨 TODO

Add the following RPC methods:

```python
class DeckTuneRPC:
    def __init__(self, ...):
        self.wizard_session = None  # Will be set via setter
    
    def set_wizard_session(self, session: WizardSession) -> None:
        """Set the wizard session instance."""
        self.wizard_session = session
    
    async def start_wizard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start wizard session.
        
        Args:
            config: {
                "target_domains": ["cpu"],
                "aggressiveness": "balanced",
                "test_duration": "short",
                "safety_limits": {"cpu": -100}
            }
        
        Returns:
            {"success": True, "session_id": "uuid"}
        """
        if not self.wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        try:
            wizard_config = WizardConfig(
                target_domains=config.get("target_domains", ["cpu"]),
                aggressiveness=AggressivenessLevel(config.get("aggressiveness", "balanced")),
                test_duration=TestDuration(config.get("test_duration", "short")),
                safety_limits=config.get("safety_limits", {})
            )
            
            # Run in background task
            self._wizard_task = asyncio.create_task(
                self.wizard_session.start(wizard_config)
            )
            
            return {
                "success": True,
                "session_id": self.wizard_session._session_id
            }
        except Exception as e:
            logger.error(f"Failed to start wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def cancel_wizard(self) -> Dict[str, Any]:
        """Cancel running wizard session."""
        if not self.wizard_session or not self.wizard_session.is_running():
            return {"success": False, "error": "No wizard running"}
        
        self.wizard_session.cancel()
        return {"success": True}
    
    async def get_wizard_status(self) -> Dict[str, Any]:
        """Get current wizard status."""
        if not self.wizard_session:
            return {"running": False, "state": "idle"}
        
        return {
            "running": self.wizard_session.is_running(),
            "state": self.wizard_session.get_state().value
        }
    
    async def check_wizard_dirty_exit(self) -> Dict[str, Any]:
        """Check for dirty exit from previous session."""
        if not self.wizard_session:
            return {"dirty_exit": False}
        
        crash_info = self.wizard_session.check_dirty_exit()
        if crash_info:
            return {
                "dirty_exit": True,
                "crash_info": crash_info
            }
        return {"dirty_exit": False}
    
    async def get_wizard_results_history(self) -> List[Dict[str, Any]]:
        """Get history of wizard results."""
        if not self.wizard_session:
            return []
        
        results = self.wizard_session.get_results_history()
        return [asdict(r) for r in results]
    
    async def apply_wizard_result(self, result_id: str, save_as_preset: bool = True) -> Dict[str, Any]:
        """Apply a wizard result.
        
        Args:
            result_id: UUID of the wizard result
            save_as_preset: Whether to save as a preset
        
        Returns:
            {"success": True, "preset_id": "..."}
        """
        if not self.wizard_session:
            return {"success": False, "error": "Wizard not initialized"}
        
        # Find result
        results = self.wizard_session.get_results_history()
        result = next((r for r in results if r.id == result_id), None)
        
        if not result:
            return {"success": False, "error": "Result not found"}
        
        # Apply CPU offset (convert to 4-core array)
        cpu_offset = result.offsets.get("cpu", 0)
        values = [cpu_offset, cpu_offset, cpu_offset, cpu_offset]
        
        success, error = await self.ryzenadj.apply_values_async(values)
        if not success:
            return {"success": False, "error": error}
        
        # Save as preset if requested
        if save_as_preset:
            preset = {
                "app_id": None,  # Global preset
                "label": result.name,
                "value": values,
                "timeout": 0,
                "use_timeout": False,
                "created_at": result.timestamp,
                "tested": True,
                "wizard_result_id": result.id,
                "chip_grade": result.chip_grade
            }
            
            presets = self.settings.getSetting("presets", [])
            presets.append(preset)
            self.settings.setSetting("presets", presets)
            
            return {"success": True, "preset_id": result.id}
        
        return {"success": True}
```

#### 4. Main Plugin Integration (`main.py`)

**Status**: 🔨 TODO

Add wizard session initialization:

```python
class Plugin:
    def __init__(self):
        # ... existing code ...
        self.wizard_session = None
    
    async def init(self):
        # ... existing initialization ...
        
        # Initialize WizardSession
        from backend.tuning.wizard_session import WizardSession
        
        self.wizard_session = WizardSession(
            ryzenadj=self.ryzenadj,
            runner=self.test_runner,
            safety=self.safety,
            event_emitter=self.event_emitter,
            settings_dir=SETTINGS_DIR
        )
        
        # Set in RPC
        self.rpc.set_wizard_session(self.wizard_session)
        
        # Check for dirty exit on startup
        crash_info = self.wizard_session.check_dirty_exit()
        if crash_info:
            decky.logger.warning(f"Wizard dirty exit detected: {crash_info}")
            # Emit event to frontend
            await self.event_emitter.emit_wizard_error(
                f"Previous wizard session crashed at {crash_info['current_offset']}mV"
            )
        
        decky.logger.info("Wizard session initialized")
    
    # Add RPC method proxies
    async def start_wizard(self, config):
        return await self.rpc.start_wizard(config)
    
    async def cancel_wizard(self):
        return await self.rpc.cancel_wizard()
    
    async def get_wizard_status(self):
        return await self.rpc.get_wizard_status()
    
    async def check_wizard_dirty_exit(self):
        return await self.rpc.check_wizard_dirty_exit()
    
    async def get_wizard_results_history(self):
        return await self.rpc.get_wizard_results_history()
    
    async def apply_wizard_result(self, result_id, save_as_preset=True):
        return await self.rpc.apply_wizard_result(result_id, save_as_preset)
```

### Frontend Components

#### 1. Wizard Context (`src/context/WizardContext.tsx`)

**Status**: 🔨 TODO

Create a new context for wizard state management:

```typescript
import { createContext, useContext, useState, useEffect, FC, ReactNode } from "react";
import { serverAPI } from "@decky/api";

interface WizardConfig {
  targetDomains: string[];
  aggressiveness: "safe" | "balanced" | "aggressive";
  testDuration: "short" | "long";
  safetyLimits: Record<string, number>;
}

interface WizardProgress {
  state: string;
  currentStage: string;
  currentOffset: number;
  progressPercent: number;
  etaSeconds: number;
  otaSeconds: number;
  heartbeat: number;
  liveMetrics: Record<string, any>;
}

interface CurveDataPoint {
  offset: number;
  result: "pass" | "fail" | "crash";
  temp: number;
  timestamp: string;
}

interface WizardResult {
  id: string;
  name: string;
  timestamp: string;
  chipGrade: string;
  offsets: Record<string, number>;
  curveData: CurveDataPoint[];
  duration: number;
  iterations: number;
}

interface WizardContextType {
  isRunning: boolean;
  progress: WizardProgress | null;
  result: WizardResult | null;
  resultsHistory: WizardResult[];
  dirtyExit: { detected: boolean; crashInfo: any } | null;
  
  startWizard: (config: WizardConfig) => Promise<void>;
  cancelWizard: () => Promise<void>;
  applyResult: (resultId: string, saveAsPreset: boolean) => Promise<void>;
  checkDirtyExit: () => Promise<void>;
  loadResultsHistory: () => Promise<void>;
}

const WizardContext = createContext<WizardContextType | undefined>(undefined);

export const WizardProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState<WizardProgress | null>(null);
  const [result, setResult] = useState<WizardResult | null>(null);
  const [resultsHistory, setResultsHistory] = useState<WizardResult[]>([]);
  const [dirtyExit, setDirtyExit] = useState<{ detected: boolean; crashInfo: any } | null>(null);
  
  // Listen for server events
  useEffect(() => {
    const handleServerEvent = (event: any) => {
      if (event.type === "wizard_progress") {
        setProgress(event.data);
        setIsRunning(true);
      } else if (event.type === "wizard_complete") {
        setResult(event.data);
        setIsRunning(false);
        loadResultsHistory();
      } else if (event.type === "wizard_error") {
        setIsRunning(false);
        // Handle error
      }
    };
    
    serverAPI.addEventListener("server_event", handleServerEvent);
    return () => serverAPI.removeEventListener("server_event", handleServerEvent);
  }, []);
  
  const startWizard = async (config: WizardConfig) => {
    const response = await serverAPI.callPluginMethod("start_wizard", config);
    if (response.success) {
      setIsRunning(true);
      setResult(null);
    }
  };
  
  const cancelWizard = async () => {
    await serverAPI.callPluginMethod("cancel_wizard", {});
    setIsRunning(false);
  };
  
  const applyResult = async (resultId: string, saveAsPreset: boolean) => {
    await serverAPI.callPluginMethod("apply_wizard_result", {
      result_id: resultId,
      save_as_preset: saveAsPreset
    });
  };
  
  const checkDirtyExit = async () => {
    const response = await serverAPI.callPluginMethod("check_wizard_dirty_exit", {});
    if (response.dirty_exit) {
      setDirtyExit({ detected: true, crashInfo: response.crash_info });
    }
  };
  
  const loadResultsHistory = async () => {
    const response = await serverAPI.callPluginMethod("get_wizard_results_history", {});
    setResultsHistory(response);
  };
  
  // Check for dirty exit on mount
  useEffect(() => {
    checkDirtyExit();
    loadResultsHistory();
  }, []);
  
  return (
    <WizardContext.Provider value={{
      isRunning,
      progress,
      result,
      resultsHistory,
      dirtyExit,
      startWizard,
      cancelWizard,
      applyResult,
      checkDirtyExit,
      loadResultsHistory
    }}>
      {children}
    </WizardContext.Provider>
  );
};

export const useWizard = () => {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error("useWizard must be used within WizardProvider");
  }
  return context;
};
```

#### 2. Refactored WizardMode Component (`src/components/WizardMode.tsx`)

**Status**: 🔨 TODO - Major Refactor Required

The existing component needs to be completely refactored to use the new wizard system:

**New Structure**:
1. **Configuration Screen** - Goal selection with advanced settings
2. **Execution Screen** - Real-time progress with ETA/OTA
3. **Results Screen** - Curve visualization and chip grading
4. **Crash Recovery Modal** - Dirty exit detection UI

**Key Changes**:
- Remove old autotune/binning integration
- Add wizard context integration
- Implement curve chart (using recharts or simple SVG)
- Add heartbeat visual indicator
- Add crash recovery UI
- Add results history browser

#### 3. Curve Visualization Component

**Status**: 🔨 TODO

Create a simple curve chart component:

```typescript
import { FC } from "react";
import { CurveDataPoint } from "../context/WizardContext";

interface CurveChartProps {
  data: CurveDataPoint[];
}

export const CurveChart: FC<CurveChartProps> = ({ data }) => {
  // Simple SVG-based chart
  // X-axis: Voltage offset (mV)
  // Y-axis: Temperature (°C) or Pass/Fail indicator
  // Color code: Green (pass), Red (fail), Orange (crash)
  
  const width = 300;
  const height = 150;
  const padding = 30;
  
  // Calculate scales
  const xMin = Math.min(...data.map(d => d.offset));
  const xMax = Math.max(...data.map(d => d.offset));
  const yMin = 0;
  const yMax = Math.max(...data.map(d => d.temp), 100);
  
  const xScale = (x: number) => 
    padding + ((x - xMin) / (xMax - xMin)) * (width - 2 * padding);
  
  const yScale = (y: number) => 
    height - padding - ((y - yMin) / (yMax - yMin)) * (height - 2 * padding);
  
  return (
    <svg width={width} height={height} style={{ backgroundColor: "#1a1d24" }}>
      {/* Grid lines */}
      {/* ... */}
      
      {/* Data points */}
      {data.map((point, i) => (
        <circle
          key={i}
          cx={xScale(point.offset)}
          cy={yScale(point.temp)}
          r={4}
          fill={
            point.result === "pass" ? "#4caf50" :
            point.result === "fail" ? "#f44336" :
            "#ff9800"
          }
        />
      ))}
      
      {/* Connecting line */}
      <polyline
        points={data.map(d => `${xScale(d.offset)},${yScale(d.temp)}`).join(" ")}
        fill="none"
        stroke="#1a9fff"
        strokeWidth={2}
      />
      
      {/* Axes */}
      {/* ... */}
    </svg>
  );
};
```

## Implementation Checklist

### Backend
- [x] Create `WizardSession` class with state management
- [x] Implement step-down search algorithm
- [x] Add crash recovery with dirty exit detection
- [x] Implement chip quality grading
- [x] Add curve data collection
- [x] Update `EventEmitter` with wizard events
- [ ] Add RPC methods to `DeckTuneRPC`
- [ ] Integrate wizard session in `main.py`
- [ ] Add unit tests for wizard session

### Frontend
- [ ] Create `WizardContext` with state management
- [ ] Refactor `WizardMode` component
- [ ] Create configuration screen UI
- [ ] Create execution screen with progress
- [ ] Create results screen with curve chart
- [ ] Create crash recovery modal
- [ ] Add results history browser
- [ ] Integrate with preset system
- [ ] Add per-game profile support

### Testing
- [ ] Test step-down algorithm accuracy
- [ ] Test crash recovery flow
- [ ] Test dirty exit detection
- [ ] Test preset generation
- [ ] Test curve data visualization
- [ ] Test chip grading accuracy
- [ ] Test ETA/OTA calculations
- [ ] Test heartbeat watchdog

### Documentation
- [ ] Update user guide with wizard workflow
- [ ] Document aggressiveness levels
- [ ] Document chip grading scale
- [ ] Add troubleshooting section
- [ ] Create video tutorial

## File Structure

```
backend/
  tuning/
    wizard_session.py          ✅ Created
  api/
    events.py                  ✅ Updated
    rpc.py                     🔨 TODO
main.py                        🔨 TODO

src/
  context/
    WizardContext.tsx          🔨 TODO
  components/
    WizardMode.tsx             🔨 TODO (refactor)
    CurveChart.tsx             🔨 TODO
    WizardConfig.tsx           🔨 TODO
    WizardProgress.tsx         🔨 TODO
    WizardResults.tsx          🔨 TODO
    CrashRecoveryModal.tsx     🔨 TODO
```

## Next Steps

1. **Implement RPC Integration** - Add wizard methods to `DeckTuneRPC` class
2. **Update Main Plugin** - Initialize wizard session in `main.py`
3. **Create Frontend Context** - Implement `WizardContext.tsx`
4. **Refactor UI Component** - Complete overhaul of `WizardMode.tsx`
5. **Add Visualization** - Create curve chart component
6. **Testing** - Comprehensive testing of all flows
7. **Documentation** - Update user guides

## Safety Considerations

1. **Hard Limits**: Platform-specific limits enforced (LCD: -100mV, OLED: -80mV)
2. **Consecutive Failures**: Stop after 3 failures to prevent damage
3. **Crash Recovery**: Automatic rollback to last stable values
4. **Watchdog**: Heartbeat monitoring with automatic revert
5. **Safety Margins**: Configurable margins based on aggressiveness
6. **User Confirmation**: Require confirmation before applying aggressive settings

## Performance Estimates

- **Safe Mode**: ~15-20 minutes (2mV steps, 30s tests)
- **Balanced Mode**: ~5-10 minutes (5mV steps, 30s tests)
- **Aggressive Mode**: ~3-5 minutes (10mV steps, 30s tests)
- **Thorough Mode**: 2-3x longer (120s tests instead of 30s)

## Success Metrics

- ✅ One-click operation (minimal user input)
- ✅ Transparent progress (real-time ETA/OTA)
- ✅ Crash recovery (automatic rollback)
- ✅ Result visualization (curve chart)
- ✅ Chip quality feedback (grading system)
- ✅ Preset integration (automatic save)
- ✅ Safety guarantees (hard limits, watchdog)
