# Reconciliation Analysis

## Instructions to Run
A live deployed version of the application can be found on
https://reconciliation-analysis.onrender.com/

Alternatively, the app can also be run locally using the following commands.

`git clone https://github.com/sprihaapandey/reconciliation-analysis.git`

`python3 webapp/server.py` 

Access the web app at http://127.0.0.1:5050

### Limitations
The uploaded files must be .csv. Similar to the brief, the transactions csv should have `date` and `amount` columns and the balance csv should have `date` and `balance` columns.

## Project Structure

`transcript.md` has the transcripts from the conversations with Claude Code. **The core logic and the tests were written manually, and the web app was the only component developed using an LLM, in order to be able to complete the task within 90 minutes** 

`screenshots` contains relevant screenshots of the web app

`tests` contains .csv files that were used for testing 

`webapp` contains the .js, .html, and .css files used for the frontend as well as the web server in server.py 

`reconcile.py` contains the core logic for the app 

`requirements.txt` was necessary for deployment on render, but is currently empty since there are no dependencies 