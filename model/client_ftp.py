# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from openerp import models, fields, api
from openerp.tools.translate import _
from ftplib import FTP, FTP_TLS
from openerp.exceptions import Warning
from StringIO import StringIO


class ClientFTP(models.Model):
    """
        Simple model for easier connecting to FTP server and some helpers.
    """
    _name = 'client.ftp'

    name = fields.Char('Name', size=64, required=True)
    host = fields.Char('Host', size=64, required=True)
    port = fields.Integer('Port', size=5, required=True, default=21)
    user = fields.Char('User', size=64)
    password = fields.Char('Password', size=64)
    tls = fields.Boolean('TLS')

    @api.multi
    def test_connection(self):
        try:
            ftp_conn = self.connect()
            ftp_conn.retrlines('LIST')
        except:
            raise
        else:
            ftp_conn.quit()
            raise Warning(
                _('Success!'),
                _('Successfully connected to ftp server')
            )

        return True

    def connect(self):
        self.ensure_one()

        if self.tls:
            ftp_conn = FTP_TLS(timeout=15)
        else:
            ftp_conn = FTP(timeout=15)

        try:
            ftp_conn.connect(host=self.host, port=self.port)
            ftp_conn.login(user=self.user, passwd=self.password)
            if self.tls:
                ftp_conn.prot_p()
        except Exception as exc:
            raise Warning(
                _('FTP Error'),
                _('Could not connect to FTP Server\n\n%s') % exc
            )

        return ftp_conn

    @staticmethod
    def upload(ftp_conn, filedata, filepaths):
        try:
            for filepath in filepaths:
                ftp_conn.storbinary('STOR %s' % filepath, StringIO(filedata))
        except Exception as exc:
            raise Warning(
                _('FTP Error'),
                _('Could not upload file to FTP Server\n\n%s') % exc
            )

        return True

    @staticmethod
    def download(ftp_conn, filepath):
        data = StringIO()
        try:
            ftp_conn.retrbinary('RETR %s' % filepath, data.write)
        except Exception as exc:
            raise Warning(
                _('FTP Error'),
                _('Could not download file from FTP Server\n\n%s') % exc
            )

        return data.getvalue()

    @staticmethod
    def get_file_list(ftp_conn, dirpath):
        try:
            return ftp_conn.nlst(dirpath)
        except Exception as exc:
            raise Warning(
                _('FTP Error'),
                _('Could not get file list from FTP Server\n\n%s') % exc
            )
