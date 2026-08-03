import boto3

def get_boto_session(profile_name=None, region_name=None):
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        return session
    except Exception as e:
        print(f"Error initializing AWS Session: {e}")
        raise e

def get_client(service_name, profile_name=None, region_name=None):
    session = get_boto_session(profile_name, region_name)
    return session.client(service_name)

def get_resource(service_name, profile_name=None, region_name=None):
    session = get_boto_session(profile_name, region_name)
    return session.resource(service_name)
