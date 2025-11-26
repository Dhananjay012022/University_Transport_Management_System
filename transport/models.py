from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class BusRoute(models.Model):
    route_name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)

    # 🔹 New fields to make it richer
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=40, help_text="Total seat capacity of the bus/route")

    def __str__(self):
        return f"{self.route_name} ({self.start_location} → {self.end_location})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    bus_route = models.ForeignKey(
        BusRoute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class BusPass(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bus_passes")
    issue_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()

    # 🔹 Auto-generated, unique pass number
    pass_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated unique pass number"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Pass {self.pass_number} for {self.student}"

    def clean(self):
        """
        Extra validation rule:
        - expiry_date must be after issue_date
        """
        super().clean()

        # If object not saved yet, issue_date may not be set; use today's date
        issue = self.issue_date or timezone.now().date()
        if self.expiry_date and self.expiry_date <= issue:
            raise ValidationError("Expiry date must be after the issue date.")

    def save(self, *args, **kwargs):
        """
        - Auto-generate pass_number on first save
        - Run full_clean() to apply validation
        """
        if not self.pass_number:
            # Example: 8-character uppercase ID
            self.pass_number = uuid.uuid4().hex[:8].upper()

        # Ensure validation is applied
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """
        Convenience property to check if pass is expired.
        """
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()
