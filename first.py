__author__ = 'pchubak'

import sys, getopt, glob
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl

#config.enable_debug_mode()
#logging.update_logging(config)

def parse_args(argv):
  global input_dir, output_dir
  input_dir = '.'
  output_dir = '.'
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["idir=","odir="])
  except getopt.GetoptError:
    print 'hdr2nii.py -i <input_dir> -o <output_dir>'
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

#FIRST is a wrapper for run_first_all. Segment all nii files in input dir
first = pe.Node(interface=fsl.FIRST(), name='first')
first.base_dir = output_dir
first.iterables = ("in_file", [f for f in glob.glob(input_dir + '*.nii.gz')])
first.inputs.terminal_output = 'none'
# first.inputs.out_file

#create the workflow, add nodes, connect them and run the workflow
workflow = pe.Workflow(name='first_run_all')
workflow.base_dir = output_dir
workflow.add_nodes([first])

workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 4})