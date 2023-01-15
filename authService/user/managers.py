from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):

    # function handling creation of users (normal and superusers)
    def _create_users(
        self,
        email,
        phone,
        user_name,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):

        # validate
        if not email:
            raise ValueError("email field is required")
        if not phone:
            raise ValueError("phone field is required")
        if not user_name:
            raise ValueError('user_name is required')

        # normalize the email
        email = self.normalize_email(email)

        # create user
        user = self.model(
            email=email,
            phone=phone,
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        # set user password
        user.set_password(password)

        # save
        user.save(using=self._db)
        return user

    """
    create outward facing functions to handle creation of users and superusers
    """

    # function to create normal users
    def create_user(
        self,
        email,
        phone,
        user_name,
        first_name=None,
        last_name=None,
        password=None,
        **extra_fields
    ):

        # set superuser privileges to default to false
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_users(
            email, phone, user_name, first_name, last_name, password, **extra_fields
        )

    # function to create superusers
    def create_superuser(
        self,
        email,
        phone,
        user_name,
        first_name=None,
        last_name=None,
        password=None,
        **extra_fields
    ):

        # set the superuser privileges to true
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # perform validation checks
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_users(
            email, phone, user_name, first_name, last_name, password, **extra_fields
        )
