import django.db.models
from django.core.exceptions import ValidationError


class Category(django.db.models.Model):
    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )
    description = django.db.models.TextField()

    def __str__(self):
        return self.name


class Producer(django.db.models.Model):
    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )
    contact_info = django.db.models.TextField()

    def __str__(self):
        return self.name


class Supplier(django.db.models.Model):
    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )
    contact_info = django.db.models.TextField()
    delivery_terms = django.db.models.TextField()

    def __str__(self):
        return self.name


class Warehouse(django.db.models.Model):
    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )
    address = django.db.models.TextField()
    contact_info = django.db.models.TextField()

    def __str__(self):
        return self.name


class Product(django.db.models.Model):
    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )

    description = django.db.models.TextField()

    price = django.db.models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    category = django.db.models.ForeignKey(
        Category,
        on_delete=django.db.models.PROTECT,
        related_name='products',
    )

    quantity_in_stock = django.db.models.PositiveIntegerField()

    producer = django.db.models.ForeignKey(
        Producer,
        on_delete=django.db.models.PROTECT,
        related_name='products',
        null=False,
    )

    warehouse = django.db.models.ForeignKey(
        Warehouse,
        on_delete=django.db.models.CASCADE,
        related_name='products',
        null=False,
    )

    date_added = django.db.models.DateField(
        auto_now_add=True,
    )

    image = django.db.models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True,
    )

    def clean(self):
        errors = {}

        if self.price is not None and self.price < 0:
            errors["price"] = "Цена не может быть отрицательной"

        if self.quantity_in_stock is not None and self.quantity_in_stock < 0:
            errors["quantity_in_stock"] = "Количество не может быть отрицательным"

        if not self.name:
            errors["name"] = "Название обязательно"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
