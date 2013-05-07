# -*- coding: UTF-8 -*-
from distutils.core import setup  
import py2exe  
import sys
from glob import glob

sys.argv.append("py2exe")
files = [("Microsoft.VC90.CRT", glob(r'D:\Project\Analysis\Code\test\MS.VC90.CRT\*.*'))]
options={ 'py2exe': {'includes': 'paramiko',"bundle_files": 1} }
setup(options = options,console=["utilTool.py"],data_files=files) 
#setup(console=["test.py"],data_files=files,zipfile=None) #zipFile使所有的Dll都打进exe