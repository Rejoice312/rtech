# Requirements
read the my mail history with {email} and figure out his country if he mentioned it in our conversation. If he didn't mention it, reply with null.

## Mail History
{prior_conversations}

# Expectation
- Your result should be just json data with these keys:
  - 'email': 'the persons email address i mentioned earlier',
  - 'country': 'his country' or null


- There should be no surrounding text
- There should be no extra expressions, only the python dictionary should be returned
- The country name should be in its full form, e.g United States instead of U.S.