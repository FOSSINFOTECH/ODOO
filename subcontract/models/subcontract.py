# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import itertools
from operator import itemgetter
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # To create a purchase order while clicking on produce button:
    @api.multi
    def open_produce_product(self):
        res = super(MrpProduction, self).open_produce_product()
        vals_item = {}
        vals_line_item = {}
        po_obj = self.env['purchase.order']
        pol_obj = self.env['purchase.order.line']
        if self.subcontract_prod and not self.purchase_ids:
            vals_item = {
                'partner_id': self.vendor.id,
                'state': 'draft',
                'mrp_id': self.id,
                'origin': self.name,
            }
            po_id = po_obj.create(vals_item)
            vals_line_item = {
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'date_planned': self.date_planned_start,
                'product_qty': self.product_qty,
                'product_uom': self.product_id.uom_id.id,
                'price_unit': 0.0,
                'taxes_id': [(6, 0, self.product_id.supplier_taxes_id.ids)],
                'order_id': po_id.id,
            }
            pol_obj.create(vals_line_item)
        return res

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        if self.purchase_ids:
            for po in self.purchase_ids:
                for mo in self.finished_move_line_ids:
                    for po_line in po.order_line:
                        if not po_line.qty_received == mo.qty_done and not self.env.user.has_group('mrp.group_mrp_manager'):
                            raise UserError(_('Quantity to produce and Produced Qty Should be same for validation by user.'))
        return res

    @api.multi
    def action_purchase_view(self):
        action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]
        result['domain'] = "[('id', 'in', " + str(self.purchase_ids.ids) + ")]"
        return result

    @api.onchange('vendor')
    def onchange_picking_type(self):
        if self.subcontract_prod:
            self.location_src_id = self.vendor.property_stock_supplier.id
            self.location_dest_id = self.vendor.property_stock_supplier.id

    @api.depends('purchase_ids')
    def _purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids)

    purchase_count = fields.Integer(compute='_purchase_count', string='# Purchases')
    purchase_ids = fields.One2many('purchase.order', 'mrp_id', string='Pickings')
    vendor = fields.Many2one('res.partner', string="Vendor")
    subcontract_prod = fields.Boolean(string="Subcontract")


class Location(models.Model):
    _inherit = "stock.location"

    def should_bypass_reservation(self):
        res = super(Location, self).should_bypass_reservation()
        action = self.usage in ('customer', 'inventory', 'production') or self.scrap_location
        return action


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mrp_id = fields.Many2one('mrp.production', string="Manufacturing Order")


class Picking(models.Model):
    _inherit = 'stock.picking'

    subcontract = fields.Boolean(string="Subcontract")
    bom_material_ids = fields.One2many('bom.materials', 'picking_id', string="BoM Products")
    flag = fields.Boolean(string="Flag", default=False)

    @api.multi
    def button_validate(self):
        self.mrp_validation()
        if self.picking_type_code in ('outgoing', 'internal'):
            for ml in self.move_lines:
                sq = self.env['stock.quant'].search([('product_id', '=', ml.product_id.id), ('location_id', '=', self.location_id.id)])
                if sq.id == False:
                    raise UserError(_('There is no stock available for the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) in the stock location. Kindly add the required stock.'))
                else:
                    for i in sq:
                        if ml.quantity_done > i.quantity:
                            raise UserError(_('You cannot validate this stock operation because the stock level of the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) would become negative on the stock location and negative stock is not allowed for this product.'))
        res = super(Picking, self).button_validate()
        return res

    @api.multi
    def mrp_validation(self):
        if self.purchase_id.mrp_id.product_id:
            for line in self.move_lines:
                if line.product_id == self.purchase_id.mrp_id.product_id:
                    total_qty = 0
                    if self.purchase_id.mrp_id.finished_move_line_ids:
                        for mrp in self.purchase_id.mrp_id.finished_move_line_ids:
                            if mrp.done_move:
                                total_qty += mrp.qty_done
                        if not line.purchase_line_id.qty_received:
                            if line.quantity_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the Processed Mrp Qty. (or) There is no or less Processed Qty in Stock Move.'))
                        else:
                            curr_qty_done = line.purchase_line_id.qty_received + line.quantity_done
                            if curr_qty_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the processed Mrp Qty .Few of the quantities may be Received'))
                        if self.purchase_id.mrp_id.product_qty == total_qty:
                            self.purchase_id.mrp_id.button_mark_done()
                    else:
                        raise UserError(_('Kindly Process the respective MRP / Work Order for Qty.'))
        return True

    @api.multi
    def get_bom_materials(self):
        list_prod = []
        if not self.bom_material_ids:
            raise UserError(_('Atleast One item is must in BoM Products to update.'))
        if self.bom_material_ids:
            for line in self.bom_material_ids:
                if line.produce_qty <= 0:
                    raise UserError(_('BoM Quantity should not be Zero to Update.'))
            for bom_id in self.bom_material_ids:
                bom_br = self.env['mrp.bom'].browse(bom_id.product_id.id)
                for bom_line_id in bom_br.bom_line_ids:
                    create_vals = {}
                    create_vals = {
                        'name': bom_line_id.product_id.name,
                        'product_id': bom_line_id.product_id.id,
                        'product_uom': bom_line_id.product_uom_id.id,
                        'product_uom_qty': bom_id.produce_qty * bom_line_id.product_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'picking_id': self.id,
                    }
                    list_prod.append(create_vals)
        list_prod.sort(key=itemgetter('product_id'))
        move_temp = []
        for key, items in itertools.groupby(list_prod, key=itemgetter('product_id', 'name', 'product_uom', 'location_id', 'location_dest_id')):
            move_temp.append({
                'product_id': key[0],
                'name': key[1],
                'product_uom': key[2],
                'location_id': key[3],
                'location_dest_id': key[4],
                'product_uom_qty': sum([item["product_uom_qty"] for item in items])
            })
        for new_line in move_temp:
            move_id = self.env['stock.move'].create(new_line)
            move_id.update({'picking_id': self.id})
        self.flag = True
        return True


class BomMaterials(models.Model):
    _name = 'bom.materials'

    picking_id = fields.Many2one('stock.picking', string="Picking")
    product_id = fields.Many2one('mrp.bom', string="BoM Product")
    produce_qty = fields.Float(string="Quantity")
