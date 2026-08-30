"""
data_feed/news_feed.py
Fetches recent news articles for the Groq catalyst engine.
"""
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from config import APCA_API_KEY_ID, APCA_API_SECRET_KEY

class NewsFeedClient:
    def __init__(self):
        self.client = NewsClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

    def get_latest_news(self, symbol: str, limit: int = 5) -> str:
        """
        Fetches the latest news headlines for a specific symbol.
        Returns a single string block formatted for the LLM.
        """
        req = NewsRequest(symbols=symbol, limit=limit)
        try:
            news = self.client.get_news(req)
            if not news.news:
                return "No recent news found."
                
            news_block = f"Recent news for {symbol}:\n"
            for item in news.news:
                news_block += f"- [{item.created_at.strftime('%Y-%m-%d %H:%M')}] {item.headline}\n"
                if item.summary:
                    news_block += f"  Summary: {item.summary}\n"
            return news_block
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return "Error retrieving news."

if __name__ == "__main__":
    nf = NewsFeedClient()
    print(nf.get_latest_news("AAPL", limit=2))
