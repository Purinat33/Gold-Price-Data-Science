import requests
import csv
import os
from datetime import datetime


thai_to_english_month = {
    'มกราคม': 'January',
    'กุมภาพันธ์': 'February',
    'มีนาคม': 'March',
    'เมษายน': 'April',
    'พฤษภาคม': 'May',
    'มิถุนายน': 'June',
    'กรกฎาคม': 'July',
    'สิงหาคม': 'August',
    'กันยายน': 'September',
    'ตุลาคม': 'October',
    'พฤศจิกายน': 'November',
    'ธันวาคม': 'December'
}


def buddhist_to_gregorian(year):
    return year - 543


def convert_thai_date(thai_date_str):
    # Split the date string into day, month, and year
    day, thai_month, thai_year = thai_date_str.split()

    # Convert the year from Buddhist Era (BE) to Common Era (CE)
    gregorian_year = str(int(thai_year) - 543)

    # Convert the Thai month name to English month name
    english_month = thai_to_english_month[thai_month]

    # Combine the components into a final date string
    english_date = f"{day} {english_month} {gregorian_year}"

    return english_date


def convert_thai_time(thai_time: str):
    time, hour_minutes, oclock = thai_time.split()
    return hour_minutes


def up_or_down(symbol: str):
    if symbol == '+':
        return 'up'
    elif symbol == '-':
        return 'down'
    else:
        return 'no change'  # Don't know if this exists


# https://stackoverflow.com/questions/2953746/python-parse-comma-separated-number-into-int
def float_number(number: str) -> float:
    return float(number.replace(',', ''))


# https://stackoverflow.com/questions/53483389/find-the-last-row-from-a-csv-input-python
def is_duplicate_of_previous_line(data: list[str], filename="gold_prices.csv") -> bool:
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
            lines = scraped.readlines()

            # If the file is empty or has only the header row
            if len(lines) <= 1:
                print(
                    "File is empty or contains only the header row: No duplicate check needed.")
                return False

            final_line = lines[-1].strip()
            list_final_line = final_line.split(',')
            # Just check for datetime equal is enough (String because datetime object is odd)
            if str(data[0]) == str(list_final_line[0]):
                print("Current datetime is duplicate of final line: Skipping...")
                return True

        return False

    except FileNotFoundError:
        print("File not found: No duplicate check needed.")
        return False


def to_datetime(dmy_or_hrmin: str):
    if ":" not in dmy_or_hrmin:
        date_obj = datetime.strptime(dmy_or_hrmin, '%d %B %Y').date()
        return date_obj
    else:
        time_obj = datetime.strptime(dmy_or_hrmin, "%H:%M").time()
        return time_obj


def append_to_csv(data, filename='gold_prices.csv'):
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writerow([
                'datetime',
                'gold_buy_price',
                'gold_sell_price',
                'gold_bar_buy_price',
                'gold_bar_sell_price',
                'compare_previous',
                'compare_yesterday'
            ])

        eng_date = convert_thai_date(data['response']['date'])
        eng_time = convert_thai_time(data["response"]['update_time'])
        combined_datetime = datetime.strptime(
            f"{eng_date} {eng_time}", '%d %B %Y %H:%M')

        new_data = [
            combined_datetime,
            float_number(data['response']['price']['gold']['buy']),
            float_number(data['response']['price']['gold']['sell']),
            float_number(data['response']['price']['gold_bar']['buy']),
            float_number(data['response']['price']['gold_bar']['sell']),
            up_or_down(data['response']['price']
                       ['change']['compare_previous']),
            up_or_down(data['response']['price']
                       ['change']['compare_yesterday'])
        ]

        if is_duplicate_of_previous_line(new_data, filename):
            return

        # Write the data
        writer.writerow(new_data)
        print("Gold prices appended to CSV file successfully.")


# Define the API endpoint
url = 'https://api.chnwt.dev/thai-gold-api/latest'

# Make the GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        append_to_csv(data)
    else:
        print("Failed to retrieve gold prices")
else:
    print(f"Failed to connect to API. Status code: {response.status_code}")
