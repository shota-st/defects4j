"""スクリプトの説明

* プロンプトの作成スクリプト
* 前提：識別子名をマスクされたバグありソースまで完成している状態

# 入力：`data/project_name/method_snippet/`
# 出力：`data/project_name/prompt/`

"""


import json
import os
import sys
import re
import csv


def create_OOO_prompt_txt(spec, method):
    prompt_former = '<task>\nThe next method follows specification.\nAnd it has a bug.\nPlease fix it.\n</task>\n\n<specification>\n'
    prompt_txt = prompt_former + spec + '</specification>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_OOX_prompt_txt(spec, method):
    prompt_former = '<task>\nThe next method follows specification.\nAnd it has a bug.\nPlease fix it.\nHowever, do not change variable names such as \"$1\" when fixing it.\n</task>\n\n<specification>\n'
    prompt_txt = prompt_former + spec + '</specification>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_OXO_prompt_txt(spec, method):
    prompt_former = '<task>\nThe next method follows specification.\nAnd it has a bug.\nPlease fix it.\nHowever, do not change the method name such as \"$1\" when fixing it.\n</task>\n\n<specification>\n'
    prompt_txt = prompt_former + spec + '</specification>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_OXX_prompt_txt(spec, method):
    prompt_former = '<task>\nThe next method follows specification.\nAnd it has a bug.\nPlease fix it.\nHowever, do not change method names and variable names such as \"$1\" when fixing it.\n</task>\n\n<specification>\n'
    prompt_txt = prompt_former + spec + '</specification>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_XOO_prompt_txt(method):
    prompt_txt = '<task>\nThe next method has a bug.\nPlease fix it.\n</task>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_XOX_prompt_txt(method):
    prompt_txt = '<task>\nThe next method has a bug.\nPlease fix it.\nHowever, do not change variable names such as \"$1\" when fixing it.\n</task>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_XXO_prompt_txt(method):
    prompt_txt = '<task>\nThe next method has a bug.\nPlease fix it.\nHowever, do not change the method name such as \"$1\" when fixing it.\n</task>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt

def create_XXX_prompt_txt(method):
    prompt_txt = '<task>\nThe next method has a bug.\nPlease fix it.\nHowever, do not change method names and variable names such as \"$1\" when fixing it.\n</task>\n\n<method>\n' + method + '\n</method>'
    return prompt_txt



def get_target_projects():
    target_projects=[]
    with open('../data/jsoup/json_data/jsoup_target_id.csv', mode = 'r', encoding="utf-8-sig" ) as file:
        reader = csv.reader(file)
        for row in reader:
            target_projects.append(row)
    # print(target_projects)
    return target_projects

def get_dir_list(input_dir):
    try:
        list = os.listdir(input_dir)
        return list
    except FileNotFoundError:
        print(f"The directory `{input_dir}` doesn't have children dirs.")


# specの整形
def spec_shaping(spec_original):
    spec_txt = []
    for line in spec_original:
        spec_line = re.sub(r'^[\s*/\0]*', '', line) #先頭から " "，"*" ，"/"の三つを削除
        spec_txt.append(spec_line)
    return "".join(spec_txt)


def create_prompt(project_name):
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[3]=="o"):
            print(id[0])
            create_prompt_each(project_name, id[0])




# 4つのメソッドスニペットを取得して8つのプロンプトを作成する
def create_prompt_each(project_name, repo_name):
    print(repo_name)
    spec_path = "../data/" + project_name + "/repo_info/b" +repo_name+ "/spec.txt"
    # try:
    with open(spec_path) as f:
        spec_origin = f.readlines()
    spec = spec_shaping(spec_origin)
    operate_prompt(project_name, "OO", repo_name, spec)
    operate_prompt(project_name, "OX", repo_name, spec)
    operate_prompt(project_name, "XO", repo_name, spec)
    operate_prompt(project_name, "XX", repo_name, spec)
    # except FileNotFoundError:
    #     print ("cant open spec")


#identifierをマスクしているときのプロンプト生成
def operate_prompt(project_name, pattern, repo_name, spec):
    method_path = "../data/" + project_name + "/method_snippet/b" + repo_name+ "/" + pattern + ".txt"
    file_method = open(method_path, "r")
    method = file_method.read()
    file_method.close()
    match pattern:
        case "OO":
            prompt_spec = create_OOO_prompt_txt(spec, method)
            prompt_no_spec = create_XOO_prompt_txt(method)
        case "OX":
            prompt_spec = create_OOX_prompt_txt(spec, method)
            prompt_no_spec = create_XOX_prompt_txt(method)
        case "XO":
            prompt_spec = create_OXO_prompt_txt(spec, method)
            prompt_no_spec = create_XXO_prompt_txt(method)
        case "XX":
            prompt_spec = create_OXX_prompt_txt(spec, method)
            prompt_no_spec = create_XXX_prompt_txt(method)            
    os.makedirs("../data/" + project_name + "/prompt/b" + repo_name, exist_ok=True) #ディレクトリがない場合の作成
    spec_prompt_path = "../data/" + project_name + "/prompt/b" +repo_name+ "/O" + pattern + ".txt"
    non_spec_prompt_path = "../data/" + project_name + "/prompt/b" + repo_name + "/X" + pattern + ".txt"
    with open(spec_prompt_path, mode='w') as f:
        f.write(prompt_spec)
    with open(non_spec_prompt_path, mode='w') as f:
        f.write(prompt_no_spec)





args = sys.argv 
if (len(args) == 1):
    print( "Please input \"ProjectName\"")
else :
    print("Create prompt " + args[1])
    for index in range(len(args) - 1):
        create_prompt(args[index+1])
        print('Finished creating prompts for ' + args[index+1])
    print("Finished")


