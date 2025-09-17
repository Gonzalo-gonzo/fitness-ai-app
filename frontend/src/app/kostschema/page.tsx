"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

type FoodItem = {
    mat: string;
    mangd_g: number;
    kcal: number;
    protein: number;
    fett: number;
    kolhydrater: number;
};

type PlanResult = {
    user: string;
    bmr: number;
    tdee: number;
    calories: number;
    targetWeight?: number;
    macros: {
        protein_g: number;
        fat_g: number;
        carbs_g: number;
    };
    menu: {
        frukost: FoodItem[];
        mellanmal_1: FoodItem[];
        lunch: FoodItem[];
        pre_workout_meal: FoodItem[];
        middag: FoodItem[];
    };
};

export default function KostschemaPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [result, setResult] = useState<PlanResult | null>(null);

    useEffect(() => {
        const name = searchParams.get("name") || "Användare";
        const age = Number(searchParams.get("age") || 25);
        const weight = Number(searchParams.get("weight") || 70);
        const height = Number(searchParams.get("height") || 175);
        const gender = searchParams.get("gender") || "male";
        const activity = searchParams.get("activity") || "moderate";
        const goal = searchParams.get("goal") || "maintain";
        const diet = searchParams.get("diet") || "";
        const targetWeight = searchParams.get("targetWeight");

        // Hämta plan från backend
        fetch("http://127.0.0.1:8080/generate_plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                age,
                weight,
                height,
                gender,
                activity,
                goal,
                diet,
                allergies: [], // kan skickas från formuläret senare
                targetWeight: targetWeight ? Number(targetWeight) : undefined,
            }),
        })
            .then((res) => res.json())
            .then((data) => setResult(data));
    }, [searchParams]);

    if (!result) return <p>Laddar kostschema...</p>;

    return (
        <main className="p-6 max-w-2xl mx-auto">
            {/* Titel + tillbaka-pil */}
            <div className="flex items-center gap-3 mb-6">
                <button
                    onClick={() => router.push("/")}
                    className="p-2 rounded-full hover:bg-gray-200"
                >
                    ←
                </button>
                <h1 className="text-3xl font-bold text-gray-800">
                    {result.user ? `${result.user}s kostschema` : "Ditt kostschema"}
                </h1>
            </div>

            <div className="bg-green-50 p-4 rounded-xl shadow mb-6">
                <h2 className="text-2xl font-bold text-green-700 mb-2">
                    🌱 Kostschema för {result.user}
                </h2>
                <p className="text-gray-600">Målvikt: {result.targetWeight || "-"} kg</p>
                <p className="text-gray-600">Kalorier/dag: {result.calories} kcal</p>
            </div>

            {Object.entries(result.menu).map(([mealName, items]) => (
                <div key={mealName} className="bg-white p-4 rounded-lg shadow mb-4">
                    <h3 className="text-xl font-semibold mb-3">
                        {mealName === "frukost" && "🥣 Frukost"}
                        {mealName === "mellanmal_1" && "🥪 Mellanmål 1"}
                        {mealName === "lunch" && "🍗 Lunch"}
                        {mealName === "pre_workout_meal" && "⚡ Pre-workout"}
                        {mealName === "middag" && "🍲 Middag"}
                    </h3>

                    <table className="w-full text-left text-gray-700 mb-3">
                        <thead>
                            <tr>
                                <th>Mat</th>
                                <th>Gram</th>
                                <th>Kcal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.map((f, i) => (
                                <tr key={i}>
                                    <td>{f.mat}</td>
                                    <td>{f.mangd_g} g</td>
                                    <td>{f.kcal}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div className="text-sm text-gray-600">
                        <p>🍗 Protein: {items.reduce((a, f) => a + f.protein, 0)} g</p>
                        <p>🥑 Fett: {items.reduce((a, f) => a + f.fett, 0)} g</p>
                        <p>🍞 Kolhydrater: {items.reduce((a, f) => a + f.kolhydrater, 0)} g</p>
                    </div>
                </div>
            ))}

            {/* Dagssummering */}
            <div className="bg-green-100 p-4 rounded-xl shadow mt-6">
                <h3 className="text-xl font-bold text-green-800 mb-2">📊 Totalt för dagen</h3>
                <p>Kalorier: {result.calories} kcal</p>
                <p>Protein: {result.macros.protein_g} g</p>
                <p>Fett: {result.macros.fat_g} g</p>
                <p>Kolhydrater: {result.macros.carbs_g} g</p>
            </div>

        </main>
    );
}
