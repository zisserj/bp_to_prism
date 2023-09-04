import bppy as bp
from bppy.model.sync_statement import *
from bppy.model.b_thread import b_thread
from bppy.model.b_event import BEvent
from bppy.utils.dfs import DFSBThread
from bppy.utils.exceptions import BPAssertionError


# adjusting https://github.com/bThink-BGU/BPpy/blob/master/bppy/utils/dfs.py
# program to only map individual threads without the graph exploration


class DFSBProgram:
    def __init__(self, bprogram_generator, event_list,
                 bthread_names, max_trace_length=1000):
        self.bprogram_generator = bprogram_generator
        self.event_list = event_list
        self.bthread_names = bthread_names
        self.max_trace_length = max_trace_length

    def get_graph(self):
        init = []
        mapper = {}
        n = len(self.bprogram_generator().bthreads)
        ess = self.bprogram_generator().event_selection_strategy
        for i in range(n):
            f = lambda: self.bprogram_generator().bthreads[i]
            dfs = DFSBThread(f, ess, self.event_list)
            init_s, visited = dfs.run()
            mapper[self.bthread_names[i]] = visited
            init.append(init_s)
        return init, mapper


@b_thread
def add_hot():  # requests "HOT" two times
    for i in range(2):
        yield {request: bp.BEvent("HOT")}


@b_thread
def add_cold():  # requests "COLD" two times
    for i in range(2):
        yield {request: bp.BEvent("COLD")}


@b_thread
def control():  # blocking 2 consecutive HOT events
    while True:
        yield {request: bp.BEvent("XX"), waitFor: bp.BEvent("HOT"), block: bp.BEvent("COLD")}
        yield {request: bp.BEvent("XX"), waitFor: bp.BEvent("COLD"), block: bp.BEvent("HOT")}


# function that generates a b-program with the control b-thread
def bp_gen():
    return bp.BProgram(bthreads=[add_hot(), add_cold(), control()],
                       event_selection_strategy=bp.SimpleEventSelectionStrategy())


dfs = DFSBProgram(bp_gen, [BEvent("COLD"), BEvent("HOT"), BEvent("XX")],
                    ["hot_bt", "cold_bt", "interleave"])
init, bp_states = dfs.get_graph()

# start composing prism file here

event_names = [x.name for x in dfs.event_list]
events = {e: BEvent(e) for e in event_names}
bt_names = dfs.bthread_names


rule_template = "formula is_{}_{} = {};"
bt_condition = "(is_{}_{}_{}={})"

header = 'dtmc\n\n'

req = [rule_template.format(e, "requested",
        ' | '.join([bt_condition.format(bt,'requesting',e,'true')
        for bt in bt_names]))
      for e in event_names]

block = [rule_template.format(e, "blocked",
        ' | '.join([bt_condition.format(bt,'blocking',e,'true')
        for bt in bt_names]))
      for e in event_names]

select = [rule_template.format(e, "selected",
        ' & '.join([f'(is_{e}_requested=true)',
                    f'(is_{e}_blocked=false)']))
      for e in event_names]

labels = ["label \"{}\" = (is_{}_selected=true);".format(e, e)
      for e in event_names]

header += '\n\n'.join(
    ['\n'.join(sec) for sec in [req,block,select,labels]])

header += '\n//-----------------------\n\n'

def format_bt_module(name, event_names, bt_states):

    node_to_s = {s: i for i, s in enumerate(bp_states[name])}

    bt_req = {e: [] for e in event_names}
    bt_block = {e: [] for e in event_names}
    bt_trans = {}

    for node, n in node_to_s.items():
        bt_trans[n] = {}
        for e in event_names:
            if ('request' in node.data) and (node.data['request'] == events[e]):
                bt_req[e].append(n)
            if ('block' in node.data) and (node.data['block'] == events[e]):
                bt_block[e].append(n)
            bt_trans[n][e] = (node_to_s[node.transitions[events[e]]] if
                            events[e] in node.transitions else n)


    module_template = '\nmodule {}\n\t{}\n\n\t{}\nendmodule\n'
    state_template = "formula is_{}_{}_{} = {};"
    state_name = f's_{name}'
    state_init = f'{state_name}: [0..{len(bt_states)-1}] init 0;'
    event_transition = '[{}] ({}={}) & (is_{}_selected=true) -> 1: ({}\'={});'

    req = [state_template.format(name, "requesting", e,
            ' | '.join([('({}={})').format(state_name, n)
            for n in bt_req[e]]) if len(bt_req[e]) > 0 else 'false')
        for e in event_names]

    block = [state_template.format(name, "blocking", e,
            ' | '.join([('({}={})').format(state_name, n)
            for n in bt_block[e]]) if len(bt_block[e]) > 0 else 'false')
        for e in event_names]

    transitions = []
    for n, tr in bt_trans.items():
        string_tr = [event_transition.format(e, state_name,
                        n, e, state_name, s_tag) for e, s_tag in tr.items()]
        transitions.append('\n\t'.join(string_tr))

    module = ''
    module += '\n\n'.join(
        ['\n'.join(sec) for sec in [req,block]])

    module += module_template.format(name,
                            state_init, '\n\t\n\t'.join(transitions))

    return module


content = '\n\n'.join([format_bt_module(bt_name, event_names,
                        bp_states[bt_name]) for bt_name in bt_names])


with open("test_out.pm", "w") as f:
    f.write(header)
    f.write(content)
