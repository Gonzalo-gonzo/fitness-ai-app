"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

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
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login"); // 👈 skickar till login om inte inloggad
    }
  }, [router]);

  // ✅ Hämta plan från query-param om den finns
  useEffect(() => {
    const planParam = searchParams.get("plan");
    if (planParam) {
      try {
        const parsed: PlanResult = JSON.parse(decodeURIComponent(planParam));
        setResult(parsed);
        return; // vi behöver inte hämta från backend i detta fall
      } catch (err) {
        console.error("Kunde inte parsa plan-param:", err);
      }
    }
  }, [searchParams]);

// ✅ PDF-knappfunktion
const handleDownloadPDF = () => {
  if (!result) return;

  const doc = new jsPDF();

  // Header
  doc.setFontSize(16);
  doc.text(`Kostschema – ${result.user}`, 14, 16);
  doc.setFontSize(10);
  doc.text(
    `BMR: ${result.bmr}  •  TDEE: ${result.tdee}  •  Kalorier/dag: ${result.calories}`,
    14,
    22
  );
  if (result.targetWeight) {
    doc.text(`Målvikt: ${result.targetWeight} kg`, 14, 28);
  }

  let y = result.targetWeight ? 36 : 32;

  const meals: Array<[keyof typeof result.menu, string]> = [
    ["frukost", "Frukost"],
    ["mellanmal_1", "Mellanmål 1"],
    ["lunch", "Lunch"],
    ["pre_workout_meal", "Pre-workout"],
    ["middag", "Middag"],
  ];

  meals.forEach(([key, title]) => {
    const items = result.menu[key];
    if (!items || items.length === 0) return; // 👈 hoppa över om undefined eller tom

    doc.setFontSize(12);
    doc.text(title, 14, y);
    y += 4;

    const rows = (result.menu[key] || []).map((f) => [
      f.mat,
      `${f.mangd_g} g`,
      `${f.kcal}`,
      `${f.protein} g`,
      `${f.fett} g`,
      `${f.kolhydrater} g`,
    ]);

    autoTable(doc, {
      head: [["Mat", "Gram", "kcal", "Protein", "Fett", "Kolhydrater"]],
      body: rows,
      startY: y,
      margin: { left: 14, right: 14 },
      styles: { fontSize: 9, cellPadding: 2 },
      headStyles: { fillColor: [34, 197, 94] },
      theme: "grid",
    });

    // @ts-expect-error — lastAutoTable finns runtime
    y = doc.lastAutoTable.finalY + 8;
  });

  // Totalt för dagen
  doc.setFontSize(12);
  doc.text("Totalt för dagen", 14, y);
  y += 4;

  autoTable(doc, {
    head: [["Kalorier", "Protein", "Fett", "Kolhydrater"]],
    body: [
      [
        `${result.calories} kcal`,
        `${result.macros.protein_g} g`,
        `${result.macros.fat_g} g`,
        `${result.macros.carbs_g} g`,
      ],
    ],
    startY: y,
    margin: { left: 14, right: 14 },
    styles: { fontSize: 10, cellPadding: 2 },
    theme: "striped",
  });

  doc.save(`${result.user || "kostschema"}.pdf`);
};


  if (!result) return <p>Laddar kostschema...</p>;

  return (
    <main className="p-6 max-w-2xl mx-auto">
      {/* Titel + knappar */}
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
        <button
          onClick={handleDownloadPDF}
          className="px-4 py-2 bg-green-500 text-white rounded-lg shadow hover:bg-green-600"
        >
          Ladda ner PDF
        </button>
      </div>

      {/* 👇 Här behåller vi ditt UI oförändrat */}
      <div id="kostschema-content">
        <div className="bg-green-50 p-4 rounded-xl shadow mb-6">
          <h2 className="text-2xl font-bold text-green-700 mb-2">
            🌱 Kostschema för {result.user}
          </h2>
          <p className="text-gray-600">
            Målvikt: {result.targetWeight || "-"} kg
          </p>
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
              <p>
                🍗 Protein: {items.reduce((a, f) => a + f.protein, 0)} g
              </p>
              <p>🥑 Fett: {items.reduce((a, f) => a + f.fett, 0)} g</p>
              <p>
                🍞 Kolhydrater: {items.reduce((a, f) => a + f.kolhydrater, 0)} g
              </p>
            </div>
          </div>
        ))}

        {/* Totalsummering */}
        <div className="bg-green-100 p-4 rounded-xl shadow mt-6">
          <h3 className="text-xl font-bold text-green-800 mb-2">
            📊 Totalt för dagen
          </h3>
          <p>Kalorier: {result.calories} kcal</p>
          <p>Protein: {result.macros.protein_g} g</p>
          <p>Fett: {result.macros.fat_g} g</p>
          <p>Kolhydrater: {result.macros.carbs_g} g</p>
        </div>
      </div>
    </main>
  );
}
