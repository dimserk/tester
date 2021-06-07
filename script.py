# import os
# import subprocess
# import json

# fl = os.listdir(".")


# with open("res.txt", "w") as fout:
#     res = subprocess.run(["./a.out", "1"], stdout=fout)

# print("./a.out 1:", res.returncode)
# print("listdir()", fl)

# res = subprocess.run(["diff", "test.c", "script.py"], stdout=subprocess.DEVNULL)

# print("diff:", res.returncode)

# red_underline = "\033[31m\033[4mmessage\033[0m"
# green_underline = "\033[33m\033[4mmessage\033[0m"

# with open("test_data.json") as jfile:
#     data = json.load(jfile)

# print(data)

# for item in data:
#     print(item["file"], item["code"])

fail_string = "\033[41m\033[37m\033[4m Failed \033[0m"
pass_string = "\033[42m\033[37m\033[4m Passed \033[0m"

import subprocess
def e_call(command):
    if command == None:
        return None
    else:
        return subprocess.run(command,
            shell=True,
            capture_output=True)

import sys
import yaml

yaml_config_filename = "tests.yml"
tese_log_filename = "test_log.txt"

pre_command_key = "pre_command"
command_key = "command"
after_command_key = "after_command"
name_key = "name"
expected_key = "expected"

def _log(stream, result):
    stream.write("stdout:\n{}\nstderr:\n{}\n".format(
        result.stdout.decode("utf-8") if len(result.stdout) != 0 else "None\n",
        result.stderr.decode("utf-8") if len(result.stderr) != 0 else "None\n"
    ))

def log(stream, p_res, res, a_res, test):
    if (p_res != None):
        stream.write("Pre command: {}\n".format(test[pre_command_key]))
        _log(stream, p_res)
        stream.write("\n" + "-" * 40 + "\n\n")


    stream.write("Command: {}\n".format(test[command_key]))
    _log(stream, res)
    stream.write("return:   {}\nexpected: {}\n".format(
        res.returncode,
        test[expected_key]
    ))

    if (a_res != None):
        stream.write("\n" + "-" * 40 + "\n\n")
        stream.write("After command: {}\n".format(test[after_command_key]))
        _log(stream, a_res)

    stream.write("\n" + "=" * 79 + "\n\n")


if __name__ == "__main__":
    with open(yaml_config_filename) as yaml_config:
        tests = yaml.load(yaml_config, Loader=yaml.CLoader)

    total_tests = len(tests)
    print(f"Found {total_tests} tests")

    # TODO Validate tests
    # TODO print Valid tests

    log_file = open("log.txt", "w")

    i = 1
    for test in tests:
        pre_res = None
        res     = None
        aft_res = None

        if pre_command_key in  test:
            pre_res = e_call(test[pre_command_key])

        res = e_call(test[command_key])
        test_result = res.returncode

        if after_command_key in test:
            aft_res = e_call(test[after_command_key])

        log(log_file, pre_res, res, aft_res, test)

        # Вывод информации в консоль
        print("-" * 80)
        print("{:>3}/{:<3}".format(i, total_tests), end=' ')
        i += 1

        if test_result == test[expected_key]:
            print(pass_string, end=' ')
        else:
            print(fail_string, end=' ')

        if name_key in test:
            print(test[name_key])

    log_file.close()

    # log_file = open("log.txt", "w")

    # log_file.write(f"Command: {sys.argv[1]}\n")

    # res = e_call(sys.argv[1])
    # if res.returncode == 0:
    #     print("Passed")
    # else:
    #     print("Failed")

    # log_file.write(f"stdout: {res.stdout.decode('utf-8')}\n")
    # log_file.write(f"stderr: {res.stderr.decode('utf-8')}\n")

    # log_file.write(f"command_finished\n")

    # log_file.close()
