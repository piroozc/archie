__author__ = 'pchubak'

import sys, glob, argparse, json
from pprint import pprint
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
from nipype.interfaces.utility import Function

#function to interface with fslorient command!
# TODO: dynamically generate function string code from info in pipeline json
fslorient = 'def fslorient(in_file_name, main_options):\n' + \
            '  import subprocess, os\n' + \
            '  command = ["fslorient"]\n' + \
            '  for option in main_options:\n' + \
            '    command.append(option)\n' + \
            '  command.append(in_file_name)\n' + \
            '  subprocess.call(command)\n' + \
            '  return os.path.abspath(in_file_name)'


fslorient_interface = Function(input_names=["in_file_name", "main_options"],
                               output_names=["out_file_name"],
                                function=fslorient)

class WorkflowParser:
  def __init__(self, data):
    self.nodes = {}
    self.connections = []
    self.wf = None
    self._parse_data(data)

  def _get_interface_instance(self, interface_name):
    import nipype
    name_list = interface_name.split('.')
    attr = getattr(nipype, name_list[0], None)
    if not attr:
      return globals()[interface_name]
    for a in name_list[1:]:
      attr = getattr(attr, a)
    return attr()

  def _parse_iterables(self, iterable):
    return (iterable['name'],
            [f for f in glob.glob(iterable['path'] + iterable['files'])])

  def _get_nipype_node(self, node):
    np_node = pe.Node(interface=self._get_interface_instance(node['interface']),
                      name=node['name'])
    for param in node['params'].keys():
      param_attrs = param.split('.')
      if param == 'iterables':
        setattr(np_node, param, self._parse_iterables(node['params'][param]))
      else:
        import types
        value = node['params'][param]
        if isinstance(value, types.ListType):
          value = tuple(value)
        setattr(reduce(getattr, param_attrs[:-1], np_node),
                param_attrs[-1], value)
    return np_node

  def _get_nipype_connections(self, connection):
    pass

  def _add_nodes(self, nodes):
    for node in nodes:
      self.nodes[node['name']] = self._get_nipype_node(node)

  def _add_connections(self, connections):
    for connection in connections:
      self.connections.append(connection)

  def _add_workflow_param(self, key, val):
    if key == 'name':
      self.wf = pe.Workflow(name=val)
    if key == 'base_dir':
      self.wf.base_dir = val

  global fslorient_interface

  def _parse_data(self, data):
    for param in data.keys():
      if param != 'nodes' and param != 'connections':
        self._add_workflow_param(param, data[param])
    if 'nodes' in data.keys():
      self._add_nodes(data['nodes'])
      self.wf.add_nodes(self.nodes.values())
    if 'connections' in data.keys():
      self._add_connections(data['connections'])
      for c in self.connections:
        self.wf.connect(self.nodes[c['source']], str(c['output']), self.nodes[c['target']], str(c['input']))
    return data

  def run(self):
    self.wf.run()

#Create the argument parser
parser = argparse.ArgumentParser(prog='parser', description='Parse and run a json workflow')
parser.add_argument('workflow_file', nargs=1, help='json workflow filename to parse')
args = parser.parse_args(sys.argv[1:])
print args.workflow_file

#Read the json data
try:
  json_data=open(args.workflow_file[0]).read()
  data = json.loads(json_data)
  wf = WorkflowParser(data)
  wf.run()
  #pprint(data)
except IndexError:
  exit(0)
