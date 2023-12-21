# Awesome Curriculum Vitae
Python program intended for use in Windows OS that uses a modified version of [Posquit0's Awesome-CV](https://github.com/posquit0/Awesome-CV) LaTeX template to generate a CV in `pdf` format based on a `json` blueprint of the CV provided by the user.

## Installation
Begin by installing Miktex, which is required in order to be able to compile the intermediate `tex` file generated by the program into a `pdf` file. It is recommended that you go for the [portable edition](https://miktex.org/howto/portable-edition) of Miktex and do the following:
- Follow the instructions listed under the **Download** and **How to Install** sections.
- Go to Windows search and find "Edit the system environment variables", click "Environment Variables". Under "System Variables", look for the variable `Path`, select it then click "Edit". Click "New" and add the absolute path to the Miktex x64 folder; this path should have the form `...\miktex-portable\texmfs\install\miktex\bin\x64`, where `...` is the prefix of the absolute path (i.e. of the form `C:\etc\etc\etc`).
- Extract the json2cv folder from `json2cv.zip` and place it somewhere.

## Usage
Point `cmd` to the json2cv directory; the easiest way to do this is by opening the json2cv directory and typing `cmd` into the address bar of the file explorer. To run the tool, type `json2cv`; you should see an error message asserting the valid arguments that you must or can pass to the tool.

Inside the json2cv folder, you should see an `example.json` blueprint. You can rename this file to whatever you wish; this name will be passed to the tool and will also be used to assign the name of the `pdf` output file. The `example.json` file serves as an example of what can be achieved with this tool. It is recommended that you have a look at its contents and run it, then create your own CV from there. To get you started with running, here is an example:

```
json2cv resume -n "First Last" -p "Employee Role" -m "000-000-0000" -e "email@provider.tld" -l "linkedin-id" -a "City, PV" -g "GithubUsername" -c "DC3522" --footer
```