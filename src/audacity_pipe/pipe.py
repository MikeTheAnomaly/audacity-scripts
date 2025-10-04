"""
Core pipe communication module for Audacity scripting.

This module handles the low-level communication with Audacity through named pipes.
It provides a Python interface that mirrors the functionality of the official
pipe_test.py and pipeclient.py examples from the Audacity project.
"""

import os
import sys
import platform
import time
from typing import Optional, Union, Any


class AudacityError(Exception):
    """Exception raised for Audacity-related errors."""
    pass


class AudacityPipe:
    """
    Main class for communicating with Audacity through mod-script-pipe.
    
    This class handles the named pipe communication and provides a Python
    interface for sending commands to Audacity.
    
    Example:
        >>> with AudacityPipe() as audacity:
        ...     audacity.do_command("Help:")
        ...     audacity.do_command("Import2: Filename='audio.wav'")
    """
    
    def __init__(self, timeout: float = 10.0):
        """
        Initialize the Audacity pipe connection.
        
        Args:
            timeout: Maximum time to wait for pipe operations (seconds)
        """
        self.timeout = timeout
        self.to_pipe = None
        self.from_pipe = None
        self._is_connected = False
        
        # Platform-specific pipe names
        if platform.system() == "Windows":
            self.to_pipe_name = r"\\.\pipe\ToSrvPipe"
            self.from_pipe_name = r"\\.\pipe\FromSrvPipe"
        else:
            # Unix-like systems (Linux, macOS)
            # Pipes are created per-user with process ID
            import getpass
            username = getpass.getuser()
            self.to_pipe_name = f"/tmp/audacity_script_pipe.to.{username}"
            self.from_pipe_name = f"/tmp/audacity_script_pipe.from.{username}"
    
    def connect(self) -> None:
        """
        Establish connection to Audacity pipes.
        
        Raises:
            AudacityError: If connection cannot be established
        """
        if self._is_connected:
            return
            
        try:
            print(f"Connecting to Audacity...")
            print(f"To pipe: {self.to_pipe_name}")
            print(f"From pipe: {self.from_pipe_name}")
            
            # Open pipes for communication
            if platform.system() == "Windows":
                self._connect_windows()
            else:
                self._connect_unix()
                
            self._is_connected = True
            print("Connected to Audacity successfully!")
            
        except Exception as e:
            raise AudacityError(f"Failed to connect to Audacity: {e}")
    
    def _connect_windows(self) -> None:
        """Connect to pipes on Windows."""
        # Windows uses named pipes with specific syntax
        self.to_pipe = open(self.to_pipe_name, 'w', encoding='utf-8')
        self.from_pipe = open(self.from_pipe_name, 'rt', encoding='utf-8')
    
    def _connect_unix(self) -> None:
        """Connect to pipes on Unix-like systems."""
        # Unix uses FIFO pipes
        if not os.path.exists(self.to_pipe_name):
            raise AudacityError(
                f"Audacity pipe not found: {self.to_pipe_name}\\n"
                "Make sure Audacity is running with mod-script-pipe enabled."
            )
        
        if not os.path.exists(self.from_pipe_name):
            raise AudacityError(
                f"Audacity pipe not found: {self.from_pipe_name}\\n"
                "Make sure Audacity is running with mod-script-pipe enabled."
            )
        
        self.to_pipe = open(self.to_pipe_name, 'w', encoding='utf-8')
        self.from_pipe = open(self.from_pipe_name, 'r', encoding='utf-8')
    
    def disconnect(self) -> None:
        """Close the pipe connections."""
        if self.to_pipe:
            try:
                self.to_pipe.close()
            except:
                pass
            self.to_pipe = None
        
        if self.from_pipe:
            try:
                self.from_pipe.close()
            except:
                pass
            self.from_pipe = None
        
        self._is_connected = False
        print("Disconnected from Audacity.")
    
    def is_connected(self) -> bool:
        """Check if currently connected to Audacity."""
        return self._is_connected
    
    def send_command(self, command: str) -> None:
        """
        Send a command to Audacity.
        
        Args:
            command: The command string to send
            
        Raises:
            AudacityError: If not connected or send fails
        """
        if not self._is_connected:
            raise AudacityError("Not connected to Audacity")
        
        if not self.to_pipe:
            raise AudacityError("To-pipe not available")
        
        try:
            print(f"Sending command: {command}")
            self.to_pipe.write(command + '\n')
            self.to_pipe.flush()
        except Exception as e:
            raise AudacityError(f"Failed to send command '{command}': {e}")
    
    def receive_response(self) -> str:
        """
        Read response from Audacity.
        
        Returns:
            The response string from Audacity
            
        Raises:
            AudacityError: If not connected or receive fails
        """
        if not self._is_connected:
            raise AudacityError("Not connected to Audacity")
        
        if not self.from_pipe:
            raise AudacityError("From-pipe not available")
        
        try:
            response = ""
            start_time = time.time()
            
            while True:
                line = self.from_pipe.readline()
                if not line:
                    if time.time() - start_time > self.timeout:
                        raise AudacityError("Timeout waiting for response")
                    time.sleep(0.1)
                    continue
                
                # Empty line signals end of response, but only if we've received something
                if line.strip() == "":
                    if response:  # Only break if we've accumulated some response
                        break
                    else:
                        continue  # Skip leading empty lines
                
                response += line
            
            # Clean up Audacity's status messages from the response
            response = response.strip()
            response = response.replace("BatchCommand finished: OK", "").strip()
            
            print(f"Received response: {response}")
            return response
            
        except Exception as e:
            raise AudacityError(f"Failed to receive response: {e}")
    
    def do_command(self, command: str) -> str:
        """
        Send a command to Audacity and get the response.
        
        Args:
            command: The command to execute
            
        Returns:
            Response from Audacity
            
        Raises:
            AudacityError: If command execution fails
        """
        if not self._is_connected:
            self.connect()
        
        self.send_command(command)
        response = self.receive_response()
        
        print(f"Response: {response}")
        return response
    
    def quick_command(self, command: str) -> str:
        """
        Execute a command with automatic connection management.
        
        This is a convenience method that handles connection automatically.
        
        Args:
            command: The command to execute
            
        Returns:
            Response from Audacity
        """
        with self:
            return self.do_command(command)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
    
    def close(self) -> None:
        """Alias for disconnect() for compatibility."""
        self.disconnect()


def test_connection() -> bool:
    """
    Test if Audacity pipe connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with AudacityPipe() as audacity:
            response = audacity.do_command("Help:")
            return "Command" in response or "Help" in response
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def main():
    """Simple test function."""
    print("Testing Audacity pipe connection...")
    
    if test_connection():
        print("✓ Connection test passed!")
        
        # Try a few basic commands
        try:
            with AudacityPipe() as audacity:
                print("\\nTesting basic commands:")
                
                # Get help
                print("\\n1. Getting help...")
                help_response = audacity.do_command("Help:")
                print(f"Help response length: {len(help_response)} characters")
                
                # Get project info
                print("\\n2. Getting project info...")
                info_response = audacity.do_command("GetInfo: Type=Tracks")
                print(f"Info response: {info_response[:200]}...")
                
                print("\\n✓ All tests passed!")
        except Exception as e:
            print(f"✗ Command test failed: {e}")
    else:
        print("✗ Connection test failed!")
        print("\\nTroubleshooting:")
        print("1. Make sure Audacity is running")
        print("2. Enable mod-script-pipe in Audacity preferences")
        print("3. Restart Audacity after enabling mod-script-pipe")


if __name__ == "__main__":
    main()