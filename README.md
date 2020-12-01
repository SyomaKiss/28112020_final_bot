# Анализ текста для кейса МВД
## Запуск решения
```
cd service/mvd
docker build . --tag mvd:1.0 
docker run --publish 8501:8501 --detach --name mvd mvd:1.0
```
## Запуск макроса
```
cd service/mvd
export FLASK_APP=flask_app.py; export FLASK_ENV=development; export FLASK_DEBUG=0; python -m flask run

cp macros1.py /Applications/LibreOffice.app/Contents/Resources/Scripts/python/
cp transform_w_highlights.py /Applications/LibreOffice.app/Contents/Resources/Scripts/python/
```
Where the path /Applications/LibreOffice.app/Contents/Resources/Scripts/python/ is platform dependent. Here is an example for MacOS

## Создание локальной версии, без необходимости интернета
Добавьте следующий код в файл cli.py, находящийся в локальной папке streamlit (`${YOUR_CONDA_ENV}/lib/site-packages/streamlit/cli.py`)  
**[cli.py]**
```python
def _main_run_clExplicit(file, command_line, args=[ ]):
    streamlit._is_running_with_streamlit = True
    bootstrap.run(file, command_line, args)
```
Запустить скрипт 
```
pyinstaller --onefile --additional-hooks-dir=./hooks run_main.py --clean
```
Отредактировать файл и добавить следущие строки:  
[run_main.spec]
```
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['run_main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 (
                     "{$YOURPYTHONENV}/Lib/site-packages/altair/vegalite/v4/schema/vega-lite-schema.json",
                     "./altair/vegalite/v4/schema/"
                 ),
                 (
                     "${YOURPYTHONENV}/Lib/site-packages/streamlit/static",
                     "./streamlit/static"
                 )
            ],
            ...,
            noarchive=False)
pyz = PYZ(...)
exe = EXE(...)
```
Запустить
```
pyinstaller --onefile --additional-hooks-dir=./hooks run_main.spec --clean
```
Скопировать `.streamlit` и все `.py` файлы в директорию `dist` 
 
Для создания executable для другой платформы, требуется запустить тот же код, на этой платформе


