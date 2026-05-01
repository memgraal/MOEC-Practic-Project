import decimal

import django.db.models
import django.db.transaction
import django.utils.timezone

import users.models
import products.models


class Discount(django.db.models.Model):
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

    def mark_as_cancelled(self):
        """
        Возвращаем товар на склад,
        если заказ уже был оплачен.
        """

        if self.status == self.Status.PAID:
            with django.db.transaction.atomic():
                for item in self.items.select_related('product'):
                    product = (
                        products.models.Product.objects
                        .select_for_update()
                        .get(pk=item.product.pk)
                    )

                    product.quantity_in_stock += item.quantity
                    product.save(
                        update_fields=['quantity_in_stock']
                    )

        self.status = self.Status.CANCELLED
        self.save(update_fields=['status'])

    def __str__(self):
        return f'Заказ #{self.id}'


class OrderItem(django.db.models.Model):
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
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    discount_percent = django.db.models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    final_price = django.db.models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = 'order_items'
        unique_together = ('order', 'product')

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
        Только проверка наличия.
        Со склада пока не списываем.
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
                    f'Недостаточно товара "{product.name}"'
                )

            if self.price is None:
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
        order = self.order

        super().delete(*args, **kwargs)

        order.calculate_total()

    def __str__(self):
        return (
            f'{self.product.name} × '
            f'{self.quantity} = '
            f'{self.subtotal}'
        )


class Transaction(django.db.models.Model):
    class PaymentMethod(django.db.models.TextChoices):
        CARD = 'Card', 'Оплата картой'
        PAYPAL = 'PayPal', 'PayPal'
        CASH = 'Cash', 'Наличные'
        SBP = 'SBP', 'СБП'

    payment_method = django.db.models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        db_index=True,
    )

    order = django.db.models.OneToOneField(
        Order,
        on_delete=django.db.models.CASCADE,
        related_name='transaction',
    )

    transaction_date = django.db.models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    paid_amount = django.db.models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        null=True,
    )

    class Meta:
        db_table = 'transactions'

    def save(self, *args, **kwargs):
        """
        Оплата прошла -> списываем товар.
        """

        is_new = self.pk is None

        with django.db.transaction.atomic():
            if is_new:
                order = (
                    Order.objects
                    .select_for_update()
                    .get(pk=self.order.pk)
                )

                if order.status == Order.Status.PAID:
                    raise ValueError(
                        'Заказ уже оплачен'
                    )

                for item in order.items.select_related('product'):
                    product = (
                        products.models.Product.objects
                        .select_for_update()
                        .get(pk=item.product.pk)
                    )

                    if product.quantity_in_stock < item.quantity:
                        raise ValueError(
                            f'Недостаточно товара "{product.name}"'
                        )

                    product.quantity_in_stock -= item.quantity
                    product.save(
                        update_fields=['quantity_in_stock']
                    )

                order.status = Order.Status.PAID
                order.save(update_fields=['status'])

                self.paid_amount = order.total_amount

            super().save(*args, **kwargs)

    @property
    def price(self):
        return self.paid_amount

    def __str__(self):
        return (
            f'Транзакция #{self.id} '
            f'на сумму {self.paid_amount}'
        )
