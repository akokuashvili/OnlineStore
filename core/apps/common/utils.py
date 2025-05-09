import secrets
from .models import BaseModel


def generate_unique_code(model: BaseModel, field: str) -> str:
    """
    Generate a unique code for a specified model and field.

    Args:
        model (BaseModel): The model class to check for uniqueness.
        field (str): The field name to check for uniqueness.

    Returns:
        str: A unique code.
    """
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    code = "".join(secrets.choice(allowed_chars) for _ in range(12))
    similar_object_exists = model.objects.filter(**{field: code}).exists()
    if not similar_object_exists:
        return code
    return generate_unique_code(model, field)


class UpdateMixin:
    """Class adds update method to custom serializer"""
    def update(self, instance, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance