
call venv-friendly-traceback-3.8\scripts\activate
cd tests
call python trb_english.py
call python trb_syntax_english.py
call deactivate

cd ..\..\friendly-docs
call make html
cd ..\friendly-traceback
call venv-friendly-traceback-3.9\scripts\activate
