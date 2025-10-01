"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";

type Food = {
  id: number;
  mat: string;
  kcal_per_100g: number;
  protein: number;
  fett: number;
  kolhydrater: number;
};

type FoodWithAmount = Food & {
  grams?: number;
  kcal?: number;
  protein_g?: number;
  fett_g?: number;
  kolhydrater_g?: number;
};

type Plan = {
  frukost: FoodWithAmount[];
  mellanmal: FoodWithAmount[];
  lunch: FoodWithAmount[];
  preworkout: FoodWithAmount[];
  middag: FoodWithAmount[];
};

export default function FoodsPage() {
  const [foods, setFoods] = useState<Food[]>([]);
  const [search, setSearch] = useState("");
  const [dailyCalories, setDailyCalories] = useState<number | "">("");
  const [calculatedGoals, setCalculatedGoals] = useState({
    protein: 0,
    fat: 0,
    carbs: 0,
  });
  const [myPlan, setMyPlan] = useState<Plan>({
    frukost: [],
    mellanmal: [],
    lunch: [],
    preworkout: [],
    middag: [],
  });
  const [gramInputs, setGramInputs] = useState<{ [key: number]: number }>({});
  const [openMeal, setOpenMeal] = useState<keyof Plan | null>(null);
  const [editGoals, setEditGoals] = useState(false);

  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  // dagens datum
  const todayDate = new Date();
  const formatDate = (date: Date) => {
    const weekdays = [
      "Söndag",
      "Måndag",
      "Tisdag",
      "Onsdag",
      "Torsdag",
      "Fredag",
      "Lördag",
    ];
    const dayName = weekdays[date.getDay()];
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    return `${dayName} ${day}-${month}`;
  };

  // Hämta livsmedel
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await fetch("http://127.0.0.1:8080/foods", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setFoods(data);
        }
      } catch (err) {
        console.error("Kunde inte hämta livsmedel", err);
      }
    })();
  }, [token]);

  // Beräkna macros från kcal
  useEffect(() => {
    if (dailyCalories && Number(dailyCalories) > 0) {
      const kcal = Number(dailyCalories);
      const protein = Math.round((kcal * 0.2) / 4);
      const fat = Math.round((kcal * 0.2) / 9);
      const carbs = Math.round((kcal * 0.6) / 4);
      setCalculatedGoals({ protein, fat, carbs });
    } else {
      setCalculatedGoals({ protein: 0, fat: 0, carbs: 0 });
    }
  }, [dailyCalories]);

  // Lägg till i plan
  const addToPlan = (food: Food, grams: number, meal: keyof Plan) => {
    const factor = grams / 100;
    const foodWithAmount: FoodWithAmount = {
      ...food,
      grams,
      kcal: Math.round(food.kcal_per_100g * factor),
      protein_g: Math.round(food.protein * factor),
      fett_g: Math.round(food.fett * factor),
      kolhydrater_g: Math.round(food.kolhydrater * factor),
    };
    setMyPlan((prev) => ({
      ...prev,
      [meal]: [...prev[meal], foodWithAmount],
    }));
  };

  // Summera totals
  const calculateTotals = (plan: Plan) => {
    const totals = { kcal: 0, protein: 0, fett: 0, kolhydrater: 0 };
    Object.values(plan).forEach((mealFoods) => {
      mealFoods.forEach((f) => {
        totals.kcal += f.kcal || 0;
        totals.protein += f.protein_g || 0;
        totals.fett += f.fett_g || 0;
        totals.kolhydrater += f.kolhydrater_g || 0;
      });
    });
    return totals;
  };

  const totals = calculateTotals(myPlan);

  // Filtrera mat (max 10 resultat)
  const filteredFoods = foods
    .filter((f) => f.mat.toLowerCase().includes(search.toLowerCase()))
    .slice(0, 10);

  return (
    <main className="p-6 max-w-2xl mx-auto pb-20">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        📋 Planera ditt schema
      </h1>

      {/* 🎯 Dina mål */}
      <div className="bg-white rounded-xl shadow p-4 mb-6 space-y-3">
        <h2 className="text-xl font-semibold text-green-600 mb-2">🎯 Dina mål</h2>
        {!editGoals ? (
          <>
            <p>
              kcal: {dailyCalories || 0} <br />
              Protein: {calculatedGoals.protein} g <br />
              Fett: {calculatedGoals.fat} g <br />
              Kolhydrater: {calculatedGoals.carbs} g
            </p>
            <button
              onClick={() => setEditGoals(true)}
              className="mt-3 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg shadow"
            >
              ✏️ Redigera
            </button>
          </>
        ) : (
          <div className="space-y-2">
            <input
              type="number"
              placeholder="Kalorier"
              className="border p-2 rounded w-full"
              value={dailyCalories}
              onChange={(e) => setDailyCalories(Number(e.target.value))}
            />
            <button
              onClick={() => setEditGoals(false)}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg shadow"
            >
              ✅ Spara
            </button>
          </div>
        )}
      </div>

      {/* 📅 Din dagbok */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <h2 className="text-xl font-semibold text-green-600 mb-2">
          🗓️ Din dagbok
        </h2>
        <p>{formatDate(todayDate)}</p>
        <p>
          Mål: {dailyCalories || 0} kcal (P {calculatedGoals.protein}g, F{" "}
          {calculatedGoals.fat}g, K {calculatedGoals.carbs}g)
        </p>
        <p>
          Ätit: {totals.kcal} kcal (P {totals.protein}g, F {totals.fett}g, K{" "}
          {totals.kolhydrater}g)
        </p>
        <p>
          Återstår: {dailyCalories ? Number(dailyCalories) - totals.kcal : 0} kcal
        </p>
      </div>

      {/* Måltider */}
      {(Object.keys(myPlan) as (keyof Plan)[]).map((meal) => (
        <div key={meal} className="bg-white rounded-xl shadow p-4 mb-6">
          <h3 className="text-lg font-semibold capitalize">{meal}</h3>
          {myPlan[meal].length === 0 ? (
            <p className="text-gray-500">Inget tillagt</p>
          ) : (
            <ul className="space-y-1">
              {myPlan[meal].map((f, i) => (
                <li key={i} className="flex justify-between items-center">
                  <span>
                    {f.mat} ({f.grams} g)
                  </span>
                  <div className="flex items-center gap-3">
                    <span>
                      {f.kcal} kcal – P {f.protein_g}g, F {f.fett_g}g, K{" "}
                      {f.kolhydrater_g}g
                    </span>
                    <button
                      onClick={() =>
                        setMyPlan((prev) => ({
                          ...prev,
                          [meal]: prev[meal].filter((_, idx) => idx !== i),
                        }))
                      }
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      ❌
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {/* Lägg till livsmedel för denna måltid */}
          <button
            onClick={() => setOpenMeal(openMeal === meal ? null : meal)}
            className="mt-3 bg-green-500 text-white px-4 py-2 rounded-lg"
          >
            {openMeal === meal ? "❌ Stäng livsmedel" : "🔎 Lägg till livsmedel"}
          </button>

          {openMeal === meal && (
            <div className="mt-3">
              <input
                type="text"
                placeholder="Lägg till livsmedel..."
                className="w-full border p-2 rounded mb-3"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              {filteredFoods.length === 0 ? (
                <p className="text-gray-500">Inga livsmedel hittades.</p>
              ) : (
                <table className="w-full text-left text-gray-700">
                  <thead>
                    <tr>
                      <th>Mat</th>
                      <th>kcal/100g</th>
                      <th>P</th>
                      <th>F</th>
                      <th>K</th>
                      <th>Gram</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFoods.map((f) => (
                      <tr key={f.id}>
                        <td>{f.mat}</td>
                        <td>{f.kcal_per_100g}</td>
                        <td>{f.protein} g</td>
                        <td>{f.fett} g</td>
                        <td>{f.kolhydrater} g</td>
                        <td>
                          <input
                            type="number"
                            min="1"
                            className="w-20 border p-1 rounded"
                            value={gramInputs[f.id] || 100}
                            onChange={(e) =>
                              setGramInputs({
                                ...gramInputs,
                                [f.id]: Number(e.target.value),
                              })
                            }
                          />
                        </td>
                        <td>
                          <button
                            onClick={() =>
                              addToPlan(f, gramInputs[f.id] || 100, meal)
                            }
                            className="text-sm text-green-600 hover:underline"
                          >
                            ➕ Lägg till
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      ))}

      <Navbar />
    </main>
  );
}
