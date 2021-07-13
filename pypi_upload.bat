echo off
:Ask
echo Did you update the version?(y/n)
set ANSWER=
set /P ANSWER=Type input: %=%
If /I "%ANSWER%"=="y" goto Ask2
If /I "%ANSWER%"=="n" goto no
echo Incorrect input & goto Ask

:Ask2
echo Did you run the unit tests?(y/n)
set ANSWER=
set /P ANSWER=Type input: %=%
If /I "%ANSWER%"=="y" goto yes
If /I "%ANSWER%"=="n" goto no
echo Incorrect input & goto Ask2
:yes
del /Q dist\*.*
python setup.py sdist bdist_wheel
twine upload dist/*
:no
