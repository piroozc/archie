import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
from nipype.interfaces.utility import Function

changeDTer = pe.Node(interface = fsl.ChangeDataType(), name = 'changeDT')
changeDTer.inputs.in_file = '/home/pchubak/career/archie/data/HANDY_POWER_098_9_1.hdr'
# changeDTer.inputs.out_file = '/home/pchubak/career/archie/data/HANDY_POWER_098_9_1.nii.gz'
changeDTer.inputs.output_type = 'NIFTI_GZ'
changeDTer.inputs.output_datatype = 'input'
changeDTer.inputs.terminal_output = 'none'
changeDTer.base_dir = '.'


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

deleteOrienter = pe.Node(interface = fslorient_interface, name = 'deleteOrient')
deleteOrienter.inputs.main_option = '-deleteorient'
# deleteOrienter.inputs.in_file_name = '/home/pchubak/career/archie/data/HANDY_POWER_098_9_1.hdr'


swapDimer = pe.Node(interface = fsl.SwapDimensions(), name = 'swapDimension')
# swapDimer.inputs.in_file = "../../data/HANDY_POWER_098_9_1.hdr"
swapDimer.inputs.new_dims = 'x', 'y', 'z'
swapDimer.inputs.terminal_output = 'file'


setqfc = pe.Node(interface = fslorient_interface, name = 'setqfc')
setqfc.inputs.main_option ='-setqformcode', '1'
# setqfc.inputs.in_file_name = '../../data/HANDY_POWER_098_9_1.hdr'


workflow = pe.Workflow(name = 'hdr2nii')
workflow.base_dir = '.'
workflow.add_nodes([changeDTer, deleteOrienter, swapDimer, setqfc])

workflow.connect(changeDTer, 'out_file', deleteOrienter, 'in_file_name')
workflow.connect(changeDTer, 'out_file', swapDimer, 'in_file')
workflow.connect(changeDTer, 'out_file', setqfc, 'in_file_name')

workflow.run()