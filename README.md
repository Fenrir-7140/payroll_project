# Payroll Engine Python & SQLAlchemy

Moteur de calcul de paie universel avec gestion de règles dynamiques.

## Installation
1. Cloner le dépôt
2. Créer et activer l'environnement virtuel (venv) :
   * **Sur Windows :**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
   * **Sur Mac:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
3. `pip install -r requirements.txt`
4. Configurer le fichier `.env` avec votre accès PostgreSQL
    ```
   DATABASE_URL=postgresql://login:pass@localhost:5432/db_name
   

## Lancement

`streamlit run ui/Dashboard.py`