import boto3

ecr = boto3.client("ecr")


def __getattr__(name):
    return getattr(ecr, name)


def get_image_tags(repository_name: str) -> list[str]:
    response = ecr.describe_images(repositoryName=repository_name)
    return [
        tag for image in response["imageDetails"] for tag in image.get("imageTags", [])
    ]
