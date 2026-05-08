import django.contrib.admin

from core.mixins import AuditAdminMixin

from products.models import (
    Category,
    Producer,
    Supplier,
    Warehouse,
    Product,
)

@django.contrib.admin.register(Category)
class CategoryAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Category"

    list_display = (
        "id",
        "name",
        "description_short",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "id",
    )

    def description_short(self, obj):
        return obj.description[:50]

    description_short.short_description = "Описание"


@django.contrib.admin.register(Producer)
class ProducerAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Producer"

    list_display = (
        "id",
        "name",
        "contact_short",
    )

    search_fields = (
        "name",
        "contact_info",
    )

    ordering = (
        "id",
    )

    def contact_short(self, obj):
        return obj.contact_info[:50]

    contact_short.short_description = "Контакты"


@django.contrib.admin.register(Supplier)
class SupplierAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Supplier"

    list_display = (
        "id",
        "name",
        "contact_short",
        "delivery_short",
    )

    search_fields = (
        "name",
        "contact_info",
        "delivery_terms",
    )

    ordering = (
        "id",
    )

    def contact_short(self, obj):
        return obj.contact_info[:50]

    contact_short.short_description = "Контакты"

    def delivery_short(self, obj):
        return obj.delivery_terms[:50]

    delivery_short.short_description = "Условия поставки"


@django.contrib.admin.register(Warehouse)
class WarehouseAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Warehouse"

    list_display = (
        "id",
        "name",
        "address_short",
        "contact_short",
    )

    search_fields = (
        "name",
        "address",
        "contact_info",
    )

    ordering = (
        "id",
    )

    def address_short(self, obj):
        return obj.address[:50]

    address_short.short_description = "Адрес"

    def contact_short(self, obj):
        return obj.contact_info[:50]

    contact_short.short_description = "Контакты"


@django.contrib.admin.register(Product)
class ProductAdmin(AuditAdminMixin, django.contrib.admin.ModelAdmin):
    model_name = "Product"

    list_display = (
        "id",
        "name",
        "category",
        "producer",
        "warehouse",
        "price",
        "quantity_in_stock",
        "date_added",
    )

    list_filter = (
        "category",
        "producer",
        "warehouse",
        "date_added",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
        "producer__name",
        "warehouse__name",
    )

    ordering = (
        "-date_added",
        "name",
    )

    autocomplete_fields = (
        "category",
        "producer",
        "warehouse",
    )

    readonly_fields = (
        "date_added",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "description",
                    "image",
                ),
            },
        ),
        (
            "Категория и производитель",
            {
                "fields": (
                    "category",
                    "producer",
                ),
            },
        ),
        (
            "Стоимость и склад",
            {
                "fields": (
                    "price",
                    "quantity_in_stock",
                    "warehouse",
                ),
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "date_added",
                ),
            },
        ),
    )
