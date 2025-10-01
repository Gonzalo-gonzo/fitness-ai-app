# backend/seed_foods.py
from sqlmodel import Session, select
from backend.database import engine, init_db
from backend.models import Food
 


def seed_foods():
    init_db()

    foods_data = [
        # --- Protein (15) ---
        {"mat": "Kycklingfilé", "kcal_per_100g": 165, "protein": 31, "fett": 3, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
        {"mat": "Nötkött", "kcal_per_100g": 250, "protein": 26, "fett": 17, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
        {"mat": "Lax", "kcal_per_100g": 208, "protein": 20, "fett": 13, "kolhydrater": 0, "category": "protein", "tags": ["fish"]},
        {"mat": "Tonfisk (konserv)", "kcal_per_100g": 132, "protein": 28, "fett": 1, "kolhydrater": 0, "category": "protein", "tags": ["fish"]},
        {"mat": "Ägg", "kcal_per_100g": 155, "protein": 13, "fett": 11, "kolhydrater": 1, "category": "protein", "tags": ["egg"]},
        {"mat": "Kycklinglår", "kcal_per_100g": 190, "protein": 27, "fett": 8, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
        {"mat": "Kalkonbröst", "kcal_per_100g": 135, "protein": 29, "fett": 1, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
        {"mat": "Fläskfilé", "kcal_per_100g": 143, "protein": 21, "fett": 6, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
        {"mat": "Torsk", "kcal_per_100g": 82, "protein": 18, "fett": 0, "kolhydrater": 0, "category": "protein", "tags": ["fish"]},
        {"mat": "Räkor", "kcal_per_100g": 99, "protein": 24, "fett": 0, "kolhydrater": 0, "category": "protein", "tags": ["fish"]},
        {"mat": "Ostron", "kcal_per_100g": 68, "protein": 7, "fett": 2, "kolhydrater": 4, "category": "protein", "tags": ["fish"]},
        {"mat": "Krabba", "kcal_per_100g": 97, "protein": 19, "fett": 1, "kolhydrater": 0, "category": "protein", "tags": ["fish"]},
        {"mat": "Tofu", "kcal_per_100g": 76, "protein": 8, "fett": 5, "kolhydrater": 2, "category": "protein", "tags": ["vegan"]},
        {"mat": "Seitan", "kcal_per_100g": 143, "protein": 25, "fett": 2, "kolhydrater": 9, "category": "protein", "tags": ["vegan", "contains_gluten"]},
        {"mat": "Tempeh", "kcal_per_100g": 192, "protein": 20, "fett": 11, "kolhydrater": 8, "category": "protein", "tags": ["vegan"]},

        # --- Kolhydrater (15) ---
        {"mat": "Ris", "kcal_per_100g": 130, "protein": 2, "fett": 0, "kolhydrater": 28, "category": "carb", "tags": []},
        {"mat": "Potatis", "kcal_per_100g": 77, "protein": 2, "fett": 0, "kolhydrater": 17, "category": "carb", "tags": []},
        {"mat": "Pasta", "kcal_per_100g": 131, "protein": 5, "fett": 1, "kolhydrater": 25, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Havregryn", "kcal_per_100g": 360, "protein": 13, "fett": 7, "kolhydrater": 60, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Quinoa", "kcal_per_100g": 120, "protein": 4, "fett": 2, "kolhydrater": 21, "category": "carb", "tags": []},
        {"mat": "Sötpotatis", "kcal_per_100g": 86, "protein": 2, "fett": 0, "kolhydrater": 20, "category": "carb", "tags": []},
        {"mat": "Durumbröd", "kcal_per_100g": 270, "protein": 9, "fett": 3, "kolhydrater": 52, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Majs", "kcal_per_100g": 96, "protein": 3, "fett": 1, "kolhydrater": 21, "category": "carb", "tags": []},
        {"mat": "Bulgur", "kcal_per_100g": 342, "protein": 12, "fett": 1, "kolhydrater": 76, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Kuskus", "kcal_per_100g": 112, "protein": 4, "fett": 0, "kolhydrater": 23, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Polenta", "kcal_per_100g": 70, "protein": 2, "fett": 0, "kolhydrater": 15, "category": "carb", "tags": []},
        {"mat": "Jasminris", "kcal_per_100g": 129, "protein": 2, "fett": 0, "kolhydrater": 28, "category": "carb", "tags": []},
        {"mat": "Basmatiris", "kcal_per_100g": 121, "protein": 3, "fett": 0, "kolhydrater": 26, "category": "carb", "tags": []},
        {"mat": "Fullkornsbröd", "kcal_per_100g": 252, "protein": 10, "fett": 4, "kolhydrater": 43, "category": "carb", "tags": ["contains_gluten"]},
        {"mat": "Knäckebröd", "kcal_per_100g": 330, "protein": 9, "fett": 2, "kolhydrater": 67, "category": "carb", "tags": ["contains_gluten"]},

        # --- Grönsaker (15) ---
        {"mat": "Broccoli", "kcal_per_100g": 35, "protein": 3, "fett": 0, "kolhydrater": 7, "category": "veg", "tags": []},
        {"mat": "Spenat", "kcal_per_100g": 23, "protein": 3, "fett": 0, "kolhydrater": 4, "category": "veg", "tags": []},
        {"mat": "Tomat", "kcal_per_100g": 18, "protein": 1, "fett": 0, "kolhydrater": 4, "category": "veg", "tags": []},
        {"mat": "Morot", "kcal_per_100g": 41, "protein": 1, "fett": 0, "kolhydrater": 10, "category": "veg", "tags": []},
        {"mat": "Paprika", "kcal_per_100g": 31, "protein": 1, "fett": 0, "kolhydrater": 6, "category": "veg", "tags": []},
        {"mat": "Grönkål", "kcal_per_100g": 50, "protein": 4, "fett": 1, "kolhydrater": 9, "category": "veg", "tags": []},
        {"mat": "Zucchini", "kcal_per_100g": 17, "protein": 1, "fett": 0, "kolhydrater": 3, "category": "veg", "tags": []},
        {"mat": "Gurka", "kcal_per_100g": 16, "protein": 1, "fett": 0, "kolhydrater": 3, "category": "veg", "tags": []},
        {"mat": "Rödbeta", "kcal_per_100g": 43, "protein": 2, "fett": 0, "kolhydrater": 10, "category": "veg", "tags": []},
        {"mat": "Blomkål", "kcal_per_100g": 25, "protein": 2, "fett": 0, "kolhydrater": 5, "category": "veg", "tags": []},
        {"mat": "Sallad", "kcal_per_100g": 14, "protein": 1, "fett": 0, "kolhydrater": 2, "category": "veg", "tags": []},
        {"mat": "Brysselkål", "kcal_per_100g": 43, "protein": 3, "fett": 0, "kolhydrater": 9, "category": "veg", "tags": []},
        {"mat": "Sparris", "kcal_per_100g": 20, "protein": 2, "fett": 0, "kolhydrater": 4, "category": "veg", "tags": []},
        {"mat": "Lök", "kcal_per_100g": 40, "protein": 1, "fett": 0, "kolhydrater": 9, "category": "veg", "tags": []},
        {"mat": "Vitlök", "kcal_per_100g": 149, "protein": 6, "fett": 0, "kolhydrater": 33, "category": "veg", "tags": []},

        # --- Frukt (15) ---
        {"mat": "Banan", "kcal_per_100g": 90, "protein": 1, "fett": 0, "kolhydrater": 23, "category": "fruit", "tags": []},
        {"mat": "Äpple", "kcal_per_100g": 52, "protein": 0, "fett": 0, "kolhydrater": 14, "category": "fruit", "tags": []},
        {"mat": "Apelsin", "kcal_per_100g": 47, "protein": 1, "fett": 0, "kolhydrater": 12, "category": "fruit", "tags": []},
        {"mat": "Blåbär", "kcal_per_100g": 57, "protein": 1, "fett": 0, "kolhydrater": 14, "category": "fruit", "tags": []},
        {"mat": "Jordgubbar", "kcal_per_100g": 33, "protein": 1, "fett": 0, "kolhydrater": 8, "category": "fruit", "tags": []},
        {"mat": "Mango", "kcal_per_100g": 60, "protein": 1, "fett": 0, "kolhydrater": 15, "category": "fruit", "tags": []},
        {"mat": "Kiwi", "kcal_per_100g": 61, "protein": 1, "fett": 0, "kolhydrater": 15, "category": "fruit", "tags": []},
        {"mat": "Ananas", "kcal_per_100g": 50, "protein": 1, "fett": 0, "kolhydrater": 13, "category": "fruit", "tags": []},
        {"mat": "Päron", "kcal_per_100g": 57, "protein": 0, "fett": 0, "kolhydrater": 15, "category": "fruit", "tags": []},
        {"mat": "Persika", "kcal_per_100g": 39, "protein": 1, "fett": 0, "kolhydrater": 10, "category": "fruit", "tags": []},
        {"mat": "Plommon", "kcal_per_100g": 46, "protein": 0, "fett": 0, "kolhydrater": 11, "category": "fruit", "tags": []},
        {"mat": "Druvor", "kcal_per_100g": 69, "protein": 0, "fett": 0, "kolhydrater": 18, "category": "fruit", "tags": []},
        {"mat": "Granatäpple", "kcal_per_100g": 83, "protein": 2, "fett": 1, "kolhydrater": 19, "category": "fruit", "tags": []},
        {"mat": "Hallon", "kcal_per_100g": 52, "protein": 1, "fett": 0, "kolhydrater": 12, "category": "fruit", "tags": []},
        {"mat": "Björnbär", "kcal_per_100g": 43, "protein": 1, "fett": 0, "kolhydrater": 10, "category": "fruit", "tags": []},

        # --- Nötter, frön, baljväxter & mejeri (20) ---
        {"mat": "Mandel", "kcal_per_100g": 579, "protein": 21, "fett": 50, "kolhydrater": 22, "category": "nuts", "tags": ["contains_nuts"]},
        {"mat": "Valnötter", "kcal_per_100g": 654, "protein": 15, "fett": 65, "kolhydrater": 14, "category": "nuts", "tags": ["contains_nuts"]},
        {"mat": "Cashewnötter", "kcal_per_100g": 553, "protein": 18, "fett": 44, "kolhydrater": 30, "category": "nuts", "tags": ["contains_nuts"]},
        {"mat": "Jordnötter", "kcal_per_100g": 567, "protein": 25, "fett": 49, "kolhydrater": 16, "category": "nuts", "tags": ["contains_nuts"]},
        {"mat": "Chiafrön", "kcal_per_100g": 486, "protein": 17, "fett": 31, "kolhydrater": 42, "category": "seeds", "tags": ["vegan"]},
        {"mat": "Solrosfrön", "kcal_per_100g": 584, "protein": 21, "fett": 51, "kolhydrater": 20, "category": "seeds", "tags": ["vegan"]},
        {"mat": "Linfrön", "kcal_per_100g": 534, "protein": 18, "fett": 42, "kolhydrater": 29, "category": "seeds", "tags": ["vegan"]},
        {"mat": "Pumpafrön", "kcal_per_100g": 559, "protein": 30, "fett": 49, "kolhydrater": 11, "category": "seeds", "tags": ["vegan"]},
        {"mat": "Kikärtor", "kcal_per_100g": 164, "protein": 9, "fett": 3, "kolhydrater": 27, "category": "legumes", "tags": ["vegan"]},
        {"mat": "Svarta bönor", "kcal_per_100g": 132, "protein": 9, "fett": 0, "kolhydrater": 24, "category": "legumes", "tags": ["vegan"]},
        {"mat": "Kidneybönor", "kcal_per_100g": 127, "protein": 8, "fett": 0, "kolhydrater": 23, "category": "legumes", "tags": ["vegan"]},
        {"mat": "Linsor (gröna)", "kcal_per_100g": 116, "protein": 9, "fett": 0, "kolhydrater": 20, "category": "legumes", "tags": ["vegan"]},
        {"mat": "Grekisk yoghurt (10%)", "kcal_per_100g": 97, "protein": 9, "fett": 5, "kolhydrater": 4, "category": "dairy", "tags": ["contains_lactose"]},
        {"mat": "Naturell yoghurt", "kcal_per_100g": 61, "protein": 3, "fett": 3, "kolhydrater": 5, "category": "dairy", "tags": ["contains_lactose"]},
        {"mat": "Ost", "kcal_per_100g": 402, "protein": 25, "fett": 33, "kolhydrater": 1, "category": "dairy", "tags": ["contains_lactose"]},
        {"mat": "Mjölk 3%", "kcal_per_100g": 61, "protein": 3, "fett": 3, "kolhydrater": 5, "category": "dairy", "tags": ["contains_lactose"]},
        {"mat": "Sojamjölk", "kcal_per_100g": 45, "protein": 3, "fett": 2, "kolhydrater": 4, "category": "dairy_alt", "tags": ["vegan"]},
        {"mat": "Mandelmjölk", "kcal_per_100g": 39, "protein": 1, "fett": 3, "kolhydrater": 2, "category": "dairy_alt", "tags": ["vegan"]},
        {"mat": "Havremjölk", "kcal_per_100g": 46, "protein": 1, "fett": 1, "kolhydrater": 9, "category": "dairy_alt", "tags": ["vegan"]},
        {"mat": "Kokosmjölk", "kcal_per_100g": 230, "protein": 2, "fett": 24, "kolhydrater": 6, "category": "dairy_alt", "tags": ["vegan"]},
    ]

    with Session(engine) as session:
        for f in foods_data:
            normalized = f["mat"].strip().lower()
            exists = session.exec(select(Food).where(Food.mat_normalized == normalized)).first()
            if not exists:
                food = Food(
                    mat=f["mat"],
                    mat_normalized=normalized,
                    kcal_per_100g=f["kcal_per_100g"],
                    protein=f["protein"],
                    fett=f["fett"],
                    kolhydrater=f["kolhydrater"],
                    category=f.get("category"),
                    tags=f.get("tags", []),
                )
                session.add(food)
        session.commit()
        print(f"✅ Seedade {len(foods_data)} livsmedel")


if __name__ == "__main__":
    seed_foods()