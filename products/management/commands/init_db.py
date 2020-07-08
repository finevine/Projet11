import requests
from django.core.management.base import BaseCommand
from products.models import Product, Category

API_URL = 'https://fr-en.openfoodfacts.org/cgi/search.pl'
SEARCH_HEADER = {
    "user-agent": "Purbeurre - https://github.com/finevine/Projet8"
    }


class Command(BaseCommand):
    help = 'Create DB and populate it'

    def get_products(self, page):
        SEARCH_PARAM = {
            "action": "process",
            "tagtype_0": "countries",
            "tag_contains_0": "contains",
            "tag_0": "france",
            "sort_by": "unique_scans_n",
            "page_size": 500,
            "page": page,
            "json": 1,
        }
        req = requests.get(
            API_URL,
            params=SEARCH_PARAM,
            headers=SEARCH_HEADER)
        # Output of request as a json file
        req_output = req.json()

        # Get results
        return req_output["products"]

    def create_product(self, product):
        '''return product in DB created if nutriscore_grade else None'''
        product_to_create = Product(
            code=int(product.get("code", 0)),
            name=product.get(
                "product_name", product.get("product_name_fr")),
            nutritionGrade=product.get("nutriscore_grade", ''),
            image=product.get(
                "selected_images", {}).get(
                    "front", {}).get(
                        "display", {}).get(
                            "fr"),
            sugar=product["nutriments"].get("sugars_100g", 0),
            satFat=product["nutriments"].get("saturated-fat_100g", 0),
            salt=product["nutriments"].get("salt_100g", 0),
            fat=product["nutriments"].get("fat_100g", 0),
        )

        return product_to_create

    def handle(self, *args, **options):
        count = 0
        broken = False
        association = []
        through_to_create = []

        # pages of openFoodFacts request
        for page in range(1, 9000 // 500):
            if broken:
                break
            print(f'page {page} ({count} save in DB)')
            products = self.get_products(page)

            for product in products:
                # limit to products (Heroku_db < 10000 rows)
                if count >= 9000:
                    broken = True
                    break
                product_to_create = self.create_product(product)
                count += 1

                if product_to_create.nutritionGrade:
                    # 3 first categories of the product
                    categories_names = product.get('categories', '').split(',')[:3]
                    # create association
                    association.append(
                        (product_to_create,
                        [Category(name=name) for name in categories_names])
                    )
                    count += len(categories_names)
        
        product_to_create, categories_to_create = zip(*association)
        flat_cat = [val for sublist in categories_to_create for val in sublist]
        Product.objects.bulk_create(product_to_create, ignore_conflicts=True)
        Category.objects.bulk_create(flat_cat, ignore_conflicts=True)

        for product, category_names in association:
            for category_name in category_names:
                prodcat_to_create = Product.categories.through(
                    product_id=product.code,
                    category_id=Category.objects.get(name=category_name).id
                )
                through_to_create.append(prodcat_to_create)
        Product.categories.through.objects.bulk_create(
            through_to_create,
            ignore_conflicts=True)
