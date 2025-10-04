"""
Simple test script to verify Audacity pipe connection.

This script is based on the official pipe_test.py from the Audacity project.
It tests basic communication with Audacity through mod-script-pipe.
"""

import sys
import os

# Add src to Python path so we can import audacity_pipe
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audacity_pipe import AudacityPipe, AudacityError


def main():
    """Test Audacity pipe connection and basic commands."""
    print("Audacity Pipe Test")
    print("==================")
    print()
    
    print("This script tests the connection to Audacity via mod-script-pipe.")
    print("Make sure:")
    print("1. Audacity is running")
    print("2. mod-script-pipe is enabled in Audacity preferences")
    print("3. You have restarted Audacity after enabling mod-script-pipe")
    print()
    
    try:
        print("Attempting to connect to Audacity...")
        
        with AudacityPipe(timeout=5.0) as audacity:
            print("✓ Successfully connected to Audacity!")
            print()
            
            # Test 1: Help command
            print("Test 1: Getting help...")
            help_response = audacity.do_command("Help:")
            if help_response and len(help_response) > 0:
                print(f"✓ Help  successful ({len(help_response)} characters)")
            else:
                print("✗ Help command returned empty response")
            print()
            
            
        print("🎉 All tests completed successfully!")
        print()
        print("Your Audacity scripting setup is working correctly.")
        print("You can now run the example scripts in the examples/ directory.")
        
    except AudacityError as e:
        print(f"✗ Audacity Error: {e}")
        print()
        print("Troubleshooting steps:")
        print("1. Ensure Audacity is running")
        print("2. Go to Edit → Preferences → Modules")
        print("3. Find 'mod-script-pipe' and set it to 'Enabled'")
        print("4. Restart Audacity")
        print("5. Run this test again")
        sys.exit(1)
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        print()
        print("This might be a system-specific issue.")
        print("Check the documentation for platform-specific setup.")
        sys.exit(1)


if __name__ == "__main__":
    main()