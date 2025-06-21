itnr_1 = """
Given that you have to plan a trip to {city_name}, can you divide the types of things that we can do there i need a JSON which will be something like:
we need the list of famous attractions neatly classified
so search for famous attractions not just the ones mentioned above, create more classifications apart from what are given above
{{ "Museums": [" "], "Parks": [" "], "Restaurants/breweries": [" "] , "Temples": [" "], "Treks/beaches/natural attractions": [" "], "Amusement Parks/Game Zones": [" "] }}
NO extra text, just the JSON above - If you cant find anything just give an empty list
"""

itnr_2 = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format

{{
  "title": "....",
  "overview": "....",
  "days": [
    {{
      "day": 1,
      "title": "....",
      "narrative": "....",
      "activities": [
        {{
          "time": "....",
          "name": "....",
          "location": "....",
          "notes": "...."
        }},
        {{
          "time": "....",
          "name": "....",
          "location": "....",
          "notes": "...."
        }}
      ],
    }},
    {{
      "day": 2,
      "title": "....",
      "narrative": "....",
      "activities": [
        {{
          "time": "....",
          "name": "....",
          "location": "....",
          "notes": "...."
        }},
        {{
          "time": "....",
          "name": "....",
          "location": "....",
          "notes": "...."
        }}
      ],
    }}
  ]
}}
No extra text just the JSON above.
"""

itnr_3 = """
keep the items same but now try to optimize the itinerary based on their locations and distances
"""