# python code used in various bioinformatics pipelines

### Windows conda environment (see right after this for normal conda environment)

Just running the command below doesn't work instead first run this command instead of the command below to create a slightly different environment 

open up the anaconda prompt, you can find this by looking it up in the start menu that is where you will be running all of these commands

`conda create -c bioconda -c plotly -n compbio python=3 pandas seaborn matplotlib scipy numpy statsmodels jupyter scikit-learn plotly`

This command is the same as the one below except cmappy is removed from it, then activate the conda environment using the command:  `conda activate compbio` 

once you have compbio activated run the command 

`pip install cmapPy` 

This will add cmappy into the compbio environment, to check to see if it was added open a notebook in jupyter notebook and run this command

 `import cmapPy.pandasGEXpress.parse` 

if it doesn't give you an error then congratulations it worked, it if does make sure your ran the install cmapPy command while in the compbio environment if you did both of those ask someone for help

### create a conda environment

run this command to create the environment:

`conda create -c bioconda -c plotly -n compbio python=3 pandas seaborn matplotlib scipy numpy statsmodels jupyter cmappy scikit-learn plotly`

What does it all mean?

`conda create` indicates create a new conda environment

`-c bioconda -c plotly` indicates use the public repositories "bioconda" and "plotly" to look for some of the libraries

`-n compbio` indicates the name of the new environment:  compbio

subsequent entries are the specific libraries to add to the environment:

- `python=3` is for version 3 of python
- `pandas` is a library for data manipulation
- `seaborn matplotlib plotly` are for plotting, data visualization, interactive diagrams
- `jupyter` allows you to run python code and immediately see the results of calculations our plotting next to the code
- `scipy, numpy, statsmodels, scikit-learn` are mathematics, statistics and AI / machine learning libraries
- `cmappy` is library for data manipulation and some mathematics

### activate the conda environment

run the command:  `conda activate compbio`

### notes to fix import errors and module not found 

navigate to the top level directory of summer2020 while in compbio

run the command: `python setup.py develop`



### start the jupyter notebook

run the command:  `jupyter-notebook`

a log of what the jupyter-notebook "server" is doing will be displayed in your terminal window - leave this open

Also a new browser window should open - this is the directory / organization of the jupyter notebooks

### start coding!

 In the jupyter notebook window, go to the "new" menu and choose "Python 3" (should be at the top".  A new window should open, in the cell at the top you can type in some python code and run it - try it out!  Try adding some additional cells, add code to them, run them separately.
