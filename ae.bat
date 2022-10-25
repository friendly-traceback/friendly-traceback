echo off
REM Default is Python 3.9

if "%1"=="3.6" goto py_36
if "%1"=="3.7" goto py_37
if "%1"=="3.8" goto py_38
if "%1"=="3.10" goto py_310
if "%1"=="3.11" goto py_311
if "%1"=="3.12" goto py_312
goto py_310


:py_36
venv-friendly-traceback-3.6\scripts\activate
goto end

:py_37
venv-friendly-traceback-3.7\scripts\activate
goto end

:py_38
venv-friendly-traceback-3.8\scripts\activate
goto end

:py_39
venv-friendly-traceback-3.9\scripts\activate
goto end

:py_310
venv-friendly-traceback-3.10\scripts\activate
goto end

:py_311
venv-friendly-traceback-3.11\scripts\activate
goto end

:py_312
venv-friendly-traceback-3.12\scripts\activate
goto end

:end
