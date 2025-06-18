@echo off
echo Starting Zara Assistant build process...

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or later.
    exit /b 1
)

REM Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install requirements
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Create necessary directories
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Ensure data directories exist
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "config" mkdir config
if not exist "logs" mkdir logs

REM Copy necessary files
echo Copying resource files...
xcopy /E /I /Y "models" "dist\models"
xcopy /E /I /Y "config" "dist\config"
xcopy /E /I /Y "MobileNetSSD_deploy.prototxt" "dist"

REM Create spec file
echo Creating PyInstaller spec file...
echo from PyInstaller.utils.hooks import collect_data_files > zara.spec
echo # -*- mode: python -*- >> zara.spec
echo block_cipher = None >> zara.spec
echo a = Analysis(['zara\\__main__.py'], >> zara.spec
echo     pathex=['%CD%'], >> zara.spec
echo     binaries=[], >> zara.spec
echo     datas=[ >> zara.spec
echo         ('models/*', 'models'), >> zara.spec
echo         ('config/*', 'config'), >> zara.spec
echo         ('MobileNetSSD_deploy.prototxt', '.'), >> zara.spec
echo     ], >> zara.spec
echo     hiddenimports=['pyttsx3.drivers', 'pyttsx3.drivers.sapi5'], >> zara.spec
echo     hookspath=[], >> zara.spec
echo     runtime_hooks=[], >> zara.spec
echo     excludes=[], >> zara.spec
echo     win_no_prefer_redirects=False, >> zara.spec
echo     win_private_assemblies=False, >> zara.spec
echo     cipher=block_cipher, >> zara.spec
echo     noarchive=False >> zara.spec
echo ) >> zara.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> zara.spec
echo exe = EXE(pyz, >> zara.spec
echo     a.scripts, >> zara.spec
echo     a.binaries, >> zara.spec
echo     a.zipfiles, >> zara.spec
echo     a.datas, >> zara.spec
echo     [], >> zara.spec
echo     name='Zara Assistant', >> zara.spec
echo     debug=False, >> zara.spec
echo     bootloader_ignore_signals=False, >> zara.spec
echo     strip=False, >> zara.spec
echo     upx=True, >> zara.spec
echo     upx_exclude=[], >> zara.spec
echo     runtime_tmpdir=None, >> zara.spec
echo     console=False, >> zara.spec
echo     disable_windowed_traceback=False, >> zara.spec
echo     target_arch=None, >> zara.spec
echo     codesign_identity=None, >> zara.spec
echo     entitlements_file=None, >> zara.spec
echo     icon='resources\\icon.ico' >> zara.spec
echo ) >> zara.spec

REM Run PyInstaller
echo Building executable...
pyinstaller --clean --win-private-assemblies -y zara.spec

REM Copy additional runtime files
echo Copying runtime files...
xcopy /E /I /Y "dist\models" "dist\Zara Assistant\models"
xcopy /E /I /Y "dist\config" "dist\Zara Assistant\config"
copy "MobileNetSSD_deploy.prototxt" "dist\Zara Assistant"

echo Build complete! Executable is in dist\Zara Assistant folder.
echo Remember to:
echo 1. Install Ollama from https://ollama.ai/download
echo 2. Run 'ollama pull llama2' to download the language model
echo 3. Start Ollama service before running Zara

REM Deactivate virtual environment
deactivate

pause