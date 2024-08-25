import re

def extraction_sessionID(session_ID: str):

    match = re.search(r'/sessions/(.*?)/contexts/', session_ID)

    if match:
        exctractingSessionID = match.group(1)
        return exctractingSessionID

    return ""

def get_str_from_dic(food_dict: dict):
    return ', '.join([f'{int(value)} {key}' for key, value in food_dict.items()])

if __name__ == '__main__':
    # print(extraction_sessionID("projects/iadiee-chatbot-o9vi/agent/se ssions/b8b4e8f3-f8aa-c2b8-10df-8202754491d5/contexts/ongoing-order"))
    print(get_str_from_dic({"aaa": 11, "bbb": 22}))