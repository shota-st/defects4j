"""識別子名の復元をする

テストによる実行をするために，`data/project_name/response/`の識別子名を復元する
また識別子名の復元ができたかどうかを出力する
入力：`data/project_name/response/`，`data/project_name/json_data/identifier_correspondence/`
出力：`data/project_name/pre_embed_method/`，`data/result/success_restore_identifier/`

"""

import os
import sys
import json 
import csv

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

def run(project_name):
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[3]=="o"):
            print(id[0])
            loop_attempt(project_name, id[0])

def loop_attempt(project_name, repo_num):
    attempt_dir = "../data/"+project_name+ "/response/b" +repo_num
    attempt_nums = get_dir_list(attempt_dir)
    for attempt_num in attempt_nums: # 基本3回
        run_all_pattern(project_name, repo_num, attempt_num)

def run_all_pattern(project_name,repo_num, attempt_num):
    response_dir = "../data/" + project_name + "/response/b" +repo_num+ "/" + attempt_num
    all_pattern = [ f for f in os.listdir(response_dir) if os.path.isfile(os.path.join(response_dir, f))] #ファイル名の取得
    for pattern in all_pattern:
        response_path = response_dir + "/" + pattern
        response_f = open(response_path, "r")
        response = response_f.read()
        response_f.close()
        print(pattern)
        only_pattern = pattern.rsplit(".", 1)[0]
        print(pattern)
        embed_method = get_embed_method(only_pattern, response, project_name,repo_num, attempt_num)
        # embed_method = get_embed_method(only_pattern, response, project_name, package_name, file_name, method_num, bug_num, attempt_num)
        output_dir = "../data/" + project_name + "/pre_embed_method/b" + repo_num + "/" + attempt_num
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir + "/" + pattern
        with open(output_path, mode='w') as f:
            f.write(embed_method)

def get_embed_method(pattern, response, project_name, repo_num,  attempt_num):
    match pattern:
        case "OOO":
            return response
        case "OOX":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, OX)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_OOX.append(result)
            return restored_response
        case "OXO":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, XO)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_OXO.append(result)
            return restored_response
        case "OXX":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, XX)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_OXX.append(result)
            return restored_response
        case "XOO":
            return response
        case "XOX":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, OX)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_XOX.append(result)
            return restored_response
        case "XXO":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, XO)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_XXO.append(result)
            return restored_response 
        case "XXX":
            restored_response, success_restore = restore_identifier(response, project_name,repo_num, XX)
            result = dict(zip(result_dict_key, [repo_num, attempt_num, success_restore]))
            result_XXX.append(result)
            return restored_response

# 対象となるjsonのリストを探す
def restore_identifier(response, project_name, repo_num, replace_map):
    for obj in replace_map:
        if obj["fileName"] == "b"+repo_num:
            co_list = obj["list"]
            restored_method, success_restore = restore_method_by_map(response, co_list)
            return restored_method, success_restore

# リストをもとに文字列を変換する
def restore_method_by_map(response_method, map):
    restored_method = response_method
    success_restore = True
    for key, really_name in map.items():
        old_restore_method = restored_method #復元前のメソッド
        restored_method = restored_method.replace(key, really_name) #復元後のメソッド
        if old_restore_method == restored_method and not(really_name in old_restore_method): #復元前と復元後で変化がなかった時は，keyが見つからなかった証拠．
            success_restore = False
    return restored_method, success_restore


# 識別子名の復元の結果
def write_result(project_name):
    result_dir = "../data/" + project_name + "/result/success_restore_identifier"
    result_writer(result_dir + "/OOX.json", result_OOX)
    result_writer(result_dir + "/OXO.json", result_OXO)
    result_writer(result_dir + "/OXX.json", result_OXX)
    result_writer(result_dir + "/XOX.json", result_XOX)
    result_writer(result_dir + "/XXO.json", result_XXO)
    result_writer(result_dir + "/XXX.json", result_XXX)


def result_writer(file_path, list):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, mode='w') as f:
            json.dump(list, f ,ensure_ascii=False, indent=4) 
    except FileNotFoundError:
        print(dir_path + "の作成に失敗しました．")




args = sys.argv 
if (len(args) == 1):
    print( "Please input \"ProjectName\"")   
else :
    print("Restoring identifier names in " + args[1])
    json_root_path = "../data/" + args[1] + "/json_data/identifier_correspondence"
    with open(json_root_path + "/identifier_mask.json", "r") as file:
        XX = json.load(file)
    with open(json_root_path + "/method_mask.json", "r") as file:
        XO = json.load(file)
    with open(json_root_path + "/variable_mask.json", "r") as file:
        OX = json.load(file)
    output_json_root = "../data/" + args[1] + "/json_data/result_embed"
    result_dict_key = [ "repo", "attempt_num", "result"]
    # result_OOO = []
    result_OOX = []
    result_OXO = []
    result_OXX = []
    # result_XOO = []
    result_XOX = []
    result_XXO = []
    result_XXX = []
    for index in range(len(args) - 1):
        run(args[index+1])
        write_result(args[index+1])
        print('Finished creating pre_embed_method for ' + args[index+1])
        
