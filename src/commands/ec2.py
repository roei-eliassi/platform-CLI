import click
from tabulate import tabulate
from src.utils.aws import get_client, get_resource

TAG_KEY = "CreatedBy"
TAG_VALUE = "platform-cli"
MAX_INSTANCES = 2
ALLOWED_INSTANCE_TYPES = ["t3.micro", "t3.small"]

def get_latest_ubuntu_ami(ssm_client):
    parameter_name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
    response = ssm_client.get_parameter(Name=parameter_name)
    return response['Parameter']['Value']

def get_cli_instances(ec2_resource):
    filters = [
        {'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]},
        {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopped']}
    ]
    return list(ec2_resource.instances.filter(Filters=filters))

def get_cli_instance_by_id(ec2_resource, instance_id):
    instances = get_cli_instances(ec2_resource)
    for inst in instances:
        if inst.id == instance_id:
            return inst
    return None

def create_instance(name, owner, instance_type="t3.micro"):
    if instance_type not in ALLOWED_INSTANCE_TYPES:
        allowed_str = ", ".join(ALLOWED_INSTANCE_TYPES)
        click.secho(f"Error: Only instance types [{allowed_str}] are allowed!", fg="red")
        return

    if not owner or not owner.strip():
        click.secho("Error: Owner name is required!", fg="red")
        return

    ec2_resource = get_resource('ec2')
    ssm_client = get_client('ssm')

    existing_instances = get_cli_instances(ec2_resource)
    if len(existing_instances) >= MAX_INSTANCES:
        click.secho(f"Error: Quota limit reached! Maximum allowed instances: {MAX_INSTANCES}", fg="red")
        return

    ami_id = get_latest_ubuntu_ami(ssm_client)

    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name},
                    {'Key': 'Owner', 'Value': owner},
                    {'Key': TAG_KEY, 'Value': TAG_VALUE}
                ]
            }
        ]
    )

    instance = instances[0]
    click.secho(f"Successfully created EC2 instance '{name}' ({instance_type}) (ID: {instance.id}) for Owner '{owner}'", fg="green")

def list_instances():
    ec2_resource = get_resource('ec2')
    instances = get_cli_instances(ec2_resource)

    if not instances:
        click.echo("No instances found created by platform-cli.")
        return

    table_data = []
    for inst in instances:
        name = "N/A"
        owner = "N/A"
        if inst.tags:
            for tag in inst.tags:
                if tag['Key'] == 'Name':
                    name = tag['Value']
                elif tag['Key'] == 'Owner':
                    owner = tag['Value']

        table_data.append([
            inst.id,
            name,
            owner,
            inst.instance_type,
            inst.state['Name'],
            inst.public_ip_address or "N/A"
        ])

    headers = ["Instance ID", "Name", "Owner", "Type", "State", "Public IP"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

def start_instance(instance_id):
    ec2_resource = get_resource('ec2')
    ec2_client = get_client('ec2')

    instance = get_cli_instance_by_id(ec2_resource, instance_id)
    if not instance:
        click.secho(f"Error: Instance '{instance_id}' was not found or was not created by platform-cli!", fg="red")
        return

    if instance.state['Name'] == 'running':
        click.secho(f"Instance '{instance_id}' is already running.", fg="yellow")
        return

    try:
        instance.start()
        click.secho(f"Starting instance '{instance_id}'... Please wait.", fg="yellow")

        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])

        click.secho(f"Successfully started instance '{instance_id}'.", fg="green")
    except Exception as e:
        click.secho(f"Error starting instance: {e}", fg="red")

def stop_instance(instance_id):
    ec2_resource = get_resource('ec2')
    ec2_client = get_client('ec2')

    instance = get_cli_instance_by_id(ec2_resource, instance_id)
    if not instance:
        click.secho(f"Error: Instance '{instance_id}' was not found or was not created by platform-cli!", fg="red")
        return

    if instance.state['Name'] == 'stopped':
        click.secho(f"Instance '{instance_id}' is already stopped.", fg="yellow")
        return

    try:
        instance.stop()
        click.secho(f"Stopping instance '{instance_id}'... Please wait.", fg="yellow")

        waiter = ec2_client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])

        click.secho(f"Successfully stopped instance '{instance_id}'.", fg="green")
    except Exception as e:
        click.secho(f"Error stopping instance: {e}", fg="red")

def terminate_instance(instance_id):
    ec2_resource = get_resource('ec2')
    ec2_client = get_client('ec2')

    instance = get_cli_instance_by_id(ec2_resource, instance_id)
    if not instance:
        click.secho(f"Error: Instance '{instance_id}' was not found or was not created by platform-cli!", fg="red")
        return

    try:
        instance.terminate()
        click.secho(f"Terminating instance '{instance_id}'... Please wait.", fg="yellow")

        waiter = ec2_client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=[instance_id])

        click.secho(f"Successfully terminated instance '{instance_id}'. It's fully gone!", fg="green")
    except Exception as e:
        click.secho(f"Error terminating instance: {e}", fg="red")
