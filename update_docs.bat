cd tests\syntax

call ..\..\venv-friendly-traceback-3.6\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly-traceback-3.7\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly-traceback-3.8\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly-traceback-3.9\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly-traceback-3.10\scripts\activate
call python compile_data.py
call deactivate

call ..\..\venv-friendly-traceback-3.11\scripts\activate
call python compile_data.py
call deactivate

call python compare_data.py
copy compare_data.html ..\..\..\friendly-docs\source\compare_data.html
del compare_data.html

cd ..

call ..\venv-friendly-traceback-3.6\scripts\activate
call python trb_english.py
call python trb_syntax_english.py
call python what.py
call deactivate

call ..\venv-friendly-traceback-3.7\scripts\activate
call python trb_english.py
call python trb_syntax_english.py
call deactivate

call ..\venv-friendly-traceback-3.8\scripts\activate
call python trb_english.py
call python trb_syntax_english.py
call deactivate

call ..\venv-friendly-traceback-3.9\scripts\activate
call python trb_english.py
call python trb_syntax_english.py
call deactivate

call ..\venv-friendly-traceback-3.10\scripts\activate
call python trb_english.py
call python trb_french.py
call python trb_hebrew.py
call python trb_italian.py
call python trb_russian.py
call python trb_spanish.py
call python trb_tamil.py
call python trb_syntax_english.py
call python trb_syntax_french.py
call python trb_syntax_hebrew.py
call python trb_syntax_italian.py
call python trb_syntax_russian.py
call python trb_syntax_spanish.py
call python trb_syntax_tamil.py
call deactivate

call ..\venv-friendly-traceback-3.11\scripts\activate
call python trb_english.py
call python trb_syntax_english.py
call deactivate

call python compare_messages.py
copy compare_messages.html ..\..\docs\source\compare_messages.html
del compare_messages.html

cd ..\..\friendly-docs
call make html
cd ..\friendly-traceback
call venv-friendly-traceback-3.10\scripts\activate
