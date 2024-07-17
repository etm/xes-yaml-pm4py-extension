import pm4py

if __name__ == "__main__":
  log = pm4py.read_yaml('ca2328b4-2831-431f-af1d-e187ff267f72.xes.yaml')

  print(log.columns)
  log = log[log['cpee:activity']!='external']
  log = log[log['cpee:lifecycle:transition']=='activity/done']
  print(log)
   
  heuristic_net = pm4py.discover_heuristics_net(log,case_id_key='cpee:instance',activity_key='cpee:activity',timestamp_key='time:timestamp', dependency_threshold=0.0)
  pm4py.view_heuristics_net(heuristic_net, format="svg")
  petri_net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log,case_id_key='cpee:instance',activity_key='concept:name')
  pm4py.view_petri_net(petri_net, initial_marking, final_marking, format="svg")

  result_token_based = pm4py.fitness_token_based_replay(log,petri_net,initial_marking,final_marking,activity_key='cpee:activity',case_id_key='cpee:instance')
  result_alignments = pm4py.fitness_alignments(log,petri_net,initial_marking,final_marking,activity_key='cpee:activity',case_id_key='cpee:instance')
  print(result_token_based)
  print(result_alignments)

  pm4py.write_xes(log,"output",case_id_key="cpee:instance")
  pm4py.write_yaml(log,"output")
   

