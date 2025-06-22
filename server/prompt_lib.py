itnr_1 = """
Given that you have to plan a trip to {city_name}, can you divide the types of things that we can do there i need a JSON which will be something like:
we need the list of famous attractions neatly classified
so search for famous attractions not just the ones mentioned above, create more classifications apart from what are given above
{{ "Museums": [" "], "Parks": [" "], "Restaurants/breweries": [" "] , "Temples": [" "], "Treks/beaches/natural attractions": [" "], "Amusement Parks/Game Zones": [" "] }}
NO extra text, just the JSON above - If you cant find anything just give an empty list
"""

# PERSONA 1: NIGHTLIFE ENTHUSIAST - Late starts, post-dinner activities, bars/clubs
itnr_2_nightlife = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for someone who enjoys nightlife and late-night activities.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "11:00 AM",
          "name": "Brunch Spot",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "1:00 PM",
          "name": "Main Attraction",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "4:00 PM",
          "name": "Afternoon Activity",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "6:30 PM",
          "name": "Happy Hour/Drinks",
          "location": "....",
          "category": "meal",
          "meal_type": "drinks",
          "notes": "...."
        }},
        {{
          "time": "9:00 PM",
          "name": "Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "11:00 PM",
          "name": "Night Bar/Club",
          "location": "....",
          "category": "nightlife",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Late breakfast/brunch, happy hours, post-dinner nightlife, bars, clubs, night markets, late-night food spots.
No extra text just the JSON above.
"""

# PERSONA 2: FAMILY TRAVELER - Early starts, structured meals, family-friendly activities
itnr_2_family = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a family with structured meal times and kid-friendly activities.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "8:00 AM",
          "name": "Family Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "9:30 AM",
          "name": "Morning Activity",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "12:30 PM",
          "name": "Lunch Break",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "2:00 PM",
          "name": "Afternoon Activity",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "4:00 PM",
          "name": "Snack Time",
          "location": "....",
          "category": "meal",
          "meal_type": "snack",
          "notes": "...."
        }},
        {{
          "time": "6:30 PM",
          "name": "Family Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "8:00 PM",
          "name": "Evening Walk/Light Activity",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Family restaurants, kid-friendly attractions, regular meal schedules, early evening activities, parks, interactive museums.
No extra text just the JSON above.
"""

# PERSONA 3: LUXURY TRAVELER - Upscale dining, spa time, premium experiences
itnr_2_luxury = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a luxury traveler who prefers premium experiences and relaxed pace.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "9:30 AM",
          "name": "Gourmet Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "11:00 AM",
          "name": "Private Tour/Premium Attraction",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "2:00 PM",
          "name": "Fine Dining Lunch",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "4:00 PM",
          "name": "Spa/Wellness Activity",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "8:00 PM",
          "name": "Upscale Dinner Experience",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "10:00 PM",
          "name": "Premium Bar/Lounge",
          "location": "....",
          "category": "nightlife",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: High-end restaurants, premium experiences, spa treatments, private tours, luxury shopping, upscale lounges.
No extra text just the JSON above.
"""

# PERSONA 4: BACKPACKER/BUDGET - Street food, free activities, social experiences
itnr_2_backpacker = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a budget-conscious backpacker who loves authentic local experiences.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "9:00 AM",
          "name": "Local Street Food Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "10:00 AM",
          "name": "Free Walking Tour",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "1:00 PM",
          "name": "Market Food/Street Lunch",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "2:30 PM",
          "name": "Free Museum/Park",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "5:00 PM",
          "name": "Local Cafe/Social Hub",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "7:30 PM",
          "name": "Authentic Local Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "9:00 PM",
          "name": "Local Bar/Hostel Social",
          "location": "....",
          "category": "nightlife",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Street food, free attractions, local markets, authentic experiences, budget bars, social spaces, walking tours.
No extra text just the JSON above.
"""

# PERSONA 5: CULTURAL EXPLORER - Museums, historical sites, learning experiences
itnr_2_cultural = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a cultural enthusiast who wants deep, educational experiences.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "8:30 AM",
          "name": "Traditional Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "9:30 AM",
          "name": "Historical Museum/Site",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "12:30 PM",
          "name": "Cultural Restaurant",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "2:00 PM",
          "name": "Art Gallery/Cultural Center",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "4:30 PM",
          "name": "Cultural Workshop/Experience",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "7:00 PM",
          "name": "Traditional Cuisine Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "8:30 PM",
          "name": "Cultural Show/Performance",
          "location": "....",
          "category": "entertainment",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Museums, historical sites, cultural workshops, traditional cuisine, art galleries, cultural performances, educational experiences.
No extra text just the JSON above.
"""

# PERSONA 6: ADVENTURE SEEKER - Early starts, outdoor activities, packed schedule
itnr_2_adventure = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for an adventure seeker who wants action-packed, outdoor experiences.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "6:30 AM",
          "name": "Quick Energy Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "7:30 AM",
          "name": "Morning Hike/Outdoor Adventure",
          "location": "....",
          "category": "adventure",
          "notes": "...."
        }},
        {{
          "time": "11:30 AM",
          "name": "Packed Lunch/Trail Food",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "12:30 PM",
          "name": "Water Sports/Extreme Activity",
          "location": "....",
          "category": "adventure",
          "notes": "...."
        }},
        {{
          "time": "3:30 PM",
          "name": "Energy Snack/Recovery",
          "location": "....",
          "category": "meal",
          "meal_type": "snack",
          "notes": "...."
        }},
        {{
          "time": "4:00 PM",
          "name": "Rock Climbing/Adventure Sport",
          "location": "....",
          "category": "adventure",
          "notes": "...."
        }},
        {{
          "time": "7:30 PM",
          "name": "Hearty Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "9:00 PM",
          "name": "Campfire/Stargazing",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Hiking, water sports, extreme activities, outdoor adventures, energy foods, nature experiences, physical challenges.
No extra text just the JSON above.
"""

# PERSONA 7: ROMANTIC COUPLE - Intimate dining, sunset views, couple activities
itnr_2_romantic = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a romantic couple seeking intimate and memorable experiences.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "9:00 AM",
          "name": "Romantic Breakfast for Two",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "10:30 AM",
          "name": "Couples Activity/Scenic Walk",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "1:30 PM",
          "name": "Intimate Lunch",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "3:00 PM",
          "name": "Couples Spa/Wine Tasting",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "5:30 PM",
          "name": "Sunset Cocktails",
          "location": "....",
          "category": "meal",
          "meal_type": "drinks",
          "notes": "...."
        }},
        {{
          "time": "8:00 PM",
          "name": "Candlelight Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "10:00 PM",
          "name": "Moonlight Walk/Night Views",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Romantic restaurants, couple activities, sunset views, wine experiences, intimate settings, scenic walks, private experiences.
No extra text just the JSON above.
"""

# PERSONA 8: BUSINESS TRAVELER - Efficient schedule, networking, quick meals
itnr_2_business = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a business traveler with limited time seeking efficient experiences.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "7:30 AM",
          "name": "Quick Business Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "8:30 AM",
          "name": "Major Attraction (Efficient Visit)",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "11:00 AM",
          "name": "Business District/Professional Site",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "1:00 PM",
          "name": "Business Lunch/Networking Venue",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "2:30 PM",
          "name": "Key Cultural Site (1 hour)",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "4:00 PM",
          "name": "Coffee/Work-Friendly Cafe",
          "location": "....",
          "category": "meal",
          "meal_type": "drinks",
          "notes": "...."
        }},
        {{
          "time": "7:00 PM",
          "name": "Professional Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "8:30 PM",
          "name": "Hotel Bar/Networking",
          "location": "....",
          "category": "nightlife",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Efficient attractions, business-friendly venues, quick meals, networking opportunities, professional settings, time-optimized visits.
No extra text just the JSON above.
"""

# PERSONA 9: WELLNESS RETREAT - Slow pace, healthy food, mindful activities
itnr_2_wellness = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for someone seeking wellness, relaxation, and mindful travel.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "8:00 AM",
          "name": "Mindful Morning/Yoga",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "9:30 AM",
          "name": "Healthy Breakfast",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "11:00 AM",
          "name": "Nature Walk/Garden Visit",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "1:00 PM",
          "name": "Fresh, Light Lunch",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "2:30 PM",
          "name": "Spa Treatment/Massage",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "4:30 PM",
          "name": "Herbal Tea/Meditation",
          "location": "....",
          "category": "meal",
          "meal_type": "drinks",
          "notes": "...."
        }},
        {{
          "time": "7:00 PM",
          "name": "Organic Dinner",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "8:30 PM",
          "name": "Sunset Meditation/Reflection",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Yoga, meditation, healthy cuisine, spa treatments, nature experiences, slow travel, mindfulness, organic food.
No extra text just the JSON above.
"""

# PERSONA 10: FOODIE - Food tours, cooking classes, markets, culinary experiences
itnr_2_foodie = """
User likes {user_pref}, use the list above --> dont worry about the hotel bookings and all, just make an itinerary based on the above lists
make a {n_days} Day itinerary in the following format. This is for a food enthusiast who wants to explore local cuisine deeply.

IMPORTANT: Keep all titles, overviews, narratives, and notes as crisp one-liners with minimal words (max 5-8 words).

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
          "time": "8:30 AM",
          "name": "Local Market Breakfast Tour",
          "location": "....",
          "category": "meal",
          "meal_type": "breakfast",
          "notes": "...."
        }},
        {{
          "time": "10:00 AM",
          "name": "Food Market Exploration",
          "location": "....",
          "category": "attraction",
          "notes": "...."
        }},
        {{
          "time": "11:30 AM",
          "name": "Street Food Tasting",
          "location": "....",
          "category": "meal",
          "meal_type": "snack",
          "notes": "...."
        }},
        {{
          "time": "1:30 PM",
          "name": "Traditional Cooking Class",
          "location": "....",
          "category": "activity",
          "notes": "...."
        }},
        {{
          "time": "3:30 PM",
          "name": "Cooking Class Lunch (What You Made)",
          "location": "....",
          "category": "meal",
          "meal_type": "lunch",
          "notes": "...."
        }},
        {{
          "time": "5:00 PM",
          "name": "Local Brewery/Wine Tasting",
          "location": "....",
          "category": "meal",
          "meal_type": "drinks",
          "notes": "...."
        }},
        {{
          "time": "8:00 PM",
          "name": "Signature Restaurant Experience",
          "location": "....",
          "category": "meal",
          "meal_type": "dinner",
          "notes": "...."
        }},
        {{
          "time": "10:00 PM",
          "name": "Dessert/Late Night Food Spot",
          "location": "....",
          "category": "meal",
          "meal_type": "snack",
          "notes": "...."
        }}
      ]
    }}
  ]
}}

Focus on: Food markets, cooking classes, street food, local breweries, signature restaurants, food tours, culinary workshops.
No extra text just the JSON above.
"""

itnr_3 = """
keep the items same but now try to optimize the itinerary based on their locations and distances. Make sure it adheres JSOn strcuture, no unneccesary \n characters.
"""