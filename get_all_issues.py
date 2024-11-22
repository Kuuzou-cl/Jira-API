# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
from bigtree import dataframe_to_tree_by_relation, preorder_iter
import pandas as pd


empresa = 'AXA'

url = "https://proyectosan.atlassian.net/rest/api/3/search/jql"

auth = HTTPBasicAuth("carlo.bernucci@aguasnuevas.cl", "ATATT3xFfGF0QJMW2deqscfBig7PLfDPNjNk-aGVpF9FZgAHilK7wTQaCTHQldVXqTtBZqb25aA9u8WQHJJlTJ76AOMIa_o4X88YfAC5j9s2IJ27NWg4bYfcr3BijwDMEnmuP3CwuULAthmvsjGE70DTukWTZWzdxLpDl7jaHp4-vE5HtV2PJVQ=BD4752CB")


headers = {
  "Accept": "application/json"
}

query = {
  'jql': 'project = KAN ' 
  +'AND labels = ' + empresa + ' '
  +'AND type IN (Task, Subtask, Epic) '
  +'AND status IN ("In Progress", Done) '
  +'AND comment ~ "Informe:" '
  #+'AND statuscategorychangeddate >= "2024-11-11" AND statuscategorychangeddate <= "2024-11-15" '
  #+'AND ( statuscategorychangeddate >= "2024-11-11" AND statuscategorychangeddate <= "2024-11-15" OR comment ~ "Informe:")'
  +'ORDER BY created ASC',
  'maxResults': '50',
  'fields': 'id,key,assignee,comment, parent, summary',
  #'fields': '*all'
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query,
   auth=auth
)

jira_response_str = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
jira_response = json.loads(jira_response_str)

jira_issues = jira_response['issues']

data_raw = []

for tsk in jira_issues:
    data_temp = {
      'key': tsk['key'],
      'title': tsk['fields']['summary'],
      'parent': empresa,
      'comment': 'none'
    }

    if 'comment' in tsk['fields']:
      comments = tsk['fields']['comment']['comments']
      for comment in comments:
        #validar fecha con campo created, mismo nivel que body, format 2024-11-14T16:11:09.266-0300
        if 'Informe:' in comment['body']['content'][0]['content'][0]['text']:
          data_temp['comment'] = comment['body']['content'][0]['content'][0]['text'].replace('Informe:', '')

    if 'parent' in tsk['fields']:
      data_temp['parent'] = tsk['fields']['parent']['key']

      query_task_parent = {
        'jql': 'project = KAN and key =' + tsk['fields']['parent']['key'],
        'fields': 'id, key, parent, summary',
      }

      response_task_parent = requests.request(
        "GET",
        url,
        headers=headers,
        params=query_task_parent,
        auth=auth
      )

      jira_task_parent_response_str = json.dumps(json.loads(response_task_parent.text), sort_keys=True, indent=4, separators=(",", ": "))
      jira_task_parent_response = json.loads(jira_task_parent_response_str)

      jira_parent = jira_task_parent_response['issues']

      jira_issues += jira_parent

    data_raw.append([data_temp['key'],data_temp['parent'],data_temp['title'],data_temp['comment']])

data_structure = pd.DataFrame(data_raw,
   columns=["child", "parent", "title", "comment"],
)

print(data_structure)

root = dataframe_to_tree_by_relation(data_structure)
root.show()

print([node.name for node in preorder_iter(root)])
#print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))