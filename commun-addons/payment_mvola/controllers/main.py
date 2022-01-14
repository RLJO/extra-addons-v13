# -*- coding: utf-8 -*-

import logging
import json
import werkzeug
from odoo import http
from odoo.http import request
from zeep import Client, helpers

_logger = logging.getLogger(__name__)


class MvolaController(http.Controller):
    _notify_url = '/payment/mvola/notification'
    _return_url = '/payment/mvola/validation'
    _cancel_url = '/payment/mvola/cancel'
    _api_version = '2.0.0'

    @http.route('/payment/mvola/', type='http', auth='none', methods=['GET', 'POST'], csrf=False, website=True)
    def mvola_validation(self, **post):
        reference = post.get('item_number')
        tx = None
        if reference:
            tx = request.env['payment.transaction'].search([('reference', '=', reference)]).sudo()
            mvola_urls = request.env['payment.acquirer']._get_mvola_urls(tx and tx.acquirer_id.state or 'enabled')
            mvola_data = {
                'APIVersion': self._api_version,
                'Login_WS': tx.acquirer_id.mvola_api_username,
                'Password_WS': tx.acquirer_id.mvola_api_password,
                'HashCode_WS': tx.acquirer_id.mvola_hashcode,
                'ShopTransactionAmount': post.get('amount'),
                'ShopTransactionID': post.get('item_number'),
                'ShopTransactionLabel': post.get('item_name'),
                'ShopShippingName': post.get('first_name'),
                'ShopShippingAddress': post.get('address1'),
                'UserField1': None,
                'UserField2': None,
                'UserField3': None
            }

            # PaymentRequest
            ClientWS = Client(mvola_urls.get('mvola_ws_url'))
            ResultWS = ClientWS.service.WS_MPGw_PaymentRequest(self._api_version, mvola_data)
            if ResultWS.ResponseCodeDescription == 'OK':
                tx.sudo().write({
                    'mvola_token_id': ResultWS.MPGw_TokenID,
                })
                payment_url = mvola_urls.get('mvola_transaction_url') + ResultWS.MPGw_TokenID
                return werkzeug.utils.redirect(payment_url)
            else:
                return ResultWS.ResponseCodeDescription
        return 'Transaction error'

    @http.route('/mv/validation', type='http', auth='none', methods=['GET'], csrf=False)
    def url_validaiton(self, **post):
        # to do : redirect according to payment type : e-commerce - customer portal
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return werkzeug.utils.redirect(werkzeug.urls.url_join(base_url, '/shop/confirmation'))

    @http.route('/mv/cancel', type='http', auth='none', methods=['GET'], csrf=False)
    def url_annulation(self, **post):
        _logger.exception('Payment cancelled')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/mv/notification', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def url_notification(self, **post):
        reference = post.get('Shop_TransactionID')
        tx = request.env['payment.transaction'].search([('reference', '=', reference)])
        if tx:
            # check data
            check_data = {
                'Login_WS': tx.acquirer_id.mvola_api_username,
                'Password_WS': tx.acquirer_id.mvola_api_password,
                'HashCode_WS': tx.acquirer_id.mvola_hashcode,
                'MPGw_TokenID': tx.mvola_token_id,
            }
            mvola_urls = request.env['payment.acquirer']._get_mvola_urls(tx and tx.acquirer_id.state or 'enabled')
            ClientWS = Client(mvola_urls.get('mvola_ws_url'))
            StatusWS = ClientWS.service.WS_MPGw_CheckTransactionStatus(self._api_version, check_data)
            StatusWSDict = helpers.serialize_object(StatusWS)
            print(type(StatusWSDict))
            if StatusWSDict.get('MvolaTransactionStatus') == 'SUCCESS':
                tx.sudo().write({
                    'acquirer_reference': StatusWSDict.get('MvolaTransactionID')
                })
                tx.sudo()._set_transaction_done()
                tx.sudo()._post_process_after_done()
            return json.dumps({'TransactionStatusDescription': StatusWSDict.get('TransactionStatusDescription')})
        else:
            return 'Transaction error'
