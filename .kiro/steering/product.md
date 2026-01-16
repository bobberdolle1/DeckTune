# DeckTune Product Overview

DeckTune is an automated undervolting and tuning solution for Steam Deck (LCD/OLED) with safety guarantees. It's a Decky Loader plugin that transforms complex CPU tuning into a one-button procedure.

## Core Features

- **Auto Platform Detection**: Detects Jupiter (LCD) or Galileo (OLED) with appropriate safety limits (cached for fast startup)
- **Autotune**: Automatic discovery of optimal undervolt values via binary search
- **Dynamic Mode (gymdeck3)**: Real-time CPU load-based undervolt adjustment using a Rust daemon
- **Fan Control (v3.0)**: Low-level fan curve control via hwmon sysfs, integrated into gymdeck3
- **Safety System**: Multi-layer protection with watchdog, automatic rollback, LKG (Last Known Good) values
- **Per-Game Profiles**: Automatic profile switching based on running game (AppID detection)
- **Silicon Binning**: Advanced chip quality testing to find maximum stable undervolt
- **Expert Mode**: Extended range (-100mV) for advanced users with explicit risk confirmation
- **Built-in Stress Tests**: CPU, RAM, and Combo tests for stability verification
- **Real-Time Telemetry**: Live temperature and power graphs with session history tracking
- **Crash Recovery Metrics**: Track recovery events with detailed history
- **Setup Wizard**: Guided first-run experience for new users

## Target Platform

- Steam Deck (LCD Jupiter or OLED Galileo)
- SteamOS 3.x
- Requires Decky Loader plugin framework
- Requires root privileges for ryzenadj operations

## Safety Philosophy

Multiple protection layers:
- Platform-specific safe limits (-30mV LCD, -35mV OLED, -25mV unknown)
- Watchdog monitoring (5s heartbeat, 30s timeout)
- Boot recovery (automatic rollback on reboot during tuning)
- Binning crash recovery (restores last stable value after crash)
- Panic disable button (instant reset to 0)
- Expert mode requires explicit user confirmation

## User Modes

- **Wizard Mode**: Simplified interface with preset goals (Quiet/Cool, Balanced, Max Battery, Max Performance)
- **Expert Mode**: Advanced controls for manual tuning, preset management, testing, and diagnostics
