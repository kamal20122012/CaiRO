import sqlite3
import json
import numpy as np
from google import genai
from google.genai import types
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Gemini client
client = genai.Client()

# Define personas with descriptions for embedding
PERSONAS = {
    "nightlife": {
        "name": "Nightlife Enthusiast",
        "description": "Loves bars, clubs, late-night activities, happy hours, party scenes, social drinking, nightclubs, rooftop bars, night markets, late dinners, weekend parties",
        "prompt_key": "itnr_2_nightlife"
    },
    "family": {
        "name": "Family Traveler", 
        "description": "Traveling with kids, family-friendly activities, structured schedules, early bedtime, child-safe attractions, family restaurants, parks, interactive museums, educational experiences",
        "prompt_key": "itnr_2_family"
    },
    "luxury": {
        "name": "Luxury Traveler",
        "description": "High-end experiences, fine dining, premium hotels, spa treatments, private tours, upscale shopping, luxury brands, exclusive access, first-class service, expensive restaurants",
        "prompt_key": "itnr_2_luxury"
    },
    "backpacker": {
        "name": "Backpacker/Budget",
        "description": "Budget travel, backpacking, hostels, street food, free activities, local experiences, authentic culture, cheap eats, walking tours, social travelers, budget-friendly",
        "prompt_key": "itnr_2_backpacker"
    },
    "cultural": {
        "name": "Cultural Explorer",
        "description": "Museums, historical sites, art galleries, cultural workshops, traditional cuisine, local customs, heritage sites, educational tours, historical learning, cultural immersion",
        "prompt_key": "itnr_2_cultural"
    },
    "adventure": {
        "name": "Adventure Seeker",
        "description": "Outdoor activities, hiking, extreme sports, water sports, rock climbing, adventure tours, physical challenges, nature experiences, adrenaline activities, active travel",
        "prompt_key": "itnr_2_adventure"
    },
    "romantic": {
        "name": "Romantic Couple",
        "description": "Romantic dinners, couple activities, sunset views, intimate settings, wine tasting, scenic walks, honeymoon, anniversary, romantic getaway, candlelit dinners",
        "prompt_key": "itnr_2_romantic"
    },
    "business": {
        "name": "Business Traveler",
        "description": "Efficient travel, business meetings, networking, professional venues, quick meals, time-optimized, work-friendly spaces, corporate travel, business centers",
        "prompt_key": "itnr_2_business"
    },
    "wellness": {
        "name": "Wellness Retreat",
        "description": "Yoga, meditation, spa treatments, healthy food, mindfulness, relaxation, organic cuisine, wellness centers, mental health, stress relief, holistic healing",
        "prompt_key": "itnr_2_wellness"
    },
    "foodie": {
        "name": "Foodie",
        "description": "Food tours, cooking classes, local cuisine, street food, restaurants, culinary experiences, food markets, wine tasting, gastronomic adventures, chef experiences",
        "prompt_key": "itnr_2_foodie"
    }
}

def create_database():
    """Create SQLite database and personas table"""
    conn = sqlite3.connect('personas.db')
    cursor = conn.cursor()
    
    # Create table for persona embeddings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persona_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_key TEXT UNIQUE NOT NULL,
            persona_name TEXT NOT NULL,
            description TEXT NOT NULL,
            prompt_key TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn

def get_embedding(text):
    """Get embedding for given text using Gemini"""
    try:
        result = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=text,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        )
        return result.embeddings[0].values
    except Exception as e:
        logging.error(f"Error getting embedding for text: {text[:50]}... - {e}")
        raise

