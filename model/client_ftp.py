# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from openerp.osv import orm, fields
from openerp.tools.translate import _
from ftplib import FTP, FTP_TLS
from StringIO import StringIO
from utils import generate_paths


class ClientFTP(orm.Model):
    """
        Simple model for easier connecting to FTP server and some helpers.
    """
    _name = 'client.ftp'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'host': fields.char('Host', size=64, required=True),
        'port': fields.integer('Port', size=5, required=True),
        'user': fields.char('User', size=64),
        'password': fields.char('Password', size=64),
        'tls': fields.boolean('TLS'),
        'upload_paths': fields.char('Upload paths', size=128,
            help=("A comma separated list of UNIX paths where "
                  "files will be uploaded, ex. tmp,uploads/oe ")),
    }
    _defaults = {
        'port': 21,
    }

    def get_upload_paths_one(self, cr, uid, id, filename, context=None):
        """
            Generates a list of UNIX paths from upload_paths
            and appends the filename.
        """
        upload_paths = self.read(
            cr, uid, [id], ['upload_paths'],
            context=context)[0]['upload_paths']
        return generate_paths(upload_paths, filename)

    def get_upload_paths(self, cr, uid, ids, filename, context=None):
        results = [
            self.get_upload_paths_one(cr, uid, id, filename, context)
            for id in ids]
        return dict(zip(ids, results))

    def test_connection(self, cr, uid, ids, context=None):
        try:
            ftp_conn = self.connect(cr, uid, ids, context)
            ftp_conn.retrlines('LIST')
        except:
            raise
        else:
            ftp_conn.quit()
            raise orm.except_orm(
                _('Success!'),
                _('Successfully connected to ftp server')
            )

        return True

    def connect(self, cr, uid, ids, context=None):
        ids = ids[0] if isinstance(ids, (list, tuple)) else ids
        settings = self.read(cr, uid, ids, [], context)

        if settings['tls']:
            ftp_conn = FTP_TLS(timeout=15)
        else:
            ftp_conn = FTP(timeout=15)

        try:
            ftp_conn.connect(host=settings['host'], port=settings['port'])
            ftp_conn.login(user=settings['user'], passwd=settings['password'])
            if settings['tls']:
                ftp_conn.prot_p()
        except Exception as exc:
            raise orm.except_orm(
                _('FTP Error'),
                _('Could not connect to FTP Server\n\n%s') % exc
            )

        return ftp_conn

    def upload(self, cr, uid, ids, ftp_conn, filedata, filepaths, context=None):
        try:
            for filepath in filepaths:
                ftp_conn.storbinary('STOR %s' % filepath, StringIO(filedata))
        except Exception as exc:
            raise orm.except_orm(
                _('FTP Error'),
                _('Could not upload file to FTP Server\n\n%s') % exc
            )

        return True

    def download(self, cr, uid, ids, ftp_conn, filepath, context=None):
        data = StringIO()
        try:
            ftp_conn.retrbinary('RETR %s' % filepath, data.write)
        except Exception as exc:
            raise orm.except_orm(
                _('FTP Error'),
                _('Could not download file from FTP Server\n\n%s') % exc
            )

        return data.getvalue()

    def get_file_list(self, cr, uid, ids, ftp_conn, dirpath, context=None):
        try:
            return ftp_conn.nlst(dirpath)
        except Exception as exc:
            raise orm.except_orm(
                _('FTP Error'),
                _('Could not get file list from FTP Server\n\n%s') % exc
            )
