@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building EXE...
pyinstaller comic-utils.spec

echo Done!
echo Executable is in the dist folder.
pause
