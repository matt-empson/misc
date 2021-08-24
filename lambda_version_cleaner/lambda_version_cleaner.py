#!/usr/bin/env python

"""Lambda Version Cleaner
This script allows the user to list versions of a Lambda Function that are older than a specified number of days
(default 90 days), or delete those versions.

By default the script will list versions. If the --no-dry-run flag is specified, Lambda Functions will be DELETED!!!
"""

import argparse
from datetime import datetime, timedelta

import boto3

cmd_options = argparse.ArgumentParser(description="List or Delete old Lambda Versions")
cmd_options.add_argument(
    "--region",
    type=str,
    help="Region that the Lambda's are located in. Defaults to us-west-2.",
    default="us-west-2",
)
cmd_options.add_argument("--func-name", type=str, help="Name of the Lambda Function")
cmd_options.add_argument(
    "--days",
    type=int,
    help="Lambda Functions older than this number of days will be listed/deleted. Defaults to 90 days.",
    default=90,
)
cmd_options.add_argument(
    "--no-dry-run",
    help="When this flag is specified, the script DELETES old Lambda Versions.",
    default=False,
    action="store_true",
)

args = cmd_options.parse_args()

date = datetime.now() - timedelta(days=args.days)

lambda_client = boto3.client("lambda", region_name=args.region)

aliases = [
    alias
    for alias in lambda_client.list_aliases(FunctionName=args.func_name)["Aliases"]
]

paginator = lambda_client.get_paginator("list_versions_by_function")

paginator_iterator = paginator.paginate(FunctionName=args.func_name)

functions = [
    func
    for item in paginator_iterator
    for func in item["Versions"]
    if func["LastModified"] <= str(date)
]

purge_list = []

if len(functions) > 0:
    print(f"Getting versions for {args.func_name} {args.days} days or older")
    for func in functions:
        purge_list.append(func["Version"])
        for alias in aliases:
            if (
                alias["FunctionVersion"] == func["Version"]
                or func["Version"] == "$LATEST"
            ):
                print(
                    f'\t- Version {func["Version"]} is aliased as {alias["Name"]}. WON\'T be deleted'
                )
                purge_list.remove(func["Version"])
                break
else:
    print(
        f"No Lambda Function versions for {args.func_name} older than {args.days} days."
    )

if len(purge_list) == 0:
    print("Nothing to list or delete. Exiting. No changes made.")
else:
    if not args.no_dry_run:
        print(f"\nThe following versions of {args.func_name} can be deleted.")
        print(purge_list)

    if args.no_dry_run:
        print(
            f"\nThe following versions of {args.func_name} WILL be PERMANENTLY DELETED."
        )
        print(purge_list)
        confirm = input("Do you want to continue? (Y/N)" or "N")

        if confirm != str.lower("y"):
            print("Exiting. No changes made")
        else:
            print("DELETING LAMBDA VERSIONS:")
            for version in purge_list:
                try:
                    print(f"Deleting version {version} of {args.func_name}")
                    del_function = lambda_client.delete_function(
                        FunctionName=args.func_name, Qualifier=version
                    )
                    print(f"{del_function}\n")
                except:
                    print("Error deleting version")
