__author__ = 'pchubak'
import sys, getopt, glob
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
from nipype.interfaces.utility import Function

def parse_args(argv):
  global input_dir, output_dir
  input_dir = '.'
  output_dir = '.'
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["idir=","odir="])
  except getopt.GetoptError:
    print 'test.py -i <input_dir> -o <output_dir>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'test.py -i <input_dir> -o <output_dir>'
      sys.exit()
    elif opt in ("-i", "--idir"):
      input_dir = arg
    elif opt in ("-o", "--odir"):
      output_dir = arg
  print 'Input directory is "', input_dir
  print 'Output directory is "', output_dir


parse_args(sys.argv[1:])

#function to interface with sienax command
def sienax(in_file_name, options):
  import subprocess
  command = ["sienax"]
  for o in options:
    command.append(o)
    if o == '-o':
      output_
  command.append(in_file_name)
  subprocess.call(command)
  return in_file_name

