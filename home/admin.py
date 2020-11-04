from django.contrib import admin
from . import models


# === PRODUCT SECTION ===
class CategoryAdmin(admin.ModelAdmin):
    model = models.Category
    list_display = ['category']


class ProductSpecificationInline(admin.StackedInline):
    model = models.ProductSpecification
    extra = 1


class RelatedProductInline(admin.StackedInline):
    model = models.RelatedProduct
    fk_name = 'prod'
    extra = 1


class ProductImagesInline(admin.StackedInline):
    model = models.ProductImages
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'price']
    inlines = [ProductSpecificationInline, RelatedProductInline, ProductImagesInline]

# === END PRODUCT SECTION ===


# === ORDER SECTION ===
class ProductListInline(admin.StackedInline):
    model = models.ProductList
    fk = 'order'
    extra = 1
    readonly_fields = ['product', 'price', 'quantity']


class OrderAdmin(admin.ModelAdmin):
    model = models.Order
    list_display = ['oid', 'order_date_time', 'total', 'payment_status', 'status']
    readonly_fields = ['oid', 'user', 'total', 'payment_status', 'order_date_time', 'name', 'phone', 'address', 'city',
                       'state', 'pin_code']
    inlines = [ProductListInline]

# === END ORDER SECTION ===


# === USER PRODUCT SECTION ===
class QuestionAdmin(admin.ModelAdmin):
    model = models.Question
    list_display = ['question', 'product', 'date_time', 'read']

# === END USER PRODUCT SECTION ===


class ContactUsAdmin(admin.ModelAdmin):
    model = models.ContactUs
    list_display = ['name', 'date_time', 'email', 'subject', 'query', 'seen']


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.ContactUs, ContactUsAdmin)
admin.site.register(models.ForgotPassword)