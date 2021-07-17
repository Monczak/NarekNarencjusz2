@echo off

echo Building!

echo Removing current build
rmdir dist /s /q

echo Building with pyinstaller
pyinstaller main.py --name NarekNarencjusz2 --onefile --additional-hooks-dir extra-hooks

echo Copying Opus DLLs
copy venv\Lib\site-packages\discord\bin\libopus-0.x64.dll dist\libopus-0.x64.dll
copy venv\Lib\site-packages\discord\bin\libopus-0.x86.dll dist\libopus-0.x86.dll

echo Creating config
mkdir dist\config
copy config\config.json dist\config\config.json

echo --- You will need to provide a token file (named "token", with no extension) in the config folder which contains your bot token for the bot to run ---

echo Done!