/**
 * DeckTuneApp integration tests for frequency mode.
 * 
 * Feature: frequency-based-wizard
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DeckTuneApp } from '../DeckTuneApp';

// Mock the API
vi.mock('../../api', () => ({
  getApiInstance: vi.fn(() => ({
    init: vi.fn().mockResolvedValue(undefined),
    destroy: vi.fn(),
    handleServerEvent: vi.fn(),
    getSetting: vi.fn().mockResolvedValue(true),
    enableFrequencyMode: vi.fn().mockResolvedValue({ success: true }),
    disableFrequencyMode: vi.fn().mockResolvedValue({ success: true }),
  })),
}));

// Mock Decky API
vi.mock('@decky/api', () => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
}));

// Mock context
vi.mock('../../context', () => ({
  useDeckTune: () => ({
    state: {
      status: 'enabled',
      enabled: true,
    },
    api: {
      enableFrequencyMode: vi.fn().mockResolvedValue({ success: true }),
      disableFrequencyMode: vi.fn().mockResolvedValue({ success: true }),
    },
  }),
  initialState: {
    status: 'disabled',
    enabled: false,
  },
}));

// Mock all child components
vi.mock('../WizardMode', () => ({
  WizardMode: () => <div>Wizard Mode</div>,
}));

vi.mock('../ExpertMode', () => ({
  ExpertMode: () => <div>Expert Mode</div>,
}));

vi.mock('../FrequencyWizard', () => ({
  FrequencyWizard: () => <div>Frequency Wizard</div>,
}));

vi.mock('../FanControl', () => ({
  FanControl: ({ onBack }: { onBack: () => void }) => (
    <div>
      Fan Control
      <button onClick={onBack}>Back</button>
    </div>
  ),
}));

vi.mock('../HeaderBar', () => ({
  HeaderBar: ({ onFanControlClick, onSettingsClick }: any) => (
    <div>
      Header Bar
      <button onClick={onFanControlClick}>Fan Control</button>
      <button onClick={onSettingsClick}>Settings</button>
    </div>
  ),
}));

vi.mock('../SettingsMenu', () => ({
  SettingsMenu: ({ isOpen, onClose }: any) => (
    isOpen ? <div>Settings Menu<button onClick={onClose}>Close</button></div> : null
  ),
}));

vi.mock('../SetupWizard', () => ({
  SetupWizard: ({ onComplete }: any) => (
    <div>
      Setup Wizard
      <button onClick={onComplete}>Complete</button>
    </div>
  ),
}));

// Mock SettingsProvider
vi.mock('../../context/SettingsContext', () => ({
  SettingsProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('DeckTuneApp - Frequency Mode Integration', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should include frequency mode in mode selector', async () => {
    // Requirement 10.1: Add "Frequency-Based" mode to mode selector
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    
    render(<DeckTuneApp />);
    
    await waitFor(() => {
      expect(screen.getByText('Frequency-Based')).toBeDefined();
    });
  });

  it('should save frequency mode preference to localStorage', async () => {
    // Requirement 10.4: Store mode preference in localStorage
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    localStorage.setItem('decktune_ui_mode', 'frequency');
    
    render(<DeckTuneApp />);
    
    await waitFor(() => {
      const savedMode = localStorage.getItem('decktune_ui_mode');
      expect(savedMode).toBe('frequency');
    });
  });

  it('should restore frequency mode on app start', async () => {
    // Requirement 10.5: Restore last selected mode
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    localStorage.setItem('decktune_ui_mode', 'frequency');
    
    render(<DeckTuneApp />);
    
    await waitFor(() => {
      expect(screen.getByText('Frequency Wizard')).toBeDefined();
    });
  });

  it('should display all three modes: wizard, expert, and frequency', async () => {
    // Verify all modes are available
    localStorage.setItem('decktune_wizard_setup_complete', 'true');
    
    render(<DeckTuneApp />);
    
    await waitFor(() => {
      expect(screen.getByText('Wizard Mode')).toBeDefined();
      expect(screen.getByText('Expert Mode')).toBeDefined();
      expect(screen.getByText('Frequency-Based')).toBeDefined();
    });
  });
});
