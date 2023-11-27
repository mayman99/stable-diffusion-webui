@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--port 3000 --xformers --listen --api --no-download-sd-model --skip-version-check --share

call webui.bat
