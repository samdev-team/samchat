# SAM-Chat
Epic chat app

## PyAudio Module
#### To use SAM-Chat with python you must install a custom fork of PyAudio
**[Custom PyAudio Fork](https://git.skeh.site/skeh/pyaudio.git)**

### Get the PyAudio and PortAudio repo
If you haven't pulled the submodules before then you will need pull it. To do this type this command.
```shell
$ git submodule update --init --recursive
```
If you have already pulled the submodules. \
Make sure you update them with the following command.
```shell
$ git submodule update --recursive
```

### Setup virtual environment
**I recommend that you should create a virtual environment for SAM-Chat** \
To do this type this command.
```shell
$ python3 -m venv venv
```
this command creates a virtual environment called venv. you can activate the virtual environment by typing 

| Platform |      Shell      | Command to Activate virtual environment | 
|:--------:|:---------------:|:----------------------------------------|
|  POSIX   |    BASH/ZSH     | $ source venv/bin/activate            |
|          |      FISH       | $ source venv/bin/activate.fish       |
|          |    CSH/TCSH     | $ source venv/bin/activate.csh        |
|          | Powershell Core | $ venv/bin/Activate.ps1               |
| Windows  |     cmd.exe     | C:\> venv\Scripts\activate.bat        |
|          |   PowerShell    | PS C:\> venv\Scripts\Activate.ps1     |

[Source - python.org](https://docs.python.org/3/library/venv.html)

## Installing PortAudio
**Installing PyAudio requires the portaudio-devel package to be installed for linux.** \
**Check with your distro's package manager to see if it is available.** 
**If portaudio is not available then you have to build it manually.**

**Windows users are required to build portaudio manually.**

### Building PortAudio Manually
### Building in linux:
**libasound-devel is required for building PortAudio, make sure that it is installed. 
Development tools are also required for building, make sure you install your distro's
development tools.**


To get started go into the portaudio submodule and type the following commands.
```shell
$ ./configure

$ make

$ make install # you may need root for this
```
after you have done this you have successfully installed portaudio

### Building in windows:
idk yet

## Installing PyAudio
Now that you have Installed portaudio you have to add the module to the virtual environment.
To add it in linux do this:
```shell
$ cd pyaudio

$ python3 setup.py install
```
To do it in windows do this:
```shell
$ python setup.py install --skip-build
```
