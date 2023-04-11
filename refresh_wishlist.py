import requests
import json
import selenium
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from tqdm import tqdm


with open('config.json') as f:
    config = json.load(f)

url_sim = config['url_sim']
url_auth = config['url_auth']
r_list = config['r_list']
region_id = config['region_id']
server_xpath = config['server_xpath']
server = config['server']
char_xpath = config['char_xpath']
presence = config['presence']
run_optimizer = config['run_optimizer']
Source_xpath = config['Source_xpath']
url_copy = config['url_copy']
sim_options = config['sim_options']
patchwerk = config['patchwerk']
fight_style = config['fight_style']
audit_login_b = config['audit_login_b']
wishlist_post_url = config['wishlist_post_url']
spec_error = config['spec_error']
percent = config['percent']
stage = config['stage']
bnet_l_field = config['bnet_l_field']
bnet_p_field = config['bnet_p_field']
login = config['login']
passwo = config['passwo']
authorization = config['authorization']

#options
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')


def post_report(report_id, id, name):
    json_data = {'report_id': report_id, 'character_id': id, 'character_name': name, 'configuration_name': 'Single Target', 'replace_manual_edits': True, 'clear_conduits': True}
    post_wishlist(config['wishlist_post_url'], json_data)
    print(f'{name} is posted')

def get_character_names_and_ids():
    url = 'https://wowaudit.com/v1/characters'
    headers = {'accept': 'application/json', 'Authorization': authorization}

    response = requests.get(url, headers=headers)
    
    if os.stat('r_list.txt').st_size != 0:
        open('r_list.txt', 'w').close()
    if response.status_code == 200:
        data = json.loads(response.text)
        for element in data:

            character_data = (element['name'] + ':' + str(element['id']))
            with open('r_list.txt', 'a', encoding='utf-8') as f:
                f.write(character_data + '\n')

    else:
        print(f'Request failed with status code {response.status_code}')
    
def post_wishlist(url, json_data):
    headers = {'Content-type': 'application/json', 'accept' : 'application/json', 'Authorization': authorization}
    response = requests.post(url, data=json.dumps(json_data), headers=headers)
    return response

def driver_init(options):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    print('driver initialised')
    return driver


def login_sim(driver, login, passwo):
    driver.get(url_auth)
    driver.find_element(By.ID, 'loginEmail').send_keys(login)
    driver.find_element(By.ID, 'loginPassword').send_keys(passwo)
    driver.find_element(By.ID, 'loginSubmit').send_keys(Keys.ENTER)
    print('logged in')
    time.sleep(1)

def is_class_supported(driver):
    try:
        driver.find_element(By.XPATH, spec_error)
        return False
    except:
        return True



def get_name_and_id(txt):
    name = txt.split(':')[0]
    id = txt.split(':')[1]
    return name, id

def select_region(driver):
    driver.get(url_sim)
    WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.ID, region_id)))
    select = Select(driver.find_element(By.ID, region_id))
    select.select_by_visible_text('EU')

def enter_server(driver, server):
    driver.find_element(By.XPATH, server_xpath).send_keys(server)
    driver.find_element(By.XPATH, server_xpath).send_keys(Keys.ENTER)

def enter_character(driver, name):
    driver.find_element(By.ID, char_xpath).clear()
    driver.find_element(By.ID, char_xpath).send_keys(name)
    WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, presence)))
    WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, Source_xpath)))

def is_class_supported(driver):
    try:
        driver.find_element(By.XPATH, sim_options)
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False

def click_source(driver):
    driver.execute_script(
    "arguments[0].scrollIntoView({'block':'center','inline':'center'})", driver.find_element(By.XPATH, Source_xpath))
    driver.find_element(By.XPATH, Source_xpath).click()

def select_fight_style(driver):
    try:
        driver.find_element(By.XPATH, patchwerk)
        driver.execute_script(
        "arguments[0].scrollIntoView({'block':'center','inline':'center'})", driver.find_element(By.XPATH, sim_options))
        driver.find_element(By.XPATH, sim_options).click()
        WebDriverWait(driver=driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, fight_style)))
        select = Select(driver.find_element(By.XPATH, fight_style))
        select.select_by_visible_text('Light Movement')
    except selenium.common.exceptions.NoSuchElementException:
        pass


def _run_optimizer(driver, name):
    driver.find_element(By.XPATH, run_optimizer).click()
    show_progress_bar(name, driver)
    WebDriverWait(driver=driver, timeout=600).until(EC.presence_of_element_located((By.XPATH, url_copy)))
    url_parts = driver.current_url.split('/')
    report_id = url_parts[-1]
    return report_id


def show_progress_bar(name, driver):
    print(f'running {name}...')
    WebDriverWait(driver=driver, timeout=30).until(EC.presence_of_element_located((By.XPATH, percent)))
    total_iterations = 100
    progress_bar = tqdm(total=total_iterations, desc=name)
    while True:
        
        color = driver.find_element(By.XPATH, stage).value_of_css_property('color')
        if color == 'rgba(17, 17, 17, 1)':
            break
    tmp = 0
    while True:
        try:
            percentage = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, percent))).text.strip('%')
            progress_bar.update(int(percentage) - tmp)
            tmp = int(percentage)
            if progress_bar.n == 100:
                progress_bar.close()
                break
        except:
            progress_bar.update(100 - tmp)
            progress_bar.close()
            break
        



def report_get(txt, driver):
    name, id = get_name_and_id(txt)
    select_region(driver)
    enter_server(driver, server)
    enter_character(driver, name)
    if not is_class_supported(driver):
        print(f'{name} is not supported')
        return
    click_source(driver)
    select_fight_style(driver)
    report_id = _run_optimizer(driver, name)
    post_report(report_id, id, name)

    
get_character_names_and_ids()
print('names and ids updated')
driver = driver_init(options)
login_sim(driver, login, passwo)



with open(r_list, encoding='UTF-8') as r_txt:
    for line in r_txt:
        report_get(line, driver)
    print('All done')


#Таланты, корутины
