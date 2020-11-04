from django.db import models
from django.contrib.auth.models import User


# === PRODUCT SECTION ===
class Category(models.Model):
    category = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['category']


class Product(models.Model):
    thumbnail = models.ImageField(verbose_name='Thumbnail', null=True, blank=True)
    name = models.CharField(verbose_name='Name', max_length=200, null=False, blank=False)
    description = models.TextField(verbose_name='description', null=False, blank=False)
    price = models.IntegerField(verbose_name='Price', null=False)
    discount = models.IntegerField(verbose_name='Discount (%)', default=0.0, null=False)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        return int(self.price*(100-self.discount)/100)

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['name']


class ProductSpecification(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    text = models.TextField(null=False, blank=False)


class RelatedProduct(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='main_prod', related_query_name='main_prod')
    rel_prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rel_prod', related_query_name='rel_prod')


class ProductImages(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=False, blank=False)
    # zoom = models.ImageField(upload_to='product_images_zoom/', null=False, blank=False)

# === END PRODUCT SECTION ===


# === ORDER SECTION ===
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    address = models.TextField()
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    pin_code = models.CharField(max_length=6)


class Order(models.Model):
    oid = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=1, default='1', choices=[('1', 'Pending payment'), ('2', 'Payment done')])
    status = models.CharField(max_length=1, default='1',
                              choices=[('1', 'Order received'), ('2', 'Packed'), ('3', 'Shipped'), ('4', 'Delivered'), ('5', 'Canceled'), ('6', 'Requested for return'), ('7', 'Refunded')])
    status_message = models.TextField(null=True, blank=True, default='')
    order_date_time = models.DateTimeField(null=False, auto_now_add=True)

    # copied address
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    address = models.TextField()
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    pin_code = models.CharField(max_length=6)

    class Meta:
        verbose_name_plural = 'Orders'
        ordering = ('-order_date_time',)


class ProductList(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(null=False)

    def __str__(self):
        return self.product.name

# === END ORDER SECTION ===


# === USER PRODUCT SECTION ===
class BaseUserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        abstract = True
        ordering = ['date_time']


class Review(BaseUserProduct):
    rating = models.CharField(max_length=1, null=False, default=5)
    review = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Reviews'


class Question(BaseUserProduct):
    question = models.TextField(null=False, blank=False)
    answer = models.TextField(null=True, blank=True)
    read = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Questions'

# === END USER PRODUCT SECTION ===


# === CART SECTION ===
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)

# === END CART SECTION ===


class ContactUs(models.Model):
    name = models.CharField(verbose_name='Name', max_length=200, null=False, blank=False)
    email = models.EmailField(verbose_name='Email address', null=False, blank=False)
    subject = models.CharField(verbose_name='Subject', max_length=200, null=True, blank=True)
    query = models.TextField(verbose_name='Query', null=False, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    seen = models.CharField(max_length=1, default='0', choices=[('0', 'Unseen'), ('1', 'Seen')], null=False)

    def __str__(self):
        return self.query[:50]

    class Meta:
        verbose_name_plural = 'Contact Us'
        ordering = ['date_time']


class ForgotPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)