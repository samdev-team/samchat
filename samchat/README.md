# SAM-Chat
Epic chat app

## Setup virtual environment
**I recommend that you should create a virtual environment for SAM-Chat** \
To make this compatible with cygwin and mingw on Windows, I recommend install 
virtualenv a pip package. you can do this by running this command,
```shell
$ pip install virtualenv
```

Then to create the virtualenv type this
```shell
$ virtualenv venv
```
this command creates a virtualenv called venv. you can activate the virtual environment by typing
one of the following commands:

| Platform |      Shell      | Command to Activate virtual environment | 
|:--------:|:---------------:|:----------------------------------------|
|  POSIX   |    BASH/ZSH     | $ source venv/bin/activate              |
|          |      FISH       | $ source venv/bin/activate.fish         |
|          |    CSH/TCSH     | $ source venv/bin/activate.csh          |
|          | Powershell Core | $ venv/bin/Activate.ps1                 |
| Windows  |     cmd.exe     | C:\> venv\Scripts\activate.bat          |
|          |   PowerShell    | PS C:\> venv\Scripts\Activate.ps1       |

[Source - python.org](https://docs.python.org/3/library/venv.html)