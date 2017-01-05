from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from twilio.rest import TwilioRestClient
import os
import time
import datetime


# send SMS (from +4915735981929)
account_sid = "AC6cd6df60141eeb7454b852fba8799181" # Your Account SID from www.twilio.com/console
auth_token  = "d145c2335a886a23870f3d5c7d9ac4ae"  # Your Auth Token from www.twilio.com/console


xtra_wait = 3
target_date = '20170126'

class GoesScraper():

    def wait4element(self, wait, element):
        try:
            wait.until(
                EC.presence_of_element_located((By.NAME, element))
            )
        except TimeoutException:
            print("timeout while waiting")


    def earlier_than(self, test_date, target_date):
        earliest_date = datetime.datetime.strptime(test_date, "%Y%m%d")
        cutoff_date = datetime.datetime.strptime(target_date, "%Y%m%d")

        if earliest_date <= cutoff_date:
            return True
        else:
            return False



    def run(self, send_sms=True, quit_on_end=True):

        client = TwilioRestClient(account_sid, auth_token)

        os.environ['PATH'] = "$PATH:/Users/dan/dev/tools/selenium/"

        browser = webdriver.Firefox()

        try:
            wait = WebDriverWait(browser, 10)

            browser.get('https://goes-app.cbp.dhs.gov/goes/jsp/login.jsp')

            loginElem = browser.find_element_by_id('j_username')

            loginElem.send_keys('ecodan68')

            passwordElem = browser.find_element_by_id('j_password')

            passwordElem.send_keys('Ru18qtpi!')

            passwordElem.submit()

            #######
            self.wait4element(wait, 'checkMe')

            time.sleep(xtra_wait)

            humanElem = browser.find_element_by_id('checkMe')

            humanElem.click()

            #######

            self.wait4element(wait, 'manageAptm')

            mgElem = browser.find_element_by_name('manageAptm')

            mgElem.click()

            #######

            self.wait4element(wait, 'reschedule')

            reschedElem = browser.find_element_by_name('reschedule')

            reschedElem.click()

            #######

            self.wait4element(wait, 'selectedEnrollmentCenter')

            el = browser.find_element_by_id('selectedEnrollmentCenter')
            for option in el.find_elements_by_tag_name('option'):
                if option.get_attribute("value") == '5183':
                    option.click() # select() in earlier versions of webdriver
                    break

            nextElem = browser.find_element_by_name('next')

            nextElem.click()

            ########
            self.wait4element(wait, 'reschedule')

            tgt = browser.find_element_by_css_selector("td[id*='scheduleForm\:schedule1_header_']")
            print(tgt.get_attribute("id"))
            date = tgt.get_attribute("id")[30::]
            print ("earliest date: {0}".format(date))


            if (send_sms):
                if self.earlier_than(date,target_date):
                    message = "+++ maybe; earliest {0}".format(date)
                else:
                    message = "--- not looking good; earliest {0}".format(date)

                message = client.messages.create(body=message,
                                                 to="+491755838527",    # Replace with your phone number
                                                 from_="+4915735981929") # Replace with your Twilio number


        except Exception as inst:
            print('bummer, something failed :(')
            print(type(inst))
            print(inst.args)
            message = client.messages.create(body="failure",
                                             to="+491755838527",    # Replace with your phone number
                                             from_="+4915735981929") # Replace with your Twilio number
        if quit_on_end:
            browser.quit()

# GoesScraper().run()
# GoesScraper().run(send_sms=False, quit_on_end=False)