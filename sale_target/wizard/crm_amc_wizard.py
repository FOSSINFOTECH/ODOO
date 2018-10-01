# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, tools, _
from datetime import datetime
import time
from odoo.validator import expand_date
from odoo.exceptions import UserError
import calendar


class sale_target_wizard(models.TransientModel):
    _name = 'sale_target_wizard'
    _description = 'Sales Person Target Vs Actual'

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    @api.multi
    def wizard_open_window(self):
        context = dict(self._context or {})
        cr = self.env.cr
        t_day = time.strftime("%Y-%m-%d")
        if context.get('default_from_menu') != 'sales_target':
            if self.from_date and self.to_date:
                end_date = datetime.strftime(datetime.strptime(self.to_date, "%Y-%m-%d").date(), "%Y-%m-%d 23:59:59")
                if self.from_date < '2017-05-31' or self.to_date > t_day:
                    raise UserError('Warning! \nFrom Date must be greater than 31 May 2017 and End date must be lesser that today')
                if self.from_date > self.to_date:
                    raise UserError('Warning! \nTo Date is lesser than From Date')
            else:
                raise UserError('Warning! \n Select From Date and To Date ')

        if self.period_from:
            from_date = self.period_from.date_start
            to_date = datetime.strftime(datetime.strptime(self.period_from.date_stop, "%Y-%m-%d").date(), "%Y-%m-%d 23:59:59")

        tools.drop_view_if_exists(cr, 'crm_sales_person_target_report')
        qry = """
            CREATE OR REPLACE VIEW crm_sales_person_target_report AS (
            select
                t_actual.user_id as id
                ,t_actual.branch_id as branch
                ,t_actual.user_id as assigned_id
                ,sap.sap_actual_value as sap_actual
                ,plan.values as target
                ,t_actual.order_confirmed_value as order
                ,(COALESCE(plan.values,0) - COALESCE(t_actual.order_confirmed_value,0) - COALESCE(sap.sap_actual_value,0)) as order_yet_to_reveive
                ,t_actual.enq_val as enquiry_val
                ,t_actual.lead_value_buffer as lead_val
                ,t_actual.quotation_value as quotation
                ,(COALESCE(t_actual.enq_val,0) + COALESCE(t_actual.lead_value_buffer,0)) as order_expected
                ,(COALESCE(plan.values,0) - COALESCE(t_actual.order_confirmed_value,0) - COALESCE(sap.sap_actual_value,0) - (COALESCE(t_actual.enq_val,0) + COALESCE(t_actual.lead_value_buffer,0))) as deficit
                ,COALESCE(t_actual.enq_lost_val,0) as enquiry_lost_val
                ,t_actual.quotation_lost_val as quotation_lost_val
                ,(COALESCE(t_actual.quotation_lost_val,0) + COALESCE(t_actual.enq_lost_val,0)) as quotation_enq_lost_val
            from
                    (
                        select
                            c.id as user_id
                            , c.branch_id
                            ,(
                                select
                                    ((sum(price))*50)/100 as lead_value_buffer
                                    from
                                    product_line
                                    where
                                    name in (
                                                select
                                                        id
                                                from
                                                        crm_lead
                                                where
                                                        stage_id in (select id from crm_stage where name = 'New') and
                                                        type = 'lead' and
                                                        user_id = c.id and
                                                        order_excepted_date >= '""" + from_date + """' and
                                                        order_excepted_date <= '""" + to_date + """'
                                            )
                            )
                            ,(
                                select
                                    ((sum(price))*75)/100 as enq_val
                                from
                                    product_line
                                where
                                    name in (
                                                select
                                                     id
                                                from
                                                     crm_lead
                                                where
                                                    stage_id in (select id from crm_stage where name in ('New', 'Demo', 'Site Survey')) and
                                                    type = 'opportunity' and
                                                    user_id = c.id and
                                                    order_excepted_date >= '""" + from_date + """' and
                                                    order_excepted_date <= '""" + to_date + """'
                                            )
                            ),
                            (
                                select 
                                    sum(price) as enq_lost_val
                                from 
                                    product_line
                                where
                                    name in (
                                                select
                                                     id
                                                from
                                                     crm_lead
                                                where
                                                    user_id = c.id and
                                                    stage_id = (select id from crm_stage where name = 'Lost') and
                                                    lead_lost_date >= '""" + from_date + """' and 
                                                    lead_lost_date <= '""" + to_date + """')
                            ),
                            (
                                select
                                    sum(amount_untaxed) as quotation_value
                                from
                                    sale_order
                                where
                                    user_id = c.id and
                                    state in ('sent','draft')  and
                                    order_excepted_date >= '""" + from_date + """' and
                                    order_excepted_date <= '""" + to_date + """'
                            ),
                            (
                                select
                                    sum(amount_untaxed) as quotation_lost_val
                                from
                                    sale_order
                                where
                                    user_id = c.id and
                                    state = 'cancel'  and
                                    lost_date >= '""" + from_date + """' and
                                    lost_date <= '""" + to_date + """'
                            ),
                            (
                                select
                                    sum(amount_untaxed) as order_confirmed_value
                                from
                                    sale_order
                                where
                                    user_id = c.id and
                                    state = 'progress'  and
                                    sale_date_done >= '""" + from_date + """' and
                                    sale_date_done <= '""" + to_date + """'
                            )
                        from res_users c
                        where
                        c.product_classification = 'Sales' and
                        c.active = True
                        group by c.id, c.branch_id order by c.branch_id
                    ) t_actual

            left join
                    (
                        SELECT
                            user_id,
                            year,
                            unnest(array[04, 05, 06, 07, 08, 09, 10, 11, 12, 01, 02, 03]) AS "month",
                            unnest(array[month_1, month_2, month_3, month_4, month_5, month_6, month_7, month_8, month_9, month_10, month_11, month_12]) AS "values"
                        FROM
                            target_sale_engineer
                        ORDER BY user_id, "month"
                    ) plan
            on plan.user_id = t_actual.user_id and plan.month='""" + str(self.period_from.name).split('/')[0] + """' and 
            plan.year = """ + str(self.period_from.fiscalyear_id.id) + """


            left join
                    (
                    SELECT
                        user_id as sap_user
                        ,max(actual_value) as sap_actual_value
                    FROM
                        sap_salesperson_table
                    where 
                        month='""" + str(self.period_from.name).split('/')[0] + """' and
                        year='""" + str(self.period_from.date_start)[0:4] + """'
                    group by user_id
                        ORDER BY user_id 
                    ) sap
                    on sap.sap_user = t_actual.user_id
            )"""
        print qry, '-----sales_report'
        cr.execute(qry)

        view_ref = self.env['ir.model.data'].get_object_reference('roots_reports', 'crm_sales_person_target_tree')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Target vs Sales vs  Order Expected (' + self.period_from.name + ')'),
            'res_model': 'crm.sales.person.target.report',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
