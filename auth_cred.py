import argparse
import json

parse = argparse.ArgumentParser(description="select attribute (--attr) from the received json (--sjson) and retrieve the value with the key set as parameter (--key)")

parse.add_argument("--key", required=True)
parse.add_argument("--sjson", required=True)
parse.add_argument("--attr", required=True)

args = parse.parse_args()

if not args.key or not args.sjson or not args.attr:
    print("error: need the parameter --attr, --key and --sjson")
    exit(1)

try:
    body = json.loads(args.sjson)
except Exception as e:
    print(str(e))
    exit(1)

print(body[args.attr][args.key].strip(' ').strip('\n'))
