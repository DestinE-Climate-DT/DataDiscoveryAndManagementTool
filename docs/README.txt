To create the sphinx documentation from the python source filesi, create docs folder under the project folder and execute the following from the docs folder.
1. sphinx-quickstart  --- options mostly default, for seperate build and source , choose yes.
2. Edit conf.py to 
	a.Add 'sphinx_rtd_theme' in html_theme.
	b.Add the following extensions to the conf.py:
		extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

		napoleon_google_docstring = True
		napoleon_numpy_docstring = False
		napoleon_include_init_with_doc = True
		napoleon_include_private_with_doc = False
	c.Add the following :
		import os
		import sys
		sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'src')))
3.Edit index.rst to add 'modules'.
4. sphinx-apidoc -o ./source ../src
5. make html
6. make latexpdf
6a. make latexpdf runs from 'terminal' in Jupyterhub but not from 'terminal' opened in the local laptop.
6b.Modify the *.tex in 'docs/build/latex' to add newline to the author names and run 'make' in  'docs/build/latex' to create the pdf.
  If 'make latexpdf' is run from 'docs/' author names appear in single line.  
6c.The newline for sphinx is '\\' for example :
    "
    \\Karsten Peters\sphinxhyphen{}von Gehlen
    \\Stephan Kindermann}
    "
