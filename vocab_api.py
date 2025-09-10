import requests

def get_meaning(word):
    """Free Dictionary API에서 단어 뜻 가져오기"""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            return data[0]['meanings'][0]['definitions'][0]['definition']
        except (IndexError, KeyError):
            return None
    return None