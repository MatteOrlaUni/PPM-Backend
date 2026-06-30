# PPM - Secondo parziale

**Studente:** Orlandi Matteo

## Project Information
- **Tipologia progetto:** Full-Stack Web Application, traccia 4: Servizio di musica in streaming
- **Framework utilizzato:** Django

## Descrizione
Questa applicazione permette agli utenti di esplorare brani musicali, visualizzare artisti e generi, creare le proprie playlist personalizzate e gestire il proprio profilo.

## Ruoli

**Listener (utente comune):**
- **Navigazione:** Accesso libero alla Home page e a tutto il catalogo musicale.
- **Ricerca e Filtri:** Ricerca testuale dinamica per Brani, Artisti, Generi e Utenti.
- **Playlist:** Creazione, visualizzazione, modifica del nome e cancellazione delle proprie playlist. Aggiunta e rimozione di brani.
- **Profilo:** Modifica delle proprie credenziali (username e password) ed eliminazione del proprio account.

**Curator (amministratore):**
- Tutte le funzionalità e i privilegi concessi al Listener.
- **Gestione Catalogo (CRUD):** Aggiunta, modifica ed eliminazione di brani musicali, generi e artisti.
- **Gestione Utenti:** Modifica e cancellazione degli account altrui.
- **Pannello Admin:** Accesso totale al sistema e alla supervisione del database.

## Local Installation Instructions

Per testare questo progetto localmente, seguire i seguenti passaggi nel terminale:

1. **Clonare la repository:**
   ```bash
   git clone https://github.com/MatteOrlaUni/PPM-Backend
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

4. **Avviare il server:**
   *(Nota: Il database è già popolato, quindi non è necessario eseguire le migrazioni)*
   ```bash
   python manage.py runserver
   ```
   Visitare `http://127.0.0.1:8000/` nel browser.

## Database
Il progetto include il file `db.sqlite3` pre-popolato in root.

## Demo Accounts
Account per il testing:

- **amministratore:** utente1 / password1
- **utente comune:** utente2 / password2

## Scenario di test

Di seguito sono descritte le operazioni consentite in base allo stato di autenticazione e al ruolo dell'utente:

1. **Utente Non Autenticato (Anonimo)**
   - **Funzioni utilizzabili:** Può esclusivamente visualizzare la pagina di login/registrazione e visitare il catalogo. Per la gestione delle playlist è necessario almeno un account base.

2. **Utente loggato come "utente comune" (Listener)**
   - **Collegamenti visibili:** Home, Catalogo, Le mie Playlist, Profilo e Logout.
   - **Funzioni utilizzabili:** 
     - Sfogliare l'intero catalogo musicale (brani, artisti, generi) e ricercare elementi tramite la barra di ricerca.
     - Creare, rinominare ed eliminare le proprie playlist personali.
     - Aggiungere e rimuovere brani dalle proprie playlist.
     - Modificare i dati del proprio profilo (username, password) ed eliminare l'account.

3. **Utente loggato come "amministratore" (Curator)**
   - **Collegamenti visibili:** Tutti i collegamenti dell'utente comune, con l'aggiunta della sezione "Utenti" e delle operazioni CRUD di ogni elemento del catalogo.
   - **Funzioni utilizzabili:**
     - Tutte le funzioni concesse all'utente comune.
     - **CRUD Catalogo:** Aggiungere nuovi brani, artisti e generi tramite form. Modificare il nome, il genere o l'artista di brani esistenti. Eliminare definitivamente elementi dal database.
     - **Gestione Utenti:** Cercare e visualizzare profili di altri utenti nella scheda "Utenti" del catalogo. Eliminare e modificare le informazioni di una account di un qualsiasi utente.
     - **Limitazioni:** Non può modificare o eliminare le playlist altrui.

## Online Deployment
- **Deployment URL:** https://matteorlauni.pythonanywhere.com

