# TruecallerBot
Find me if you can 

git clone https://github.com/problems-arelifepartner/TruecallerBot/

cd TruecallerBot

pip install selenium requests webdriver-manager

python3 WhatsAppBot.py



# How This Works
Opens WhatsApp Web in a headless Chrome browser.
Waits for you to scan the QR code once (session is saved in ./user_data folder).
Periodically checks chats for unread messages.
If the sender is not in known_contacts (assumed unsaved), it fetches info from Truecaller API.
Sends the fetched info as a reply.
Keeps running until interrupted.

WhatsApp Web automation: WhatsApp actively tries to block automation. Using Selenium with WhatsApp Web can break anytime. For production, consider official WhatsApp Business API or third-party services.
Truecaller API: You must have a valid premium API key and understand their API endpoints and request format.
Running on Termux or cloud platforms: Selenium requires a headless browser (like Chrome or Firefox). You must install and configure these browsers and drivers accordingly.
Legal and ethical considerations: Scraping or automating WhatsApp and Truecaller data may violate their terms of service. Use responsibly.
