from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Custom User Manager.

    https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_trusted', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_trusted', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model.

    Disable username and make email the new username field.
    https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    display_name = models.CharField(max_length=150, blank=True)
    is_trusted = models.BooleanField(
        _('trusted status'),
        default=False,
        null=False,
        help_text=_('Designates whether the user is trusted and allowed to start labs.'),
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    def get_real_display_name(self):
        if self.display_name is "" or self.display_name is None:
            return self.get_full_name()
        return self.display_name
