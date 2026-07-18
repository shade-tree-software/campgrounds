===================================================================
 EKKO Trips — portable USB edition
===================================================================

This stick runs the EKKO Trips web app entirely on its own. It carries its
own copy of Python and every library the app needs, so it works on an
x86_64 Linux Mint machine that has NO Python and NO internet.

-------------------------------------------------------------------
 RUN THE APP (works offline)
-------------------------------------------------------------------
1. Plug the stick in. It mounts under /media/<you>/<something>/.
2. Open a terminal in that folder (in the file manager: right-click >
   "Open in Terminal"), then run:

       ./START-EKKO.sh

3. Your browser opens at  http://localhost:5001  automatically.
   (If it doesn't, open that address yourself.)
4. Log in with your usual EKKO username/password.
5. To stop: press Ctrl+C in this terminal window.

Nothing is installed on the host machine — everything lives on the stick.
Your data (trips, photos, users) is written back to the stick too.

-------------------------------------------------------------------
 RESTORE A BACKUP (works offline)
-------------------------------------------------------------------
Stop the app first (Ctrl+C), then:

       ./restore-backup.sh  /path/to/ekko-backup-YYYYMMDD-HHMMSS.tar.gz

It snapshots the current data first (into app/backup/) so it's reversible,
then extracts the bundle and validates it. Restart with ./START-EKKO.sh.

If your backup also has photos (made with backup.sh --with-photos), they are
restored too.

-------------------------------------------------------------------
 UPDATE THE CODE (needs internet)
-------------------------------------------------------------------
Plug into a machine with internet, then:

       ./update.sh

This pulls the latest app code from GitHub (public repo, no login needed)
and re-syncs any new Python dependencies. Your data is left untouched.

-------------------------------------------------------------------
 REBUILD THE PYTHON ENVIRONMENT (needs internet)
-------------------------------------------------------------------
Only needed if the ./python folder is missing or broken:

       ./build-env.sh          # installs Python + libraries onto the stick
       ./build-env.sh --fresh  # also re-downloads the interpreter

-------------------------------------------------------------------
 WHAT'S ON THE STICK
-------------------------------------------------------------------
  python/                 self-contained CPython 3.12 + all app libraries
  app/                    the EKKO Trips source (a git checkout of the repo)
  app/.env                secrets/config (session key, API tokens) — private
                          (optional; omitted by default — see NOTES)
  requirements-ekko.txt   the Python packages the app needs
  START-EKKO.sh           launch the app in your browser (offline)
  restore-backup.sh       restore an ekko-backup-*.tar.gz bundle (offline)
  update.sh               pull latest code from GitHub (needs internet)
  build-env.sh            (re)build python/ (needs internet)
  README.txt              this file

-------------------------------------------------------------------
 NOTES
-------------------------------------------------------------------
* Target machines: x86_64, reasonably recent Linux Mint (or similar glibc).
* The stick's files are owned by the primary user (uid 1000). On a standard
  single-user Mint machine that's your login, so read/write "just works".
* No .env is shipped by default. A normal user needs none of it (the app
  auto-generates a session key). Drop an .env into app/ to enable the
  internet-backed admin extras (live GPS track fetch, RIDB lookups).
