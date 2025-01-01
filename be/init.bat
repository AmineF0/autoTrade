:: Define variables
set ENV_NAME=env
set REQUIREMENTS=requirements.txt

:: Check for Python installation
echo Checking for Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

:: Create a virtual environment
echo Creating virtual environment "%ENV_NAME%"...
python -m venv %ENV_NAME%
if errorlevel 1 (
    echo Failed to create a virtual environment. Please check your Python installation.
    pause
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment...
call "%ENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate the virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
if exist %REQUIREMENTS% (
    echo Installing dependencies from "%REQUIREMENTS%"...
    pip install -r %REQUIREMENTS%
    if errorlevel 1 (
        echo Failed to install dependencies. Please check your requirements file.
        pause
        exit /b 1
    )
) else (
    echo Requirements file "%REQUIREMENTS%" not found.
    pause
    exit /b 1
)


:: Completion message
echo Installation and script execution completed successfully!
pause
exit /b 0
