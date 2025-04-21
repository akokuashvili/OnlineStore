from rest_framework.serializers import Serializer


class DymanicFieldSerializer(Serializer):
    """
    A Serializer that takes an additional `exclude_fields` argument that
    controls which fields should be dropped.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('exclude_fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are specified in the `exclude_fields` argument.
            for field_name in fields:
                self.fields.pop(field_name)