from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from twilio.rest import TwilioRestClient
import os
import time
import datetime
import configparser
import re

### requires selenium drivers at the appropriate path

### requires config file with the following
# [auth]
# twilio_sid=
# twilio_auth_token=
# goes_user=
# goes_pw=
#
# [tn]
# twilio_tn=
# my_tn=
#
# [general]
# target_date=20170126
# selenium_driver_path=$PATH:[your path]
###

config = configparser.ConfigParser()
config.read('config.txt')

account_sid = config.get('auth', 'twilio_sid') # Your Account SID from www.twilio.com/console
auth_token  = config.get('auth', 'twilio_auth_token')  # Your Auth Token from www.twilio.com/console


xtra_wait = 3
target_date = config.get('general', 'target_date')

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

        os.environ['PATH'] = config.get('general', 'selenium_driver_path')

        # browser = webdriver.Firefox()
        browser = webdriver.Chrome()

        try:
            #####
            ## login

            wait = WebDriverWait(browser, 10)

            browser.get('https://goes-app.cbp.dhs.gov/goes/jsp/login.jsp')

            loginElem = browser.find_element_by_id('j_username')

            loginElem.send_keys(config.get('auth', 'goes_user'))

            passwordElem = browser.find_element_by_id('j_password')

            passwordElem.send_keys(config.get('auth', 'goes_pw'))

            passwordElem.submit()

            #######
            ## prove you're a human

            self.wait4element(wait, 'checkMe')

            time.sleep(xtra_wait)

            humanElem = browser.find_element_by_id('checkMe')

            humanElem.click()

            #######
            ## click "manage appointments"

            self.wait4element(wait, 'manageAptm')

            mgElem = browser.find_element_by_name('manageAptm')

            mgElem.click()

            #######
            ## click "reschedule"

            self.wait4element(wait, 'reschedule')

            reschedElem = browser.find_element_by_name('reschedule')

            reschedElem.click()

            #######
            ## select enrollment center

            self.wait4element(wait, 'selectedEnrollmentCenter')

            el = browser.find_element_by_id('selectedEnrollmentCenter')
            for option in el.find_elements_by_tag_name('option'):
                if option.get_attribute("value") == '5183':
                    option.click() # select() in earlier versions of webdriver
                    break

            nextElem = browser.find_element_by_name('next')

            nextElem.click()

            ########
            ## check for earliest available date

            # self.wait4element(wait, 'reschedule')

            tgt = browser.find_element_by_css_selector("td[id*='scheduleForm\:schedule1_header_']")
            # print(tgt.get_attribute("id"))
            date = tgt.get_attribute("id")[30::]
            # print ("earliest date: {0}".format(date))

            nextElem = browser.find_element_by_name('scheduleForm:j_id_id22')

            nextElem.click()

            ########
            ## select another enrollment center

            self.wait4element(wait, 'selectedEnrollmentCenter')

            el = browser.find_element_by_id('selectedEnrollmentCenter')
            for option in el.find_elements_by_tag_name('option'):
                if option.get_attribute("value") == '11981':
                    option.click() # select() in earlier versions of webdriver
                    break

            nextElem = browser.find_element_by_name('next')

            nextElem.click()

            ########
            ## check for text indicating no appointments

            field_office_unavail = re.search(r'Currently there are no available appointments at this enrollment center', browser.page_source)


            ########
            ## send SMS

            if (send_sms):
                message = ''

                if self.earlier_than(date,target_date):
                    message += "Ohare: +++ {0}".format(date)
                else:
                    message += "Ohare: --- {0}".format(date)

                if field_office_unavail:
                    message += " | Field: ---".format(date)
                else:
                    message += " | Field: +++".format(date)

                print(message)

                client.messages.create(body=message,
                                                 to=config.get('tn', 'my_tn'),    # Replace with your phone number
                                                 from_=config.get('tn', 'twilio_tn')) # Replace with your Twilio number

            ########
            ## log out

            nextElem = browser.find_element_by_link_text('Log off')

            nextElem.click()



        except Exception as inst:
            print('bummer, something failed :(')
            print(type(inst))
            print(inst.args)
            client.messages.create(body="failure",
                                             to=config.get('tn', 'my_tn'),    # Replace with your phone number
                                             from_=config.get('tn', 'twilio_tn')) # Replace with your Twilio number

        if quit_on_end:
            browser.quit()

GoesScraper().run()
# GoesScraper().run(send_sms=False, quit_on_end=False)