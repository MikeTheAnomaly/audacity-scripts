"""
Export Each Clip Individually

This script exports each clip in the current Audacity project to separate files.
Only clips from unmuted tracks are exported. Each clip is exported with its clip name
as the filename.

Usage:
    python export_clips_individually.py

The script will prompt you for:
- Output directory path
- Output file format/extension (default: wav)
- Optional filename prefix
"""

import sys
import os
import json
import re
import time
# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audacity_pipe import AudacityPipe, Commands, AudacityError


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be a valid filename.
    
    Args:
        name: The original name
        
    Returns:
        A sanitized filename safe for use on all platforms
    """
    # Replace invalid characters with underscores
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    # Limit length
    if len(name) > 200:
        name = name[:200]
    # Handle empty names
    if not name:
        name = "unnamed"
    return name


def get_user_input():
    """
    Get export settings from the user.
    
    Returns:
        dict: Dictionary containing output_dir, prefix, and file_extension
    """
    print("\n" + "="*60)
    print("Export Each Clip Individually")
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
    
    # Get optional prefix
    prefix = input("\nEnter filename prefix (optional, e.g., 'clip_'): ").strip()
    if prefix:
        print(f"✓ Files will be prefixed with: '{prefix}'")
    
    # Get file extension
    file_extension = input("\nEnter file extension (default: wav): ").strip()
    if not file_extension:
        file_extension = "wav"
    # Remove leading dot if user included it
    file_extension = file_extension.lstrip('.')
    
    print(f"✓ Files will be saved as .{file_extension} format")
    
    return {
        'output_dir': output_dir,
        'prefix': prefix,
        'file_extension': file_extension
    }


def export_clips_individually(output_dir: str, prefix: str, file_extension: str):
    """
    Export each clip from unmuted tracks to separate files.
    
    Args:
        output_dir: Directory to save the exported files
        prefix: Optional prefix for filenames
        file_extension: File extension (e.g., 'wav', 'mp3', 'flac')
    """
    try:
        with AudacityPipe() as audacity:
            cmd = Commands(audacity)
            
            print("\n" + "="*60)
            print("Starting Clip Export Process")
            print("="*60 + "\n")
            
            # Get track information to check mute status
            print("1. Retrieving track information...")
            tracks_info = cmd.get_info("Tracks")
            tracks_data = json.loads(tracks_info)
            
            # Create a dict of track index to mute status
            track_mute_status = {}
            for i, track in enumerate(tracks_data):
                track_mute_status[i] = track.get('mute', 0) == 1
            
            print(f"✓ Found {len(tracks_data)} track(s) in the project")
            
            # Get clip information
            print("2. Retrieving clip information...")
            clips_info = cmd.get_info("Clips")
            
            try:
                clips_data = json.loads(clips_info)
            except json.JSONDecodeError as e:
                print("Error: Could not parse clip information from Audacity.")
                print(f"JSON Error: {e}")
                print("Response received:")
                print(clips_info)
                return
            
            if not clips_data:
                print("\n⚠ No clips found in the current project.")
                print("Please open a project with audio clips in Audacity.")
                return
            
            # Filter clips from unmuted tracks
            clips_to_export = []
            for clip in clips_data:
                track_idx = clip.get('track', 0)
                is_muted = track_mute_status.get(track_idx, False)
                
                if not is_muted:
                    clips_to_export.append(clip)
                else:
                    print(f"  Skipping clip '{clip.get('name', 'Unnamed')}' (track {track_idx + 1} is muted)")
            
            if not clips_to_export:
                print("\n⚠ No clips found in unmuted tracks.")
                print("Please unmute some tracks or check that clips exist.")
                return
            
            print(f"✓ Found {len(clips_to_export)} clip(s) to export from unmuted tracks\n")
            
            # Create a temporary export track at the end
            print("3. Creating temporary export track...")
            cmd.new_stereo_track()
            
            # Get updated track count to know the index of our temp track
            tracks_info_updated = cmd.get_info("Tracks")
            tracks_data_updated = json.loads(tracks_info_updated)
            temp_track_idx = len(tracks_data_updated) - 1
            print(f"✓ Created temporary track at index {temp_track_idx}\n")
            
            # Export each clip

            # Mute all other tracks except the temp track
            num_tracks = len(tracks_data_updated)
            for t in range(num_tracks):
                cmd.select_none()
                cmd.select_tracks(track=t, track_count=1, mode="Set")
                if t == temp_track_idx:
                    cmd.set_track_audio(mute=False)
                else:
                    cmd.set_track_audio(mute=True)

            exported_count = 0
            for i, clip in enumerate(clips_to_export, start=1):
                clip_name = clip.get('name', f'clip_{i}')
                track_idx = clip.get('track', -1)
                start_time = clip.get('start', -10.0)
                end_time = clip.get('end', -10.0)
                if track_idx == -1 or start_time < 0 or end_time <= start_time:
                    print(f"  Skipping clip '{clip_name}' due to invalid data")
                    continue
                
                # Sanitize the clip name for use as filename
                safe_name = sanitize_filename(clip_name)
                
                # Construct output filename
                if prefix:
                    output_filename = f"{prefix}{safe_name}.{file_extension}"
                else:
                    output_filename = f"{safe_name}.{file_extension}"
                
                output_path = os.path.join(output_dir, output_filename)
                
                # Handle duplicate filenames
                counter = 1
                base_output_path = output_path
                while os.path.exists(output_path):
                    if prefix:
                        output_filename = f"{prefix}{safe_name}_{counter}.{file_extension}"
                    else:
                        output_filename = f"{safe_name}_{counter}.{file_extension}"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                
                print(f"Exporting clip {i}/{len(clips_to_export)}: '{clip_name}'")
                print(f"  Track: {track_idx + 1}")
                print(f"  Time: {start_time:.3f}s - {end_time:.3f}s")
                print(f"  → {output_path}")
                
                try:
                    # Select the specific track with the clip
                    cmd.select_none()
                    cmd.select_tracks(track=track_idx, track_count=1, mode="Set")
                    
                    # Select the time range of this clip
                    cmd.select_time(start=start_time, end=end_time, relative_to="ProjectStart")
                    
                    # Copy the selected audio
                    cmd.copy()
                    
                    # Select the temporary export track
                    # Clear any existing audio in the temp track
                    cmd.select_none()
                    cmd.select_tracks(track=temp_track_idx, track_count=1, mode="Set")
                    cmd.select_time(start=0, end=100, relative_to="ProjectStart")
                    cmd.delete()

                    cmd.select_none()
                    cmd.select_tracks(track=temp_track_idx, track_count=1, mode="Set")

                    # Paste the clip into the temp track
                    cmd.paste()
                    
                    # Select the temp track and export it
                    cmd.select_none()
                    cmd.select_tracks(track=temp_track_idx, track_count=1, mode="Set")
                    cmd.select_time(start=0, end= end_time - start_time, relative_to="ProjectStart")
                    result = cmd.export_audio(output_path, num_channels=2)
                    
                    exported_count += 1
                    print(f"  ✓ Export complete\n")
                    
                except Exception as e:
                    print(f"  ✗ Failed to export clip: {e}\n")
                    continue
            
            print("="*60)
            print(f"✓ Successfully exported {exported_count}/{len(clips_to_export)} clips to: {output_dir}")
            print("="*60)
            
    except AudacityError as e:
        print(f"\n✗ Audacity Error: {e}")
        print("\nMake sure:")
        print("  1. Audacity is running")
        print("  2. mod-script-pipe is enabled (Edit → Preferences → Modules)")
        print("  3. You have a project with clips loaded")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON parsing error: {e}")
        print("The response from Audacity was not valid JSON.")
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
        print("Note: Only clips from UNMUTED tracks will be exported.")
        confirm = input("Proceed with export? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Export cancelled.")
            return
        
        # Export the clips
        export_clips_individually(
            settings['output_dir'],
            settings['prefix'],
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
