# Build a distributable app (Windows .exe)

This project includes a desktop launcher command: `zotify-app`.

If you want a single installable executable for Windows:

1. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install pyinstaller
   ```
2. Build the executable from the repo root:
   ```powershell
   pyinstaller --name ZotifyDesktop --onefile --windowed -m zotify.gui
   ```
3. The generated executable will be at:
   - `dist/ZotifyDesktop.exe`

## Notes
- You still need ffmpeg available on the machine.
- First launch may trigger Windows SmartScreen for unsigned executables.

## No-command option for end users

Repository maintainers can run the **Build Windows App** GitHub Action and share the generated artifact (`ZotifyDesktop-Windows`) so users only download and open `ZotifyDesktop.exe`.
