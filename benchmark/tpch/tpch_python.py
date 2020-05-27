import sys
sys.path.append("../../")
from schema import *
from query import *
from pred import *
from nesting import *
from plan_search import *
from ilp.ilp_manager import *
from ds_manager import *
from codegen.codegen_test import *
from populate_database import *
import globalv

workload_name = "tpch"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

#scale=10000
scale = 1000
lineitem = Table('lineitem', 6000*scale)
customer = Table('customer', 150*scale)
order = Table('corder', 1500*scale)
supplier = Table('supplier', 10*scale)
nation = Table('nation', 25)
region = Table('region', 5)
part = Table('part', 200*scale)
partsupp = Table('partsupp', 800*scale)

#lineitem
linenumber = Field('linenumber', 'uint')
quantity = Field('quantity', 'uint')
quantity.range = [1, 50]
extendedprice = Field('extendedprice', 'float')
extendedprice.range = [0, 1000000]
discount = Field('discount', 'float')
discount.range = [0, 0.1]
tax = Field('tax', 'float')
tax.range = [0, 0.08]
returnflag = Field('returnflag', 'varchar(1)')
returnflag.value_with_prob = [('A', 33), ('R', 33), ('N', 33)]
linestatus = Field('linestatus', 'varchar(1)')
linestatus.value_with_prob = [('O', 50), ('F', 50)]
shipdate = Field('shipdate', 'date')
commitdate = Field('commitdate', 'date')
receiptdate = Field('receiptdate', 'date')
shipinstruct = Field('shipinstruct', 'varchar(18)')
shipinstruct.value_with_prob = [('DELIVER IN PERSON', 25), ('COLLECT COD', 25), ('None', 25), ('TAKE BACK RETURN', 25)]
shipmode = Field('shipmode', 'varchar(7)')
shipmode.value_with_prob = [('AIR REG', 14), ('AIR', 14), ('TRUCT', 14), ('MAIL', 14), ('RAIL', 14), ('FOB', 14), ('SHIP', 16)]
comment = Field('comment', 'string')

lineitem.add_fields([linenumber, quantity, extendedprice, discount, tax, \
returnflag, linestatus, shipdate, commitdate, receiptdate, \
shipinstruct, shipmode, comment])

#order
orderstatus = Field('orderstatus', 'varchar(1)')
orderstatus.value_with_prob = [('O', 50), ('F', 50)]
totalprice = Field('totalprice', 'float')
orderdate = Field('orderdate', 'date')
orderpriority = Field('orderpriority', 'varchar(15)')
orderpriority.value_with_prob = [('1-URGENT', 20), ('2-HIGH', 20), ('3-MEDIUM', 20), ('4-NOT SPECIFIED', 20), ('5-LOW', 20)]
clerk = Field('clerk', 'varchar(4)')
shippriority = Field('shippriotiy', 'bool')
shippriority.value_with_prob = [(False, 90), (True, 10)]
comment = Field('comment', 'string')
order.add_fields([orderstatus, totalprice, orderdate, orderpriority, clerk, shippriority, comment])


#customer
name = Field('name', 'varchar(8)')
address = Field('address', 'varchar(16)')
phone = Field('phone', 'varchar(10)')
acctbal = Field('acctbal', 'float')
mktsegment = Field('mktsegment', 'varchar(10)')
mktsegment.value_with_prob = [('AUTOMOBILE', 20), ('BUILDING', 20), ('FURNITURE', 20), ('MACHINERY', 20), ('HOUSEHOLD', 20)]
comment = Field('comment', 'string')
customer.add_fields([name, address, phone, acctbal, mktsegment, comment])

