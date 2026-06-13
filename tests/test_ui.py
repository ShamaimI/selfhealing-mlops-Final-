from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("http://localhost:32500")
        wait = WebDriverWait(driver, 10)

        text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
        text_input.send_keys("The cinematography was breathtaking and the performances were outstanding")

        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        time.sleep(3)

        result_output = driver.find_element(By.ID, "result-output")
        result_text = result_output.text

        assert result_text != ""
        assert any(word in result_text for word in ["POSITIVE", "NEGATIVE", "Confidence"])

    finally:
        driver.quit()
