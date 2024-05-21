"""テストを実行して結果を保存する

入力：`data/project_name/pre_embed_method/`，`data/project_name/json_data/methodInfo`，`project_name_for_test/`
出力：`data/project_name/result/`

テストの実行コマンドは`mvn test`

"""


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

def list_writer(file_path, list_txt):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, mode='w', encoding="utf-8") as f:
            f.writelines(list_txt)
    except FileNotFoundError:
        print(dir_path + "の作成に失敗しました．")

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
        

# 8つのパターンについて実行
def run_all_pattern(project_name, repo_num, attempt_num):
    pre_embed_method_dir = "../data/" + project_name + "/pre_embed_method/b" +repo_num+ "/" + attempt_num
    global amount_of_progress
    try:
        all_pattern = [ f for f in os.listdir(pre_embed_method_dir) if os.path.isfile(os.path.join(pre_embed_method_dir, f))] #ファイル名の取得
        for pattern in all_pattern: # OOO.txt
            pre_embed_method_path = pre_embed_method_dir + "/" + pattern
            with open(pre_embed_method_path, "r", encoding="utf-8") as file:
                pre_embed_method = file.readlines()
            pre_embed_method.append("\n")
            only_pattern = pattern.rsplit(".", 1)[0]
            repo_info = get_repo_info(repo_num) 
            package_splits = repo_info[0][0].split(".")# org.jsoup.examples → [org, jsoup, examples]
            package_path = ""
            for package_split in package_splits:
                package_path = package_path + package_split + "/" 
            
            ######################projectで変更#
            target_file_name = "../data/" + project_name + "/repo/b"+repo_num+"/src/main/java/" + package_path +"/"+ repo_info[0][1]
            ######################projectで変更#
            
            embed_method(target_file_name, pre_embed_method , repo_info)
            timeout_flag = run_test(project_name,repo_num, attempt_num, pattern)
            # result_object = get_test_result("jsoup", timeout_flag)
            # store_result(only_pattern, package_name, file_name, method_num, bug_num, attempt_num, result_object)
            original_file_name = "../data/" + project_name + "/repo_info/b" + repo_num +"/Correct.java"
            restore_project(target_file_name, original_file_name)
        # write_result(project_name)
        amount_of_progress += 1
        print(amount_of_progress)
        if(amount_of_progress % 50 == 0):
            write_result_evacuate(project_name)
            print("progress time :" , datetime.datetime.now())
    except NotADirectoryError:
        return

def get_repo_info(repo_num):
    repo_info =[]
    with open('../data/jsoup/repo_info/b'+repo_num+'/method.csv', mode = 'r', encoding="utf-8-sig" ) as file:
        reader = csv.reader(file)
        for row in reader:
            repo_info.append(row)
        print(repo_info)
    return repo_info

##おそらく一緒やけど確認する必要はあり
def embed_method(target_file_name, pre_embed_method, repo_info):
    with open(target_file_name, "r", encoding="utf-8") as file:
        original_file = file.readlines()
    original_file[int(repo_info[0][2])-1 : int(repo_info[0][3])] = pre_embed_method
    list_writer(target_file_name, original_file) # 対象ファイルに埋め込み


def run_test(project_name, repo_num, attempt_num, pattern):
    timeout_flag = False
    # command_cd = "..\\" + project_name + "_for_test\\"

    
    file_path = "../data/"+project_name+"/test_context/b"+repo_num+"/"+attempt_num+"/"+pattern
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    print(file_path)
    with open(file_path, "w") as f:

        command_cd = "../data/" + project_name + "/repo/b"+repo_num
        os.chdir(command_cd)
        test_command = "defects4j test"        
    # test_process = subprocess.Popen(test_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        test_process = subprocess.Popen(test_command, stdout = f, shell=True)
        try:
            test_process.communicate(timeout=40)
        except subprocess.TimeoutExpired:
            print("timeout")
            kill_processes(test_process.pid)
            test_process.kill()
            timeout_flag = True
        # os.chdir("..\\script")
        os.chdir("../../../../script")
    return timeout_flag

#process idを指定してその子プロセスもすべて終了させる
def kill_processes(process_id):
    parent = psutil.Process(process_id)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    parent.kill()

def get_test_result(project_name, timeout_flag):
    if timeout_flag == True:
        return None
    # 仮配列
    result = [
    ["test_set", "tests_run", "failures", "errors", "skipped", "time_elapsed", "test_class"],
    [0,0,0,0,0,0,0]
    ]
    # result_dir_path = "../"+project_name+"/target/surefire-reports"
    result_dir_path = "../"+project_name+"/gson/target/surefire-reports"
    try: 
        result_files = os.listdir(result_dir_path)
        for result_file in result_files:
            result_path = os.path.join(result_dir_path, result_file)
            if os.path.isfile(result_path) and result_path.endswith(".txt"):
                with open(result_path, 'r', encoding="utf-8") as file:
                    result.append(parse_result(file.read()))
        result_array = []
        key = result[0]
        for row in result[2:]:
            # result_dict[row[0]] = dict(zip(result[0][1:], row[1:])) #json用の形に変換
            row_dict = dict(zip(key, row))
            result_array.append(row_dict)
        result_object = json.dumps(result_array, ensure_ascii=False, indent=4)
    except FileNotFoundError: # コンパイルに失敗してレポートが出力できていないとき
        result_object = None
    return result_object

def parse_result(text):
    pattern = r'Test set: (.+)\n-+\nTests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+), Time elapsed: ([\d.]+) s(.+)-- in (.+)\n' ##failureのとき変な奴が入る
    match = re.search(pattern, text)
    if match:
        test_set = match.group(1)
        tests_run = int(match.group(2))
        failures = int(match.group(3))
        errors = int(match.group(4))
        skipped = int(match.group(5))
        time_elapsed = float(match.group(6))
        test_class = match.group(8)
        return [test_set, tests_run, failures, errors, skipped, time_elapsed, test_class]
    else:
        return None


