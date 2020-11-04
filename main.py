import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import smtplib
import configparser
from email.message import EmailMessage
import sys
import schedule
import time

def check_for_update():
  BASE_URL = "https://www.amazon.co.uk/s?k=1440p+144hz+monitor&i=computers&rh=n%3A428652031%2Cp_n_specials_match%3A21583550031"

  options = uc.ChromeOptions()
  options.headless=True
  options.add_argument('--headless')
  chrome = uc.Chrome(options=options)
  chrome.get(BASE_URL)
  html = chrome.page_source

  soup = BeautifulSoup(html, features='lxml')

  results_html = soup.find_all(attrs={"data-component-type": "s-search-results"})[0].select(".s-main-slot")[0].findChildren(attrs={"data-component-type": "s-search-result"}, recursive=False)

  titles = list(map(lambda res: res.find(attrs={"class": "a-size-medium"}).get_text(), results_html))
  titles.sort()

  title_str = ''.join(titles)

  with open('results_cache.txt', "r") as f:
    if f.read() != title_str:
      send_notification()
      print("Sending notification")

  with open('results_cache.txt', 'w') as f:
    f.write(title_str)


def send_notification():
  msg = EmailMessage()
  msg.set_content("")

  msg['Subject'] = f'Monitor Update'
  msg['From'] = "nikhil1231@hotmail.co.uk"
  msg['To'] = "nikhil1231@hotmail.co.uk"

  config = configparser.ConfigParser()
  config.read("creds.ini")

  server = smtplib.SMTP('smtp.live.com', 25)
  server.starttls()
  server.login(config['DEFAULT']['email'], config['DEFAULT']['password'])

  server.send_message(msg)
  server.quit()

if __name__ == "__main__":
  avg_wait_time = int(sys.argv[1])
  variance = 0.3
  schedule.every(int(avg_wait_time * (1 - variance))).to(int(avg_wait_time * (1 + variance))).minutes.do(check_for_update)

  while 1:
    schedule.run_pending()
    time.sleep(1)