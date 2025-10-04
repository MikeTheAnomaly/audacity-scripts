"""
Export Each Track Individually

This script exports each track in the current Audacity project to separate files
in a user-specified directory.

Usage:
    python export_tracks_individually.py

The script will prompt you for:
- Output directory path
- Output file format/extension (default: wav)
- Base filename (tracks will be named: basename_track1.ext, basename_track2.ext, etc.)
"""

import sys
import os
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audacity_pipe import AudacityPipe, Commands, AudacityError


def get_user_input():
    """
    Get export settings from the user.
    
    Returns:
        dict: Dictionary containing output_dir, base_filename, and file_extension
    """
    print("\n" + "="*60)
    print("Export Each Track Individually")
    print("="*60 + "\n")
    
    # Get output directory
    while True:
        output_dir = input("Enter output directory path: ").strip()
        if not output_dir:
            print("Error: Output directory cannot be empty.")
            continue
        
        # Expand user path and normalize
        output_dir = os.path.expanduser(output_dir)
        output_dir = os.path.abspath(output_dir)
        
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            create = input(f"\nDirectory '{output_dir}' does not exist. Create it? (y/n): ").strip().lower()
            if create == 'y':
                try:
                    os.makedirs(output_dir)
                    print(f"✓ Created directory: {output_dir}")
                    break
                except Exception as e:
                    print(f"Error creating directory: {e}")
                    continue
            else:
                continue
        else:
            print(f"✓ Using directory: {output_dir}")
            break
    
    # Get base filename
    base_filename = input("\nEnter base filename (e.g., 'track'): ").strip()
    if not base_filename:
        base_filename = "track"
        print(f"Using default: '{base_filename}'")
    
    # Get file extension
    file_extension = input("\nEnter file extension (default: wav): ").strip()
    if not file_extension:
        file_extension = "wav"
    # Remove leading dot if user included it
    file_extension = file_extension.lstrip('.')
    
    print(f"\n✓ Files will be saved as: {base_filename}_1.{file_extension}, {base_filename}_2.{file_extension}, etc.")
    
    return {
        'output_dir': output_dir,
        'base_filename': base_filename,
        'file_extension': file_extension
    }


def export_tracks_individually(output_dir: str, base_filename: str, file_extension: str):
    """
    Export each track in the current Audacity project to a separate file.
    
    Args:
        output_dir: Directory to save the exported files
        base_filename: Base name for the exported files
        file_extension: File extension (e.g., 'wav', 'mp3', 'flac')
    """
    try:
        with AudacityPipe() as audacity:
            cmd = Commands(audacity)
            
            print("\n" + "="*60)
            print("Starting Export Process")
            print("="*60 + "\n")
            
            # Get track information
            print("1. Retrieving track information...")
            tracks_info = cmd.get_info("Tracks")
            
            # Parse the JSON response
            try:
                tracks_data = json.loads(tracks_info)
            except json.JSONDecodeError as e:
                print("Error: Could not parse track information from Audacity.")
                print(f"JSON Error: {e}")
                print("Response received:")
                print(tracks_info)
                return
            
            # Count the number of tracks
            num_tracks = len(tracks_data)
            
            if num_tracks == 0:
                print("\n⚠ No tracks found in the current project.")
                print("Please open a project with audio tracks in Audacity.")
                return
            
            print(f"✓ Found {num_tracks} track(s) in the project\n")
            
            # Export each track individually
            for i, track in enumerate(tracks_data, start=1):
                track_name = track.get('name', f'Track {i}')
                track_index = i - 1  # Audacity uses 0-based indexing
                
                # Construct output filename
                output_filename = f"{base_filename}_{i}.{file_extension}"
                output_path = os.path.join(output_dir, output_filename)
                
                print(f"Exporting track {i}/{num_tracks}: '{track_name}'")
                print(f"  → {output_path}")
                
                # Mute all tracks first
                for j in range(num_tracks):
                    cmd.select_tracks(track=j, track_count=1, mode="Set")
                    cmd.set_track_audio(mute=True)
                
                # Unmute only the current track (solo it)
                cmd.select_tracks(track=track_index, track_count=1, mode="Set")
                cmd.set_track_audio(mute=False)
                
                # Select all time for this track
                cmd.select_all()
                
                # Export the track
                result = cmd.export_audio(output_path, num_channels=2)
                
                print(f"  ✓ Export complete\n")
            
            # Unmute all tracks after export is complete
            print("Restoring track states...")
            for j in range(num_tracks):
                cmd.select_tracks(track=j, track_count=1, mode="Set")
                cmd.set_track_audio(mute=False)
            print("✓ All tracks unmuted\n")
            
            print("="*60)
            print(f"✓ All tracks exported successfully to: {output_dir}")
            print("="*60)
            
    except AudacityError as e:
        print(f"\n✗ Audacity Error: {e}")
        print("\nMake sure:")
        print("  1. Audacity is running")
        print("  2. mod-script-pipe is enabled (Edit → Preferences → Modules)")
        print("  3. You have a project with tracks loaded")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function to run the script."""
    try:
        # Get user input for export settings
        settings = get_user_input()
        
        # Confirm before proceeding
        print("\n" + "-"*60)
        confirm = input("\nProceed with export? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Export cancelled.")
            return
        
        # Export the tracks
        export_tracks_individually(
            settings['output_dir'],
            settings['base_filename'],
            settings['file_extension']
        )
        
    except KeyboardInterrupt:
        print("\n\nExport cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
