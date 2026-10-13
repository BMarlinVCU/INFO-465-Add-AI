# INFO-465-Lesson-7
# Putting Your App into Production

Up to now your Streamlit app has run on your own laptop or in your Codespace. This week we put it on the internet so that anyone with the link can open it. This README covers what changes when an app moves from your machine to a server, and the few things your repo needs before that will work.

## What "putting work into production" means

Production is the version of your app that real people use. When you ran `streamlit run app.py` in VS Code, the app lived on your computer and only you could see it. When the app is in production, it runs on someone else's computer (a server), it has a public web address, and it stays up when your laptop is closed.

The important change is that the server does not have anything you did by hand. It does not have the packages you installed, the database you built, or the files sitting in your folder that you never committed. It only has what is on `main` in your GitHub repo. If your app needs something to run, that thing has to be in the repo or the app has to create it itself.

This is also why "done means it runs from main." Your deployed app is built from the `main` branch. Work that is still on a feature branch is not in the app, no matter how well it runs on your laptop.

## Why our database is not saved in the repo

`project.db` is listed in `.gitignore`, so it is never committed and it does not exist on the server. This is on purpose.

The files in `data/` are the source. They are the raw snapshots we collected from the API, and they cannot be recreated if they are lost, so they are committed. The database is derived from those files. `build_db.py` reads every snapshot and builds `project.db` from scratch, so we can always make a fresh copy whenever we need one.

Keeping the database out of the repo has a few benefits. A database is a binary file, so Git cannot show you what changed inside it, and two people who rebuild it at the same time would create a merge conflict nobody can read. It would also go out of date the moment someone added a new snapshot. Rebuilding it from the snapshots means the database always matches the data.

The cost is that the server starts with no database at all. On your laptop the app works because you ran `build_db.py` at some point and the file is still sitting there. On the server nobody runs anything by hand, so the app has to build its own database when it starts. If it does not, you will see a file-not-found error or an empty table. The section on `app.py` below shows how to fix this.

## What `requirements.txt` is

`requirements.txt` is a plain text file that lists the third-party packages your app needs. When the server builds your app, it reads this file and installs everything in it. If a package is missing from the list, the server will not install it, and your app will crash when it tries to import it.

Our `requirements.txt` contains these five packages:

```
pandas
matplotlib
plotly
streamlit
requests
```

Streamlit has to be in the list even though the server is running a Streamlit app. The server does not add it for you.

`sqlite3` is not in the list, and it should not be. It is part of the Python standard library, which means it comes with Python already. Putting it in `requirements.txt` makes the install fail, because there is no package by that name to download. The general rule is that you list packages you had to install with `pip`, and you leave out anything that came with Python (such as `sqlite3`, `json`, and `pathlib`).

## Why other files have to be callable from `app.py`

When Streamlit runs your app, it runs exactly one file, which is `app.py`. It does not run `build_db.py`, `fetch.py`, or any other file on its own. If `app.py` needs work from another file, `app.py` has to import that file and call it.

Right now `build_db.py` is written as a script. Its code sits at the top level of the file and runs from top to bottom when you type `py build_db.py`. To make it usable from `app.py`, we put that code inside a function and add a guard at the bottom:

```python
# build_db.py
import json
import sqlite3
from pathlib import Path

def build_db(db_path="project.db"):
    conn = sqlite3.connect(db_path)
    # ... the code that was already in this file goes here ...
    conn.close()

if __name__ == "__main__":
    build_db()
    print("Rebuilt project.db")
```

The function lets `app.py` call `build_db()` whenever it needs to. The `if __name__ == "__main__":` line means the code underneath it only runs when you run the file directly. You can still type `py build_db.py` and it works the same way it always did, but importing the file from `app.py` will not set anything off by accident.

Then `app.py` imports the function and calls it at startup:

```python
# app.py
import streamlit as st
from build_db import build_db

@st.cache_resource
def setup():
    build_db()

setup()

# ... the rest of your app ...
```

Streamlit reruns all of `app.py` every time someone clicks a filter or moves a slider. Without `@st.cache_resource`, the app would rebuild the whole database on every click. With it, Streamlit runs `setup()` once when the app starts and skips it after that.

The same idea applies to any other file your app depends on. If your charts live in `chart.py` or your queries live in `analyze.py`, put the work in functions and import them into `app.py` rather than copying the code over.

## What Streamlit Community Cloud is

Streamlit Community Cloud, at [share.streamlit.io](https://share.streamlit.io), is a free hosting service from the company that makes Streamlit. You sign in with your GitHub account, point it at a repo, a branch, and a file, and it builds and runs your app on its servers. It gives your app a public web address that you can share with anyone.

A few things to know about how it works:

**It deploys from a branch you choose.** We always choose `main`. Every time something is pushed or merged to `main`, the app rebuilds itself automatically. You do not have to redeploy or click anything.

**You tell it which file to run.** Our app file is at `src/app.py`, so that is the path we enter as the main file path.

**Set the Python version to 3.12 when you deploy.** This setting is under Advanced settings. The default is a newer version that our packages do not work as well with, and the version cannot be changed after the app is deployed. Fixing it later means deleting the app and deploying it again.

**The logs are where you look when something breaks.** On the running app, open "Manage app" in the bottom right corner. The logs show the install and any errors your code raised.

**Apps go to sleep.** If nobody visits your app for about twelve hours, it shuts down to save resources. The next visitor sees a page with a button to wake it up. This is normal and does not mean your app is broken.

## Common problems

| What you see | What it usually means |
|---|---|
| The install fails during the build | `sqlite3` is in `requirements.txt`, or a package name is misspelled |
| The app loads, then errors on a missing database | `app.py` is not calling `build_db()` at startup |
| The app loads with no data | Snapshots in `data/` were never committed, or they are on a branch and not on `main` |
| The app does not show your latest change | The change is not merged to `main` yet |
| Package errors on an app that works on your laptop | The Python version was left at the default instead of 3.12 |
