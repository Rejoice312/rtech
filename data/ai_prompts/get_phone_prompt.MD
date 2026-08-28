# Requirements
read the my mail history with {email} and figure out his phone number if he mentioned it in our conversation. If he didn't mention it, reply with null. if he mentioned his country in the mail conversation, write the phone number along the coountry code in the international format

## Mail History
{prior_conversations}

# Expectation
- Your result should be just json data with these keys:
  - 'email': 'the persons email address i mentioned earlier',
  - 'phone': 'his phone number in international format' or null


- There should be no surrounding text
- There should be no extra expressions, only the python dictionary should be returned