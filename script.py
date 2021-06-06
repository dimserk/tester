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
        if pre_command_key in  test:
            result = e_call(test[pre_command_key])
            log_file.write("Pre command:\n")
            log_file.write(result.stdout.decode("utf-8") + "\n")
            log_file.write(result.stderr.decode("utf-8") + "\n")
            log_file.write("\n")

        result = e_call(test[command_key])
        log_file.write(result.stdout.decode("utf-8") + "\n")
        log_file.write(result.stderr.decode("utf-8") + "\n")
        log_file.write("return: " + str(result.returncode)
             + " expected: " + str(test[expected_key]))
        log_file.write("\n")
        test_result = result.returncode

        if after_command_key in test:
            result = e_call(test[after_command_key])
            log_file.write("After command:\n")
            log_file.write(result.stdout.decode("utf-8") + "\n")
            log_file.write(result.stderr.decode("utf-8") + "\n")
            log_file.write("\n")

        log_file.write("=" * 80 + "\n")

        print("=" * 80)
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
