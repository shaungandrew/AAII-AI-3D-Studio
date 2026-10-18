# AAII AI 3D Studio V1.2

Windows local browser-based 3D studio: extract video front/left/back/right frames, generate a coarse non-AI silhouette mesh from transparent views, integrate an external multi-view AI command, and export a scaled GLB for Roblox Studio.

## Windows EXE
On GitHub, open **Actions → Build AAII AI 3D Studio Windows EXE**. The workflow runs on Windows and uploads the executable ZIP if packaging succeeds. Extract the entire ZIP and double-click `AAII_AI_3D_Studio.exe`. The application opens a local browser window. An actual native-Windows build has not been verified yet.

## Important limitations
- Multi-view AI is **not included**. Set `AAII_MULTIVIEW_COMMAND` to an installed, trusted model backend with `{front} {left} {back} {output}` placeholders.
- Silhouette preview is **not AI** and requires transparent PNGs.
- GLB export is scaled but does not include avatar rigging or animation.
- Python 3.10 recommended for building locally.

Source build command: `build_windows.bat`.
