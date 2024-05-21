"""GPTの修正結果を得る

GPT に`data/project_name/prompt/`のプロンプトを与え結果を出力する
同じプロンプトに対して 3 回の実行を行う

入力：`data/project_name/prompt/`
出力：`data/project_name/response/`

"""

import os
import sys
from openai import OpenAI
import logging as logger
import datetime

client = OpenAI(api_key=os.environ["OPENAI_KUSUMOTOLAB_API_KEY"])

# gpt呼び出し
def get_response_gpt(prompt):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    timeout=60,
    temperature = 0,
    max_tokens = 4096,
    messages=[
        {"role": "system", "content": "Always output only code."},
        {"role": "user", "content": prompt},
    ],
    )
    return response


def get_dir_list(input_dir):
    try:
        list = os.listdir(input_dir)
        return list
    except FileNotFoundError:
        print(f"The directory `{input_dir}` doesn't have children dirs.")

def create_response(project_name):
    target_projects = get_target_projects()
    for id in target_projects:
        if(id[3]=="o"):
            print(id[0])
            get_response_each(project_name, id[0])


def get_response_each(project_name,repo_name):
    prompt_dir = "../data/" + project_name + "/prompt/b" +repo_name
    prompt_patterns = [ f for f in os.listdir(prompt_dir) if os.path.isfile(os.path.join(prompt_dir, f))] #ファイル名の取得
    global attempt
    attempt += 1
    print("attempt ", attempt, " : ", datetime.datetime.now())
    for prompt_pattern in prompt_patterns:
        prompt_path = prompt_dir + "/" + prompt_pattern
        prompt_f = open(prompt_path, "r")
        prompt = prompt_f.read()
        prompt_f.close()
        only_pattern = prompt_pattern.rsplit(".", 1)[0]
        for i in range(3): #3回の試行
            global amount_of_prompt
            amount_of_prompt += 1
            try:
                response = get_response_gpt(prompt)
            except OpenAI.APIError as e:
                logger.error(prompt_path + " is timeout. ")
                continue
            response_path = "../data/" + project_name + "/response/b"+repo_name+ "/" + str(i) + "/" + prompt_pattern
            response_writer(response_path, response.choices[0].message.content.lstrip("```java").rstrip("```"))

#
def response_writer(file_path, txt):
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, mode='w') as f:
            f.write(txt)
    except FileNotFoundError:
        print(dir_path + "の作成に失敗しました．")


#####################################
############ test ###################
#####################################

#temperature=0のときに異なる解答をするのかを検証（10回）
def amount_of_trial_test():
    prompt_path = "../data/jsoup/prompt/org.jsoup.examples/HtmlToPlainText/5/01/OXX.txt"
    prompt_f = open(prompt_path, "r")
    prompt = prompt_f.read()
    prompt_f.close()
    for i in range(10):
        print(prompt)
        response = get_response_gpt(prompt)
        response_writer("../test/response_amount_of_attempts/" + str(i) + ".txt", response.choices[0].message.content.lstrip("```java").rstrip("```"))


#適切なsystem promptの検証
def system_prompt_test():
    # path_list =[
    # "prompt_1_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/1/OXX.txt",
    # "prompt_2_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/2/OXX.txt",
    # "prompt_3_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/3/OXX.txt",
    # "prompt_4_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/1/OXX.txt",
    # "prompt_5_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/2/OXX.txt",
    # "prompt_6_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/1/XXX.txt",
    # "prompt_7_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/2/XXX.txt",
    # "prompt_8_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/3/XXX.txt",
    # "prompt_9_dir" = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/1/XXX.txt",
    # "prompt_10_di"r = "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/2/XXX.txt"
    # ]
    path_list =[
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/1/OXX.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/2/OXX.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/3/OXX.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/1/OXX.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/2/OXX.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/1/OXO.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/2/OXO.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/3/OXO.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/1/OXO.txt",
    "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/2/OXO.txt",
    # "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/1/XXX.txt",
    # "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/2/XXX.txt",
    # "../data/jsoup/prompt/org.jsoup.nodes/Attribute/2/3/XXX.txt",
    # "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/1/XXX.txt",
    # "../data/jsoup/prompt/org.jsoup.nodes/Attribute/5/2/XXX.txt"
    ]
    for i, path_name in enumerate(path_list):
        prompt_f = open(path_name, "r")
        prompt = prompt_f.read()
        prompt_f.close()
        response = get_response_gpt(prompt)
        response_writer("../test/response/model-0125-test/" + str(i) + ".txt", response.choices[0].message.content.lstrip("```java").rstrip("```"))

#####################################

args = sys.argv 
# amount_of_trial_test()
print("start time :" , datetime.datetime.now())
attempt = 0
# system_prompt_test()
# print("fin time :" , datetime.datetime.now())
amount_of_prompt = 0
if (len(args) == 1):
    print( "Please input \"ProjectName\"")
else :
    print("Create response by gpt")
    for index in range(len(args) - 1):
        create_response(args[index+1])
        # get_response_each("jsoup", "org.jsoup.helper", "AuthenticationHandler","1", "1")
        print("fin time :" , datetime.datetime.now())
        print("amount of prompt is : " , str(amount_of_prompt))
        print('Finished creating responses for ' + args[index+1])

