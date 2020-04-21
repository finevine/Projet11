from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Product(models.Model):
    '''
    code, name, nutritionGrade, image (url),
    fat, satFat, sugar, salt, compared_to_category
    '''

    code = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, null= True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null= True)
    nutritionGrade = models.CharField(max_length=1, null= True)
    image = models.URLField(null= True)
    fat = models.DecimalField("Fat in 100g", max_digits=5, decimal_places=2, default=0)
    satFat = models.DecimalField("Saturated fat in 100g", max_digits=5, decimal_places=2, default=0)
    sugar = models.DecimalField("Sugar in 100g", max_digits=5, decimal_places=2, default=0)
    salt = models.DecimalField("Salt in 100g", max_digits=5, decimal_places=2, default=0)
    category = models.ForeignKey('Category', related_name="category", on_delete=models.CASCADE, null= True)

    def __str__(self):
        return f'{self.slug}'
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] + '-' + self.code
        super(Product, self).save(*args, **kwargs)

class Category(models.Model):
    '''
    name
    '''
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField("Category name", max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False, null= True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] + '-' + str(self.id)
        super(Category, self).save(*args, **kwargs)

class Favourite(models.Model):
    ''' codeHealthy, codeUnhealthy '''
    codeHealthy = models.ForeignKey('Product', related_name="healthy", on_delete=models.CASCADE)
    codeUnhealthy = models.ForeignKey('Product', related_name="unhealthy", on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.codeHealthy} replaces {self.codeUnhealthy}'