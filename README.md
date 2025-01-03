Mapas WRC
=========

Cómo crear un `.exe` de forma local. Una vez clonado el repositorio se han de ejecutar los siguientes comandos para crear un entorno virtual, instalar las dependencias y empaquetar todo como un `.exe`, que aparecerá en `./dist/mapasWRC.exe`.

```
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m PyInstaller --windowed --onefile --hidden-import fiona._shim --add-data "./resources/icon.ico:./resources/" --icon "./resources/icon.ico" .\src\mapasWRC.py
```