#part
name = Field('name', 'varchar(15)')
mfgr = Field('mgfr', 'varchar(15)')
brand = Field('brand', 'varchar(8)')
brand.value_with_prob = [('BRAND#11', 4),('BRAND#12', 4),('BRAND#13', 4),('BRAND#14', 4),('BRAND#15', 4),\
('BRAND#21', 4),('BRAND#22', 4),('BRAND#23', 4),('BRAND#24', 4),('BRAND#25', 4),\
('BRAND#31', 4),('BRAND#32', 4),('BRAND#33', 4),('BRAND#34', 4),('BRAND#35', 4),\
('BRAND#41', 4),('BRAND#42', 4),('BRAND#43', 4),('BRAND#44', 4),('BRAND#45', 4),\
('BRAND#51', 4),('BRAND#52', 4),('BRAND#53', 4),('BRAND#55', 4),('BRAND#55', 4)]
ptype = Field('p_type', 'varchar(8)')
ptype.value_with_prob = [('STANDARD', 17), ('PROMO', 17), ('SMALL', 17), ('MEDIUM', 17), ('LARGE', 17), ('ECONOMY', 15)]
psize = Field('p_size', 'uint')
psize.range = [1, 25]
container = Field('container', 'varchar(9)')
container.value_with_prob = [('SM CASE',4),('SM BOX',4),('SM BAG',4),('SM JAR',4),('SM PKG',4),\
('MED CASE',4),('MED BOX',4),('MED BAG',4),('MED JAR',4),('MEDPKG',4),\
('LG CASE',4),('LG BOX',4),('LG BAG',4),('LG JAR',4),('LG PKG',4),\
('JUNBO CASE',4),('JUMBO BOX',4),('JUMBO BAG',4),('JUMBO JAR',4),('JUMBO PKG',4),\
('WRAP CASE',4),('WRAP BOX',4),('WRAP BAG',4),('WRAP JAR',4),('WRAP PKG',4)]
retailprice = Field('retailprice', 'float')
comment = Field('comment', 'string')
part.add_fields([name, mfgr, brand, ptype, psize, container, retailprice, comment])

#partsupp
availqty = Field('availqty', 'uint')
supplycost = Field('supplycost', 'float')
partsupp.add_fields([availqty, supplycost])

#supplier
name = Field('name', 'varchar(15)')
address = Field('address', 'varchar(20)')
phone = Field('phone', 'varchar(15)')
acctbal = Field('acctbal', 'float')
comment = Field('comment', 'string')
supplier.add_fields([name, address, phone, acctbal, comment])

#nation
name = Field('name', 'varchar(25)')
name.value_with_prob = [('ALGERIA', 4), ('ARGENTINA', 4), ('BRAZIL', 4), \
('CANADA', 4), ('EGYPT', 4), ('ETHIOPIA', 4), \
('FRANCE', 4),('GERMANY', 4),('INDIA', 4), \
('INDONESIA', 4),('IRAN', 4),('IRAQ', 4), \
('JAPAN', 4),('JORDAN', 4),('KENYA', 4), \
('MOROCCO', 4),('MOZAMBIQUE', 4),('PERU', 4), \
('CHINA', 4),('ROMANIA', 4),('SAUDI ARABIA', 4), \
('VIETNAM', 4),('RUSSIA', 4),('UNITED KINGDOM', 4), \
('UNITED STATES', 4)]
comment = Field('comment', 'varchar(152)')
nation.add_fields([name, comment])


#region
name = Field('name', 'varchar(25)')
name.value_with_prob = [('AFRICA', 20), ('AMERICA', 20), ('ASIA', 20), ('EUROPE', 20), ('MIDDLE EAST', 20)]
comment = Field('comment', 'varchar(152)')
region.add_fields([name, comment])


assoc1 = get_new_assoc("order_to_item", "one_to_many", order, lineitem, "lineitems", "order")
assoc2 = get_new_assoc("supplier_to_item", "one_to_many", supplier, lineitem, "lineitems", "supplier")
assoc3 = get_new_assoc("nation_to_supplier", "one_to_many", nation, supplier, 'suppliers', 'nation')
assoc4 = get_new_assoc("region_to_nation", "one_to_many", region, nation, 'nations', 'region')
assoc5 = get_new_assoc("customer_to_order", "one_to_many", customer, order, "orders", "customer")
assoc6 = get_new_assoc("nation_to_customer", "one_to_many", nation, customer, "customers", "nation")
assoc7 = get_new_assoc("lineitem_to_part", "one_to_many", part, lineitem, "lineitems", "part", 0, 0)
assoc8 = get_new_assoc("supplier_part_part", "one_to_many", part, partsupp, 'partsupps', 'part')
assoc9 = get_new_assoc("supplier_part_supp", "one_to_many", supplier, partsupp, 'partsupps', 'supplier')


globalv.tables = [lineitem, customer, order, supplier, nation, region, part, partsupp]
globalv.associations = [assoc1, assoc2, assoc3, assoc4, assoc5, assoc6, assoc7, assoc8, assoc9]

#generate_db_data_files(datafile_dir, tables, associations)
#exit(0)

q1_inner = get_all_records(lineitem)
q1_inner.pfilter(BinOp(f('shipdate'), LE, Parameter('shipdate')))
q1 = q1_inner.groupby([f('returnflag'), f('linestatus')], 6)
q1.orderby([f('returnflag'), f('linestatus')])
q1.get_include(f('lineitems')).aggr(UnaryExpr(SUM, f('quantity')), 'sum_qty')
q1.get_include(f('lineitems')).aggr(UnaryExpr(SUM, f('extendedprice')), 'sum_base_price')
q1.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'sum_disc_price')
q1.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
  BinaryExpr(f('extendedprice'), MULTIPLY, \
    BinaryExpr(BinaryExpr(AtomValue(1), MINUS, f('discount')), MULTIPLY, \
               BinaryExpr(AtomValue(1), ADD, f('tax'))))), 'sum_charge')
