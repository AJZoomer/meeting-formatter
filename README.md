# Meeting Formatter
![GitHub release (latest by date)](https://img.shields.io/github/v/release/AJZoomer/meeting-formatter)

Meeting Formatter is a small desktop tool that cleans up messy meeting notes and turns them into something readable. It runs locally, doesn’t send anything anywhere, and is basically just a quick way to tidy up agendas, minutes, brainstorm dumps, or whatever else you throw at it.

## Features

- Cleans spacing, indentation, and stray blank lines
- Normalises bullet points
- Agenda and Minutes modes
- Fully offline
- Simple UI: paste → format → copy
- Can export the formatted output as **.txt**, **.md**, or **.pdf**
- Available as an installer or a portable version

## Installation and Uninstallation

If you're just trying to use the app, download the installer from the Releases page and install it from there. Don’t download the source code unless you're a developer.

Important: **Do not uninstall the app through Windows' “Add or Remove Programs.”**  
Windows won’t remove everything and will leave files behind.  
To uninstall properly, run the installer again and choose the uninstall option. That’s the only method that fully removes the app.

## For Developers vs Users

If you want to look at the code or build the app yourself, you can clone the repo and run everything directly.

If you're just here to use the app, ignore the source code and go straight to the Releases page. The installer is the version meant for normal users.

## Getting Started

### Download
Grab the latest release from the Releases page.

### How to Use
1. Paste your notes into the left panel  
2. Pick your formatting options  
3. Hit “Format”  
4. Copy the output from the right panel or export it as a file  

## Tech Stack

- Python  
- PyInstaller  
- HTML/CSS UI  
- Custom formatting logic  

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Feedback

If you find a bug or want something added, open an issue.

