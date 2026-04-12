from django.contrib import admin
from .models import Category, Product, Order, OrderItem, SupplierProduct

# Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

# Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock")
    list_filter = ("category",)
    search_fields = ("name",)

# Order Items inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "total_amount", "status", "created_at")
    list_filter = ("status", "payment_method")
    list_editable = ("status",)

from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "phone", "is_active")
    search_fields = ("company_name", "email")

from django.contrib import admin
from .models import SupplierProduct, Product

from django.contrib import admin
from django.utils.html import format_html
from .models import SupplierProduct, Product


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "supplier",
        "is_approved",
        "approve_button",
    )
    list_filter = ("is_approved", "category")

    def approve_button(self, obj):
        if obj.is_approved:
            return "✅ Approved"
        return format_html(
            '<a class="button" href="/admin/shop/supplierproduct/{}/approve/">Approve & Publish</a>',
            obj.id
        )

    approve_button.short_description = "Action"

from django.urls import path
from django.shortcuts import redirect, get_object_or_404


class SupplierProductAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/approve/",
                self.admin_site.admin_view(self.approve_product),
                name="approve_supplier_product",
            )
        ]
        return custom_urls + urls

    def approve_product(self, request, pk):
        supplier_product = get_object_or_404(SupplierProduct, pk=pk)

        # avoid duplicate product
        if not Product.objects.filter(name=supplier_product.name).exists():
            Product.objects.create(
                name=supplier_product.name,
                category=supplier_product.category,
                price=supplier_product.price,
                stock=supplier_product.stock,
                image=supplier_product.image,
            )

        supplier_product.is_approved = True
        supplier_product.save()

        self.message_user(request, "Product approved and published successfully.")
        return redirect("/admin/shop/supplierproduct/")

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")

from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'role',
        'rating',
        'is_visible',
        'created_at',
    )

    list_filter = (
        'role',
        'rating',
        'is_visible',
        'created_at',
    )

    search_fields = (
        'name',
        'message',
    )

    list_editable = (
        'is_visible',
    )

    ordering = ('-created_at',)

