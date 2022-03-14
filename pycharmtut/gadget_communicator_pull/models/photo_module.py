import uuid
from django.db import models

from gadget_communicator_pull.constants.photo_constants import PHOTO_INIT


class PhotoModule(models.Model):
    photo_id = models.UUIDField(default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='images/', null=True)
    photo_status = models.CharField(max_length=20, default=PHOTO_INIT)
