import { useState } from "react";
import MedicineCard from "./MedicineCard";
import { medicine, category } from "../data";

function MedicineListings() {
  const [selectedCategory, setSelectedCategory] = useState("all");

  const filteredMedicine =
    selectedCategory === "all"
      ? medicine
      : medicine.filter((item) => item.category === selectedCategory);

  return (
    <section className="px-8 py-8 lg:py-8">
      <div className="mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Top trending medicines worldwide
        </h2>
        <p className="text-lg text-muted-foreground">
          Discover the most trending medicines worldwide for an unforgettable
          experience.
        </p>
      </div>

      {/* Category filter tabs */}
      <div className="flex items-center flex-wrap gap-x-4 mb-8">
        <button
          onClick={() => setSelectedCategory("all")}
          className={`px-4 py-2 rounded ${
            selectedCategory === "all"
              ? "bg-primary text-white"
              : "bg-gray-200 text-gray-700"
          }`}
        >
          All
        </button>
        {category.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded ${
              selectedCategory === cat
                ? "bg-primary text-white"
                : "bg-gray-200 text-gray-700"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Medicine grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {filteredMedicine.map((med) => (
          <MedicineCard key={med._id} medicine={med} />
        ))}
      </div>
    </section>
  );
}

export default MedicineListings;
