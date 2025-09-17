"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  const [form, setForm] = useState({
    name: "",
    age: "",
    weight: "",
    height: "",
    gender: "male",
    activity: "moderate",
    goal: "maintain",
    allergies: [] as string[],
    diet: "",
    targetWeight: "",
  });

  const handleCheckbox = (value: string) => {
    setForm((prev) => {
      if (prev.allergies.includes(value)) {
        return { ...prev, allergies: prev.allergies.filter((a) => a !== value) };
      }
      return { ...prev, allergies: [...prev.allergies, value] };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const params = new URLSearchParams({
      name: form.name,
      age: String(form.age),
      weight: String(form.weight),
      height: String(form.height),
      gender: form.gender,
      activity: form.activity,
      goal: form.goal,
      diet: form.diet,
      targetWeight: form.targetWeight,
      allergies: JSON.stringify(form.allergies), // skicka som JSON-sträng
    });

    router.push(`/kostschema?${params.toString()}`);
  };

  return (
    <main className="bg-gray-50 min-h-screen py-10 px-6">
      <div className="max-w-xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          🥦 Generera kostplan
        </h1>

        {/* Formulär */}
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-md rounded-xl p-6 space-y-6"
        >
          {/* Sektion 1 – Personuppgifter */}
          <div>
            <h2 className="text-xl font-semibold text-green-600 mb-3">
              Dina uppgifter
            </h2>
            <div className="space-y-3">
              <input
                className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                placeholder="Namn"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
              <input
                className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                placeholder="Ålder"
                type="number"
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
              />
              <input
                className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                placeholder="Vikt (kg)"
                type="number"
                value={form.weight}
                onChange={(e) => setForm({ ...form, weight: e.target.value })}
              />
              <input
                className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                placeholder="Längd (cm)"
                type="number"
                value={form.height}
                onChange={(e) => setForm({ ...form, height: e.target.value })}
              />

              <div>
                <h2 className="text-xl font-semibold text-green-600 mb-3">
                  Träningsnivå
                </h2>
                <select
                  className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                  value={form.activity}
                  onChange={(e) =>
                    setForm({ ...form, activity: e.target.value })
                  }
                >
                  <option value="sedentary">Stillastående</option>
                  <option value="light">Lätt aktiv</option>
                  <option value="moderate">Måttligt aktiv</option>
                  <option value="active">Aktiv</option>
                  <option value="very_active">Väldigt aktiv</option>
                </select>
              </div>
            </div>
          </div>

          {/* Sektion 2 – Kostpreferenser */}
          <div>
            <h2 className="text-xl font-semibold text-green-600 mb-3">
              Kostpreferenser
            </h2>
            <div className="space-y-3">
              <div>
                <label className="block font-medium text-gray-700">
                  Allergier
                </label>
                <div className="flex gap-4 mt-2">
                  <label>
                    <input
                      type="checkbox"
                      checked={form.allergies.includes("gluten")}
                      onChange={() => handleCheckbox("gluten")}
                    />{" "}
                    Gluten
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={form.allergies.includes("laktos")}
                      onChange={() => handleCheckbox("laktos")}
                    />{" "}
                    Laktos
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={form.allergies.includes("nötter")}
                      onChange={() => handleCheckbox("nötter")}
                    />{" "}
                    Nötter
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-medium text-gray-700">
                  Kosttyp
                </label>
                <select
                  className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
                  value={form.diet}
                  onChange={(e) => setForm({ ...form, diet: e.target.value })}
                >
                  <option value="">Ingen specifik</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="pescetarian">Pescetarian</option>
                </select>
              </div>

              {/* Premiumfält */}
              <div className="bg-gray-100 border border-gray-300 rounded-lg p-3 text-gray-500 flex items-center justify-between">
                <span>🍽️ Maträtter jag inte gillar</span>
                <span className="text-sm text-orange-500">Premium 🔒</span>
              </div>
            </div>
          </div>

          {/* Sektion 3 – Mål */}
          <div>
            <h2 className="text-xl font-semibold text-green-600 mb-3">Mål</h2>
            <select
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
              value={form.goal}
              onChange={(e) => setForm({ ...form, goal: e.target.value })}
            >
              <option value="maintain">Behålla vikt</option>
              <option value="bulk">Gå upp (bulk)</option>
              <option value="cut">Gå ner (cut)</option>
            </select>
            <input
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-green-400"
              placeholder="Målvikt (kg)"
              type="number"
              value={form.targetWeight}
              onChange={(e) =>
                setForm({ ...form, targetWeight: e.target.value })
              }
            />
          </div>

          {/* Skicka-knapp */}
          <button className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg shadow-md transition">
            Generera plan
          </button>
        </form>
      </div>
    </main>
  );
}
