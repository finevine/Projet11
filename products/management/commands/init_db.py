import requests
import os
import json
from json import load
from django.core.management.base import BaseCommand
from products.models import Product, Category, ProductCategories

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

    def remove_duplic_dicts(self, l):
        list_of_strings = [
            json.dumps(d, sort_keys=True)
            for d in l
        ]

        list_of_strings = set(list_of_strings)

        return [
            json.loads(s)
            for s in list_of_strings
        ]

    def list_categories_to_create(self, categories, cat_names, cat_res=[]):
        ''' from a list of categories id, return list of categories
        to bulk_create
        categories (list of strings)
        cat_names (dict)'''
        for category in categories:
            if category and cat_names.get(category, ''):
                category_to_save = {
                    "id": category,
                    "name": cat_names.get(category)
                    }
                # for integrity reasons
                if category_to_save in cat_res:
                    pass
                else:
                    cat_res.append(category_to_save)

        return self.remove_duplic_dicts(cat_res)

    def dic_product_to_create(self, product):
        '''return product in DB created if nutriscore_grade else None'''
        sugar = product["nutriments"].get("sugars_100g", 0)
        satFat = product["nutriments"].get("saturated-fat_100g", 0)
        salt = product["nutriments"].get("salt_100g", 0)
        fat = product["nutriments"].get("fat_100g", 0)

        # If product has nutritiongrade
        if product.get("nutriscore_grade"):
            code_to_store = int(product["code"])
            product_dic = {
                "code": code_to_store,
                "name": product.get(
                    "product_name", product.get("product_name_fr")),
                "nutritionGrade": product.get("nutriscore_grade"),
                "image": product.get(
                    "selected_images", {}).get(
                        "front", {}).get(
                            "display", {}).get(
                                "fr"),
                "sugar": sugar,
                "satFat": satFat,
                "salt": salt,
                "fat": fat,
            }
        else:
            raise Exception('NoProduct')
        return product_dic

    def handle(self, *args, **options):
        count = 0
        # Open json of all categories to associate id & names
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "categories_cleaned.json"), 'r') as json_file:
            category_names = load(json_file)

        # pages of openFoodFacts request
        broken = False

        products_to_create, categories_to_create, prodcat_to_create = [], [], []
        asso_table = {}

        for page in range(1, 18):
            if broken:
                break
            print(f'page {page} ({count} save in DB)')
            products = self.get_products(page)

            for product in products:
                # limit to products (Heroku_db < 10000 rows)
                if count >= 9000:
                    broken = True
                    break
                    print(f'page {page} ({count} save in DB)')
                try:
                    product_to_create = self.dic_product_to_create(product)
                    # concatenate product to bulk_create
                    products_to_create.append(product_to_create)
                    count += 1

                    # categories of the product
                    categories = product.get('categories_tags', [])[:3]
                    compared_to_category = product.get('compared_to_category')
                    if compared_to_category not in categories:
                        categories.append(compared_to_category)
                    categories_to_create += categories

                    # asso table
                    asso_table[product_to_create['code']] = [
                        (
                            category,
                            product.get('compared_to_category') == category
                        )
                        for category in categories
                    ]


                    count += len(categories)

                except Exception:
                    pass

        categories_to_create = self.list_categories_to_create(
            categories_to_create, category_names
        )

        Product.objects.bulk_create(
            [Product(**prod) for prod in products_to_create],
            ignore_conflicts=True
            )

        Category.objects.bulk_create(
            [Category(**cat) for cat in categories_to_create],
            ignore_conflicts=True
            )
        # import pdb
        # pdb.set_trace()
        for code, list_of_cats in asso_table.items():
            for cat, compare in list_of_cats:
                # pdb.set_trace()
                product = Product.objects.get(code=code)
                category = Category.objects.get(id=cat)
                prodcat_to_create.append(
                    ProductCategories(
                        product=product,
                        category=category,
                        to_compare=compare
                    )
                )
        ProductCategories.objects.bulk_create(prodcat_to_create)
