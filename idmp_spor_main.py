from datetime import datetime
from datetime import date
from lib2to3.pytree import Base
from re import M
from socket import timeout
from wsgiref import headers
from selenium import webdriver
import time
from datetime import timedelta
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException#, ElementClickInterceptedException, ElementNotInteractableException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# import os
# import zipfile
# import glob
# import json
# import xmltodict
# import calendar
from webdriver_manager.chrome import ChromeDriverManager
import requests
import mysql.connector.pooling

class idmp():
    def __init__(self):
        self.date = datetime.now()
        db_config = {
        'user' : 'root',
        'database' : 'idmp_spor',
        'host' : 'localhost',
        'password' : 'Sql_1234',
        'port' : 3306
        }



        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                                pool_name = "new_pool",
                                pool_size = 10,
                                auth_plugin='mysql_native_password',**db_config)
        self.conn = self.connection_pool.get_connection()
        self.cursor = self.conn.cursor()
            


    def driver_conn(self):
        options = webdriver.ChromeOptions()

        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument("--disable-notifications")
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-backgrounding-occluded-windows")

        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)
        return self.driver
    
    def get_authentication(self, driver):
        try:
            driver.get("https://spor.ema.europa.eu/rmswi/#/lists")
            driver.maximize_window()
            time.sleep(5)

            # list
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/nav[2]/div/ul/li[2]/a'))).click()
            time.sleep(10)

            # view list
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/nav[2]/div/ul/li[2]/ul/li[1]/a'))).click()
            time.sleep(10)

            cookies_list = driver.get_cookies()
            auth_token = cookies_list[0]["value"]
            time.sleep(5)

            driver.close()
            return auth_token
        except BaseException as e:
            print("Exception: ", e)
    
    def get_ids(self, auth_token):
        try:
            header = {
                # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
            'accept' : "application/json",
            'Authorization': 'Bearer '+ auth_token
            }
            url = "https://spor.ema.europa.eu/v1/lists?pagesize=500"
            response = requests.get(url, headers=header)
            data = response.json()

            list_data = data["list-of-lists"]["list-summary"]
            # print(list_data)
            list_ids = []

            for i in range(len(list_data)):

                list_id = list_data[i]["list-id"]["id"]

                list_ids.append(list_id)
            return list_ids
        except BaseException as e:
            print("Exception: ", e)
    def get_rms_ids_and_names(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""select idsp_rms_list.identifier, idsp_rms_list.name, rms_table_names.name 
                        from idsp_rms_list inner join rms_table_names
                        on idsp_rms_list.identifier = rms_table_names.identifier """)
        self.combined_data = self.cursor.fetchall()
        # combined_data

        # main_ids = [list_id[0] for list_id in self.combined_data]

        self.table_names = [(list_id[1], list_id[2]) for list_id in self.combined_data]

        return self.combined_data, self.table_names


    def spor_list(self,combined_data,table_names, auth_token):
        header = {
            'accept' : "application/json",
            'Authorization': 'Bearer ' + auth_token
            }
        
        main_dict = {}
        for table_data in combined_data:
            url = f'https://spor.ema.europa.eu/v1/lists/{table_data[0]}/term-summaries?lang=en&page=1&pagesize=20&parent=all&sortby=term-name'
            response = requests.get(url,  headers=header)
        #     print(response)
            data = response.json()
            main_list = []
            sub_list = []
            while url != "":
                spor_list = []
                try:
                    response = requests.get(url,  headers=header)
                    
                    data = response.json()

                    itemlist = data['controlled-terms-list-summary']['controlled-term-summaries']["controlled-term-summary"]
                except BaseException as e:
                    break
                    
                for i in range(len(itemlist)):

                    dict_val = {}

                    list_name = data['controlled-terms-list-summary']['list-summary']['list-name']

                    id = itemlist[i]["term-id"]["id"] 
                    term_name = itemlist[i]["term-names"]["term-name"]["name"]["text"]

                    if "short-names" not in  itemlist[i].keys():
                        short_name = ""
                    else:
                        short_name=itemlist[i]["short-names"]["short-name"]["name"]["text"]

                    source_id = ""

                    status = itemlist[i]["status"]["code"]

                    dict_val["id"] = id
                    dict_val["term-name"] = term_name
                    dict_val["short-name"] = short_name
                    dict_val["source_id"] = source_id
                    dict_val["status"] = status

                    spor_list.append(dict_val)
                sub_list.extend(spor_list)
                main_list.extend(sub_list)
                main_dict[table_data[2]] = main_list

                nextpage = data["controlled-terms-list-summary"]["next-page"]
                url = nextpage
                # except Exception as e:
                #     url = ""
                #     print("Error: ", e)

                # sub_list.append(spor_list)
                # main_list.extend(sub_list)
                # main_dict[list_name] = main_list
    
        print(main_dict)
        for table_name, value in main_dict.items():
#     print(table_name)
            if table_name == "idsp_xevmpd_domain":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
        #             print(each_row)
        #             cursor.execute(f"insert into idsp_xevmpd_domain (identifier, term_name,short_name, source_id, status) values(%s,%s,%s,%s,%s)", (each_row["id"], each_row["term-name"],each_row["short-name"],each_row["source_id"],each_row["status"]))
                    self.cursor.execute(f"""insert into idsp_xevmpd_domain (identifier, term_name,short_name, source_id, status)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}', 
                                    '{each_row["status"]}' 
                                    where not exists
                                    (select identifier from idsp_xevmpd_domain where identifier = '{each_row["id"]}' )""")
                    self.conn.commit()
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_legal_status_supply":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    self.cursor.execute(f"""insert into idsp_xevmpd_legal_status_supply (identifier, term_name,short_name, source_id, status)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}', 
                                    '{each_row["status"]}' 
                                    where not exists
                                    (select identifier from idsp_xevmpd_legal_status_supply where identifier = '{each_row["id"]}' limit 1)""")
                    self.conn.commit()
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_full_indication_text":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_xevmpd_full_indication_text (identifier, term_name,short_name, source_id, status)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}', 
                                    '{each_row["status"]}' 
                                    where not exists
                                    (select identifier from idsp_xevmpd_full_indication_text where identifier = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_product_type_information":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_xevmpd_product_type_information (identifier, name, owner, version)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}'
                                    where not exists
                                    (select identifier from idsp_xevmpd_product_type_information where identifier = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_pharmaceutical_dose_forms":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_xevmpd_pharmaceutical_dose_forms (`key`, value, type)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}"
                                    where not exists
                                    (select `key` from idsp_xevmpd_pharmaceutical_dose_forms where `key` = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_legal_basis":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_legal_basis (`key`, value)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}"
                                    where not exists
                                    (select `key` from idsp_legal_basis where `key` = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)  
            elif table_name == "idsp_xevmpd_product_cross_reference_type":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    self.cursor.execute(f"""insert into idsp_xevmpd_product_cross_reference_type (identifier, term_name,short_name, source_id, status)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}', 
                                    '{each_row["status"]}' 
                                    where not exists
                                    (select identifier from idsp_xevmpd_product_cross_reference_type where identifier = '{each_row["id"]}' limit 1)""")
                    self.conn.commit()
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_marketing_status":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    self.cursor.execute(f"""insert into idsp_xevmpd_marketing_status (identifier, term_name,short_name, source_id, status)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}", 
                                    "{each_row["short-name"]}", 
                                    '{each_row["source_id"]}', 
                                    '{each_row["status"]}' 
                                    where not exists
                                    (select identifier from idsp_xevmpd_marketing_status where identifier = '{each_row["id"]}' limit 1)""")
                    self.conn.commit()
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
            elif table_name == "idsp_xevmpd_units_of_presentation":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_xevmpd_units_of_presentation (`key`, value)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}"
                                    where not exists
                                    (select `key` from idsp_xevmpd_units_of_presentation where `key` = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name) 
            elif table_name == "idsp_xevmpd_routes_of_administration":
        #         print(table_name)
                rowcount = 0
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_xevmpd_routes_of_administration (`key`, value)
                                    select 
                                    '{each_row["id"]}', 
                                    "{each_row["term-name"]}"
                                    where not exists
                                    (select `key` from idsp_xevmpd_routes_of_administration where `key` = '{each_row["id"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name) 
            elif table_name == "idsp_countries":
                for each_row in value:
                    try:
                        self.cursor.execute(f"""insert into idsp_countries (country_name, country_code)
                        select
                        '{each_row["term-name"]}',
                        ''
                        where not exists
                        (select country_name from idsp_countries where country_name = '{each_row["term-name"]}' limit 1)""")
                        self.conn.commit()
                    except Exception as e:
                        print(e)
                    if self.cursor.rowcount != 0:
                        rowcount += 1
                if rowcount == 0 :
                    print("already inserted")
                else:
                    print(rowcount," rows inserted in", table_name)
                
            
            

            
idmp = idmp()
driver = idmp.driver_conn()
try:
    auth_token = idmp.get_authentication(driver)
except:
    auth_token = ""
print("auth token: ", auth_token)

if auth_token == "" or auth_token == None :
    for i in range(5):
        driver = idmp.driver_conn()
        try:
            auth_token = idmp.get_authentication(driver)
        except:
            auth_token = ""
        print("auth token: ", auth_token)
        if auth_token != "" or auth_token != None:
            combined_data,table_names  = idmp.get_rms_ids_and_names()
            spor_list = idmp.spor_list(combined_data,table_names, auth_token)
            break      
else:
    combined_data,table_names = idmp.get_rms_ids_and_names()
   
    spor_list = idmp.spor_list(combined_data,table_names, auth_token)
    



