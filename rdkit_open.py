## Open files

import re,gc
import gzip,bz2

from Mol2Writer import Mol2MolSupplier

from rdkit import Chem

#######################################################################
## to handle the raw SDF format, python3's rdkit has a documented bug and
## hasn't been fixed since 2016. https://github.com/rdkit/rdkit/issues/1065
## To avoid it, the input file cannot be an object handle of a regular file,
## i.e. handle = open('xxx.sdf','r') will fail but handle = 'xxx.sdf' is fine.
## It only happens to regular file but not to gzip.open() or bz2.BZ2File() in
## python3 rdkit but not in python2 rdkit...
## Fix it by replace handle = open('xxx.sdf','r') with handle = 'xxx.sdf'

## Handle gzip and bzip2 file if the extension is right. otherwise, just open
## outuput: file handle
def file_handle(file_name):
  if re.search(r'.gz$', file_name):
    handle = gzip.open(file_name, 'r')
  elif re.search(r'.bz2$', file_name):
    handle = bz2.BZ2File(file_name, 'r')
  else:
    handle = file_name

#  print("## Opening "+file_name)
  return handle

#######################################################################
def rdkit_open(File_Tuple):

  List = []

  for f in (File_Tuple):
    handle = file_handle(f)

    if re.search(r'.sdf', f):
      if re.search(r'.gz$|.bz2$', f):
        Mol = [x for x in Chem.ForwardSDMolSupplier(handle, removeHs=False)
               if x is not None]
      else:
        Mol = [x for x in Chem.SDMolSupplier(handle, removeHs=False)
               if x is not None]

    if re.search(r'.smi', f):
      with handle as fi:
        first_line = fi.readline()

      if re.search(r'smiles', first_line, re.IGNORECASE):
        Mol = [x for x in Chem.SmilesMolSupplier(f, titleLine=True,
                 delimiter=' |\t|,') if x is not None]
      else:
        Mol = [x for x in Chem.SmilesMolSupplier(f, titleLine=False,
                 delimiter=' |\t|,') if x is not None]

    ## not the official RDkit function, may fail
    if re.search(r'.mol2', f):
      Mol = [x for x in Mol2MolSupplier(f, removeHs=False) if x is not None]

    print( "# Found mol in {0}: {1}".format(f, len(Mol)))
    for mol in Mol: List.append(mol)
 
  gc.collect()
  return List

