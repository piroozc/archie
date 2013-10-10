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
  print 'Input file is "', input_dir
  print 'Output file is "', output_dir


parse_args(sys.argv[1:])

#change the type of .hdr to .nii
changeDTer = pe.Node(interface = fsl.ChangeDataType(), name = 'changeDT')
changeDTer.base_dir = input_dir
changeDTer.iterables = ("in_file", [f for f in glob.glob(input_dir + '*.hdr')])
changeDTer.inputs.output_type = 'NIFTI_GZ'
changeDTer.inputs.output_datatype = 'input'
changeDTer.inputs.terminal_output = 'none'

#function to interface with fslorient command
def fslorient(in_file_name, *main_option):
  import subprocess
  args = ["fslorient"]
  for each in main_option:
    args.append(each)
  args.append(in_file_name)
  return subprocess.call(args)


fslorient_interface = Function(input_names = ["in_file_name", "*main_option"],
                               output_names = ["out_file_name"],
                               function = fslorient)

#delete the orientation of .nii image
deleteOrienter = pe.Node(interface = fslorient_interface, name = 'deleteOrient')
deleteOrienter.inputs.main_option = '-deleteorient'

#Swap dimension, fixes the dimension of the .nii file to x, y, z coordinates
swapDimer = pe.Node(interface = fsl.SwapDimensions(), name = 'swapDimension')
swapDimer.inputs.new_dims = 'x', 'y', 'z'
swapDimer.inputs.terminal_output = 'file'

#calls fslorient interface and setsqformcode.
setqfc = pe.Node(interface = fslorient_interface, name = 'setqfc')
setqfc.inputs.main_option ='-setqformcode', '1'

#create the workflow, add nodes, connect them and run the workflow
workflow = pe.Workflow(name='hdr2nii')
workflow.base_dir = output_dir
workflow.add_nodes([changeDTer, deleteOrienter, swapDimer, setqfc])

workflow.connect(changeDTer, 'out_file', deleteOrienter, 'in_file_name')
workflow.connect(changeDTer, 'out_file', swapDimer, 'in_file')
workflow.connect(changeDTer, 'out_file', setqfc, 'in_file_name')

workflow.run()