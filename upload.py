import argparse
from zipfile import ZipFile
import subprocess


lambdas = {
    "analyze": {
        "config": {
            "handler": "analyze.lambda_handler",
            "timeout": 10,  # seconds
            "runtime": "python3.6",
            "role": "arn:aws:iam::693859464061:role/lambda-repository"
        },
        "src": [
            "analyze.py",
            "block.py",
            "column.py",
            "instance.py",
            "item.py",
            "receipt.py",
            "util.py",
        ]
    },
    "url": {
        "config": {
            "handler": "url.handler",
            "timeout": 3,
            "runtime": "nodejs10.x",
            "role": "arn:aws:iam::693859464061:role/lambda-repository"
        },
        "src": ["url.js"]
    }
}


def upload(name, update_config=False, create_function=False):
    print("Processing Lambda '{}'...".format(name))
    zip_path = "./zips/{}.zip".format(name)
    with ZipFile(zip_path, "w") as z:
        for filename in lambdas[name]["src"]:
            # don't include "src" folder in zip
            z.write("src/" + filename, arcname=filename)
    print("created zip file")

    arguments = [
        "aws", "lambda", "create-function" if create_function else "update-function-code",
        "--function-name", name,
        "--zip-file", "fileb://" + zip_path
    ]
    if create_function:
        arguments.extend([
            "--runtime", lambdas[name]["config"]["runtime"],  # "nodejs10.x" | "python3.6"
            "--role", lambdas[name]["config"]["role"],  # as ARN, e.g.: arn:aws:iam::693859464061:role/my-role
            "--handler", lambdas[name]["config"]["handler"],  # in the format "file-without-suffix.method-name"
            "--timeout", str(lambdas[name]["config"]["timeout"])  # integer in seconds
        ])
    print(subprocess.check_output(arguments))

    if update_config:
        print(subprocess.check_output([
            "aws", "lambda", "update-function-configuration",
            "--function-name", name,
            "--handler", lambdas[name]["config"]["handler"],
            "--timeout", str(lambdas[name]["config"]["timeout"]),
        ]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uploading a Lambda Function")
    parser.add_argument("name", default=None, nargs="?",
                        help="specify which lambda to upload.")
    parser.add_argument("--update_config", action="store_true", default=False,
                        help="set this flag when the handler function has changed.")
    parser.add_argument("--create_function", action="store_true", default=False,
                        help="set if function does not exist yet and has to be newly created")
    args = parser.parse_args()

    for n in [args.name] if args.name is not None else lambdas.keys():
        upload(name=n, update_config=args.update_config, create_function=args.create_function)
