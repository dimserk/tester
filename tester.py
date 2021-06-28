import os
import sys
import yaml
import argparse
import subprocess
from math import ceil

# Ключевые строки словаря с тестом
name_key          = "name"
pre_command_key   = "pre_command"
command_key       = "command"
after_command_key = "after_command"
expected_key      = "expected"

fail_string = "\033[41m\033[37m\033[4m Failed \033[0m"
pass_string = "\033[42m\033[37m\033[4m Passed \033[0m"

splitter_len = 79

def validate_tests(tests):
    valid_tests = []

    for test in tests:
        # Обязательные параметры теста
        if expected_key not in test:
            continue

        if command_key not in test:
            continue

        # Необязательные параметры теста
        if pre_command_key not in test:
            test[pre_command_key] = None

        if after_command_key not in test:
            test[after_command_key] = None

        if name_key not in test:
            test[name_key] = None

        valid_tests.append(test)

    return valid_tests

def e_call(command):
    if command == None:
        return None
    else:
        return subprocess.run(command,
            shell=True,
            capture_output=True)

def log(stream, result):
    stream.write("{}".format(result.stdout.decode("utf-8") 
        if len(result.stdout) != 0 else "\n"))

    if len(result.stderr) != 0:
        stream.write("stderr:\n{}\n".format(result.stderr.decode("utf-8")))

def log_test(stream, p_res, res, a_res, test):
    if (p_res != None):
        stream.write("Pre command: {}\n".format(test[pre_command_key]))
        log(stream, p_res)
        stream.write("\n" + "=" * 5 + ">\n\n")


    stream.write("Command: {}\n".format(test[command_key]))
    log(stream, res)
    stream.write("return:   {}\nexpected: {}\n".format(
        res.returncode,
        test[expected_key]
    ))

    if (a_res != None):
        stream.write("\n" + "=" * 5 + ">\n\n")
        stream.write("After command: {}\n".format(test[after_command_key]))
        log(stream, a_res)

    stream.write("\n" + "=" * splitter_len + "\n\n")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Test util")
    argparser.add_argument("--no-log", "-n", help="turn off logging",
        action='store_true')
    argparser.add_argument("--test-dir", "-t",
        help="point to tests dir [default .]", default=".")
    args = argparser.parse_args()

    # Получение всех файлов, находящихся в одной директории с этим файлом
    os.chdir(os.path.split(os.path.abspath(sys.argv[0]))[0])
    try:
        all_files = os.listdir(args.test_dir)
    except FileNotFoundError:
        print(f"Can not look for tests at {args.test_dir}")
        sys.exit(1)

    if all_files.count == 0:
        print("No test groups found")
        exit(1)

    test_files = [file for file in all_files 
        if file.find(".yml") != -1 or file.find(".yaml") != -1]

    for test_file in test_files:
        with open(test_file) as yaml_config:
            tests = yaml.load(yaml_config, Loader=yaml.CLoader)

        test_group_name = os.path.splitext(os.path.basename(test_file))[0]
        print(f"Test group - {test_group_name}")

        tests = validate_tests(tests)

        total_tests = len(tests)
        print(f"Found {total_tests} tests")

        test_log_name = f"{test_group_name}_log.txt"
        if not args.no_log and os.path.exists(test_log_name):
            os.remove(test_log_name)

        passed_tests = 0
        for i, test in enumerate(tests, start=1):
            pre_res = None
            res     = None
            aft_res = None

            pre_res = e_call(test[pre_command_key])

            res = e_call(test[command_key])
            test_result = res.returncode == test[expected_key]

            aft_res = e_call(test[after_command_key])

            # Вывод информации в консоль
            print("-" * splitter_len + "\n{:>3}/{:<3} {} {}".format(
                i,
                total_tests,
                pass_string if test_result else fail_string,
                test[name_key] if test[name_key] != None else ""
            ))

            if test_result:
                passed_tests += 1

            if not args.no_log:
                with open(test_log_name, "a") as log_file:
                    log_test(log_file, pre_res, res, aft_res, test)

        print("-" * splitter_len)
        print(f"{ceil(passed_tests / total_tests * 100)}% passed", end="\n\n")
