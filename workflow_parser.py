__author__ = 'pchubak'

import sys, glob, argparse, json
from pprint import pprint
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl


class WorkflowParser:
  def __init__(self, data):
    self.nodes = []
    self.connections = []
    self.wf = None
    self.__parse_data(data)

  def __get_interface_instance(self, interface_name):
    if interface_name == 'fsl.FIRST()':
      return fsl.FIRST()

  def __get_nipype_node(self, node):
    np_node = pe.Node(interface=self.__get_interface_instance(node['interface']),
                      name=node['name'])
    if 'base_dir' in node.keys():
      np_node.base_dir = node['base_dir']
    if 'inputs.terminal_output' in node.keys():
      np_node.inputs.terminal_output = node['inputs.terminal_output']
    if 'in_file' in node.keys():
      if node['in_file']['type'] == 'iterable':
        np_node.iterables = ('in_file',
                             [f for f in glob.glob(node['in_file']['address'] +
                                                   node['in_file']['filetypes'])])
      else:
        np_node.inputs.in_file = node['in_file']['filename']
    return np_node

  def __get_nipype_connections(self, connection):
    pass

  def __add_nodes(self, nodes):
    for node in nodes:
      self.nodes.append(self.__get_nipype_node(node))

  def __add_connections(self, connections):
    for connection in connections:
      self.connections.append(self.__get_nipype_connections(connection))

  def __add_workflow_param(self, key, val):
    if key == 'name':
      self.wf = pe.Workflow(name=val)
    if key == 'base_dir':
      self.wf.base_dir = val

  def __parse_data(self, data):
    for param in data.keys():
      if param != 'nodes' and param != 'connections':
        self.__add_workflow_param(param, data[param])
    if 'nodes' in data.keys():
      self.__add_nodes(data['nodes'])
      self.wf.add_nodes(self.nodes)
    if 'connections' in data.keys():
      self.__add_connections(data['connections'])
      for c in self.connections:
        self.wf.connect(c['node1'], c['out1'], c['node2'], c['in2'])
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
