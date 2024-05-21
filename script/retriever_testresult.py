
import os
import re
import sys
import json 
import subprocess
import datetime
import signal
import psutil
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
    attempt_dir = "../data/"+project_name+ "/test_context/b" +repo_num
    attempt_nums = get_dir_list(attempt_dir)
    for attempt_num in attempt_nums: # 基本3回
        run_all_pattern(project_name, repo_num, attempt_num)
        

def run_all_pattern(project_name, repo_num, attempt_num):
    test_context_dir = "../data/" + project_name + "/test_context/b" +repo_num+ "/" + attempt_num
    try:
        all_pattern = [ f for f in os.listdir(test_context_dir) if os.path.isfile(os.path.join(test_context_dir, f))] #ファイル名の取得
        for pattern in all_pattern: # OOO.txt
            test_context_path = test_context_dir + "/" + pattern
            with open(test_context_path, "r", encoding="utf-8") as file:
                test_context = file.readlines()
            only_pattern = pattern.rsplit(".", 1)[0]
            print(only_pattern)
            result = get_test_result(test_context)
            store_result(only_pattern, repo_num, attempt_num, result)
    except NotADirectoryError:
        return

def get_test_result(text):
    pattern = r"Failing tests:\s*(\d+)"
    match = re.search(pattern, str(text))
    # print("mathdhdhd", match.group(1))
    if match:
        return match.group(1)
    else:
        return ""


def store_result(pattern, repo_num, attempt_num, result):
    result = dict(zip(result_dict_key, [repo_num, attempt_num, result]))
    # tmp_dict = dict(zip(result_dict_key, [package_name, file_name, method_num, bug_num, attempt_num, json.loads(result_object)]))
    match pattern:
        case "OOO":
            # detail_result_OOO.append(tmp_dict)
            result_OOO.append(result) #全リザルトの結果を保持
        case "OOX":
            # detail_result_OOX.append(tmp_dict)
            result_OOX.append(result)
        case "OXO":
            # detail_result_OXO.append(tmp_dict)
            result_OXO.append(result)
        case "OXX":
            # detail_result_OXX.append(tmp_dict)
            result_OXX.append(result)
        case "XOO":
            # detail_result_XOO.append(tmp_dict)
            result_XOO.append(result)
        case "XOX":
            # detail_result_XOX.append(tmp_dict)
            result_XOX.append(result)
        case "XXO":
            # detail_result_XXO.append(tmp_dict)
            result_XXO.append(result)
        case "XXX":
            # detail_result_XXX.append(tmp_dict)
            result_XXX.append(result)

def write_result(project_name):
    result_root_dir = "../data/" + project_name + "/result"
    result_dir = result_root_dir + "/result"
    result_writer(result_dir + "/OOO.json", result_OOO)
    result_writer(result_dir + "/OOX.json", result_OOX)
    result_writer(result_dir + "/OXO.json", result_OXO)
    result_writer(result_dir + "/OXX.json", result_OXX)
    result_writer(result_dir + "/XOO.json", result_XOO)
    result_writer(result_dir + "/XOX.json", result_XOX)
    result_writer(result_dir + "/XXO.json", result_XXO)
    result_writer(result_dir + "/XXX.json", result_XXX)


def result_writer(file_path, list):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, mode='w', encoding="utf-8") as f:
            json.dump(list, f ,ensure_ascii=False, indent=4) 
    except FileNotFoundError:
        print(dir_path + "の作成に失敗しました．")

args = sys.argv 
json_root_path = "../data/jsoup/json_data/methodInfo.json"
# json_root_path = "../data/gson/json_data/methodInfo.json"
result_dict_key = [ "repo", "attempt_num", "result"]
amount_of_progress = 0
result_OOO = []
result_OOX = []
result_OXO = []
result_OXX = []
result_XOO = []
result_XOX = []
result_XXO = []
result_XXX = []
if (len(args) == 1):
    print( "Please input \"ProjectName\"")   
else :
    # print("Restoring identifier names in " + args[1])
    # with open(json_root_path, "r", encoding="utf-8") as file:
    #     method_json = json.load(file)
    for index in range(len(args) - 1):
        print("start time :" , datetime.datetime.now())
        run(args[index+1])
        print("fin time :" , datetime.datetime.now())
        write_result(args[index+1])
        # write_detail_result(args[index+1])
        print('Finished creating responses for ' + args[index+1])
