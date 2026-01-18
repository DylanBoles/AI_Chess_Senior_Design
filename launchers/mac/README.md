# Using the launcher

If the NeuralNetChess launcher doesnt work, try deleting it and decompressing the `app.tar.gz` file from the command line. Long story. You wont have to do
that in the final version.


Some manual set up is required to use the launcher. The launcher is basically just a shell script that calls two other shell scripts that it ASSUMES you
already have on your system:
- initgui: shell script that launches the gui program on your laptop
- initpi: shell script that connects to the raspberry pis via SSH and starts their servers remotely

Because I am still debugging those scripts I had to set it up this way. The final version will have all that functionality built-in and won't require you
to already have those files.


to use:
```bash
mkdir ~/nnchess
cp path/to/initgui ~/nnchess/initgui
cp path/to/initpi ~/nnchess/initpi
```


And, if the launcher throws an error, delete it and run
```bash
tar xf app.tar.gz
```
in whatever directory you want the launcher to exist in (like `~/Desktop` or `~/Documents`)

