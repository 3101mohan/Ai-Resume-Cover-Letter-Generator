from google import genai

client = genai.Client(api_key="AIzaSyAdAP0MN9DhRUYHTZLZ5cEu3N9DFBexAss")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)