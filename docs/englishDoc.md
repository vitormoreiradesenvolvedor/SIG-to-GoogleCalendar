# SIG-to-GoogleCalendar

## A Python script to fetch class schedules from SIG and convert them into a `.csv` file to be used in Google Calendar

[Documentação em Português](https://github.com/vitormoreiradesenvolvedor/SIG-to-GoogleCalendar)

### Requirements

You need Python 3.x.x to run this script.

### Installation

Clone the repository and enter the project folder.

Then, it is strongly recommended to create and activate a virtual environment (`venv`) before installing the dependencies.

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Now install the dependencies with:

```bash
pip install -r requeriments.txt
```

### Running

With the virtual environment activated, run the following command in the terminal:

```bash
python3 sigToCalendar.py
```

You will need to provide some information in order to run the script:

- Login - Your SIG login
- Password - Your SIG password
- Start Date - The date from which you want to start replicating your class schedule
- End Date - The date until which you want to replicate your class schedule

After that, a `.csv` file will be generated. Go to `calendar.google.com > Import > Select a file from your computer` and choose the generated `.csv` file.

It is strongly recommended to create a new calendar before importing the `.csv` file.

### Contributing

Feel free to give feedback, open new issues, and submit pull requests.
