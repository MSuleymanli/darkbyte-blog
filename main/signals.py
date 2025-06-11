from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.db.models import FileField, ImageField

@receiver(post_delete)
def delete_file_on_delete(sender, instance, **kwargs):

    for field in instance._meta.fields:
        if isinstance(field, (FileField, ImageField)):
            file = getattr(instance, field.name)
            if file and file.name:
                default_storage.delete(file.path)
