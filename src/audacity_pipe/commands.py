"""
High-level command interface for common Audacity operations.

This module provides a more user-friendly interface for common Audacity
commands, with parameter validation and convenience methods.
"""

from typing import Optional, Union, List, Dict, Any
from .pipe import AudacityPipe, AudacityError


class Commands:
    """
    High-level interface for Audacity commands.
    
    This class provides typed methods for common Audacity operations,
    making it easier to use than raw command strings.
    """
    
    def __init__(self, pipe: AudacityPipe):
        """
        Initialize with an AudacityPipe instance.
        
        Args:
            pipe: Connected AudacityPipe instance
        """
        self.pipe = pipe
    
    # File Operations
    def new_project(self) -> str:
        """Create a new empty project."""
        return self.pipe.do_command("New:")
    
    def open_project(self, filename: str, add_to_history: bool = False) -> str:
        """
        Open an Audacity project file.
        
        Args:
            filename: Path to the .aup3 project file
            add_to_history: Whether to add to recent files history
        """
        cmd = f"OpenProject2: Filename='{filename}' AddToHistory={add_to_history}"
        return self.pipe.do_command(cmd)
    
    def save_project(self, filename: str, add_to_history: bool = False, 
                    compress: bool = False) -> str:
        """
        Save the current project.
        
        Args:
            filename: Path where to save the project
            add_to_history: Whether to add to recent files history
            compress: Whether to compress the project file
        """
        cmd = f"SaveProject2: Filename='{filename}' AddToHistory={add_to_history} Compress={compress}"
        return self.pipe.do_command(cmd)
    
    def import_audio(self, filename: str) -> str:
        """
        Import an audio file into the project.
        
        Args:
            filename: Path to the audio file to import
        """
        return self.pipe.do_command(f"Import2: Filename='{filename}'")
    
    def export_audio(self, filename: str, num_channels: int = 2) -> str:
        """
        Export selected audio to a file.
        
        Args:
            filename: Path where to save the exported audio
            num_channels: Number of channels (1=mono, 2=stereo)
        """
        # Convert backslashes to forward slashes for Audacity compatibility
        safe_path = filename.replace('\\', '/')
        cmd = f'Export2: Filename="{safe_path}" NumChannels={num_channels}'
        return self.pipe.do_command(cmd)
    
    # Selection Operations
    def select_all(self) -> str:
        """Select all audio in the project."""
        return self.pipe.do_command("SelectAll:")
    
    def select_none(self) -> str:
        """Clear the current selection."""
        return self.pipe.do_command("SelectNone:")
    
    def select_time(self, start: float, end: float, 
                   relative_to: str = "ProjectStart") -> str:
        """
        Select a time range.
        
        Args:
            start: Start time in seconds
            end: End time in seconds
            relative_to: Reference point ("Project", "Selection", etc.)
        """
        cmd = f"SelectTime: Start={start} End={end} RelativeTo={relative_to}"
        return self.pipe.do_command(cmd)
    
    def select_tracks(self, track: int, track_count: int = 1, 
                     mode: str = "Set") -> str:
        """
        Select specific tracks.
        
        Args:
            track: First track number (0-based)
            track_count: Number of tracks to select
            mode: Selection mode ("Set", "Add", "Remove")
        """
        cmd = f"SelectTracks: Track={track} TrackCount={track_count} Mode={mode}"
        return self.pipe.do_command(cmd)
    
    def select_frequencies(self, high: Optional[float] = None, 
                          low: Optional[float] = None) -> str:
        """
        Select frequency range (for spectral selection).
        
        Args:
            high: High frequency in Hz
            low: Low frequency in Hz
        """
        params = []
        if high is not None:
            params.append(f"High={high}")
        if low is not None:
            params.append(f"Low={low}")
        cmd = "SelectFrequencies:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    # Track Property Operations
    def set_track_status(self, name: Optional[str] = None, 
                        selected: Optional[bool] = None,
                        focused: Optional[bool] = None) -> str:
        """
        Set track status properties (name, selected, focused).
        
        Args:
            name: Track name to set
            selected: Whether track is selected
            focused: Whether track has focus
        """
        params = []
        if name is not None:
            params.append(f"Name='{name}'")
        if selected is not None:
            params.append(f"Selected={1 if selected else 0}")
        if focused is not None:
            params.append(f"Focused={1 if focused else 0}")
        cmd = "SetTrackStatus:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_track_audio(self, mute: Optional[bool] = None,
                       solo: Optional[bool] = None,
                       gain: Optional[float] = None,
                       pan: Optional[float] = None) -> str:
        """
        Set track audio properties (mute, solo, gain, pan).
        
        Args:
            mute: Whether to mute the track
            solo: Whether to solo the track
            gain: Gain level (0.0 to higher values, 1.0 = unity)
            pan: Pan position (-1.0 = left, 0.0 = center, 1.0 = right)
        """
        params = []
        if mute is not None:
            params.append(f"Mute={1 if mute else 0}")
        if solo is not None:
            params.append(f"Solo={1 if solo else 0}")
        if gain is not None:
            params.append(f"Gain={gain}")
        if pan is not None:
            params.append(f"Pan={pan}")
        cmd = "SetTrackAudio:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_track_visuals(self, height: Optional[int] = None,
                         display: Optional[str] = None,
                         scale: Optional[str] = None,
                         color: Optional[str] = None,
                         vzoom: Optional[str] = None,
                         vzoom_high: Optional[float] = None,
                         vzoom_low: Optional[float] = None,
                         spec_prefs: Optional[bool] = None,
                         spectral_sel: Optional[bool] = None,
                         scheme: Optional[str] = None) -> str:
        """
        Set track visual properties (display, colors, zoom, etc.).
        
        Args:
            height: Track height in pixels
            display: Display type ("Waveform", "Spectrogram", "Multi-view")
            scale: Scale type ("Linear", "dB")
            color: Color scheme ("Color0", "Color1", "Color2", "Color3")
            vzoom: Vertical zoom ("Reset", "Times2", "HalfWave")
            vzoom_high: Vertical zoom high value
            vzoom_low: Vertical zoom low value
            spec_prefs: Use general spectral preferences
            spectral_sel: Enable spectral selection
            scheme: Color scheme ("Color (default)", "Color (classic)", "Grayscale", "Inverse Grayscale")
        """
        params = []
        if height is not None:
            params.append(f"Height={height}")
        if display is not None:
            params.append(f"Display={display}")
        if scale is not None:
            params.append(f"Scale={scale}")
        if color is not None:
            params.append(f"Color={color}")
        if vzoom is not None:
            params.append(f"VZoom={vzoom}")
        if vzoom_high is not None:
            params.append(f"VZoomHigh={vzoom_high}")
        if vzoom_low is not None:
            params.append(f"VZoomLow={vzoom_low}")
        if spec_prefs is not None:
            params.append(f"SpecPrefs={1 if spec_prefs else 0}")
        if spectral_sel is not None:
            params.append(f"SpectralSel={1 if spectral_sel else 0}")
        if scheme is not None:
            params.append(f"Scheme='{scheme}'")
        cmd = "SetTrackVisuals:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_track(self, name: Optional[str] = None,
                 selected: Optional[bool] = None,
                 focused: Optional[bool] = None,
                 mute: Optional[bool] = None,
                 solo: Optional[bool] = None,
                 gain: Optional[float] = None,
                 pan: Optional[float] = None,
                 height: Optional[int] = None,
                 display: Optional[str] = None,
                 scale: Optional[str] = None,
                 color: Optional[str] = None) -> str:
        """
        Set multiple track properties at once (legacy command, prefer specific set_track_* methods).
        
        Args:
            name: Track name
            selected: Whether track is selected
            focused: Whether track has focus
            mute: Whether to mute the track
            solo: Whether to solo the track
            gain: Gain level
            pan: Pan position (-1.0 to 1.0)
            height: Track height in pixels
            display: Display type
            scale: Scale type
            color: Color scheme
        """
        params = []
        if name is not None:
            params.append(f"Name='{name}'")
        if selected is not None:
            params.append(f"Selected={1 if selected else 0}")
        if focused is not None:
            params.append(f"Focused={1 if focused else 0}")
        if mute is not None:
            params.append(f"Mute={1 if mute else 0}")
        if solo is not None:
            params.append(f"Solo={1 if solo else 0}")
        if gain is not None:
            params.append(f"Gain={gain}")
        if pan is not None:
            params.append(f"Pan={pan}")
        if height is not None:
            params.append(f"Height={height}")
        if display is not None:
            params.append(f"Display={display}")
        if scale is not None:
            params.append(f"Scale={scale}")
        if color is not None:
            params.append(f"Color={color}")
        cmd = "SetTrack:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_clip(self, at: Optional[float] = None,
                color: Optional[str] = None,
                start: Optional[float] = None) -> str:
        """
        Modify a clip by specifying a time within it.
        
        Args:
            at: Time position within the clip
            color: Color ("Color0", "Color1", "Color2", "Color3")
            start: New start position for the clip
        """
        params = []
        if at is not None:
            params.append(f"At={at}")
        if color is not None:
            params.append(f"Color={color}")
        if start is not None:
            params.append(f"Start={start}")
        cmd = "SetClip:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_envelope(self, time: Optional[float] = None,
                    value: Optional[float] = None,
                    delete: Optional[bool] = None) -> str:
        """
        Modify an envelope point or delete entire envelope.
        
        Args:
            time: Time position of envelope point
            value: Envelope value at that time
            delete: Delete entire envelope if True
        """
        params = []
        if time is not None:
            params.append(f"Time={time}")
        if value is not None:
            params.append(f"Value={value}")
        if delete is not None:
            params.append(f"Delete={1 if delete else 0}")
        cmd = "SetEnvelope:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def set_label(self, label: int = 0,
                 text: Optional[str] = None,
                 start: Optional[float] = None,
                 end: Optional[float] = None,
                 selected: Optional[bool] = None) -> str:
        """
        Modify an existing label.
        
        Args:
            label: Label number (0-based)
            text: Label text
            start: Start time
            end: End time
            selected: Whether label is selected
        """
        params = [f"Label={label}"]
        if text is not None:
            params.append(f"Text='{text}'")
        if start is not None:
            params.append(f"Start={start}")
        if end is not None:
            params.append(f"End={end}")
        if selected is not None:
            params.append(f"Selected={1 if selected else 0}")
        cmd = "SetLabel: " + " ".join(params)
        return self.pipe.do_command(cmd)
    
    def set_project(self, name: Optional[str] = None,
                   rate: Optional[float] = None,
                   x: Optional[int] = None,
                   y: Optional[int] = None,
                   width: Optional[int] = None,
                   height: Optional[int] = None) -> str:
        """
        Set project window properties.
        
        Args:
            name: Project window caption
            rate: Sample rate
            x: Window X position
            y: Window Y position
            width: Window width
            height: Window height
        """
        params = []
        if name is not None:
            params.append(f"Name='{name}'")
        if rate is not None:
            params.append(f"Rate={rate}")
        if x is not None:
            params.append(f"X={x}")
        if y is not None:
            params.append(f"Y={y}")
        if width is not None:
            params.append(f"Width={width}")
        if height is not None:
            params.append(f"Height={height}")
        cmd = "SetProject:" + (" " + " ".join(params) if params else "")
        return self.pipe.do_command(cmd)
    
    def get_preference(self, name: str) -> str:
        """
        Get a single preference setting.
        
        Args:
            name: Preference name
        """
        return self.pipe.do_command(f"GetPreference: Name='{name}'")
    
    def set_preference(self, name: str, value: str, reload: bool = False) -> str:
        """
        Set a single preference setting.
        
        Args:
            name: Preference name
            value: Preference value
            reload: Whether to reload preferences (slow but sometimes necessary)
        """
        cmd = f"SetPreference: Name='{name}' Value='{value}' Reload={1 if reload else 0}"
        return self.pipe.do_command(cmd)
    
    # Basic Effects
    def normalize(self, peak_level: float = -1.0, apply_gain: bool = True,
                 remove_dc: bool = True, stereo_independent: bool = False) -> str:
        """
        Normalize the selected audio.
        
        Args:
            peak_level: Target peak level in dB
            apply_gain: Whether to apply gain adjustment
            remove_dc: Whether to remove DC offset
            stereo_independent: Whether to normalize stereo channels independently
        """
        cmd = (f"Normalize: PeakLevel={peak_level} ApplyGain={apply_gain} "
               f"RemoveDcOffset={remove_dc} StereoIndependent={stereo_independent}")
        return self.pipe.do_command(cmd)
    
    def amplify(self, ratio: float) -> str:
        """
        Amplify the selected audio.
        
        Args:
            ratio: Amplification ratio (1.0 = no change, 2.0 = double volume)
        """
        return self.pipe.do_command(f"Amplify: Ratio={ratio}")
    
    def fade_in(self) -> str:
        """Apply a linear fade-in to the selection."""
        return self.pipe.do_command("FadeIn:")
    
    def fade_out(self) -> str:
        """Apply a linear fade-out to the selection."""
        return self.pipe.do_command("FadeOut:")
    
    def reverse(self) -> str:
        """Reverse the selected audio."""
        return self.pipe.do_command("Reverse:")
    
    def invert(self) -> str:
        """Invert the selected audio (flip waveform)."""
        return self.pipe.do_command("Invert:")
    
    # Advanced Effects
    def compressor(self, threshold: float = -12.0, noise_floor: float = -40.0,
                  ratio: float = 2.0, attack_time: float = 0.2,
                  release_time: float = 1.0, normalize: bool = True) -> str:
        """
        Apply compression to the selected audio.
        
        Args:
            threshold: Compression threshold in dB
            noise_floor: Noise floor level in dB
            ratio: Compression ratio
            attack_time: Attack time in seconds
            release_time: Release time in seconds
            normalize: Whether to normalize after compression
        """
        cmd = (f"Compressor: Threshold={threshold} NoiseFloor={noise_floor} "
               f"Ratio={ratio} AttackTime={attack_time} ReleaseTime={release_time} "
               f"Normalize={normalize}")
        return self.pipe.do_command(cmd)
    
    def noise_reduction(self) -> str:
        """
        Apply noise reduction to the selected audio.
        Note: This requires a noise profile to be captured first.
        """
        return self.pipe.do_command("NoiseReduction:")
    
    def reverb(self, room_size: float = 75.0, delay: float = 10.0,
              reverberance: float = 50.0, hf_damping: float = 50.0,
              wet_gain: float = -1.0, dry_gain: float = -1.0) -> str:
        """
        Apply reverb to the selected audio.
        
        Args:
            room_size: Room size percentage
            delay: Initial delay in ms
            reverberance: Reverberance percentage
            hf_damping: High frequency damping percentage
            wet_gain: Wet signal gain in dB
            dry_gain: Dry signal gain in dB
        """
        cmd = (f"Reverb: RoomSize={room_size} Delay={delay} "
               f"Reverberance={reverberance} HfDamping={hf_damping} "
               f"WetGain={wet_gain} DryGain={dry_gain}")
        return self.pipe.do_command(cmd)
    
    # Track Operations
    def new_mono_track(self) -> str:
        """Create a new mono audio track."""
        return self.pipe.do_command("NewMonoTrack:")
    
    def new_stereo_track(self) -> str:
        """Create a new stereo audio track."""
        return self.pipe.do_command("NewStereoTrack:")
    
    def new_label_track(self) -> str:
        """Create a new label track."""
        return self.pipe.do_command("NewLabelTrack:")
    
    def remove_tracks(self) -> str:
        """Remove the selected tracks."""
        return self.pipe.do_command("RemoveTracks:")
    
    # Edit Operations
    def copy(self) -> str:
        """Copy the selected audio to clipboard."""
        return self.pipe.do_command("Copy:")
    
    def paste(self) -> str:
        """Paste audio from clipboard."""
        return self.pipe.do_command("Paste:")
    
    def cut(self) -> str:
        """Cut the selected audio to clipboard."""
        return self.pipe.do_command("Cut:")
    
    def delete(self) -> str:
        """Delete the selected audio."""
        return self.pipe.do_command("Delete:")
    
    def duplicate(self) -> str:
        """Duplicate the selected audio."""
        return self.pipe.do_command("Duplicate:")
    
    def split(self) -> str:
        """Split the selected audio at the cursor position."""
        return self.pipe.do_command("Split:")
    
    def mix_and_render(self) -> str:
        """Mix selected tracks down to a single track."""
        return self.pipe.do_command("MixAndRender:")
    
    def mix_and_render_to_new_track(self) -> str:
        """Mix selected tracks to a new track (preserves originals)."""
        return self.pipe.do_command("MixAndRenderToNewTrack:")
    
    # Playback and Transport
    def play(self) -> str:
        """Start playback."""
        return self.pipe.do_command("Play:")
    
    def stop(self) -> str:
        """Stop playback/recording."""
        return self.pipe.do_command("Stop:")
    
    def pause(self) -> str:
        """Pause playback/recording."""
        return self.pipe.do_command("Pause:")
    
    def record(self) -> str:
        """Start recording."""
        return self.pipe.do_command("Record1stChoice:")
    
    # Analysis
    def get_info(self, info_type: str = "Tracks", format_type: str = "JSON") -> str:
        """
        Get information about the project.
        
        Args:
            info_type: Type of info ("Commands", "Tracks", "Clips", etc.)
            format_type: Format ("JSON", "LISP", "Brief")
        """
        cmd = f"GetInfo: Type={info_type}"
        return self.pipe.do_command(cmd)
    
    def plot_spectrum(self) -> str:
        """Open the Plot Spectrum analyzer."""
        return self.pipe.do_command("PlotSpectrum:")
    
    def contrast_analyser(self) -> str:
        """Open the Contrast Analyser."""
        return self.pipe.do_command("ContrastAnalyser:")
    
    # Utility Methods
    def help(self, command: str = "Help") -> str:
        """
        Get help information.
        
        Args:
            command: Specific command to get help for
        """
        return self.pipe.do_command(f"Help: Command={command}")
    
    def screenshot(self, path: str = "", capture_what: str = "Window",
                  background: str = "None") -> str:
        """
        Take a screenshot of Audacity.
        
        Args:
            path: Path to save screenshot
            capture_what: What to capture ("Window", "Fullscreen", etc.)
            background: Background color ("None", "Blue", "White")
        """
        cmd = f"Screenshot: Path={path} CaptureWhat={capture_what} Background={background}"
        return self.pipe.do_command(cmd)