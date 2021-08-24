# Lambda Version Cleaner

This script will clean up old versions of a Lambda Function, that aren't linked to an alias. By default, it lists/deletes versions older than 90 days.

## Script Parameters
| Parameter | Default | Purpose |
|    ---    |   ---   |   ----  |
| --region  | us-west-2 | Region the Lambda Functions are deployed in |
| --func-name | _none_ | Name of the Lambda Function |
| --days    | 90 | List/Delete Versions older than this value|
| --no-dry-run | _none_ | When this flag is supplied, script will perform a DELETE. Don't supply this flag to list the versions |

## Example Usage
### List Lambda Versions older than 90 days for "example" function in eu-central-1
    ./lambda_version_cleaner.py --region eu-central-1 --func-name example
  
### Delete Lambda Versions older than 90 days for "example" function in eu-central-1
    ./lambda_version_cleaner.py --region eu-central-1 --func-name exmaple --no-dry-run
