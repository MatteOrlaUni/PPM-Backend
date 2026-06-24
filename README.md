# Sonify - Music Streaming Service

**Studente:** Matteo (Modificare con i nomi effettivi se gruppo)

## Project Information
- **Chosen project type:** Full-Stack Web Application (Track 4: Music Streaming Service)
- **Framework used:** Django

## Short Description
Sonify è un'applicazione web full-stack per la gestione di un catalogo musicale in streaming. Permette agli utenti di esplorare brani musicali, visualizzare i generi disponibili, e ai curatori di gestire l'aggiunta di nuove tracce audio al sistema, simulando un vero e proprio servizio di Music Streaming.

## Implemented Features
L'applicazione implementa un sistema di permessi basato sui ruoli tramite un modello `CustomUser`.

**Listener (Standard User):**
- Navigazione libera della Home page e del catalogo musicale completo.
- Visualizzazione dei dettagli delle singole tracce (Titolo, Artista, Genere, Durata).
- Reindirizzamento e ascolto tramite link esterni (simulazione streaming).

**Curator (Manager/Admin):**
- Tutte le funzionalità del Listener.
- Aggiunta di nuovi brani al catalogo tramite form protetti (CreateView).
- Gestione esclusiva delle entità del database.

## Local Installation Instructions

Per eseguire questo progetto localmente sulla propria macchina, seguire questi passaggi:

1. **Clonare la repository:**
   ```bash
   git clone <INSERIRE_IL_LINK_DELLA_REPO>
   cd PPM-Backend
   ```

2. **Creare e attivare il Virtual Environment:**
   *Su Windows:*
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
   *Su macOS/Linux:*
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installare le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Avviare il server (Il database è già configurato e popolato):**
   ```bash
   python manage.py runserver
   ```
   Visitare `http://127.0.0.1:8000/` nel browser.

## Database
Il progetto include il file `db.sqlite3` pre-popolato. 
Confermo che il database contiene dati demo realistici (generi, canzoni, playlist) sufficienti per testare immediatamente tutti i workflow principali del progetto senza dover creare nulla da zero.

## Demo Accounts
Di seguito sono elencati gli account di prova per testare le funzionalità e i permessi dell'applicazione:

- **Admin/Superuser**
  - Username: `admin_demo`
  - Password: `admin12345`
  - Role: Amministratore di sistema (Accesso totale)

- **Curator**
  - Username: `manager_demo`
  - Password: `manager12345`
  - Role: Curator (Può aggiungere e gestire canzoni)

- **Listener**
  - Username: `user_demo`
  - Password: `user12345`
  - Role: Listener (Accesso in sola lettura al catalogo)

## Online Deployment
- **Deployment URL:** [INSERIRE_LINK_DEPLOYMENT] (Es. Render, PythonAnywhere, Railway)

---
*Progetto sviluppato per il corso di Back-end PPM 2026.*
