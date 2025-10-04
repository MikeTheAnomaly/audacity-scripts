# Audacity Python Scripts

Simple Python scripts to automate Audacity through the mod-script-pipe module.

## Important
Make sure audacity is running with the mod-script-pipe module enabled before running any scripts.


## Quick Setup

### 1. Enable scripting in Audacity
1. Open Audacity
2. Go to **Edit → Preferences → Modules**
3. Find **"mod-script-pipe"** and change it to **"Enabled"**
4. **Restart Audacity**

### 2. Test the connection
```bash
python test_pipe.py
```

### 3. Run a tracks example
```bash
python export_tracks_individually.py
```

## How to Use

1. **Make sure Audacity is running** with mod-script-pipe enabled
2. **Run the test**: `python test_pipe.py`
3. **Try the example**: `python export_tracks_individually.py`

## Basic Commands

```python
from audacity_pipe import AudacityPipe

with AudacityPipe() as audacity:
    audacity.do_command("Import2: Filename='your_audio.wav'")
    audacity.do_command("SelectAll:")
    audacity.do_command("Normalize:")
    audacity.do_command("Export2: Filename='output.wav'")

```

## More Info
- [Full command list](https://manual.audacityteam.org/man/scripting_reference.html)