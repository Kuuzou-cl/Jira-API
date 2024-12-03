# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
from bigtree import dataframe_to_tree_by_relation, preorder_iter, tree_to_nested_dict
import pandas as pd

empresas = ['AN','ADA','ATA','ARA','AXA','AMA']
auth = HTTPBasicAuth("carlo.bernucci@aguasnuevas.cl", "ATATT3xFfGF0QJMW2deqscfBig7PLfDPNjNk-aGVpF9FZgAHilK7wTQaCTHQldVXqTtBZqb25aA9u8WQHJJlTJ76AOMIa_o4X88YfAC5j9s2IJ27NWg4bYfcr3BijwDMEnmuP3CwuULAthmvsjGE70DTukWTZWzdxLpDl7jaHp4-vE5HtV2PJVQ=BD4752CB")
url = "https://proyectosan.atlassian.net/rest/api/3/search/jql"
headers = {"Accept": "application/json"}

jira_data = []

def main():

  html_body = ''

  for empresa in empresas:
    print('=======================================================================')
    print(empresa)
    print('==')
    
    query = {
      'jql': 'project = KAN ' 
      +'AND labels = ' + empresa + ' '
      +'AND type IN (Task, Subtask, Epic) '
      +'AND status IN ("In Progress", Done) '
      +'AND comment ~ "Informe:" '
      #+'AND statuscategorychangeddate >= "2024-11-11" AND statuscategorychangeddate <= "2024-11-15" '
      #+'AND ( statuscategorychangeddate >= "2024-11-11" AND statuscategorychangeddate <= "2024-11-15" OR comment ~ "Informe:")'
      +'ORDER BY duedate ASC',
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
          found_parent = False
        
          for parent in jira_issues:
            if parent['key'] == tsk['fields']['parent']['key']:
              found_parent = True
              break

          if not found_parent:
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

        #print(data_temp)

        data_raw.append([data_temp['key'],data_temp['parent'],data_temp['title'],data_temp['comment']])

    data_structure = pd.DataFrame(data_raw,
      columns=["child", "parent", "title", "comment"],
    )

    if not data_structure.empty:
      root = dataframe_to_tree_by_relation(data_structure)
      #root.show()
      nested_dict = tree_to_nested_dict(root, all_attrs=True)
      #print(nested_dict)
      #print(nested_dict["name"])
      jira_data.append(nested_dict)
    #for node in preorder_iter(root):
      #print(node)
      #print([node.name for node in preorder_iter(root)])
  
  for x in jira_data:
    html_body = html_body + '<h5>'  + x["name"] + '</h5>'
    if "children" in x:
      html_body = html_body + get_list(x["children"])
  
  print(html_body)


def get_list(obj):
  html_list = '<ul>'
  for x in obj:
    #print(x['name'])  
    if x['comment'] != 'none':
      html_list = html_list + '<li>' + x["title"] + ':' + x["comment"]
    else:
      html_list = html_list + '<li>' + x["title"]
    if 'children' in x:
      html_list = html_list + get_list(x['children'])
      #print(x['children'])
    html_list = html_list + '</li>'
  html_list = html_list + '</ul>'
  return html_list

if __name__ == '__main__':
    main()