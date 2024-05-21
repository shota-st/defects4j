"""
defects4jから実験の対象とするプロジェクト群を回収してくる
対象となるプロジェクトに対して，
`defects4j checkout -p jsoup -v b1 -w ../repo/jsoup/b1/`

- 対象
    - project: jsoup
    - bug: 1メソッド内で完結
    - 仕様: javadocが存在

必要な構成要素
- 対象となるプロジェクトを指定して取得
    - バージョン番号さえわかればよい
    - modified_classesを見れば1ファイルということは分かる
    - patchesを見て複数メソッドにわたるかどうかを判定可能
    
92ぐらい目で見た方が早そう
いったん候補は目で見た
"""

import csv
import subprocess
import os

def main():
    do_checkout()
    do_mkdir()
    make_files()
    # converter_java()

def do_checkout():
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[1]=="o" and not(id[2]=="x")):
            # print(id[0])
            checkout_run(id[0])

def checkout_run(str):
    # command_bug = "defects4j checkout -p Jsoup -v " +str+ "b -w ../data/jsoup/repo/b" +str
    # command_bug = "defects4j checkout -p Gson -v " +str+ "b -w ../data/gson/repo/b" +str
    command_bug = "defects4j checkout -p Math -v " +str+ "b -w ../data/math/repo/b" +str
    # command_fix = "defects4j checkout -p Jsoup -v " +str+ "f -w ../data/jsoup/repo/f" +str
    # command_fix = "defects4j checkout -p Gson -v " +str+ "f -w ../data/gson/repo/f" +str
    command_fix = "defects4j checkout -p Math -v " +str+ "f -w ../data/math/repo/f" +str
    do_checkout_bug_process = subprocess.Popen(command_bug, shell=True)
    # test_process = subprocess.Popen(test_command,shell=True)
    try:
        do_checkout_bug_process.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        print("timeout")
        kill_processes(do_checkout_bug_process.pid)
        do_checkout_bug_process.kill()
        timeout_flag = True
    
    do_checkout_fix_process = subprocess.Popen(command_fix, shell=True)
    try:
        do_checkout_fix_process.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        print("timeout")
        kill_processes(do_checkout_fix_process.pid)
        do_checkout_fix_process.kill()
        timeout_flag = True
    

def do_mkdir():
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[1]=="o" and not(id[2]=="x")):
            # print(id[0])
            mkdir_run(id[0])

def mkdir_run(str):
    # command = "mkdir ../data/jsoup/repo_info/b" +str
    # command = "mkdir ../data/gson/repo_info/b" +str
    command = "mkdir ../data/math/repo_info/b" +str
    do_process = subprocess.Popen(command, shell=True)
    try:
        do_process.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        print("timeout")
        kill_processes(do_process.pid)
        do_process.kill()
        timeout_flag = True


def make_files():
    # input_dir = "../data/jsoup/repo_info"
    # input_dir = "../data/gson/repo_info"
    input_dir = "../data/math/repo_info"
    reponames = get_dir_list(input_dir)
    file_names = ["method.csv", "Mutate.java", "method.txt", "spec.txt", "Correct.java"]
    for reponame in reponames:
        # output = "../data/jsoup/repo_info/" + reponame + "/"
        # output = "../data/gson/repo_info/" + reponame + "/"
        output = "../data/math/repo_info/" + reponame + "/"
        for name in file_names:
            f = open(output + name, mode="w")
            f.close()
    

def get_dir_list(input_dir):
    try:
        list = os.listdir(input_dir)
        print(list)
        return list
    except FileNotFoundError:
        print(f"The directory `{input_dir}` doesn't have children dirs.")

def converter_java():
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[3]=="o"):
            print(id[0])
            do_converte(id[0])
            
def do_converte(str):
    method_src = "../data/jsoup/repo_info/b" +str+ "/method.txt"
    output = "../data/jsoup/repo_info/b" +str+ "/Mutate.java"
    with open(method_src, mode="r") as f:
        method = f.read()
        with open(output, mode="w") as outfile:
            java_txt = "public class Mutate{\n\n" + method + "\n\n}"
            # print(str, "\n\n" , java_txt) 
            outfile.write(java_txt)
            


def get_target_projects():
    target_projects=[]
    # with open('../data/jsoup/json_data/jsoup_target_id.csv', mode = 'r', encoding="utf-8-sig" ) as file:
    # with open('../data/gson/meta_data/gson.csv', mode = 'r', encoding="utf-8-sig" ) as file:
    with open('../data/math/meta_data/math.csv', mode = 'r', encoding="utf-8-sig" ) as file:
        reader = csv.reader(file)
        for row in reader:
            target_projects.append(row)
    # print(target_projects)
    return target_projects

main()

# command_bug = "defects4j info -p Jsoup" 
# do_checkout_bug_process = subprocess.Popen(command_bug, shell=True)
# # test_process = subprocess.Popen(test_command,shell=True)
# try:
#     do_checkout_bug_process.communicate(timeout=40)
# except subprocess.TimeoutExpired:
#     print("timeout")
#     kill_processes(do_checkout_bug_process.pid)
#     do_checkout_bug_process.kill()
#     timeout_flag = True