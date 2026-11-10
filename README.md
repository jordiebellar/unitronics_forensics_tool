# Unitronics Forensics Tool

Python tooling for talking to a Unitronics V570 PLC over PCOM (serial), dumping its memory,
and analyzing the dumps. Part of the MS thesis work on PLC forensics.

The PLC is wired to a Raspberry Pi. Code is edited on the PC. Captures happen on the Pi.
Analysis happens on the PC.

## The one idea to remember

Code and data move in opposite directions, so they use different tools.

    PC  --(git push, then git pull on Pi)-->  Pi        code, versioned
    PC  <--(tools/sync_data.ps1, scp)-------  Pi        data, not in git

Git never holds dumps. The `data/` folder is ignored on purpose.

## File structure and what goes where

    unitronics_forensics_tool/
      README.md                 this file
      requirements.txt          Python packages needed on PC and Pi (pyserial)
      requirements-gui.txt      extra packages for the PC-only GUI (FreeSimpleGUI)
      .gitignore                keeps data and machine settings out of git
      .gitattributes            forces same line endings on Windows and Pi
      src/                      the core library. Edit code here.
        pcom_client.py          PCOM protocol, serial/PLC access, dump routines, terminal menu
        pcom_gui.py             desktop GUI on top of pcom_client (PC only)
      analysis/                 offline scripts that read dumps. No PLC needed. Run on the PC.
        compare_dumps.py            diff two operand dump folders
        compare_memory_profiles.py  diff two memory map CSVs
        locate_mi_in_raw_memory.py  find MI operands inside a raw dump
      scripts/                  one-off experiments that talk to the PLC. Run on the Pi.
        pcom_memory_hammer.py
      tools/                    workflow helpers. Not part of the forensics code.
        run.sh / run.ps1        run a script inside a fresh timestamped data folder
        deploy.ps1              push code from PC and pull it on the Pi
        sync_data.ps1           copy new run folders from Pi to PC
        pi.conf.example         copy to pi.conf and fill in your Pi details
      docs/                     notes, memory map findings, write-up material
      data/                     ALL captured data. Ignored by git.
        runs/                   new captures, one folder per run
        legacy/                 your old files from before the cleanup

Rules of thumb:
- A new reusable function goes in `src/`.
- A script that only reads existing dumps goes in `analysis/`.
- A throwaway experiment against the PLC goes in `scripts/`. If it proves useful, move the good parts into `src/`.
- Output files never go next to code. They go in `data/runs/`.

## One-time setup

### Step 1. Get the repo out of OneDrive (PC)
OneDrive can corrupt the hidden `.git` folder. Do this once.
1. In File Explorer, right-click the `Unitronics Forensics Tool` folder, choose "Always keep on this device", and wait until every file shows a green check. This also fixes `scripts/pcom_memory_hammer.py` and `analysis/locate_mi_in_raw_memory.py`, which were still cloud-only placeholders when this layout was made.
2. Commit your work first (Step 2), then cut the inner `unitronics_forensics_tool` folder and paste it into `C:\dev\` (create `C:\dev` if needed).
3. Open `C:\dev\unitronics_forensics_tool` in VS Code from now on. Delete the old OneDrive copy once you confirm everything is in `C:\dev`.

### Step 2. Commit the new layout (PC, in a terminal inside the repo)
    git add -A
    git status
    git commit -m "Restructure into src/analysis/scripts/tools layout"
    git push

`git status` should show files as "renamed", not deleted plus added. If it shows hundreds of changed lines in `pcom_client.py`, that is the line-ending change from `.gitattributes`. It is expected once.

### Step 3. Set up the PC Python environment
    cd C:\dev\unitronics_forensics_tool
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements-gui.txt

### Step 4. Set up SSH from PC to Pi
On the Pi, run `sudo raspi-config`, go to Interface Options, enable SSH, and note the Pi's address with `hostname -I`.
Then, on the PC in PowerShell:
    ssh-keygen -t ed25519
    type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh pi@raspberrypi.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
(Replace `pi` and `raspberrypi.local` with your Pi username and hostname or IP.) After this, `ssh pi@raspberrypi.local` should log in with no password. This is what lets the deploy and sync scripts run unattended.

### Step 5. Set up the Pi
SSH into the Pi, then:
    sudo apt update && sudo apt install -y git python3-pip python3-venv
    sudo usermod -aG dialout $USER        # lets you open the serial port. Log out and back in after.
    cd ~
    git clone https://github.com/jordiebellar/unitronics_forensics_tool.git
    cd unitronics_forensics_tool
    git checkout JordieBellar             # same branch you push from the PC
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

### Step 6. Tell the PC scripts where the Pi is
In `tools/`, copy `pi.conf.example` to `pi.conf` and edit the three lines (user, host, repo path). `pi.conf` is ignored by git.

## Daily workflow

1. **Edit on the PC** in VS Code. Run `analysis/` scripts and the GUI here.
2. **Commit** your change: `git add -A` then `git commit -m "what changed"`.
3. **Deploy to the Pi:** `.\tools\deploy.ps1`
4. **Capture on the Pi** (SSH in, or use the monitor). Always run through the run helper so output is organized:
       cd ~/unitronics_forensics_tool
       source .venv/bin/activate
       tools/run.sh src/pcom_client.py
   Output lands in `data/runs/<date_time>_pcom_client/` next to a `meta.txt` recording the git commit.
5. **Wait for the run to finish**, then on the PC: `.\tools\sync_data.ps1`
6. **Analyze on the PC** against the copied folders in `data/runs/`, for example:
       .\tools\run.ps1 analysis\compare_dumps.py data\runs\<baseline> data\runs\<capture>

Tip: for live debugging, VS Code's "Remote - SSH" extension lets you edit files directly on the Pi. Commit from there and `git pull` on the PC.

## Rules that keep this from getting messy again

- Never save captures in the repo folders outside `data/`.
- Rename meaningful runs after the fact: `data/runs/2026-11-12_153000_pcom_client` becomes `...__flag3_app_loaded`. `meta.txt` keeps the details.
- Back up the baseline dumps (flag0, flag1) somewhere other than this PC. They are thesis evidence and git does not have them.
- Commit before every deploy. The Pi can only run what you committed.
- Do not edit code on the Pi unless you commit and push from there, or the two copies will diverge.

## Troubleshooting

- **Permission denied on /dev/ttyUSB0:** you are not in the `dialout` group. Run the `usermod` line in Step 5, then log out and in.
- **`git pull` on the Pi says local changes would be overwritten:** someone edited a file on the Pi. Run `git stash` then `git pull`.
- **`ModuleNotFoundError: pcom_client`:** you ran a script directly. Use `tools/run.sh` or `tools\run.ps1`, which set the path for you.
- **ssh asks for a password every time:** redo Step 4.
- **GUI will not start on the Pi:** the GUI is PC only. Use the terminal menu (`src/pcom_client.py`) on the Pi.
