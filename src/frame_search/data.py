rows = [
    {
        "name": "Alice",
        "age": 25,
        "city": "New York",
        "score": 88.5,
        "passed": True,
        "Math Major": False,
    },
    {
        "name": "Bob",
        "age": 30,
        "city": "Los Angeles",
        "score": 92.0,
        "passed": True,
        "Math Major": True,
    },
    {
        "name": "Charlie",
        "age": 35,
        "city": "New York",
        "score": 85.0,
        "passed": False,
        "Math Major": False,
    },
    {
        "name": "David",
        "age": 40,
        "city": "Chicago",
        "score": 70.5,
        "passed": False,
        "Math Major": True,
    },
    {
        "name": "Eve",
        "age": 28,
        "city": "Los Angeles",
        "score": 95.0,
        "passed": True,
        "Math Major": False,
    },
    {
        "name": "Frank",
        "age": 70,
        "city": "Philadelphia",
        "score": 40.0,
        "passed": False,
        "Math Major": False,
    },
]

data = {
    "name": [row["name"] for row in rows],
    "age": [row["age"] for row in rows],
    "city": [row["city"] for row in rows],
    "score": [row["score"] for row in rows],
    "passed": [row["passed"] for row in rows],
    "Math Major": [row["Math Major"] for row in rows],
}
