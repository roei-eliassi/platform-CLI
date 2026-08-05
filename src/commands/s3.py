import os
import click
from tabulate import tabulate
from botocore.exceptions import ClientError
from src.utils.aws import get_client, get_resource

TAG_KEY = "CreatedBy"
TAG_VALUE = "platform-cli"

def get_bucket_tags(s3_client, bucket_name):
    try:
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        return {tag['Key']: tag['Value'] for tag in response.get('TagSet', [])}
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchTagSet':
            return {}
        return {}

def is_cli_bucket(s3_client, bucket_name):
    tags = get_bucket_tags(s3_client, bucket_name)
    return tags.get(TAG_KEY) == TAG_VALUE

def get_cli_buckets(s3_client):
    try:
        response = s3_client.list_buckets()
        cli_buckets = []
        
        for bucket in response.get('Buckets', []):
            name = bucket['Name']
            tags = get_bucket_tags(s3_client, name)
            
            if tags.get(TAG_KEY) == TAG_VALUE:
                cli_buckets.append({
                    'Name': name,
                    'Owner': tags.get('Owner', 'N/A'),
                    'CreationDate': bucket['CreationDate'].strftime("%Y-%m-%d %H:%M:%S")
                })
        return cli_buckets
    except Exception as e:
        click.secho(f"Error fetching buckets: {e}", fg="red")
        return []

def create_bucket(bucket_name, owner, access_type=None):
    if not owner or not owner.strip():
        click.secho("Error: Owner name is required!", fg="red")
        return

    if not access_type:
        access_type = click.prompt(
            "Select bucket access type (Private is default)",
            type=click.Choice(['private', 'public'], case_sensitive=False),
            default='private'
        )

    access_type = access_type.lower()
    is_public = (access_type == 'public')

    if is_public:
        confirm = click.prompt(
            "WARNING: You are creating a PUBLIC bucket. Are you sure? (yes/no)",
            type=str
        ).strip().lower()

        if confirm != "yes":
            click.secho("Bucket creation cancelled.", fg="yellow")
            return

    s3_client = get_client('s3')
    region = s3_client.meta.region_name

    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )

        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': TAG_KEY, 'Value': TAG_VALUE},
                    {'Key': 'Owner', 'Value': owner}
                ]
            }
        )

        if is_public:
            s3_client.delete_public_access_block(Bucket=bucket_name)
            click.secho(f"Successfully created PUBLIC S3 bucket '{bucket_name}' for Owner '{owner}'", fg="green")
        else:
            click.secho(f"Successfully created PRIVATE S3 bucket '{bucket_name}' for Owner '{owner}'", fg="green")

    except ClientError as e:
        click.secho(f"Error creating bucket: {e.response['Error']['Message']}", fg="red")
    except Exception as e:
        click.secho(f"Error creating bucket: {e}", fg="red")

def list_buckets():
    s3_client = get_client('s3')
    buckets = get_cli_buckets(s3_client)

    if not buckets:
        click.echo("No S3 buckets found created by platform-cli.")
        return

    table_data = [
        [b['Name'], b['Owner'], b['CreationDate']]
        for b in buckets
    ]

    headers = ["Bucket Name", "Owner", "Creation Date"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

def upload_file(bucket_name, file_path, object_name=None):
    s3_client = get_client('s3')

    if not is_cli_bucket(s3_client, bucket_name):
        click.secho(f"Error: Bucket '{bucket_name}' was not found or was not created by platform-cli!", fg="red")
        return

    if not os.path.exists(file_path):
        click.secho(f"Error: Local file '{file_path}' does not exist!", fg="red")
        return

    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        click.secho(f"Uploading '{file_path}' to bucket '{bucket_name}'...", fg="yellow")
        s3_client.upload_file(file_path, bucket_name, object_name)
        click.secho(f"Successfully uploaded '{object_name}' to bucket '{bucket_name}'!", fg="green")
    except Exception as e:
        click.secho(f"Error uploading file: {e}", fg="red")

def delete_bucket(bucket_name):
    s3_client = get_client('s3')
    s3_resource = get_resource('s3')

    if not is_cli_bucket(s3_client, bucket_name):
        click.secho(f"Error: Bucket '{bucket_name}' was not found or was not created by platform-cli!", fg="red")
        return

    try:
        bucket = s3_resource.Bucket(bucket_name)
        click.secho(f"Deleting all objects inside bucket '{bucket_name}'...", fg="yellow")
        bucket.objects.all().delete()
        bucket.delete()
        click.secho(f"Successfully deleted S3 bucket '{bucket_name}'!", fg="green")
    except Exception as e:
        click.secho(f"Error deleting bucket: {e}", fg="red")
