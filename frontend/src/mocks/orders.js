const mockOrders = [
  {
    id: "ORD-1001",
    date: "2026-06-28T18:30:00Z",
    items: [
      { id: "pepperoni", name: "Pepperoni", quantity: 2, price: 12.99 },
    ],
    total: 25.98,
    status: "delivered",
    address: { name: "Kevin", street: "123 Main St", city: "San Francisco", zip: "94105" },
  },
  {
    id: "ORD-1002",
    date: "2026-06-25T19:15:00Z",
    items: [
      { id: "hawaiian", name: "Hawaiian", quantity: 1, price: 11.99 },
      { id: "sausage", name: "Sausage", quantity: 1, price: 13.99 },
    ],
    total: 25.98,
    status: "delivered",
    address: { name: "Kevin", street: "456 Oak Ave", city: "San Francisco", zip: "94105" },
  },
];

export default mockOrders;
