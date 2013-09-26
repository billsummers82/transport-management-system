# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from osv import osv, fields
import time
from datetime import datetime, date
import decimal_precision as dp


# Products => We need flags for some process with TMS Module
class product_product(osv.osv):
    _name = 'product.product'
    _inherit ='product.product'

    _columns = {
        'tms_category':fields.selection([
                                          ('no_tms_product','No TMS Product'), 
                                          ('transportable','Transportable'), 
                                          ('freight','Freight'), 
                                          ('move','Move'), 
                                          ('insurance','Insurance'), 
                                          ('highway_tolls','Highway Tolls'), 
                                          ('other','Other'),
                                          ('real_expense','Real Expense'),
                                          ('madeup_expense','Made-up Expense'),
                                          ('salary','Salary'),
                                          ('salary_retention','Salary Retention'),
                                          ('salary_discount','Salary Discount'),
                                          ('negative_balance','Negative Balance'),
                                          ('fuel','Fuel'),
                                          ('indirect_expense','Indirect Expense (Agreements)'),
                                          ], 'TMS Type', required=True,
                                          help="""Product Type for using with TMS Module
  - No TMS Product: Not related to TMS
  - Transportable: Transportable Product used in Waybills
  - Freight: Represents Freight Price used in Waybills
  - Move: Represents Moves Price used in Waybills
  - Insurance: Represents Insurance for Load used in Waybills
  - Highway Tolls: Represents Highway Tolls used in Waybills
  - Other: Represents any other charge for Freight Service used in Waybills
  - Real Expense: Represent real expenses related to Travel, those that will be used in Travel Expense Checkup.
  - Made-Up Expense: Represent made-up expenses related to Travel, those that will be used in Travel Expense Checkup.
  - Fuel: Used for filtering products used in Fuel Vouchers.
  - Indirect Expense (Agreements): Used to define Accounts for Agreements Indirect Expenses.
  All of these products MUST be used as a service because they will never interact with Inventory.
""", translate=True),
            'tms_account_ids' : fields.many2many('account.account', 'tms_product_account_rel', 'product_id', 'account_id', 'Accounts for this product'),
            'tms_activity_duration': fields.float('Duration', digits=(14,2), help="Activity duration in hours"),
            'tms_property_account_income' : fields.many2one('account.account', 'Substitute Income Account', 
                                                                help='Use this to define  substitute income account for Freights, Moves, Insurance, etc', 
                                                                required=False),
            'tms_property_account_expense' : fields.many2one('account.account', 'Substitute Expense Account', 
                                                                help='Use this to define substitute account for Fuel Voucher Expense', 
                                                                required=False),

        }

    _default = {
        'tms_category': lambda *a: 'no_tms_product',
        }


    def _check_tms_product(self,cr,uid,ids,context=None):
        for record in self.browse(cr, uid, ids, context=context): 
            if record.tms_category in ['transportable']:
                return (record.type=='service' and record.procure_method == 'make_to_stock' and record.supply_method =='buy' and not record.sale_ok and not record.purchase_ok)
            elif record.tms_category in ['freight', 'move','insurance','highway_tolls','other']:
                return (record.type=='service' and record.procure_method == 'make_to_stock' and record.supply_method =='buy' and record.sale_ok)
            elif record.tms_category in ['real_expense', 'madeup_expense', 'salary', 'salary_retention', 'salary_discount', 'negative_balance', 'indirect_expense']:
                return (record.type=='service' and record.procure_method == 'make_to_stock' and record.supply_method =='buy' and record.purchase_ok)
            elif record.tms_category in ['fuel']:
                return (record.type=='product' and record.procure_method == 'make_to_stock' and record.supply_method =='buy' and record.purchase_ok)

        return True


    _constraints = [
        (_check_tms_product, 'Error ! Product is not defined correctly...Please see tooltip for TMS Category', ['tms_category'])
        ]

    def onchange_tms_category(self, cr, uid, ids, tms_category):
        val = {}
        if not tms_category or tms_category=='standard':
            return val
        if tms_category in ['transportable', 'freight', 'move','insurance','highway_tolls','other','real_expense','madeup_expense', 'salary', 'salary_retention', 'salary_discount', 'negative_balance']:
            val = {
                'type': 'service',
                'procure_method':'make_to_stock',
                'supply_method': 'buy',
                'purchase': False,
                'sale': False,
                }
        return {'value': val}

product_product()


class product_category(osv.osv):
    _name = "product.category"
    _inherit = "product.category"
    
    _columns = {
        'tms_property_account_income_categ': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Substitute Income Account",
            view_load=True,
            help="This account will be used instead of previous field to break down every move line by Vehicle and Driver."),
        'tms_property_account_expense_categ': fields.property(
            'account.account',  
            type='many2one',
            relation='account.account',
            string="Substitute Expense Account",
            view_load=True,
            help="This account will be used instead of previous field to break down every move line by Vehicle and Driver."),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
