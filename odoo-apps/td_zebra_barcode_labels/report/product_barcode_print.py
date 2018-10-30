# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, api, _
from reportlab.graphics import barcode
from base64 import b64encode


class TRReportBarcodeLabels(models.AbstractModel):
    _name = 'report.td_zebra_barcode_labels.report_product_tdzebrabarcode'

    @api.model
    def get_report_values(self, docids, data=None):
        browse_record_list = []
        product_obj = self.env["product.product"]
        config = self.env.ref('td_zebra_barcode_labels.default_tdzebrabarcode_configuration')
        if not config:
            raise Warning(_(" Please configure barcode data from "
                            "configuration menu"))
        for rec in data['form']['product_ids']:
            for loop in range(0, int(rec['qty'])):
                browse_record_list.append((
                       product_obj.browse(int(rec['product_id']))))
        return {
            'doc_ids': browse_record_list,
            'docs': docids,
            'product_name': data['form']['product_name'],
            'product_variant': data['form']['product_variant'],
            'price_display': data['form']['price_display'],
            'product_code': data['form']['product_code'],
            'get_barcode_string': self._get_barcode_string,
            'data': data,
            'get_lines': self._get_lines,
            'config': config
            }

#     @api.model
#     def _get_barcode_string(self, barcode_value, data):
#         barcode_str = barcode.createBarcodeDrawing(
#                             data['barcode_type'],
#                             value=barcode_value,
#                             format='png',
#                             width=int(data['barcode_height']),
#                             height=int(data['barcode_width']),
#                             humanReadable=data['humanreadable']
#                             )
#         encoded_string = b64encode(barcode_str.asString('png'))
#         barcode_str = "<img style='width:" + str(data['display_width']) + "px;height:" + str(data['display_height']) + "px'src='data:image/png;base64,{0}'>".format(encoded_string)
#         return barcode_str or ''

    @api.model
    def _get_barcode_string(self, barcode_value, data):
        barcode_str = barcode.createBarcodeDrawing(
                            data['barcode_type'],
                            value=barcode_value,
                            format='png',
                            width=int(data['barcode_height']),
                            height=int(data['barcode_width']),
                            humanReadable=data['humanreadable']
                            )
        encoded_string = b64encode(barcode_str.asString('png')).decode("utf-8")
        barcode_str = "<img style='width:" + str(data['display_width']) + "px;height:" + str(data['display_height']) + "px'src='data:image/png;base64,{0}'>".format(encoded_string)
        return barcode_str or ''


    @api.model
    def _get_symbol(self, product):
        symbol = ''
        if product.company_id:
            symbol = product.company_id.currency_id.symbol
        else:
            symbol = self.env.user.company_id.currency_id.symbol
        return symbol

    @api.model
    def _divided_blank_update(self, total_quantities):
        """
        Process
            -add a blank dictionaries
        """
        lists = []
        needs_to_add = total_quantities % 2
        if needs_to_add == 1:
            lists.append({'name_1': ' '})
            lists.append({'name_2': ' '})
        if needs_to_add == 2:
            lists.append({'name_2': ' '})
        return lists

    @api.model
    def _get_lines(self, form):
        prod_obj = self.env['product.product']
        result = []
        dict_data = {}
        data_append = False
        price_display = form.get('price_display')
        currency_position = form.get('currency_position', 'before') or 'before'
        total_value = 0

        lines = form and form.get('product_ids', []) or []
        total_quantities = sum([int(x['qty']) for x in lines])
        user = self.env.user
        for l in lines:
            p = prod_obj.sudo().browse(l['product_id'])
            for c in range(0, int(l['qty'])):
                value = total_value % 2
                data_append = False
                symbol = self._get_symbol(p)
                if price_display:
                    price_value = str(round(p.lst_price,2))
                    list_price = symbol+' '+price_value
                    if currency_position == 'after':
                        list_price = price_value+' '+symbol
                    dict_data.update({'list_price'+'_'+str(value): list_price})

                barcode_value = p[str(form['barcode_field'])]

                variant = ", ".join([v.name for v in p.attribute_value_ids])
                attribute_string = variant and "%s" % (variant) or ''
                dict_data.update({
                   'name'+'_'+str(value): p.name or '',
                   'code'+'_'+str(value): barcode_value,
                   'variants'+'_'+str(value): attribute_string or '',
                   'default_code'+'_'+str(value): p.default_code or '',
                  })
                total_value += 1
                if total_value % 2 == 0:
                    result.append(dict_data)
                    data_append = True
                    dict_data = {}

        if not data_append:
            result.append(dict_data)
        return [x for x in result if x]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
