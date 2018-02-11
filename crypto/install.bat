REM Python 3.6 64bit is required!
set PYTHON=c:/tools/Python36

IF EXIST ".venv" (
    rmdir /q /s .venv
)

%PYTHON%/python.exe -m venv .venv

IF NOT EXIST ".venv" (
	echo Python virtual environment faild to create.
	pause
	exit 1
)

call .venv\scripts\activate.bat
pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip
pip install -r requirements.txt
