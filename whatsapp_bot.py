import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Configuration ===
TRUECALLER_API_KEY = "your_truecaller_premium_api_key_here"
WHATSAPP_WEB_URL = "https://web.whatsapp.com/"
CHECK_INTERVAL = 5  # seconds

# === Setup Selenium with headless Chrome ===
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # comment this if you want to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-data-dir=./user_data")  # persist session to avoid QR scan every time
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(WHATSAPP_WEB_URL)
    print("Please scan the QR code if not logged in.")
    return driver

# === Truecaller API call ===
def get_truecaller_info(phone_number):
    url = f"https://api4.truecaller.com/v1/search?phone={phone_number}"
    headers = {
        "Authorization": f"Bearer {TRUECALLER_API_KEY}",
        "Accept": "application/json",
        "User -Agent": "Truecaller/Android"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Parse relevant info from Truecaller response
            if "data" in data and len(data["data"]) > 0:
                user_info = data["data"][0]
                name = user_info.get("name", "Unknown")
                city = user_info.get("city", "Unknown")
                country = user_info.get("country", "Unknown")
                return f"Name: {name}\nCity: {city}\nCountry: {country}"
            else:
                return "No information found on Truecaller."
        else:
            return f"Truecaller API error: {response.status_code}"
    except Exception as e:
        return f"Error calling Truecaller API: {str(e)}"

# === Check for new messages and unsaved contacts ===
def check_new_messages(driver, known_contacts):
    try:
        # Wait for chat list to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='grid']"))
        )
        chats = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")
        for chat in chats:
            try:
                # Check if chat is unread (new message)
                unread = chat.find_elements(By.CSS_SELECTOR, "span[aria-label='unread message']")
                if not unread:
                    continue  # no new message

                # Extract contact name or number
                contact_name_elem = chat.find_element(By.CSS_SELECTOR, "span[dir='auto']")
                contact_name = contact_name_elem.text

                # If contact is a number (unsaved), it usually looks like a phone number
                if contact_name not in known_contacts:
                    print(f"New unsaved contact/message detected: {contact_name}")
                    known_contacts.add(contact_name)
                    # Open chat
                    chat.click()
                    time.sleep(2)

                    # Send Truecaller info
                    info = get_truecaller_info(contact_name)
                    send_message(driver, info)
                    time.sleep(1)
                    # Go back to chat list
                    driver.back()
            except Exception as e:
                print(f"Error processing chat: {e}")
    except Exception as e:
        print(f"Error checking messages: {e}")

# === Send message in currently open chat ===
def send_message(driver, message):
    try:
        # Find message input box
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"))
        )
        input_box.click()
        input_box.send_keys(message)
        time.sleep(1)
        # Find send button and click
        send_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='compose-btn-send']")
        send_button.click()
        print("Sent message with Truecaller info.")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    driver = setup_driver()
    known_contacts = set()

    # Wait for user to scan QR code and WhatsApp Web to load
    print("Waiting for WhatsApp Web to load and login...")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='grid']"))
    )
    print("Logged in successfully.")

    try:
        while True:
            check_new_messages(driver, known_contacts)
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
