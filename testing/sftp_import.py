import pysftp
from base64 import decodebytes
import simplejson
import requests
import os
import csv
from datetime import datetime

from config import *
from auth.sap_api_get_token import AuthSAP

host = "sftp.sfg.inmar.com"
username = "SC_TaosFootwearT"
password = "8dxmSc9a9f"
key_data = b"""AAAAB3NzaC1yc2EAAAADAQABAAAAgQCIVugupAhmlOSw90S5E7gK9AXSflbO9Fk1HtZ3Lq6cMjNFSMomCWcfLWsdpzmhcCain+9DSs76WQc8AmGZQY4Bgw5oxSyIZu4FPwFGpx1R6BKT3iu0fdtX6XCDad6mFjit1hv6M+kLv8bSbaRT/qXnDg5pf53sGp6IcyOWRmrq1w=="""
key = pysftp.RSAKey(data=decodebytes(key_data))
cnopts = pysftp.CnOpts()
cnopts.hostkeys.add(host, 'ssh-rsa', key)


def import_files():
    located_filenames = get_ftp_filenames('/Inbox')
    print(located_filenames)

    if located_filenames:
        # 'TaosFootwear_Scans20191105103600382.csv'
        for filename in located_filenames:
            print(filename[:18])
            print(filename[:22])
            if filename[:18] == 'TaosFootwear_Scans' or filename[:22] == 'TaosFootwear_Shipments':
                print(filename)
                remote_path = '/Inbox/' + filename
                local_path = './sftp/in/wip/' + filename
                file_retrieved = get_ftp_file(remote_path, local_path)
                if file_retrieved is True:
                    delete_ftp_file(remote_path)
                    sap_doc = build_sap_doc(filename, local_path)

                    if sap_doc:
                        endpoint = ''
                        if filename[:18] == 'TaosFootwear_Scans':
                            endpoint = 'credit_memos'
                            sap_doc.update(SaveAsDraft=True)
                        elif filename[:22] == 'TaosFootwear_Shipments':
                            endpoint = 'purchase_orders'
                        create_status = create_sap_doc(sap_doc, endpoint)
                        if create_status == 'Success':
                            print('good')
                            path_to = './sftp/in/archive/' + filename
                            move_local_file(local_path, path_to)
                        else:
                            print('bad')
                            path_to = './sftp/in/error/' + filename
                            move_local_file(local_path, path_to)


def get_ftp_filenames(ftp_path):
    located_filenames = []
    sftp = pysftp.Connection(host=host, username=username, password=password, cnopts=cnopts)
    if sftp:
        print("Connection successfully established ...")
        # Switch to a remote directory
        sftp.cwd(ftp_path)

        # Obtain filenames
        filenames = sftp.listdir()
        # build list of filename
        for filename in filenames:
            located_filenames.append(filename)
        return located_filenames


def get_ftp_file(remote_path, local_path):
    sftp = pysftp.Connection(host=host, username=username, password=password, cnopts=cnopts)
    if sftp:
        print("Connection successfully established ...")
        # Check if file exist
        file_exist = sftp.isfile(remote_path)
        if file_exist:
            file = sftp.get(remotepath=remote_path, localpath=local_path)
            return True
        else:
            return False
    else:
        return False


def delete_ftp_file(remote_path):
    sftp = pysftp.Connection(host=host, username=username, password=password, cnopts=cnopts)
    if sftp:
        print("Connection successfully established ...")
        # Check if file exist
        file_exist = sftp.isfile(remote_path)
        if file_exist:
            file = sftp.remove(remote_path)
            return True
        else:
            return False
    else:
        return False


def move_local_file(path_from, path_to):
    os.replace(path_from, path_to)


