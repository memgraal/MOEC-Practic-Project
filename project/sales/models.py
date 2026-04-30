import decimal

import django.db.models
import django.db.transaction
import django.utils.timezone

import users.models
import products.models


class Discount(django.db.models.Model):
    """Скидки / акции на товары"""

    name = django.db.models.CharField(
        max_length=255,
        db_index=True,
    )

    description = django.db.models.TextField()

    discount_percent = django.db.models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    starting_date = django.db.models.DateTimeField()
    expiring_date = django.db.models.DateTimeField()

    applicable_products = django.db.models.ManyToManyField(
        products.models.Product,
        related_name='discounts',
    )

    class Meta:
        db_table = 'discounts'
        ordering = ['-discount_percent']

    def __str__(self):
        return f'{self.name} ({self.discount_percent}%)'


class Order(django.db.models.Model):
    """Заказ клиента"""

    class Status(django.db.models.TextChoices):
        NEW = 'new', 'Новый'
        PAID = 'paid', 'Оплачен'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    client = django.db.models.ForeignKey(
        users.models.Client,
        on_delete=django.db.models.PROTECT,
        related_name='orders',
    )

    status = django.db.models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )

    order_date = django.db.models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    total_amount = django.db.models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    products = django.db.models.ManyToManyField(
        products.models.Product,
        through='OrderItem',
        related_name='orders',
    )

    class Meta:
        db_table = 'orders'
        ordering = ['-order_date']

    def calculate_total(self):
        total = sum(
            item.subtotal
            for item in self.items.all()
        )

        self.total_amount = total
        self.save(update_fields=['total_amount'])

        return total

    def __str__(self):
        return f'Заказ #{self.id}'


class OrderItem(django.db.models.Model):
    """Позиция заказа"""

    order = django.db.models.ForeignKey(
        Order,
        on_delete=django.db.models.CASCADE,
        related_name='items',
    )

    product = django.db.models.ForeignKey(
        products.models.Product,
        on_delete=django.db.models.PROTECT,
        related_name='order_items',
    )

    quantity = django.db.models.PositiveIntegerField(
        default=1,
    )

    price = django.db.models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount_percent = django.db.models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    final_price = django.db.models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = 'order_items'
        unique_together = (
            'order',
            'product',
        )

    @property
    def subtotal(self):
        return self.quantity * self.final_price

    def get_active_discount(self):
        now = django.utils.timezone.now()

        discount = (
            self.product.discounts.filter(
                starting_date__lte=now,
                expiring_date__gte=now,
            )
            .order_by('-discount_percent')
            .first()
        )

        if discount:
            return discount.discount_percent

        return decimal.Decimal('0')

    def save(self, *args, **kwargs):
        """
        Проверка склада
        Применение скидки
        Пересчёт суммы заказа
        """

        with django.db.transaction.atomic():
            product = (
                products.models.Product.objects
                .select_for_update()
                .get(pk=self.product.pk)
            )

            old_quantity = 0

            if self.pk:
                old_item = OrderItem.objects.get(pk=self.pk)
                old_quantity = old_item.quantity

            diff = self.quantity - old_quantity

            if diff > 0 and product.quantity_in_stock < diff:
                raise ValueError(
                    f'Недостаточно товара "{product.name}" на складе'
                )

            product.quantity_in_stock -= diff
            product.save(update_fields=['quantity_in_stock'])

            if not self.price:
                self.price = product.price

            self.discount_percent = self.get_active_discount()

            multiplier = (
                decimal.Decimal('1')
                - self.discount_percent / decimal.Decimal('100')
            )

            self.final_price = (
                self.price * multiplier
            ).quantize(decimal.Decimal('0.01'))

            super().save(*args, **kwargs)

            self.order.calculate_total()

    def delete(self, *args, **kwargs):
        """
        Возвращаем товар на склад
        """

        with django.db.transaction.atomic():
            product = (
                products.models.Product.objects
                .select_for_update()
                .get(pk=self.product.pk)
            )

            product.quantity_in_stock += self.quantity
            product.save(update_fields=['quantity_in_stock'])

            order = self.order

            super().delete(*args, **kwargs)

            order.calculate_total()

    def __str__(self):
        return (
            f'{self.product.name} × {self.quantity} '
            f'= {self.subtotal}'
        )