def store_persona_embeddings():
    """Generate and store embeddings for all personas"""
    conn = create_database()
    cursor = conn.cursor()
    
    logging.info("🚀 Starting persona embedding generation and storage...")
    
    for persona_key, persona_data in PERSONAS.items():
        try:
            # Check if persona already exists
            cursor.execute("SELECT COUNT(*) FROM persona_embeddings WHERE persona_key = ?", (persona_key,))
            if cursor.fetchone()[0] > 0:
                logging.info(f"✅ Persona '{persona_key}' already exists, skipping...")
                continue
            
            # Generate embedding for persona description
            logging.info(f"🔄 Generating embedding for persona: {persona_data['name']}")
            embedding = get_embedding(persona_data['description'])
            
            # Convert to list for JSON storage
            embedding_list = list(embedding)
            
            # Store in database
            cursor.execute('''
                INSERT INTO persona_embeddings 
                (persona_key, persona_name, description, prompt_key, embedding_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                persona_key,
                persona_data['name'],
                persona_data['description'],
                persona_data['prompt_key'],
                json.dumps(embedding_list)
            ))
            
            logging.info(f"✅ Stored embedding for '{persona_data['name']}' ({len(embedding_list)} dimensions)")
            
        except Exception as e:
            logging.error(f"❌ Error processing persona '{persona_key}': {e}")
            continue
    
    conn.commit()
    conn.close()
    logging.info("🎉 Persona embedding storage completed!")

def get_all_persona_embeddings():
    """Retrieve all persona embeddings from database"""
    conn = sqlite3.connect('personas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT persona_key, persona_name, description, prompt_key, embedding_json
        FROM persona_embeddings
        ORDER BY persona_key
    ''')
    
    results = []
    for row in cursor.fetchall():
        persona_key, persona_name, description, prompt_key, embedding_json = row
        embedding = np.array(json.loads(embedding_json))
        results.append({
            'persona_key': persona_key,
            'persona_name': persona_name,
            'description': description,
            'prompt_key': prompt_key,
            'embedding': embedding
        })
    
    conn.close()
    return results

def find_best_persona_match(user_pref_text):
    """Find the best matching persona based on semantic similarity"""
    try:
        # Get user preference embedding
        logging.info(f"🔍 Getting embedding for user preferences: {user_pref_text[:100]}...")
        user_embedding = np.array(get_embedding(user_pref_text))
        
        # Get all persona embeddings
        personas = get_all_persona_embeddings()
        
        if not personas:
            logging.warning("⚠️ No personas found in database. Using default 'cultural' persona.")
            return "itnr_2_cultural"
        
        # Calculate similarity scores
        best_score = -1
        best_persona = None
        
        logging.info(f"📊 Comparing user preferences against {len(personas)} personas...")
        
        for persona in personas:
            # Calculate dot product (cosine similarity approximation for normalized vectors)
            similarity = np.dot(user_embedding, persona['embedding'])
            
            logging.debug(f"🎯 {persona['persona_name']}: {similarity:.4f}")
            
            if similarity > best_score:
                best_score = similarity
                best_persona = persona
        
        if best_persona:
            logging.info(f"🏆 Best match: {best_persona['persona_name']} (score: {best_score:.4f})")
            logging.info(f"📋 Selected prompt: {best_persona['prompt_key']}")
            return best_persona['prompt_key']
        else:
            logging.warning("⚠️ No best persona found. Using default 'cultural' persona.")
            return "itnr_2_cultural"
            
    except Exception as e:
        logging.error(f"❌ Error in persona matching: {e}")
        logging.warning("⚠️ Falling back to default 'cultural' persona.")
        return "itnr_2_cultural"

if __name__ == "__main__":
    # Initialize database and store persona embeddings
    store_persona_embeddings()
    
    # Test the matching system
    test_preferences = [
        "I love nightlife and going to bars and clubs",
        "Traveling with my family and kids, need safe activities", 
        "Looking for luxury experiences and fine dining",
        "Budget backpacker seeking authentic local experiences",
        "Interested in museums, history, and cultural sites"
    ]
    
    print("\n🧪 Testing persona matching system:")
    print("=" * 50)
    
    for pref in test_preferences:
        best_match = find_best_persona_match(pref)
        print(f"User: '{pref[:40]}...'")
        print(f"Match: {best_match}")
        print("-" * 50) 