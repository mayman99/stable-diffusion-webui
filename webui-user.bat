@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--xformers --listen --api --no-download-sd-model --skip-version-check

call webui.bat
