def categorize(connection):
    cursor = connection.cursor()

    categories = {
    "baggage": [
        "baggage", "bagage", "bagagge", "baggae", "bagging", "handbag", 
        "in/bag", "balostmybag", "bag-drop", "luggage", "check-in/bag", 
        "bagport", "lostbag", "cabinbag", "bagggage", "bagagge", "luggage", 
        "lugggage", "lugage", "lugagge", "suitcase", "suitcsse", "carry on", 
        "carry-on", "carryon", "checked bag", "checked-ba", "backpack"
    ],
    
    "delay_and_cancellation": [
        "delay", "planedelays", "delayedflight", "flightdelayed", "delays", 
        "delayed", "dely", "dealy", "deleyed", "postpone", "postponed", 
        "postpones", "postpon", "pospnoe", "cancel", "cancelled", "canceled", 
        "cancellation", "cancellations", "stuck", "wait", "waiting"
    ],
    
    "staff": [
        "staff", "employee", "employes", "employees", "personel", "crew", 
        "worker", "pilot", "piloot", "steward", "stewardess", "stewardes", 
        "flight attendant", "flightattendant", "flightattendent", 
        "flight-attendant", "attendant", "attendent", "host"
    ],
    
    "money": [
        "money", "refund", "compensation", "compensatoin", "klaim", "claim", 
        "pay", "pays", "afford", "affort", "paid", "price", "expensive", 
        "cheap", "cheep", "cheaper"
    ]
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
            
def drop(connection):
    cursor = connection.cursor()
    columns = ['baggage', 'delay_and_cancellation', 'staff', 'money']
    for column in columns:
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tweets' AND COLUMN_NAME = '{column}'")
        result = cursor.fetchone()
        if result[0] > 0:
            cursor.execute(f"ALTER TABLE tweets DROP COLUMN {column}")
    connection.commit()
    print("Columns dropped.")