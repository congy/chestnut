import sys
import os
sys.path.append("../../")
from schema import *
from query import *
from pred import *
from populate_database import *

from faker import Faker
fake = Faker()

workload_name = 'spree'
data_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)

#scale = 100000
scale=10

product = Table('spree_product',scale)
variant = Table('spree_variant',scale*20)
price = Table('spree_price', scale*40)


name = Field('name', 'varchar(128)')
name.set_value_generator(lambda: ' '.join(fake.words(nb=2))[:127])
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=256).replace('\t', ' ').replace('\n', ' '))
available_on = Field('available_on', 'date')
discontinue_on = Field('discontinue_on', 'date')
deleted_at = Field('deleted_at', 'date')
deleted_at.value_with_prob = [(None, 100)]
slug = Field('slug', 'string')
slug.set_value_generator(lambda: fake.text(max_nb_chars=256).replace('\t', ' ').replace('\n', ' '))
created_at = Field('created_at', 'date')
updated_at = Field('updated_at', 'date')
meta_description = Field('meta_description', 'varchar(128)')
meta_description.set_value_generator(lambda: ' '.join(fake.words(nb=2))[:63])
meta_keywords = Field('meta_keyword','varchar(128)')
meta_keywords.set_value_generator(lambda: ' '.join(fake.words(nb=2))[:63])
promotionable = Field('promotionable', 'bool')
meta_title = Field('meta_title','varchar(64)')
meta_title.set_value_generator(lambda: ' '.join(fake.words(nb=2))[:63])

product.add_fields([name, description, available_on, discontinue_on, deleted_at, created_at, updated_at,\
slug, meta_description, meta_keywords, meta_title, promotionable])

product_variant = get_new_assoc("product_variant", "one_to_many", product, variant, "variants", "product")

sku = Field('sku','varchar(64)')
weight = Field('weight', 'float')
height = Field('height', 'float')
width = Field('width','float')
depth = Field('depth', 'float')
deleted_at = Field('deleted_at', 'date')
deleted_at.value_with_prob = [(None, 100)]
cost_price = Field('cost_price', 'float')
is_master = Field('is_master', 'bool')
stock_items_count = Field('stock_items_count','uint')
updated_at = Field('updated_at','date')
position = Field('position','uint')

variant.add_fields([sku,weight,height,width,depth,deleted_at,updated_at,cost_price,is_master,stock_items_count,position])

amount = Field('amount','float')
amount.set_value_generator(lambda: '' if random.randint(0, 10)>6 else 100*random.random())
created_at = Field('created_at','date')
updated_at = Field('updated_at','date')
deleted_at = Field('deleted_at', 'date')
deleted_at.value_with_prob = [(None, 100)]
currency = Field('currency', 'varchar(8)')
currency.value_with_prob = [('USD',50), ('CNY',10), ('EUR',10),('CAD',10),('AUD',10),('GBP',10)]

price.add_fields([amount, currency, created_at, updated_at, deleted_at])
price.primary_keys = [(f('variant_id'),f('currency'))]

variant_price = get_new_assoc('variant_price','one_to_many', variant, price, 'prices', 'variant')


indexes = {product:[['available_on'],['deleted_at'],['name']],\
variant:[['sku'],['product_id'],['deleted_at'],['position']],\
price: [['variant_id','currency']]
}

tables=[product,variant,price]
associations=[variant_price,product_variant]

generate_db_data_files(data_dir, tables, associations)

s = create_psql_tables_script(data_dir, tables, associations, indexes)
f = open('load_postgres_tables.sql', 'w')
f.write(s)
f.close()
