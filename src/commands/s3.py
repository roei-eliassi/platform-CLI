import click

from services.s3_service import (
    create_bucket,
    list_buckets,
    upload_file,
    delete_bucket
)


@click.group(name="s3")
def s3_cli():
    """Manage S3 buckets."""
    pass


@s3_cli.command(name="list")
def s3_list():
    """List all CLI-managed S3 buckets."""
    list_buckets()


@s3_cli.command(name="create")
@click.option(
    "--name",
    required=True,
    help="Name of the S3 bucket."
)
@click.option(
    "--owner",
    required=True,
    prompt="Owner name",
    help="Username of the bucket owner."
)
@click.option(
    "--access-type",
    type=click.Choice(
        ["private", "public"],
        case_sensitive=False
    ),
    help="Bucket access type: private or public."
)
def s3_create(name, owner, access_type):
    """Create a new S3 bucket."""
    create_bucket(
        bucket_name=name,
        owner=owner,
        access_type=access_type
    )


@s3_cli.command(name="upload")
@click.option(
    "--bucket",
    required=True,
    help="Target S3 bucket name."
)
@click.option(
    "--file",
    "file_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to the local file to upload."
)
@click.option(
    "--key",
    help="Optional object name in S3. Defaults to the file name."
)
def s3_upload(bucket, file_path, key):
    """Upload a file to a CLI-managed S3 bucket."""
    upload_file(
        bucket_name=bucket,
        file_path=file_path,
        object_name=key
    )


@s3_cli.command(name="delete")
@click.option(
    "--name",
    required=True,
    help="Name of the S3 bucket to delete."
)
def s3_delete(name):
    """Delete a CLI-managed S3 bucket and all its contents."""
    delete_bucket(bucket_name=name)
