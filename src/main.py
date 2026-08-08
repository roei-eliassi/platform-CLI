import click

from src.commands.ec2 import ec2_cli
from src.commands.s3 import s3_cli


@click.group()
def cli():
    """
    Platform Self-Service CLI

    A tool to manage AWS resources (EC2, S3, Route53) safely.
    """
    pass


cli.add_command(ec2_cli)
cli.add_command(s3_cli)


if __name__ == "__main__":
    cli()
