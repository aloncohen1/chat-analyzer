from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
print(driver)
driver.get('https://www.yad2.co.il/realestate/forsale?topArea=2&area=11&city=6200')

# search_input = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, 'textSearchHome'))
# )
# search_input.send_keys('cars')

WebDriverWait(driver, 10).until(driver.navigate().refresh())

print('3')