def build_sap_doc(filename, local_path):
    sap_doc = {}
    imported_file = []
    # load flat file to dict
    with open(local_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            # print(dict(row))
            imported_file.append(dict(row))
    file.close()

    if imported_file:
        upc_list = []
        for row in imported_file:
            if 'UniversalIDasProvided' in row.keys():
                upc_list.append(row['UniversalIDasProvided'])
                row.update(upc=row['UniversalIDasProvided'])
            elif 'UniversalId' in row.keys():
                upc_list.append(row['UniversalId'])
                row.update(upc=row['UniversalId'])
        upc_list = list(set(upc_list))
        print(upc_list)
        upc_count = len(upc_list)

        sap_error, items_located = sap_items_check_by_upc(upc_list)
        if sap_error is False:
            items_located_count = len(items_located)
            if upc_count == items_located_count:
                print('good')
                doc_date = ''
                if filename[:18] == 'TaosFootwear_Scans':
                    card_code = 'BBB'
                    doc_date = (filename[19:27])
                elif filename[:22] == 'TaosFootwear_Shipments':
                    card_code = 'Lianyun'
                    doc_date = (filename[22:30])
                doc_date = datetime.strptime(doc_date, '%Y%m%d').strftime('%m/%d/%Y')

                sap_doc = {
                    'DocType': 'I',
                    'DocDate': doc_date,
                    'DocDueDate': doc_date,
                    'TaxDate': doc_date,
                    'CardCode': card_code,
                    'NumAtCard': '',
                    'DiscSum':  0,
                    'Comments': ''
                }

                doc_lines = []
                for row in imported_file:
                    for item in items_located:
                        if row['upc'] == item['CodeBars']:
                            doc_lines.append({'ItemCode': item['ItemCode'], 'Quantity': row['Quantity']})
                sap_doc.update({'Lines': doc_lines})

            else:
                print('bad')
                path_to = './sftp/in/error/' + filename
                move_local_file(local_path, path_to)
    return sap_doc


def sap_items_check_by_upc(upc_list):
    sap_error = False
    items_located = []
    url = SAP_URL + '/v1/items'
    token = AuthSAP.gettoken()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = {
            'columns': ['ItemCode', 'CodeBars'],
            'params': {'CodeBars': {'op': 'IN', 'value': upc_list}}
        }
        data = simplejson.dumps(data)

        sap_status = ''
        try:
            r = requests.get(url, data=data, headers=headers, verify=False)
            result = r.json()

            if r.status_code == 200 and result:
                for item in result:
                    items_located.append(dict(ItemCode=item['ItemCode'], CodeBars=item['CodeBars']))
            r.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh)
            sap_status = 'Failed'
        except requests.exceptions.ConnectionError as err:
            print('Error Connecting:', err)
            sap_status = 'Failed'
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt)
            sap_status = 'Failed'
        except requests.exceptions.RequestException as err:
            print('Request Exception:', err)
            sap_status = 'Failed'

        if sap_status == 'Failed':
            sap_error = True
    else:
        sap_error = True
    return sap_error, items_located


def create_sap_doc(sap_package, endpoint):
    url = SAP_URL + '/v1/' + endpoint
    token = AuthSAP.gettoken()
    if token:
        headers = {'authorization': 'JWT ' + token, 'content-type': 'application/json'}
        data = simplejson.dumps(sap_package)

        sap_status = 'Success'
        try:
            r = requests.post(url, data=data, headers=headers, verify=False)
            result = r.json()

            if r.status_code == 201:
                sap_status = 'Success'
                return sap_status
            elif r.status_code == 403:
                sap_status = 'Partial'
                return sap_status
            else:
                r.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh)
            sap_status = 'Failed'
        except requests.exceptions.ConnectionError as err:
            print('Error Connecting:', err)
            sap_status = 'Failed'
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt)
            sap_status = 'Failed'
        except requests.exceptions.RequestException as err:
            print('Request Exception:', err)
            sap_status = 'Failed'

        return sap_status

    else:
        return 'Failed'


if __name__ == '__main__':
    import_files()
    # build_sap_doc('TaosFootwear_Scans_20191108135832.csv', './sftp/in/wip/TaosFootwear_Scans_20191108135832.csv')
