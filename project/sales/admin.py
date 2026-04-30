import django.contrib.admin

from sales.models import (
    Discount,
    Order,
    OrderItem,
)


class OrderItemInline(django.contrib.admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = (
        'product',
    )

    readonly_fields = (
        'discount_percent',
        'final_price',
        'subtotal',
    )

    fields = (
        'product',
        'quantity',
        'price',
        'discount_percent',
        'final_price',
        'subtotal',
    )

    def subtotal(self, obj):
        if obj.pk:
            return obj.subtotal
        return '-'

    subtotal.short_description = 'Сумма'


@django.contrib.admin.register(Order)
class OrderAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'status',
        'total_amount',
        'order_date',
    )

    list_filter = (
        'status',
        'order_date',
    )

    search_fields = (
        'id',
        'client__email',
        'client__name',
        'client__surname',
    )

    autocomplete_fields = (
        'client',
    )

    readonly_fields = (
        'total_amount',
        'order_date',
    )

    inlines = (
        OrderItemInline,
    )

    fieldsets = (
        (
            'Информация о заказе',
            {
                'fields': (
                    'client',
                    'status',
                ),
            },
        ),
        (
            'Финансовая информация',
            {
                'fields': (
                    'total_amount',
                ),
            },
        ),
        (
            'Системная информация',
            {
                'fields': (
                    'order_date',
                ),
            },
        ),
    )


@django.contrib.admin.register(OrderItem)
class OrderItemAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
        'discount_percent',
        'final_price',
        'subtotal',
    )

    list_filter = (
        'product',
    )

    search_fields = (
        'order__id',
        'product__name',
    )

    autocomplete_fields = (
        'order',
        'product',
    )

    readonly_fields = (
        'discount_percent',
        'final_price',
        'subtotal',
    )

    def subtotal(self, obj):
        return obj.subtotal

    subtotal.short_description = 'Сумма'


@django.contrib.admin.register(Discount)
class DiscountAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'discount_percent',
        'starting_date',
        'expiring_date',
    )

    list_filter = (
        'starting_date',
        'expiring_date',
    )

    search_fields = (
        'name',
        'description',
    )

    filter_horizontal = (
        'applicable_products',
    )

    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'name',
                    'description',
                    'discount_percent',
                ),
            },
        ),
        (
            'Срок действия',
            {
                'fields': (
                    'starting_date',
                    'expiring_date',
                ),
            },
        ),
        (
            'Применимые товары',
            {
                'fields': (
                    'applicable_products',
                ),
            },
        ),
    )