from nipype import config, logging
import sys, getopt, glob
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
from nipype.interfaces.utility import Function

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

#change the type of .hdr to .nii
changeDT = pe.Node(interface=fsl.ChangeDataType(), name='changeDT')
changeDT.base_dir = input_dir
changeDT.iterables = ("in_file", [f for f in glob.glob(input_dir + '*.hdr')])
changeDT.inputs.output_type = 'NIFTI_GZ'
changeDT.inputs.output_datatype = 'input'
changeDT.inputs.terminal_output = 'none'

#function to interface with fslorient command
def fslorient(in_file_name, main_options):
  import subprocess
  command = ["fslorient"]
  for option in main_options:
    command.append(option)
  command.append(in_file_name)
  subprocess.call(command)
  return in_file_name


fslorient_interface = Function(input_names=["in_file_name", "main_options"],
                               output_names=["out_file_name"],
                               function=fslorient)

#delete the orientation of .nii image
deleteOrient = pe.Node(interface=fslorient_interface, name='deleteOrient')
deleteOrient.base_dir = input_dir
deleteOrient.inputs.main_options = '-deleteorient'

#Swap dimension, fixes the dimension of the .nii file to x, y, z coordinates
swapDim = pe.Node(interface=fsl.SwapDimensions(), name='swapDimension')
swapDim.inputs.new_dims = 'x', 'y', 'z'
swapDim.inputs.terminal_output = 'file'

#calls fslorient interface and setsqformcode.
setqfc = pe.Node(interface=fslorient_interface, name='setqfc')
setqfc.inputs.main_options = '-setqformcode', '1'

#create the workflow, add nodes, connect them and run the workflow
workflow = pe.Workflow(name='hdr2nii')
workflow.base_dir = output_dir
workflow.add_nodes([changeDT, deleteOrient, swapDim, setqfc])

workflow.connect(changeDT, 'out_file', deleteOrient, 'in_file_name')
workflow.connect(changeDT, 'out_file', swapDim, 'in_file')
workflow.connect(swapDim, 'out_file', setqfc, 'in_file_name')

workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 4})