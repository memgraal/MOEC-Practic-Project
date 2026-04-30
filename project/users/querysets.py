import django.db.models


class UserQuerySet(django.db.models.QuerySet):
    def active(self):
        return self.filter(
            is_active=True,
        )

    def inactive(self):
        return self.filter(
            is_active=False,
        )

    def admins(self):
        return self.filter(
            type='admin',
        )

    def clients(self):
        return self.filter(
            type='client',
        )

    def by_email(self, email: str):
        return self.filter(
            email__iexact=email,
        )

    def search(self, query: str):
        return self.filter(
            django.db.models.Q(email__icontains=query)
        )


class ClientQuerySet(UserQuerySet):

    def by_name(self, name: str):
        return self.filter(
            name__icontains=name,
        )

    def by_surname(self, surname: str):
        return self.filter(
            surname__icontains=surname,
        )

    def by_contact(self, contact: str):
        return self.filter(
            contact_info__icontains=contact,
        )
