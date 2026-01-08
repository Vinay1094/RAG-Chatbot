from app import chatbot

tests = [
    "How many holdings does Garfield have?",
    "How many trades does MNC Inv have?",
    "How many trades does HoldCo 11 have?",
    "Which fund performed best in 2023?",
    "Which fund performed best?",
]

for q in tests:
    print('Q:', q)
    print('A:', chatbot(q))
    print('-' * 60)
