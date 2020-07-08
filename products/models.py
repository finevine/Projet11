import products.managers as managers
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    '''
    name
    '''
    name = models.CharField(
        verbose_name="Category name", max_length=400, unique=True, null=True)
    # slug = models.SlugField(
    #     max_length=151, unique=True, editable=False, null=True)

    class Meta:
        verbose_name = "Catégorie"

    def __str__(self):
        return (self.name)

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.name)[:50] + '-' + str(self.id)
    #     super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    '''
    code, name, nutritionGrade, image (url),
    fat, satFat, sugar, salt
    '''

    objects = managers.ProductManager()
    code = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True, verbose_name="Nom")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    nutritionGrade = models.CharField(
        max_length=1, null=True, verbose_name="Nutriscore")
    image = models.URLField(null=True)

    fat = models.DecimalField(
        "Fat in 100g", max_digits=5, decimal_places=2, default=0)
    satFat = models.DecimalField(
        "Saturated fat in 100g", max_digits=5, decimal_places=2, default=0)
    sugar = models.DecimalField(
        "Sugar in 100g", max_digits=5, decimal_places=2, default=0)
    salt = models.DecimalField(
        "Salt in 100g", max_digits=5, decimal_places=2, default=0)

    categories = models.ManyToManyField(
        Category,
        related_name="products",
        verbose_name="Catégorie")

    class Meta:
        verbose_name = "Produit"
        # ordering = ['category__id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] + '-' + str(self.code)
        super().save(*args, **kwargs)


class Favourite(models.Model):
    ''' codeHealthy, codeUnhealthy '''
    healthy_product = models.ForeignKey(
        'Product', related_name="healthy", on_delete=models.CASCADE)
    unhealthy_product = models.ForeignKey(
        'Product', related_name="unhealthy", on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['healthy_product', 'unhealthy_product', 'owner'],
                name='unique_favourite')
        ]
        ordering = ['owner']
