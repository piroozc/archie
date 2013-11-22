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
def sienax(in_file_name):
  import subprocess, os
  command = ["sienax"]
  command.append(in_file_name)
  subprocess.call(command)
  return os.path.abspath(in_file_name)

sienax_interface = Function(input_names=["in_file_name"],
                               output_names=["out_file_name"],
                               function=sienax)

#delete the orientation of .nii image
sienax_node  = pe.Node(interface=sienax_interface, name='sienax')
sienax_node.base_dir = input_dir
sienax_node.iterables = ("in_file_name", [f for f in glob.glob(input_dir + '*.nii.gz')])

#create the workflow, add nodes, connect them and run the workflow
workflow = pe.Workflow(name='sienax_run_all')
workflow.base_dir = output_dir
workflow.add_nodes([sienax_node])

workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 2})
