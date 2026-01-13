# 📦 SmartInventory Pro - Felhő Alapú Raktárkezelő Rendszer

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)

Ez a projekt egy teljes körű, üzleti igényekre szabott raktárkészlet-nyilvántartó alkalmazás. Ideális megoldás kis- és középvállalkozások számára, amelyek szeretnék digitálisan, bárhonnan elérhető módon kezelni készleteiket.

## 🚀 Főbb funkciók és Üzleti megoldások
A fejlesztés során a stabilitást és az egyszerű kezelhetőséget tartottam szem előtt:

- **Dinamikus készletkezelés:** Termékek kategóriák szerinti rendszerezése és valós idejű módosítása.
- **Kritikus szint figyelmeztetés:** Automatikus vizuális visszajelzés (⚠️), ha egy termék mennyisége a beállított minimum alá süllyed.
- **Szerepkör alapú jogosultság:** Külön adminisztrátori felület az új termékek és kategóriák felvételéhez.
- **Eseménynapló:** A rendszer minden raktári mozgást (hozzáadás, szerkesztés, törlés) rögzít, így az utólag visszakövethető.
- **Adatexport:** Havi jelentések generálása Excel-kompatibilis CSV formátumban.
- **Mobil-first szemlélet:** Teljesen reszponzív design, amely tableten és okostelefonon is kényelmes munkavégzést biztosít.

## 🛠 Technológiai Stack
- **Backend:** Python (Flask keretrendszer)
- **Frontend:** HTML5, CSS3 (Egyedi Flexbox és Grid elrendezés)
- **Adatbázis:** SQLite3 (Könnyű hordozhatóság és gyors válaszidő)
- **Környezet:** PythonAnywhere kompatibilis felépítés

## 💻 Telepítés és Futtatás
Ha szeretnéd kipróbálni a projektet helyi környezetben:

1. Klónozd a tárolót:
   ```bash
   git clone [https://github.com/FELHASZNALONEVED/referencia_raktar.git](https://github.com/FELHASZNALONEVED/referencia_raktar.git)

2. Hozz létre egy virtuális környezetet és aktiváld:
    ```bash
    python -m venv venv
    venv\Scripts\activate

3. Telepítsd a függőségeket:
    ```bash
    pip install -r requirements.txt

4. Indítsd el az alkalmazást:
    ```bash
    python app.py

Fejlesztette: Melkvi Tibor