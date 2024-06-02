def categorize(connection):
    cursor = connection.cursor()

    categories = {
        "baggage": ["baggage", "bagage", "bagagge", "baggae", "bagging", "handbag",
        "in/bag", "balostmybag", "bag-drop", "luggage", "check-in/bag",
        "bagport", "lostbag", "cabinbag", "bagggage", "bagagge", "luggage",
        "lugggage", "lugage", "lugagge", "suitcase", "suitcsse", "carry on",
        "carry-on", "carryon", "checked bag", "checked-ba", "backpack"],
        
        "delay_and_cancellation": ["dely", "dealy", "deleyed", "postpone", "postpon", "pospnoe", "cancel",
        "cancelled", "canceled", "stuck"],
        
        "staff": ["staff", "employee", "employes", "personel", "crew", "worker", "pilot",
        "piloot", "steward"],

        "security_and_safety": ["secure", "security", "safe", "safety", "safely", "emergency", "incident",
        "emergency landing", "accident", "burning"],
        
        "money": ["money", "refund", "compensation", "claim", "pay", "paid", "price",
        "expensive", "cheap"]
    }

    category_names = set(categories.keys())
    query = "SHOW COLUMNS FROM tweets"
    cursor.execute(query)
    columns = cursor.fetchall()
    column_names = {column[0] for column in columns}
    columns_without_categories = category_names - column_names
    print(f"Columns without categories: {columns_without_categories}")
    if columns_without_categories:
        for category in columns_without_categories:
            query = f"ALTER TABLE tweets ADD {category} INT(1) DEFAULT 0"
            cursor.execute(query)
            cursor.fetchall()
            print(f'Added column {category}.')
        for category in columns_without_categories:
            words = categories[category]
            query = f"UPDATE tweets SET {category} = 1 WHERE text REGEXP '{'|'.join(words)}'"
            cursor.execute(query)
            cursor.fetchall()
            connection.commit()
            print(f'Modified column {category}.')