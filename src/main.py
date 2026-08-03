import click
from src.modules.ec2 import create_instance, list_instances, terminate_instance

@click.group()
def cli():
    """
    Platform Self-Service CLI
    A tool to manage AWS resources (EC2, S3, Route53) safely.
    """
    pass

@cli.group()
def ec2():
    """Manage EC2 Instances"""
    pass

@ec2.command(name='list')
def ec2_list():
    list_instances()

@ec2.command(name='create')
@click.option('--name', required=True, help='Name tag for the EC2 instance')
@click.option('--owner', required=True, prompt='Owner name', help='Username of the owner')
@click.option('--type', default='t3.micro', help='Instance type (default: t3.micro)')
def ec2_create(name, owner, type):
    create_instance(name=name, owner=owner, instance_type=type)

@ec2.command(name='destroy')
@click.option('--id', required=True, help='Instance ID to terminate')
def ec2_destroy(id):
    """Terminate an EC2 instance"""
    terminate_instance(instance_id=id)

@cli.group()
def s3():
    """Manage S3 Buckets"""
    pass

@cli.group()
def route53():
    """Manage Route53 DNS Zones and Records"""
    pass

if __name__ == '__main__':
    cli()
