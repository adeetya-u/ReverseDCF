import requests
from bs4 import BeautifulSoup
import statistics

def scrape_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        return None

def scrape_net_profit_second_last(symbol):
    urls = [f"https://www.screener.in/company/{symbol}/consolidated/", f"https://www.screener.in/company/{symbol}/"]

    for url in urls:
        soup = scrape_from_url(url)
        if soup:
            profit_loss_section = soup.find('section', id='profit-loss')
            if profit_loss_section:
                net_profit_row = None
                for tr in profit_loss_section.find_all('tr', class_='strong'):
                    td = tr.find('td', class_='text')
                    if td and 'Net Profit' in td.text:
                        net_profit_row = tr
                        break

                if net_profit_row:
                    net_profit_values = [td.text.strip() for td in net_profit_row.find_all('td')[1:]]
                    if len(net_profit_values) >= 2:
                        second_last_value = net_profit_values[-2]
                        net_profit = float(second_last_value.replace(',', ''))
                        return net_profit

    return None

def scrape_market_cap_and_pe(symbol):
    # URLs to try: first consolidated, then regular if the first fails.
    urls = [f"https://www.screener.in/company/{symbol}/consolidated/", f"https://www.screener.in/company/{symbol}/"]

    for url in urls:
        soup = scrape_from_url(url)
        if soup:
            data = {'Market Cap': None, 'Stock P/E': None, 'FY23 P/E': None, 'Net Profit': None}
            top_ratios = soup.find('ul', id='top-ratios')
            if top_ratios:
                for li in top_ratios.find_all('li', class_='flex flex-space-between'):
                    name_span = li.find('span', class_='name')
                    if name_span and 'Market Cap' in name_span.string:
                        market_cap_span = li.find('span', class_='number')
                        if market_cap_span:
                            market_cap_text = market_cap_span.text.strip()
                            if market_cap_text:
                                try:
                                    data['Market Cap'] = float(market_cap_text.replace('Cr.', '').replace(',', ''))
                                except ValueError:
                                    continue  # If parsing fails, continue to the next element
                    elif name_span and 'Stock P/E' in name_span.string:
                        stock_pe_span = li.find('span', class_='number')
                        if stock_pe_span:
                            stock_pe_text = stock_pe_span.text.strip()
                            if stock_pe_text:
                                try:
                                    data['Stock P/E'] = float(stock_pe_text)
                                except ValueError:
                                    continue  # If parsing fails, continue to the next element

            net_profit = scrape_net_profit_second_last(symbol)
            if net_profit is not None and data['Market Cap'] is not None:
                data['FY23 P/E'] = round(data['Market Cap'] / net_profit, 2)
                data['Net Profit'] = net_profit
                return data  # Return the data if successful

    # If both attempts fail, return None
    return None


def scrape_roce_median(symbol):
    # URLs to try: first consolidated, then regular if the first fails.
    urls = [f"https://www.screener.in/company/{symbol}/consolidated/", f"https://www.screener.in/company/{symbol}/"]

    for url in urls:
        soup = scrape_from_url(url)
        if soup:
            roce_values = []
            ratios_section = soup.find('section', id='ratios')
            if ratios_section:
                roce_tds = ratios_section.find_all('td', class_='text')
                for roce_td in roce_tds:
                    if 'ROCE %' in roce_td.text:
                        roce_tr = roce_td.parent
                        roce_values_td = roce_tr.find_all('td')[1:]
                        roce_values.extend([float(td.text.strip('%')) for td in roce_values_td if td.text.strip()])

            if len(roce_values) >= 6:
                try:
                    median = statistics.median(roce_values[-6:-1])
                    return median
                except statistics.StatisticsError:
                    print("Error: Unable to compute median for RoCE values.")
                    continue  # Continue to next URL if median computation fails

    return None  # Return None if all attempts fail


def has_valid_percentage_data(soup):
    """
    Check if the page contains valid percentage data.
    Specifically looking for actual numbers followed by '%' rather than just '%'.
    """
    tables = soup.find_all('table', class_='ranges-table')
    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2 and cells[1].text.strip() == '%':  # Checks for the placeholder '%'
                return False
    return True

def scrape_compounded_growth(symbol):
    base_url = "https://www.screener.in/company/{}/{}"
    urls_to_try = ["consolidated", ""]  # First try consolidated, then the standard page

    sales_growth_rates = []
    profit_growth_rates = []

    for url_suffix in urls_to_try:
        url = base_url.format(symbol, url_suffix)
        soup = scrape_from_url(url)
        if soup and has_valid_percentage_data(soup):
            tables = soup.find_all('table', class_='ranges-table')

            # Assuming the first two tables are always Sales Growth and Profit Growth respectively
            for table in tables[:2]:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        growth_rate = cells[1].text.strip()
                        if table.th.text.strip() == "Compounded Sales Growth":
                            sales_growth_rates.append(growth_rate)
                        else:
                            profit_growth_rates.append(growth_rate)

            return sales_growth_rates, profit_growth_rates  # Return arrays

    return None  # Return None if no valid data was found


# Example usage
# symbol = "NESTLEIND"
# market_cap_and_pe = scrape_market_cap_and_pe(symbol)
# roce_median = scrape_roce_median(symbol)
#
# if market_cap_and_pe is not None and roce_median is not None:
#     print("Stock Symbol:", symbol)
#     print("Market Cap:", market_cap_and_pe['Market Cap'], "Cr.")
#     print("Net Profit:", market_cap_and_pe['Net Profit'])
#     print("Current PE:", market_cap_and_pe['Stock P/E'])
#     print("FY23 PE:", market_cap_and_pe['FY23 P/E'])
#     print("5-yr median pre-tax RoCE:", roce_median)
# else:
#     print("Failed to retrieve necessary data.")
#
# compounded_growth = scrape_compounded_growth(symbol)
# if compounded_growth is not None:
#     print("\nCompounded Sales Growth:")
#     for duration, growth_rate in compounded_growth['Sales Growth'].items():
#         print(f"{duration}: {growth_rate}")
#
#     print("\nCompounded Profit Growth:")
#     for duration, growth_rate in compounded_growth['Profit Growth'].items():
#         print(f"{duration}: {growth_rate}")
# else:
#     print("Failed to retrieve necessary data.")

