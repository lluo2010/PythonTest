# -*- coding: UTF-8 -*-
from distutils.core import setup  
import py2exe  
import sys
from glob import glob


sys.argv.append("py2exe")
files = [("Microsoft.VC90.CRT", glob(r'D:\Project\Analysis\Code\test\MS.VC90.CRT\*.*'))]
#options={ 'py2exe': {'includes': 'paramiko',"bundle_files": 1} }
options={ 'py2exe': { "compressed": 1,"optimize": 2,"bundle_files": 1} }
#setup(options = options,console=["utilTool.py"],data_files=files) 
setup(options = options,console=["splitCRCS.py"],data_files=files,zipfile=None)
#setup(console=["crcsDetect.py"],data_files=files,zipfile=None) #zipFile使所有的Dll都打进exe