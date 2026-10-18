@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (echo Python Launcher missing & exit /b 1)
py -3.10 -m venv .venv
if errorlevel 1 goto failed
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements-app.txt "pyinstaller>=6.6,<7"
if errorlevel 1 goto failed
python -m PyInstaller --noconfirm --clean --onedir --name AAII_AI_3D_Studio --collect-all gradio --collect-all gradio_client --collect-all skimage --collect-all trimesh --collect-all PIL --collect-all cv2 --hidden-import=gradio.routes --hidden-import=gradio.blocks --hidden-import=gradio.components --hidden-import=gradio.themes --hidden-import=gradio.utils --hidden-import=fastapi --hidden-import=uvicorn --hidden-import=starlette --hidden-import=anyio --hidden-import=websockets --add-data "app.py;." --add-data "core.py;." launcher.py
if errorlevel 1 goto failed
copy /Y README.md dist\AAII_AI_3D_Studio\README.md >nul
powershell -NoProfile -Command "Compress-Archive -Path 'dist\AAII_AI_3D_Studio\*' -DestinationPath 'AAII_AI_3D_Studio_V1_2_Windows_EXE.zip' -Force"
if errorlevel 1 goto failed
echo Done
exit /b 0
:failed
echo Build failed.
exit /b 1
