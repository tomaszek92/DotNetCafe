import json
import requests
from configparser import ConfigParser
import os

def load_config():
    config = ConfigParser()
    abs_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    config.read(abs_path)
    print(f"Config sections: {config.sections()}")  # Debugging line
    return config

def load_user_data(file_path):
    # Use an absolute path
    abs_path = os.path.join(os.path.dirname(__file__), '..', 'database', file_path)
    with open(abs_path, 'r') as file:
        return json.load(file)

def analyze_travel_history(user_data):
    # Analyze user travel history to identify patterns
    # This is a placeholder for the actual analysis logic
    print("Analyzing travel history...")
    for trip in user_data:
        print(f"Visited {trip['location']['city']} in {trip['location']['country']}")

def get_recommendations(user_data, config):
    # Use OpenAI API to generate recommendations
    openai_api_key = config['API_KEYS']['openai_api_key']
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    prompt = (
        f"Based on the following travel history, suggest one new travel destination "
        f"that matches the user's preferences. Return only the city name and country: {json.dumps(user_data)}"
    )
    
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50  # Adjusted to focus on concise output
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        recommendation = response.json()['choices'][0]['message']['content']
        print("Recommended Destination:")
        print(recommendation)
        
        # Extract city and country from the recommendation
        city, country = parse_recommendation(recommendation)
        get_cultural_events(city, country, config)
    else:
        print(f"Failed to get recommendations: {response.status_code}")
        print(response.text)

def parse_recommendation(recommendation):
    # Assuming the recommendation is in the format "City, Country"
    parts = recommendation.split(',')
    if len(parts) == 2:
        city = parts[0].strip()
        country = parts[1].strip()
        return city, country
    else:
        print("Unexpected format in recommendation.")
        return None, None

def get_cultural_events(city, country, config):
    brave_api_key = config['API_KEYS']['brave_api_key']
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': brave_api_key
    }
    
    if city and country:
        print(f"Searching for cultural events in {city}, {country}...")
        
        # Use the Brave Web Search API endpoint
        response = requests.get(
            f'https://api.search.brave.com/res/v1/web/search?q=cultural+events+in+{city}+{country}',
            headers=headers
        )
        
        if response.status_code == 200:
            # Print the entire response for debugging
            response_data = response.json()
            print("API Response:", response_data)
            
            # Extract events from the 'web' key
            events = response_data.get('web', {}).get('results', [])
            
            if events:
                print(f"Upcoming events in {city}:")
                for event in events:
                    title = event.get('title', 'No title')
                    url = event.get('url', 'No URL')
                    description = event.get('description', 'No description')
                    print(f"- {title}\n  Description: {description}\n  URL: {url}\n")
            else:
                print(f"No upcoming events found in {city}.")
        else:
            print(f"Failed to get events for {city}: {response.status_code}")
            print(response.text)

def main():
    config = load_config()
    user_data = load_user_data('person_1.json')  # Pass only the filename
    analyze_travel_history(user_data)
    get_recommendations(user_data, config)

if __name__ == "__main__":
    main() 