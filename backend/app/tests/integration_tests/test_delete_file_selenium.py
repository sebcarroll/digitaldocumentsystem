'''
# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestDeletefileselenium():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_deletefileselenium(self):
    self.driver.get("http://localhost:3000/drive")
    self.driver.set_window_size(1050, 892)
    self.driver.find_element(By.CSS_SELECTOR, ".file-item:nth-child(2) .MuiSvgIcon-root").click()
    self.driver.find_element(By.CSS_SELECTOR, ".action-button:nth-child(5) > .MuiSvgIcon-root").click()
'''  