q1.get_include(f('lineitems')).aggr(UnaryExpr(AVG, f('quantity')), 'avg_qty')
q1.get_include(f('lineitems')).aggr(UnaryExpr(AVG, f('extendedprice')), 'avg_price')
q1.get_include(f('lineitems')).aggr(UnaryExpr(AVG, f('discount')), 'avg_disc')
q1.get_include(f('lineitems')).aggr(UnaryExpr(COUNT), 'count')
q1.project('*')
q1.complete()

q1_inner.assigned_param_values = {Parameter('shipdate'): '2018-06-28 17:17:17'}
globalv.pred_selectivity.append((BinOp(f('shipdate',table=lineitem), LE, Parameter('shipdate')), 0.95))

q3 = get_all_records(order)
q3.pfilter(BinOp(f('customer').f('mktsegment'), EQ, Parameter('p_mktseg')))
q3.pfilter(BinOp(f('orderdate'), LE, Parameter('date1')))
q3.finclude(f('lineitems'), pfilter=BinOp(f('shipdate'), GE, Parameter('date2', dependence=(Parameter('date1'), 0))), projection=[])
q3.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'revenue')
q3.project([f('id'), f('orderdate'), f('orderpriority')])
q3.orderby([f('revenue'), f('orderdate')])
q3.complete()

q4_inner = get_all_records(order)
q4_inner.pfilter(BinOp(f('orderdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2', dependence=(Parameter('date1'), 15)))))
q4_inner.pfilter(SetOp(f('lineitems'), EXIST, BinOp(f('commitdate'), LE, f('receiptdate'))))
q4 = q4_inner.groupby([f('orderpriority')], 5)
q4.orderby([f('orderpriority')])
q4.get_include(f('corders')).aggr(UnaryExpr(COUNT), 'count')
q4.project('*')
q4.complete()

q5_inner = get_all_records(lineitem)
q5_inner.pfilter(BinOp(f('supplier').f('nation').f('region').f('name'), EQ, Parameter('region')))
q5_inner.pfilter(BinOp(f('order').f('customer').f('nation').f('id'), EQ, f('supplier').f('nation').f('id')))
q5_inner.pfilter(BinOp(f('order').f('orderdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2', dependence=(Parameter('date1'), 60)))))
q5 = q5_inner.groupby([f('supplier').f('nation').f('name')], 25)
q5.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'revenue')
q5.project('*')
q5.orderby([f('revenue')])
q5.complete()

q6 = get_all_records(lineitem)
q6.pfilter(BinOp(f('shipdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2', dependence=(Parameter('date1'), 60)))))
q6.pfilter(BinOp(f('discount'), BETWEEN, DoubleParam(Parameter('disc1'), Parameter('disc2', dependence=(Parameter('disc1'), 0.02)))))
q6.pfilter(BinOp(f('quantity'), LE, Parameter('quant')))
q6.aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, f('discount'))), 'revenue')
q6.complete()

