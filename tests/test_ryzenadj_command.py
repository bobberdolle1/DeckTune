"""Property tests for ryzenadj command format.

Feature: decktune, Property 14: Ryzenadj Command Format
Validates: Requirements 9.2

Property 14: Ryzenadj Command Format
For any apply_values(cores) call, the executed commands SHALL be exactly 4 calls 
to `sudo ryzenadj --set-coper=<hex>` where each hex is calculate_hex(i, cores[i]) 
for i in [0,1,2,3].
"""

import re
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings

from backend.core.ryzenadj import RyzenadjWrapper


# Strategy for undervolt values (-60 to 0)
undervolt_value = st.integers(min_value=-60, max_value=0)

# Strategy for list of 4 undervolt values
undervolt_values_list = st.lists(undervolt_value, min_size=4, max_size=4)


class TestRyzenadjCommandFormat:
    """Property 14: Ryzenadj Command Format
    
    For any apply_values(cores) call, the executed commands SHALL be exactly 4 calls 
    to `sudo ryzenadj --set-coper=<hex>` where each hex is calculate_hex(i, cores[i]) 
    for i in [0,1,2,3].
    
    Validates: Requirements 9.2
    """

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_exactly_four_commands_generated(self, cores: list):
        """apply_values generates exactly 4 commands."""
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir")
        
        # Mock subprocess.run to avoid actual execution
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        commands = wrapper.get_last_commands()
        assert len(commands) == 4, f"Expected 4 commands, got {len(commands)}"

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_commands_use_sudo(self, cores: list):
        """All commands start with 'sudo'."""
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir")
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        commands = wrapper.get_last_commands()
        for i, cmd in enumerate(commands):
            assert cmd.startswith("sudo "), (
                f"Command {i} does not start with 'sudo': {cmd}"
            )

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_commands_use_set_coper_flag(self, cores: list):
        """All commands contain '--set-coper=' flag."""
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir")
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        commands = wrapper.get_last_commands()
        for i, cmd in enumerate(commands):
            assert "--set-coper=" in cmd, (
                f"Command {i} does not contain '--set-coper=': {cmd}"
            )

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_hex_values_match_calculate_hex(self, cores: list):
        """Hex values in commands match calculate_hex output for each core."""
        wrapper = RyzenadjWrapper("/path/to/ryzenadj", "/working/dir")
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        commands = wrapper.get_last_commands()
        
        for i, (cmd, value) in enumerate(zip(commands, cores)):
            expected_hex = RyzenadjWrapper.calculate_hex(i, value)
            
            # Extract hex value from command
            match = re.search(r'--set-coper=(\S+)', cmd)
            assert match is not None, f"Could not extract hex from command: {cmd}"
            
            actual_hex = match.group(1)
            assert actual_hex == expected_hex, (
                f"Core {i}: expected hex {expected_hex}, got {actual_hex}"
            )

    @given(cores=undervolt_values_list)
    @settings(max_examples=100)
    def test_command_format_structure(self, cores: list):
        """Commands follow exact format: 'sudo <binary> --set-coper=<hex>'."""
        binary_path = "/path/to/ryzenadj"
        wrapper = RyzenadjWrapper(binary_path, "/working/dir")
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        commands = wrapper.get_last_commands()
        
        for i, (cmd, value) in enumerate(zip(commands, cores)):
            expected_hex = RyzenadjWrapper.calculate_hex(i, value)
            expected_cmd = f"sudo {binary_path} --set-coper={expected_hex}"
            
            assert cmd == expected_cmd, (
                f"Command {i} format mismatch:\n"
                f"  Expected: {expected_cmd}\n"
                f"  Got: {cmd}"
            )

    def test_subprocess_called_with_correct_args(self):
        """Verify subprocess.run is called with correct arguments."""
        binary_path = "/path/to/ryzenadj"
        working_dir = "/working/dir"
        wrapper = RyzenadjWrapper(binary_path, working_dir)
        cores = [-10, -20, -30, -15]
        
        with patch('backend.core.ryzenadj.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            wrapper.apply_values(cores)
        
        # Verify 4 calls were made
        assert mock_run.call_count == 4
        
        # Verify each call
        for i, call in enumerate(mock_run.call_args_list):
            args, kwargs = call
            expected_hex = RyzenadjWrapper.calculate_hex(i, cores[i])
            expected_args = ["sudo", binary_path, f"--set-coper={expected_hex}"]
            
            assert args[0] == expected_args, (
                f"Call {i}: expected args {expected_args}, got {args[0]}"
            )
            assert kwargs.get('cwd') == working_dir
            assert kwargs.get('capture_output') is True
            assert kwargs.get('text') is True