#全部のデータを保存している
def store_result(pattern, package_name, file_name, method_num, bug_num, attempt_num, result_object):
    if(result_object != None):
        OX_result = get_only_result(result_object)
    else:
        OX_result = "compile error"
        result_object = json.dumps("{result:compile error}")
    result = dict(zip(result_dict_key, [package_name, file_name, method_num, bug_num, attempt_num, OX_result]))
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

def get_only_result(result_object):
    failures = 0
    errors = 0
    result_data = json.loads(result_object)
    for obj in result_data:
        failures = failures + obj["failures"]
        errors = errors + obj["errors"]
    if (failures == 0 and errors == 0):
        return "o"
    else :
        return "x"

# 修正結果を埋め込んだプロジェクトをもとの形に復活
def restore_project(target_file_name, original_file_name):
    original_file = open(original_file_name, "r", encoding="utf-8")
    original_src = original_file.read()
    original_file.close()
    with open(target_file_name, "w", encoding="utf-8") as file:
        file.write(original_src)


# 結果の記述
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


def write_result_evacuate(project_name):
    result_evacuate_dir = "../data/" + project_name + "/result/result_evacuate"
    result_writer(result_evacuate_dir + "/OOO.json", result_OOO)
    result_writer(result_evacuate_dir + "/OOX.json", result_OOX)
    result_writer(result_evacuate_dir + "/OXO.json", result_OXO)
    result_writer(result_evacuate_dir + "/OXX.json", result_OXX)
    result_writer(result_evacuate_dir + "/XOO.json", result_XOO)
    result_writer(result_evacuate_dir + "/XOX.json", result_XOX)
    result_writer(result_evacuate_dir + "/XXO.json", result_XXO)
    result_writer(result_evacuate_dir + "/XXX.json", result_XXX)



# def write_detail_result(project_name):
#     result_detail_dir = "../data/" + project_name + "/result" + "/detail"
#     result_writer(result_detail_dir + "/OOO.json", detail_result_OOO)
#     result_writer(result_detail_dir + "/OOX.json", detail_result_OOX)
#     result_writer(result_detail_dir + "/OXO.json", detail_result_OXO)
#     result_writer(result_detail_dir + "/OXX.json", detail_result_OXX)
#     result_writer(result_detail_dir + "/XOO.json", detail_result_XOO)
#     result_writer(result_detail_dir + "/XOX.json", detail_result_XOX)
#     result_writer(result_detail_dir + "/XXO.json", detail_result_XXO)
#     result_writer(result_detail_dir + "/XXX.json", detail_result_XXX)


def result_writer(file_path, list):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, mode='w', encoding="utf-8") as f:
            json.dump(list, f ,ensure_ascii=False, indent=4) 
    except FileNotFoundError:
        print(dir_path + "の作成に失敗しました．")



###########################################################################################
#### 手動test #######################
###########################################################################################


def test_run_test(project_name):
    run_test(project_name)


def test_embed_method():
    pre_embed_method_path = "../data/jsoup/pre_embed_method/org.jsoup.examples/HtmlToPlainText/5/01/OXX.txt"
    # pre_embed_f = open(pre_embed_method_path, "r")
    # pre_embed_method = pre_embed_f.read()
    # pre_embed_f.close()
    with open(pre_embed_method_path, "r", encoding="utf-8") as file:
        pre_embed_method = file.readlines()
    pre_embed_method.append("\n")
    embed_method("../jsoup_for_test/src/main/java/org/jsoup/examples/HtmlToPlainText.java", pre_embed_method, "jsoup", "org.jsoup.examples", "HtmlToPlainText", 5)


def test_get_test_result(project_name):
    result = get_test_result("jsoup_for_test")
    return result 

def test_store_result():
    result = test_get_test_result("jsoup")
    print(result)
    store_result("OOO", "org.jsoup.examples", "HtmlToPlainText", "5", "01", "1", result)
    store_result("OOO", "org.jsoup.examples", "HtmlToPlainText", "5", "01", "1", result)
    store_result("OOO", "org.jsoup.examples", "HtmlToPlainText", "5", "01", "1", result)
    # list_writer("../test/get_result/result_OOO.json", result_OOO)
    with open("../test/get_result/result_OOO_detail.json", "w", encoding="utf-8") as file:
        json.dump(detail_result_OOO, file,ensure_ascii=False, indent=4 )




###########################################################################################
#### 本体 #######################
###########################################################################################


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
# detail_result_OOO = []
# detail_result_OOX = []
# detail_result_OXO = []
# detail_result_OXX = []
# detail_result_XOO = []
# detail_result_XOX = []
# detail_result_XXO = []
# detail_result_XXX = []
# file_path = "../data/jsoup/test_context/f/test.txt"
# dir_path = os.path.dirname(file_path)
# os.makedirs(dir_path, exist_ok=True)
# print(file_path)
# with open(file_path, "w") as f:

#     command_cd = "../data/jsoup/repo/f10"
#     os.chdir(command_cd)
#     test_command = "defects4j test"        
# # test_process = subprocess.Popen(test_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
#     test_process = subprocess.Popen(test_command, stdout = f, shell=True)
#     try:
#         test_process.communicate(timeout=40)
#     except subprocess.TimeoutExpired:
#         print("timeout")
#         kill_processes(test_process.pid)
#         test_process.kill()
#         timeout_flag = True
#     # os.chdir("..\\script")
#     os.chdir("../../../../script")

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
