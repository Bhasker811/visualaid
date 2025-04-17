import speech_recognition as sr 
from datetime import datetime
import time
import urllib.request
import json
import worldnewsapi
from worldnewsapi.rest import ApiException

# 🔐 API Keys
WORLD_NEWS_API_KEY = "fa256668b2df4844af5f3c2a50c87699"
GNEWS_API_KEY = "c9ad3127d06d959d42a75068ada89f8c"

# PART 1: Listen for voice command
def listen_for_command(trigger_phrase="today's news", max_attempts=5):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening for the command...")

    attempts = 0

    while attempts < max_attempts:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print(f"Attempt {attempts + 1}... Please say something.")
                audio = recognizer.listen(source, timeout=5)

            print("🧠 Recognizing speech...")
            command = recognizer.recognize_google(audio).lower()
            print(f"🗣 You said: {command}")

            if trigger_phrase in command:
                print("✅ Trigger phrase detected: 'today's news'")
                return True
            else:
                print("❌ Trigger phrase not detected.")
                attempts += 1

        except sr.UnknownValueError:
            print("❗ Could not understand the audio. Please try again.")
            attempts += 1
        except sr.RequestError as e:
            print(f"⚠ API error: {e}")
            attempts += 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            attempts += 1

        if attempts < max_attempts:
            print("🔁 Waiting before next attempt...\n")
            time.sleep(2)

    print(f"⚠ Max attempts ({max_attempts}) reached. Exiting...")
    return False


# PART 2: Fetch top news using World News API
def fetch_top_news_worldnewsapi(api_key, limit=5):
    configuration = worldnewsapi.Configuration(api_key={"apiKey": api_key})
    api_instance = worldnewsapi.NewsApi(worldnewsapi.ApiClient(configuration))

    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    end_date = today.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = api_instance.search_news(
            text="",
            language="en",
            earliest_publish_date=start_date,
            latest_publish_date=end_date,
            sort="publish-time",
            sort_direction="desc",
            number=limit,
        )

        articles = response.news or []
        print(f"\n📰 Top {limit} News from World News API for {today.strftime('%Y-%m-%d')}:\n")

        news_list = []
        for i, article in enumerate(articles, start=1):
            title = article.title or "No Title"
            description = article.summary or "No Summary"
            print(f"{i}. {title}\n   {description}\n")
            news_list.append({"title": title, "description": description})

        return news_list

    except ApiException as e:
        print(f"⚠ World News API error: {e}")
        return []


def fetch_top_news_gnewsapi(api_key, limit=5):
    query = "latest"
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=us&max={limit}&apikey={api_key}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])

            print(f"\n📰 Top {limit} News from GNews API:\n")
            news_list = []

            for i, article in enumerate(articles, start=1):
                title = article.get("title", "No Title")
                description = article.get("description", "No Description")
                print(f"{i}. {title}\n   {description}\n")
                news_list.append({"title": title, "description": description})

            return news_list
    except Exception as e:
        print(f"⚠ GNews API error: {e}")
        return []


# 🚀 Main Flow
if __name__ == "__main__":
    if listen_for_command():
        # Toggle this to switch APIs
        use_gnews = True  # Set False to use World News API

        if use_gnews:
            print(">> Fetching today's top 5 news from GNews API...")
            news = fetch_top_news_gnewsapi(GNEWS_API_KEY)
        else:
            print(">> Fetching today's top 5 news from World News API...")
            news = fetch_top_news_worldnewsapi(WORLD_NEWS_API_KEY)

        if news:
            print("✅ News fetched successfully!")
        else:
            print("⚠ No news fetched.")
    else:
        print("❌ Trigger phrase not detected. Exiting.")
