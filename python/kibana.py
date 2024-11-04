import requests

# Kibana URL you want to access
kibana_url = "https://imkibanaindia.intermesh.net/app/dashboards#/view/6a0b4010-5e0e-11ef-b525-5330618c7a37?_g=(refreshInterval:(pause:!t,value:60000),time:(from:'2024-10-14T13:22:07.895Z',to:'2024-10-22T13:37:15.828Z'))&_a=()"

# If Kibana requires basic authentication, include it like this:
# Replace 'your_username' and 'your_password' with actual credentials
auth = ('devwrath.1@indiamart.com', 'Dev@800650')

# Send a GET request to access the dashboard
response = requests.get(kibana_url, auth=auth)

# Check if the request was successful
if response.status_code == 200:
    print("Accessed Kibana Dashboard successfully!")
    print(response.text)  # Prints the HTML of the dashboard page
else:
    print(f"Failed to access Kibana: {response.status_code}")
