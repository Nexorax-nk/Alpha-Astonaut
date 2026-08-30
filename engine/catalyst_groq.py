"""
engine/catalyst_groq.py
Uses Groq purely for catalyst verification.
Returns strictly formatted JSON as specified in the architecture.
"""
import json
from groq import Groq
from config import GROQ_API_KEY

class CatalystEngine:
    def __init__(self):
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here":
            self.client = None
            print("Warning: GROQ_API_KEY not set. Catalyst engine will return NEUTRAL.")
        else:
            self.client = Groq(api_key=GROQ_API_KEY)
            
    def analyze_news(self, ticker: str, news_text: str) -> dict:
        """
        Sends the news to Groq and expects a JSON response.
        If Groq fails or the JSON is malformed, returns NO TRADE (NEUTRAL).
        """
        default_response = {
            "direction": "NEUTRAL",
            "catalystStrength": 0,
            "freshness": 0,
            "relevance": 0,
            "reason": "Defaulted due to error or missing key"
        }
        
        if not self.client or "No recent news" in news_text or "Error" in news_text:
            return default_response

        system_prompt = """
        You are a quantitative trading assistant. Your ONLY job is to read news headlines for a stock and return a structured JSON evaluation.
        DO NOT invent data. DO NOT provide trading advice. Return ONLY valid JSON.
        
        Format required:
        {
          "direction": "BULLISH" | "BEARISH" | "NEUTRAL",
          "catalystStrength": 0-100,
          "freshness": 0-100,
          "relevance": 0-100,
          "reason": "short explanation"
        }
        """
        
        user_prompt = f"Evaluate this news for {ticker}:\n{news_text}"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model="llama3-8b-8192", # Fast and capable enough for this
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            response_text = chat_completion.choices[0].message.content
            data = json.loads(response_text)
            
            # Validate output
            if data.get("direction") not in ["BULLISH", "BEARISH", "NEUTRAL"]:
                data["direction"] = "NEUTRAL"
                
            return data
            
        except Exception as e:
            print(f"Groq API or parsing error: {e}")
            return default_response
