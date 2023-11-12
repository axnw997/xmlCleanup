import xml.etree.ElementTree as ET
import os
from tkinter import filedialog
import csv
import re
from decimal import Decimal


new_folder = r'/Users/xiaoyu/Desktop/dummy/新生成数据' #for testing only

def write_xml(file_original, file_modified, new_element1_value, new_element3_value): #这个最开始给e写的
    # Parse the XML file into a tree structure

    tree = ET.parse(file_original)

    # Get the root element of the XML document

    root = tree.getroot()

    components = root[0][0][2]

    totals = root[0][0][3]

    # Create two new elements

    new_element1 = ET.Element("{urn:nz:isi:interFundInvestorReport}non_tax_calc_fees")

    new_element2 = ET.Element("{urn:nz:isi:interFundInvestorReport}non_tax_calc_performance_fees")

    new_element3 = ET.Element("{urn:nz:isi:interFundInvestorReport}non_tax_calc_fees")

    new_element4 = ET.Element("{urn:nz:isi:interFundInvestorReport}non_tax_calc_performance_fees")

    # Set the text content for the new elements

    new_element1.text = new_element1_value

    new_element2.text = "0.0000000000" # predefined fixed data

    new_element3.text = new_element3_value

    new_element4.text = "0.00" # predefined fixed data

    components.append(new_element1)

    components.append(new_element2)

    totals.append(new_element3)

    totals.append(new_element4)

    tree.write(file_modified)

    # covert XML with ifir prefix

    # Parse the original XML file into a tree structure

    treeM = ET.parse(file_modified)

    root = treeM.getroot()

    # Define the new namespace prefix

    new_namespace_prefix = 'ifir'

    # Replace the old prefix with the new prefix throughout the XML

    xml_str = ET.tostring(root, encoding="utf-8").decode("utf-8")

    xml_str = xml_str.replace('ns0', new_namespace_prefix)

    root = ET.fromstring(xml_str)

    xml_output = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # Parse the XML string

    root = ET.fromstring(xml_output)

    # Register the "ifir" namespace

    ET.register_namespace("ifir", "urn:nz:isi:interFundInvestorReport")

    # Save the parsed XML to a file

    treeM = ET.ElementTree(root)

    treeM.write(file_modified, encoding='utf-8', xml_declaration=True)

    print('all done')


def calculation(investor_units_held_value, AN_price, element3_value):
    investor_units_held_value = Decimal(investor_units_held_value)
    AN_price = Decimal(AN_price)
    element3_value = Decimal(element3_value)
    value_3 = investor_units_held_value * AN_price + element3_value
    new_element3 = round(value_3, 10)
    return str(AN_price), str(new_element3)
# calculation('3777886.2756000000', '0.000067169', '12043.69')

def read_xml_folder_from_one_day_before(yesterday_folder, customer_code): #去前一天xml里提取element 3数据
    # List all files in the directory
    files = os.listdir(yesterday_folder)
    for fileName in files:
        if customer_code in fileName:
            yesterday_xml_file_path = os.path.join(yesterday_folder, fileName)
            element3_value = retrieve_xml_element3(yesterday_xml_file_path)
            return element3_value


def retrieve_xml_element3(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    namespace = {'ifir': 'urn:nz:isi:interFundInvestorReport'}
    non_tax_calc_fees = root.findall('.//ifir:non_tax_calc_fees', namespaces=namespace)
    element_3_value = non_tax_calc_fees[1].text
    return element_3_value

def read_AN_price_csv_file():
    print('选择：csv price file')
    csv_price_file = filedialog.askopenfilename()
    with open(csv_price_file, 'r') as file:
        # Create a CSV reader
        csv_reader = csv.reader(file)
        next(csv_reader)
        # Read each row in the CSV file
        for row in csv_reader:
            AN_price = row[39] # 从price csv里读取的AN数据
            return AN_price

def get_today_xml_data(xml_file_path): #从'今天需要生成的数据， 这个数据是从cap系统里出来的' ， 需要ifir:investor_units_held这个tag里的数据
    # times 今天的AN数据 + read_xml_folder_from_one_day_before里的数据， 然后直接生成带有4个new tags数据发给客人。
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    namespace = {'ifir': 'urn:nz:isi:interFundInvestorReport'}
    investor_units_held = root.find('.//ifir:investor_units_held', namespaces=namespace)
    investor_units_held_value = investor_units_held.text
    return investor_units_held_value

def read_files_fromCap_folder():
    print('选择：今天从capital导出的文件夹')
    capital_folder_path = filedialog.askdirectory() #每天从capital系统导出的文件存放的文件夹
    AN_price = read_AN_price_csv_file()
    print('选择存放前一天数据的文件夹')
    pattern = r'N\d{4}'
    yesterday_folder = filedialog.askdirectory()
    pattern = r'N\d{4}'
    # define new file folder
    print('选择:要写入的文件夹')
    file_modified_directory = filedialog.askdirectory()

    if capital_folder_path:
        # List all files in the directory
        files = os.listdir(capital_folder_path)
        for fileName in files:
            if fileName.lower().endswith('.xml') or fileName.lower().endswith('.XML'):
                today_cap_xml_file_path = os.path.join(capital_folder_path, fileName)
                result = re.search(pattern, fileName)
                if result:
                    customer_code = result.group()
                    element3_value = read_xml_folder_from_one_day_before(yesterday_folder,customer_code)
                    investor_units_held_value = get_today_xml_data(today_cap_xml_file_path)
                    print(customer_code, investor_units_held_value, AN_price, element3_value)
                    file_modified = os.path.join(file_modified_directory, fileName)
                    new_element1, new_element3 = calculation(investor_units_held_value,AN_price, element3_value)
                    write_xml(today_cap_xml_file_path, file_modified, new_element1, new_element3)

read_files_fromCap_folder()

#----测试用---get element3数据------
# test_file = r'/Users/xiaoyu/Desktop/dummy/前一天的XML数据(带4个tags)/N1011_1430_SSCET.XML'
# test_file = r'/Users/xiaoyu/Desktop/dummy/todays-cap/N1000_1016_SSCET.XML'
# retrieve_xml_element3(test_file)
# get_today_xml_data(test_file)
#----测试用---get element3数据------

# file_original = r"/Users/xiaoyu/Desktop/dummy/todays-cap/N1000_1016_SSCET.XML"
# file_modified= r"/Users/xiaoyu/Desktop/dummy/new-folder/222.XML"
# write_xml(file_original, file_modified)

#从'今天需要生成的数据， 这个数据是从cap系统里出来的' ， 需要ifir:investor_units_held这个tag里的数据
# times 今天的AN数据 + read_xml_folder_from_one_day_before里的数据， 然后直接生成带有4个new tags数据发给客人。

#N1005 3777886.2756000000 0.000067169 12043.69
#从'今天需要生成的数据， 这个数据是从cap系统里出来的' ， 需要ifir:investor_units_held这个tag里的数据
# times 今天的AN数据 + read_xml_folder_from_one_day_before里的数据， 然后直接生成带有4个new tags数据发给客人。