import click

from services.ec2_service import (
    create_instance,
    list_instances,
    start_instance,
    stop_instance,
    terminate_instance
)


@click.group(name="ec2")
def ec2_cli():
    """Manage EC2 instances."""
    pass


@ec2_cli.command(name="list")
def ec2_list():
    """List all CLI-managed EC2 instances."""
    list_instances()


@ec2_cli.command(name="create")
@click.option(
    "--name",
    required=True,
    help="Name tag for the EC2 instance."
)
@click.option(
    "--owner",
    required=True,
    prompt="Owner name",
    help="Username of the owner."
)
@click.option(
    "--type",
    "instance_type",
    default="t3.micro",
    help="Instance type: t3.micro or t3.small. Default: t3.micro."
)
def ec2_create(name, owner, instance_type):
    """Create a new EC2 instance."""
    create_instance(
        name=name,
        owner=owner,
        instance_type=instance_type
    )


@ec2_cli.command(name="start")
@click.option(
    "--instance-id",
    required=True,
    help="EC2 instance ID to start."
)
def ec2_start(instance_id):
    """Start a CLI-managed EC2 instance."""
    start_instance(instance_id=instance_id)


@ec2_cli.command(name="stop")
@click.option(
    "--instance-id",
    required=True,
    help="EC2 instance ID to stop."
)
def ec2_stop(instance_id):
    """Stop a CLI-managed EC2 instance."""
    stop_instance(instance_id=instance_id)


@ec2_cli.command(name="delete")
@click.option(
    "--instance-id",
    required=True,
    help="EC2 instance ID to terminate."
)
def ec2_delete(instance_id):
    """Terminate a CLI-managed EC2 instance."""
    terminate_instance(instance_id=instance_id)