q7_inner = get_all_records(lineitem)
q7 = q7_inner.groupby([f('supplier').f('nation').f('name'), f('order').f('customer').f('nation').f('name'), f('shipdate')], 125)
pred1 = ConnectOp(BinOp(f('shipdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))), AND, \
	ConnectOp(BinOp(f('supplier').f('nation').f('name'), EQ, Parameter('nation1')), AND, \
	 					BinOp(f('order').f('customer').f('nation').f('name'), EQ, Parameter('nation2'))))
pred2 = ConnectOp(BinOp(f('shipdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))), AND, \
	ConnectOp(BinOp(f('supplier').f('nation').f('name'), EQ, Parameter('nation2')), AND, \
	 					BinOp(f('order').f('customer').f('nation').f('name'), EQ, Parameter('nation1'))))
q7_inner.pfilter(ConnectOp(pred1, OR, pred2))
q7_inner.aggr(UnaryExpr(SUM, BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'revenue')
q7.project('*')
q7.complete()

q8_inner = get_all_records(lineitem)
q8 = q8_inner.groupby([f('order').f('orderdate')], 6)
q8_inner.pfilter(BinOp(f('order').f('orderdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))))
q8_inner.pfilter(BinOp(f('order').f('customer').f('nation').f('region').f('name'), EQ, Parameter('region_name')))
q8_inner.pfilter(BinOp(f('part').f('p_type'), EQ, Parameter('ptype')))
q8.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
	(IfThenElseExpr(BinaryExpr(f('supplier').f('nation').f('name'), BEQ, Parameter('nation')), \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount'))), AtomValue(0)))), 'l_sum')
q8.get_include(f('lineitems')).aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'l_div')
q8.project('*')
q8.complete()

q12 = get_all_records(lineitem)
q12.pfilter(BinOp(f('shipmode'), IN, MultiParam([Parameter('shipmode1'), Parameter('shipmode2')])))
q12.pfilter(BinOp(f('commitdate'), LE, f('receiptdate')))
q12.pfilter(BinOp(f('shipdate'), LE, f('commitdate')))
q12.pfilter(BinOp(f('receiptdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2', dependence=(Parameter('date1'), 60)))))
q12.aggr(UnaryExpr(SUM, \
        IfThenElseExpr(BinaryExpr(BinaryExpr(f('order').f('orderpriority'), BEQ, AtomValue('1-URGENT')), BOR, BinaryExpr(f('order').f('orderpriority'), BEQ, AtomValue('2-HIGH'))), \
        AtomValue(1), AtomValue(0))), 'high_line_count')
q12.aggr(UnaryExpr(SUM, \
        IfThenElseExpr(BinaryExpr(BinaryExpr(f('order').f('orderpriority'), BNEQ, AtomValue('1-URGENT')), BAND, BinaryExpr(f('order').f('orderpriority'), BNEQ, AtomValue('2-HIGH'))), \
        AtomValue(1), AtomValue(0))), 'low_line_count')
q12.complete()

q13_inner = get_all_records(customer)
q13_inner.finclude(f('orders'), pfilter=UnaryOp(BinOp(f('comment'), SUBSTR, Parameter('substr'))), projection=[])
q13_inner.get_include(f('orders')).aggr(UnaryExpr(COUNT), 'c_count')
q13 = q13_inner.groupby([f('c_count')], 100)
q13.orderby([f('c_count')])
q13.project('*')
q13.complete()

q14 = get_all_records(lineitem)
q14.pfilter(BinOp(f('shipdate'), BETWEEN, DoubleParam(Parameter('q14_date1'), Parameter('q14_date2', dependence=(Parameter('q14_date1'), 5)))))
q14.aggr(UnaryExpr(SUM, \
          IfThenElseExpr(BinaryExpr(f('part').f('p_type'), BEQ, AtomValue('PROMO')), \
          BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount'))), \
          AtomValue(0))), 'promo_revenue_1')
q14.aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), "promo_revenue_2")
q14.complete()

q15 = get_all_records(supplier)
q15.finclude(f('lineitems'), projection=[])
q15.get_include(f('lineitems')).pfilter(BinOp(f('shipdate'), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))))
q15.get_include(f('lineitems')).aggr(UnaryExpr(SUM, BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'total_revenue')
q15.aggr(UnaryExpr(MAX, f('total_revenue')), 'max_revenue')
q15.complete()

q19 = get_all_records(lineitem)
pred3_1 = ConnectOp(BinOp(f('part').f('brand'), EQ, Parameter('brand1')), AND, \
          ConnectOp(BinOp(f('part').f('container'), IN, \
            MultiParam([AtomValue('SM CASE'), AtomValue('SM BOX'), AtomValue('SM PACK'), AtomValue('SM PKG')])), AND, \
          ConnectOp(BinOp(f('part').f('p_size'), LE, AtomValue(5)), AND, \
          ConnectOp(BinOp(f('shipmode'), IN, MultiParam([AtomValue('AIR'), AtomValue('AIR REG')])), AND, \
          ConnectOp(BinOp(f('shipinstruct'), EQ, AtomValue('DELIVER IN PERSON')), AND, \
                    BinOp(f('quantity'), BETWEEN, DoubleParam(Parameter('a_quant1'), Parameter('a_quant2', dependence=(Parameter('a_quant1'), 10))))
          )))))
pred3_2 = ConnectOp(BinOp(f('part').f('brand'), EQ, Parameter('brand2')), AND, \
          ConnectOp(BinOp(f('part').f('container'), IN, \
            MultiParam([AtomValue('MED BAG'), AtomValue('MED BOX'), AtomValue('MED PKG'), AtomValue('MED PACK')])), AND, \
          ConnectOp(BinOp(f('part').f('p_size'), LE, AtomValue(10)), AND, \
          ConnectOp(BinOp(f('shipmode'), IN, MultiParam([AtomValue('AIR'), AtomValue('AIR REG')])), AND, \
          ConnectOp(BinOp(f('shipinstruct'), EQ, AtomValue('DELIVER IN PERSON')), AND, \
                    BinOp(f('quantity'), BETWEEN, DoubleParam(Parameter('b_quant1'), Parameter('b_quant2', dependence=(Parameter('b_quant1'), 10))))
          )))))
pred3_3 = ConnectOp(BinOp(f('part').f('brand'), EQ, Parameter('brand3')), AND, \
          ConnectOp(BinOp(f('part').f('container'), IN, \
            MultiParam([AtomValue('LG CASE'), AtomValue('LG BOX'), AtomValue('LG PACK'), AtomValue('LG PKG')])), AND, \
          ConnectOp(BinOp(f('part').f('p_size'), LE, AtomValue(15)), AND, \
          ConnectOp(BinOp(f('shipmode'), IN, MultiParam([AtomValue('AIR'), AtomValue('AIR REG')])), AND, \
          ConnectOp(BinOp(f('shipinstruct'), EQ, AtomValue('DELIVER IN PERSON')), AND, \
                    BinOp(f('quantity'), BETWEEN, DoubleParam(Parameter('c_quant1'), Parameter('c_quant2', dependence=(Parameter('c_quant1'), 10))))
          )))))

pred3 = ConnectOp(pred3_1, OR, ConnectOp(pred3_2, OR, pred3_3))

q19.pfilter(pred3)
q19.aggr(UnaryExpr(SUM, \
    BinaryExpr(f('extendedprice'), MULTIPLY, BinaryExpr(AtomValue(1), MINUS, f('discount')))), 'revenue')
q19.complete()

globalv.pred_selectivity.append((BinOp(f('shipdate', table=lineitem), LE, Parameter('shipdate')), 0.95))
globalv.pred_selectivity.append((BinOp(f('shipdate', table=lineitem), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))), 0.16))
globalv.pred_selectivity.append((BinOp(f('discount', table=lineitem), BETWEEN, DoubleParam(Parameter('disc1'), Parameter('disc2'))), 0.2))
globalv.pred_selectivity.append((BinOp(f('quantity', table=lineitem), LE, Parameter('quant')), 0.2))
globalv.pred_selectivity.append((BinOp(f('receiptdate', table=lineitem), BETWEEN, DoubleParam(Parameter('date1'), Parameter('date2'))), 0.16))
globalv.pred_selectivity.append((BinOp(f('shipdate', table=lineitem), BETWEEN, DoubleParam(Parameter('q14_date1'), Parameter('q14_date2'))), 0.01))
globalv.pred_selectivity.append((BinOp(f('part', table=lineitem).f('container', table=part), IN, \
            MultiParam([AtomValue('SM CASE'), AtomValue('SM BOX'), AtomValue('SM PACK'), AtomValue('SM PKG')])), 0.2))
globalv.pred_selectivity.append((BinOp(f('part', table=lineitem).f('container', table=part), IN, \
            MultiParam([AtomValue('MED BAG'), AtomValue('MED BOX'), AtomValue('MED PKG'), AtomValue('MED PACK')])), 0.2))
globalv.pred_selectivity.append((BinOp(f('part', table=lineitem).f('container', table=part), IN, \
            MultiParam([AtomValue('LG CASE'), AtomValue('LG BOX'), AtomValue('LG PACK'), AtomValue('LG PKG')])), 0.2))
globalv.pred_selectivity.append((BinOp(f('shipmode'), IN, MultiParam([AtomValue('AIR'), AtomValue('AIR REG')])), 0.33))


read_queries = [q1, q3, q4, q5, q6, q7, q12, q13, q14, q15]
# q8: to be fixed
#test_merge(q12)

#generate_db_data_files(datafile_dir, globalv.tables, globalv.associations)
#populate_database(datafile_dir, globalv.tables, globalv.associations, True)
#exit(0)
#prune_nesting_test(read_queries)
#test_prune_read_plan(read_queries)

#search_plans_for_one_query(q1)
test_codegen_one_query(globalv.tables, globalv.associations, q1)
#test_ilp(read_queries)

#ilp_solve(read_queries, write_queries=[], membound_factor=1.7, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
#test_read_overall(tables, associations, read_queries, memfactor=1.7, read_from_file=True, read_ilp=True)

# dsmanagers = enumerate_nestings_for_query(q5)
# for i,ds in enumerate(dsmanagers):
#   print "Nesting {}:\n".format(i)
#   print ds
#   print '--------'
