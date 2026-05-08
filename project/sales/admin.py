import django.contrib.admin
import django.contrib.messages
import django.utils.html

from core.models import AuditLog
from core.utils import write_audit_log
from core.mixins import AuditAdminMixin

from sales.models import (
    Discount,
    Order,
    OrderItem,
    Transaction,
)


class OrderItemInline(django.contrib.admin.TabularInline):
    model = OrderItem
    extra = 1

    autocomplete_fields = (
        "product",
    )

    readonly_fields = (
        "discount_percent",
        "final_price",
        "subtotal_display",
    )

    fields = (
        "product",
        "quantity",
        "price",
        "discount_percent",
        "final_price",
        "subtotal_display",
    )

    def subtotal_display(self, obj):
        if obj.pk:
            return obj.subtotal
        return "-"

    subtotal_display.short_description = "Сумма"


@django.contrib.admin.action(description="Отменить выбранные заказы")
def cancel_orders(modeladmin, request, queryset):
    count = 0

    for order in queryset:
        if order.status != Order.Status.CANCELLED:
            order.mark_as_cancelled()

            write_audit_log(
                request=request,
                action=AuditLog.Actions.UPDATE,
                model_name="Order",
                object_id=order.pk,
            )

            count += 1

    modeladmin.message_user(
        request,
        f"Отменено заказов: {count}",
        django.contrib.messages.SUCCESS,
    )


@django.contrib.admin.register(Order)
class OrderAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Order"

    list_display = (
        "id",
        "client",
        "colored_status",
        "total_amount",
        "has_transaction",
        "order_date",
    )

    list_filter = (
        "status",
        "order_date",
    )

    search_fields = (
        "id",
        "client__email",
        "client__name",
        "client__surname",
    )

    autocomplete_fields = (
        "client",
    )

    readonly_fields = (
        "total_amount",
        "order_date",
    )

    actions = (
        cancel_orders,
    )

    inlines = (
        OrderItemInline,
    )

    fieldsets = (
        (
            "Информация о заказе",
            {
                "fields": (
                    "client",
                    "status",
                ),
            },
        ),
        (
            "Финансы",
            {
                "fields": (
                    "total_amount",
                ),
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "order_date",
                ),
            },
        ),
    )

    def colored_status(self, obj):
        colors = {
            Order.Status.NEW: "gray",
            Order.Status.PAID: "green",
            Order.Status.COMPLETED: "blue",
            Order.Status.CANCELLED: "red",
        }

        color = colors.get(obj.status, "black")

        return django.utils.html.format_html(
            '<b style="color:{}">{}</b>',
            color,
            obj.get_status_display(),
        )

    colored_status.short_description = "Статус"

    def has_transaction(self, obj):
        return hasattr(obj, "transaction")

    has_transaction.boolean = True
    has_transaction.short_description = "Оплачен"


@django.contrib.admin.register(OrderItem)
class OrderItemAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "OrderItem"

    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "discount_percent",
        "final_price",
        "subtotal_display",
    )

    list_filter = (
        "product",
        "discount_percent",
    )

    search_fields = (
        "order__id",
        "product__name",
    )

    autocomplete_fields = (
        "order",
        "product",
    )

    readonly_fields = (
        "discount_percent",
        "final_price",
        "subtotal_display",
    )

    def subtotal_display(self, obj):
        return obj.subtotal

    subtotal_display.short_description = "Сумма"


@django.contrib.admin.register(Transaction)
class TransactionAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Transaction"

    list_display = (
        "id",
        "order",
        "payment_method",
        "paid_amount",
        "transaction_date",
    )

    list_filter = (
        "payment_method",
        "transaction_date",
    )

    search_fields = (
        "id",
        "order__id",
        "order__client__email",
    )

    autocomplete_fields = (
        "order",
    )

    readonly_fields = (
        "paid_amount",
        "transaction_date",
    )

    fieldsets = (
        (
            "Информация об оплате",
            {
                "fields": (
                    "order",
                    "payment_method",
                ),
            },
        ),
        (
            "Финансовая информация",
            {
                "fields": (
                    "paid_amount",
                ),
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "transaction_date",
                ),
            },
        ),
    )


@django.contrib.admin.register(Discount)
class DiscountAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Discount"

    list_display = (
        "id",
        "name",
        "discount_percent",
        "starting_date",
        "expiring_date",
    )

    list_filter = (
        "starting_date",
        "expiring_date",
        "discount_percent",
    )

    search_fields = (
        "name",
        "description",
    )

    filter_horizontal = (
        "applicable_products",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "description",
                    "discount_percent",
                ),
            },
        ),
        (
            "Срок действия",
            {
                "fields": (
                    "starting_date",
                    "expiring_date",
                ),
            },
        ),
        (
            "Товары",
            {
                "fields": (
                    "applicable_products",
                ),
            },
        ),
    )
