cd tests

call ..\venv-friendly-traceback-3.8\scripts\activate
call python trb_english.py
call  python trb_syntax_english.py
call  deactivate

cd ..\..\friendly-traceback-docs\docs
call make html
cd ..\..\friendly
call venv-friendly-traceback-3.8\scripts\activate
