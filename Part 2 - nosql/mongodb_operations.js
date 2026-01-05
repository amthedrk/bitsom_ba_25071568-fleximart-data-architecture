

// --- Operation 1: Load Data ---
db.products.drop(); // Clear existing data

var sampleData = [
  {
    "product_id": "ELEC001",
    "name": "Samsung Galaxy S21 Ultra",
    "category": "Electronics",
    "price": 79999.00,
    "stock": 150,
    "reviews": [
      { "user_id": "U001", "username": "TechGuru", "rating": 5, "comment": "Excellent!", "date": "2024-01-15" },
      { "user_id": "U012", "username": "MobileUser", "rating": 4, "comment": "Great performance.", "date": "2024-02-10" }
    ]
  },
  {
    "product_id": "ELEC002",
    "name": "Apple MacBook Pro 14-inch",
    "category": "Electronics",
    "price": 189999.00,
    "stock": 45,
    "reviews": [
      { "user_id": "U005", "username": "DevPro", "rating": 5, "comment": "Perfect for dev.", "date": "2024-01-20" }
    ]
  },
  {
    "product_id": "ELEC003",
    "name": "Sony WH-1000XM5 Headphones",
    "category": "Electronics",
    "price": 29990.00,
    "stock": 200,
    "reviews": [
      { "user_id": "U007", "username": "MusicLover", "rating": 5, "comment": "Best noise cancellation!", "date": "2024-01-25" }
    ]
  },
  {
    "product_id": "ELEC004",
    "name": "Dell 27-inch 4K Monitor",
    "category": "Electronics",
    "price": 32999.00,
    "stock": 60,
    "reviews": [
      { "user_id": "U003", "username": "GraphicDesigner", "rating": 5, "comment": "Vibrant colors.", "date": "2024-02-01" }
    ]
  },
  {
    "product_id": "ELEC005",
    "name": "OnePlus Nord CE 3",
    "category": "Electronics",
    "price": 26999.00,
    "stock": 180,
    "reviews": [
      { "user_id": "U010", "username": "BudgetBuyer", "rating": 4, "comment": "Great value.", "date": "2024-02-10" }
    ]
  },
  {
    "product_id": "ELEC006",
    "name": "Samsung 55-inch QLED TV",
    "category": "Electronics",
    "price": 64999.00,
    "stock": 35,
    "reviews": [
      { "user_id": "U008", "username": "MovieBuff", "rating": 5, "comment": "Stunning picture.", "date": "2024-01-30" }
    ]
  },
  {
    "product_id": "FASH001",
    "name": "Levi's 511 Slim Fit Jeans",
    "category": "Fashion",
    "price": 3499.00,
    "stock": 120,
    "reviews": [
      { "user_id": "U002", "username": "FashionGuy", "rating": 5, "comment": "Perfect fit.", "date": "2024-01-18" }
    ]
  },
  {
    "product_id": "FASH002",
    "name": "Nike Air Max 270 Sneakers",
    "category": "Fashion",
    "price": 12995.00,
    "stock": 85,
    "reviews": [
      { "user_id": "U004", "username": "RunnerLife", "rating": 5, "comment": "Super comfortable.", "date": "2024-01-22" }
    ]
  },
  {
    "product_id": "FASH003",
    "name": "Adidas Originals T-Shirt",
    "category": "Fashion",
    "price": 1499.00,
    "stock": 200,
    "reviews": [
      { "user_id": "U006", "username": "CasualStyle", "rating": 4, "comment": "Good quality.", "date": "2024-02-05" }
    ]
  },
  {
    "product_id": "FASH004",
    "name": "Puma RS-X Sneakers",
    "category": "Fashion",
    "price": 8999.00,
    "stock": 95,
    "reviews": [
      { "user_id": "U009", "username": "StreetStyle", "rating": 4, "comment": "Stylish.", "date": "2024-02-12" }
    ]
  }
];

db.products.insertMany(sampleData);
print("1. Data Loaded Successfully (New Dataset).");


// --- Operation 2: Basic Query ---
// Goal: Find Electronics under 50,000. Return only name, price, and stock.
// (Logic remains valid for new data)
print("\n--- Operation 2: Affordable Electronics ---");

var affordableElectronics = db.products.find(
    { 
        "category": "Electronics", 
        "price": { $lt: 50000 } 
    }, 
    { 
        "name": 1, 
        "price": 1, 
        "stock": 1, 
        "_id": 0
    }
);
affordableElectronics.forEach(printjson);


// --- Operation 3: Review Analysis ---
// Goal: Find products with average rating >= 4.0 using aggregation.
// (Logic remains valid: 'reviews.rating' path is unchanged)
print("\n--- Operation 3: Highly Rated Products ---");

var highRatedProducts = db.products.aggregate([
    {
        $addFields: {
            avg_rating: { $avg: "$reviews.rating" }
        }
    },
    {
        $match: {
            avg_rating: { $gte: 4.0 }
        }
    },
    {
        $project: {
            name: 1,
            avg_rating: 1
        }
    }
]);
highRatedProducts.forEach(printjson);


// --- Operation 4: Update Operation ---
// Goal: Add a new review to product "ELEC001".
// UPDATED: Changed schema to match new data (user_id/username instead of just user)
print("\n--- Operation 4: Adding Review to ELEC001 ---");

db.products.updateOne(
    { "product_id": "ELEC001" },
    {
        $push: {
            "reviews": {
                "user_id": "U999",       // <--- Updated Field
                "username": "ReviewerX", // <--- Updated Field
                "rating": 4,
                "comment": "Good value for a flagship.",
                "date": new Date().toISOString().split('T')[0] // formats as YYYY-MM-DD to match your data
            }
        }
    }
);
print("Review added with correct schema.");


// --- Operation 5: Complex Aggregation ---
// Goal: Calculate average price by category, sort descending.
// (Logic remains valid)
print("\n--- Operation 5: Category Price Analysis ---");

var categoryAnalysis = db.products.aggregate([
    {
        $group: {
            _id: "$category",
            avg_price: { $avg: "$price" },
            product_count: { $sum: 1 }
        }
    },
    {
        $sort: {
            avg_price: -1
        }
    }
]);
categoryAnalysis.forEach(printjson);