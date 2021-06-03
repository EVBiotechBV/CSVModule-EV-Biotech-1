"""Client-side module which will be used to download CSV files by the computational input team"""

import pandas
from bs4 import BeautifulSoup
import requests
import json


def authenticate_user(username: str, password: str) -> str:
    """Authentication module to obtain the API token for the current user. This will be used to download
    the data.
    Args:
        username: Elab journal Username
        password: Elab jounral Password
    Returns:
         API token string
    """
    while True:
        response = requests.post("https://www.elabjournal.com/api/v1/auth/user",
                                 data=({'username': username, 'password': password}))

        try:
            json_response = response.json()
            print("Login Successful")
            return json_response['token']
        except json.decoder.JSONDecodeError:
            print("Login failed. Try again.")
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")


def get_section_by_link(api_token: str, section_link: str) -> dict:
    """Retrieves the content of an experiment section by it's GET request link
    Args:
        api_token: The API access token key used to authenticates the api request
        section_link: The GET Request of the section that that is being scraped (This will be received by users via the email module)

    Returns:
        The content of an experiment section
    """
    api_request = section_link
    response = requests.get(api_request, headers={'Authorization': api_token})
    parsed_response = response.json()

    return parsed_response


class CSVDownloader:

    def __init__(self, html_response):
        """ Initialization function for the CSVDownloader class
        Args:
             html_response: html object containing data tables,
             extracted from e-lab journal using the API.get_section_by_link function
        """

        self.soup = BeautifulSoup(html_response['contents'], 'html.parser')

    def run_methods(self):
        """
        Main function
        """
        return (self.convert_to_csv(self.data_extraction(),
                                    self.headers_extraction()))

    def headers_extraction(self):
        """Extracts the data for the column headers from the soup object

        Returns:
            list containing headers for the tables to be downloaded and converted to pandas
        """
        # Attempts to find column names for the table in contents, exits the function if none are found
        headers_unformatted = []
        try:
            for i in range(len(self.soup.find_all("table"))):
                headers_unformatted.append(self.soup.find_all("table")[i].find("tr"))
        except IndexError:
            return None

        # Appends the text components to list_header for each element in headers_unformatted
        all_headers = []
        for header in headers_unformatted:
            list_header = []
            for item in header:
                try:
                    list_header.append(item.get_text())
                except:
                    continue
            all_headers.append(list_header)
        return all_headers

    def data_extraction(self):
        """Extracts the data for the table(s) from the soup object

        Returns:
            list containing data for the tables to be downloaded
        """

        # For getting the data of the table
        data_tables_unformatted = []
        for i in range(len(self.soup.find_all("table"))):
            data_tables_unformatted.append(self.soup.find_all("table")[i].find_all("tr")[1:])

        all_data_tables = []

        for html_data in data_tables_unformatted:
            data = []
            # Similar as with items in the header section
            for element in html_data:
                sub_data = []
                for sub_element in element:
                    try:
                        sub_data.append(sub_element.get_text())
                    except:
                        continue
                data.append(sub_data)
            all_data_tables.append(data)
        return all_data_tables

    def convert_to_csv(self, all_data_tables, all_headers):
        """
        Args:
            all_data_tables: list of data elements received from the data_extraction function
            all_headers: list of column headers received from the headers_extraction function
        Returns:
            extracts data tables as csv files to Downloads folder
        """

        for num, table in enumerate(all_data_tables):
            # Storing the data into Pandas DataFrame
            data_frame = pandas.DataFrame(data=table, columns=all_headers[num])

            # Converting Pandas DataFrame
            # into CSV file
            data_frame.to_csv('Downloads/Data' + str(num) + '.csv')

        return "Files converted successfully."


if __name__ == "__main__":
    API_TOKEN = authenticate_user(input("Please enter your username: "),
                                  input("Please enter your password: "))

    response = get_section_by_link(API_TOKEN, input(
        "Please paste the link you received via email into this terminal: "))

    CSVDownloader = CSVDownloader(response)
    print(CSVDownloader.run_methods())
