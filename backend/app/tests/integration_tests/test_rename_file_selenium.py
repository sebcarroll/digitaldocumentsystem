import pytest
from selenium.webdriver.common.by import By

@pytest.mark.usefixtures("chrome_driver")
class TestRename:
    def test_rename(self):
        self.driver.get("http://localhost:3000/drive")
        self.driver.set_window_size(1050, 892)
        self.driver.find_element(By.CSS_SELECTOR, ".file-item:nth-child(1) path").click()
        self.driver.find_element(By.CSS_SELECTOR, ".action-button:nth-child(7) > .MuiSvgIcon-root").click()
        self.driver.find_element(By.CSS_SELECTOR, ".popup-input").send_keys("Test")
        self.driver.find_element(By.CSS_SELECTOR, ".ok-button").click()