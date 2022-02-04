import base64
import re
import time

import browser_cookie3
import cv2
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract
from PyQt5.QtCore import pyqtSignal, QThread


class Macro(QThread):
    logged = pyqtSignal(str)
    opt = None
    url = ""
    pw = ""

    def run(self) -> None:
        self.logged.emit("크롬 드라이버를 준비합니다.")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        self.logged.emit("브라우저를 실행합니다.")
        driver.get("https://naver.com")

        self.logged.emit("쿠키를 브라우저에 주입합니다.")
        for c in browser_cookie3.chrome():
            if c.domain == ".naver.com":
                cookie = {
                    "domain": c.domain,
                    "name": c.name,
                    "value": c.value,
                }
                if c.expires:
                    cookie["expiry"] = c.expires
                if c.path_specified:
                    cookie["path"] = c.path
                driver.add_cookie(cookie)

        self.logged.emit("구매 페이지로 이동합니다.")
        driver.get(self.url)

        self.logged.emit("구매를 시작합니다.")
        while True:
            try:
                if self.opt is not None:
                    driver.find_element(
                        "xpath",
                        "//a[text()='(선택하기)']",
                    ).click()
                    options = driver.find_element(
                        "xpath",
                        "//a[text()='(선택하기)']/following-sibling::ul",
                    )
                    options.find_elements(
                        "xpath",
                        ".//*",
                    )[self.opt].click()
                driver.find_element(
                    "xpath",
                    "//span[text()='구매하기']/parent::a",
                ).click()
            except UnexpectedAlertPresentException:
                driver.refresh()
            else:
                break

        self.logged.emit("결제를 진행합니다.")
        while True:
            try:
                driver.find_element(
                    "xpath",
                    "//button[text()='결제하기']",
                ).click()
            except NoSuchElementException:
                pass
            else:
                break

        while len(driver.window_handles) < 2:
            time.sleep(0.1)

        driver.switch_to.window(driver.window_handles[1])

        self.logged.emit("키패드를 인식 중입니다.")
        while True:
            try:
                css_data = driver.find_element(
                    "xpath",
                    '//span[contains(@class, "SecureKeyboard")]',
                ).get_attribute("style")
            except NoSuchElementException:
                pass
            else:
                break

        img_data = css_data[css_data.find(",") + 1 : css_data.rfind('"')]

        img_name = "keypad.png"
        with open(img_name, "wb") as f:
            f.write(base64.b64decode(img_data.encode("ascii")))

        img = np.asarray(Image.open(img_name))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        transformed_img = np.concatenate((img[:50], img[50:100]), axis=1)
        transformed_img = np.concatenate((transformed_img, img[100:150]), axis=1)
        transformed_img = np.concatenate((transformed_img, img[150:200]), axis=1)
        inverted_img = 255 - transformed_img

        text = pytesseract.image_to_string(
            inverted_img,
            config="--psm 7 -c tessedit_char_whitelist=0123456789",
        )
        numbers = list(re.sub(r"[^0-9]", "", text))

        self.logged.emit("키패드를 인식을 마쳤습니다.")
        self.logged.emit("찾은 숫자: " + ", ".join(numbers))

        keypads = driver.find_elements(
            "xpath",
            '//span[contains(@class, "SecureKeyboard")]',
        )

        self.logged.emit("비밀번호를 입력합니다.")
        for x in self.pw:
            keypads[numbers.index(x)].click()
