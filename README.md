# Audacity Python Scripts

Simple Python scripts to automate Audacity through the mod-script-pipe module.

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

### 3. Run a simple example
```bash
python examples\simple_example.py
```

## That's it!

## How to Use

1. **Make sure Audacity is running** with mod-script-pipe enabled
2. **Run the test**: `python test_pipe.py`
3. **Try the example**: `python examples\simple_example.py`

## Basic Commands

```python
from audacity_pipe import AudacityPipe

with AudacityPipe() as audacity:
    audacity.do_command("Import2: Filename='your_audio.wav'")
    audacity.do_command("SelectAll:")
    audacity.do_command("Normalize:")
    audacity.do_command("Export2: Filename='output.wav'")
```

## Common Commands
- `Import2: Filename='file.wav'` - Import audio
- `SelectAll:` - Select all audio  
- `Normalize:` - Normalize volume
- `Amplify: Ratio=1.5` - Change volume
- `Export2: Filename='output.wav'` - Export audio

## More Info
- [Full command list](https://manual.audacityteam.org/man/scripting_reference.html)
- Check `examples\simple_example.py` for a basic template