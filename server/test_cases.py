test_cases = [
    {
        "city_name": "Mumbai",
        "user_pref": "Bollywood culture, diverse cuisine, local trains, and urban exploration",
        "n_days": 4
    },
    {
        "city_name": "Delhi",
        "user_pref": "historical monuments, street food, markets, and Mughal architecture",
        "n_days": 4
    },
    {
        "city_name": "Jaipur",
        "user_pref": "royal palaces, traditional crafts, colorful markets, and Rajasthani culture",
        "n_days": 3
    },
    {
        "city_name": "Goa",
        "user_pref": "beaches, Portuguese heritage, seafood, and relaxed coastal lifestyle",
        "n_days": 5
    },
    {
        "city_name": "Varanasi",
        "user_pref": "spiritual experiences, Ganges river, ancient temples, and cultural immersion",
        "n_days": 3
    },
    {
        "city_name": "Kerala (Kochi)",
        "user_pref": "backwaters, Ayurvedic treatments, spice plantations, and traditional dance",
        "n_days": 6
    },
    {
        "city_name": "Udaipur",
        "user_pref": "lake views, royal architecture, romantic settings, and heritage hotels",
        "n_days": 4
    },
    {
        "city_name": "Rishikesh",
        "user_pref": "yoga retreats, adventure sports, spiritual learning, and Himalayan foothills",
        "n_days": 5
    }
]

# Alternative format as individual test case functions for easier testing
def get_test_case(index):
    """Get a specific test case by index (0-17)"""
    if 0 <= index < len(test_cases):
        return test_cases[index]
    else:
        raise IndexError(f"Test case index {index} out of range. Available: 0-{len(test_cases)-1}")

def get_all_test_cases():
    """Get all test cases"""
    return test_cases

# Example usage:
# test_case = get_test_case(0)
# city = test_case["city_name"]
# preferences = test_case["user_pref"] 
# days = test_case["n_days"] 