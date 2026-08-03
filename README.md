# Platform Self-Service CLI

A modular Python CLI tool for managing AWS resources safely with built-in policy guardrails.

## Features

- **EC2 Management**: Create, list, and terminate instances.
- **Enforced Policies**:
  - Restricts instance creation strictly to `t3.micro`.
  - Enforces mandatory `Owner` tag.
  - Quotas limit: Maximum 2 concurrent instances managed by the CLI.
  - Uses latest Ubuntu 24.04 LTS AMI fetched via SSM.

## Prerequisites & Setup

1. **Configure AWS Credentials**

   Make sure your AWS credentials and region are set up before running any CLI commands:

   ```bash
   aws configure
   ```

2. **Clone the repository and navigate to the project directory**

   ```bash
   git clone <repository-url>
   cd platform-CLI
   ```

3. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set the Python path**

   ```bash
   export PYTHONPATH=.
   ```

## Usage Examples

1. **List instances**

   ```bash
   python3 src/main.py ec2 list
   ```

2. **Create an instance**

   ```bash
   python3 src/main.py ec2 create --name web-server --owner roei
   ```

3. **Destroy an instance**

   ```bash
   python3 src/main.py ec2 destroy --id i-XXXXXXXXXXXXXXXXX
   ```
