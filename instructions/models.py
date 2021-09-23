from django.db import models
from lab_orchestrator_lib_django_adapter.models import LabModel


class InstructionPageModel(models.Model):
    """A page that contains instructions for VMs."""
    title = models.CharField(max_length=128, null=False)
    content = models.TextField(null=True)
    lab = models.ForeignKey(LabModel, on_delete=models.CASCADE, null=False, related_name="instructions")

    def __str__(self):
        return self.title
