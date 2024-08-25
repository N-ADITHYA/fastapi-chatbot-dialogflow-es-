import psycopg2
from config import setting


conn = psycopg2.connect(host = setting.host, database = setting.database, user = setting.user, password = setting.password)

cursor = conn.cursor()


def insert_order_item(food_item: str, quantity, next_order_id):
    try:
        cursor = conn.cursor()

        cursor.execute("CALL insert_order_item(%s::VARCHAR, %s::INTEGER, %s::INTEGER);", (food_item, int(quantity), next_order_id))
        # cursor.callproc("insert_order_item", (food_item, quantity, next_order_id))

        conn.commit()

        print("Order item inserted successfully")

        return 1
    except psycopg2.Error as err:
        print(err)
        conn.rollback()

        return -1
    except Exception as e:
        print(e)
        conn.rollback()

        return -1


def get_order_status(order_id: int):
    query = f"SELECT * FROM order_tracking WHERE order_id = {order_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    # conn.close()
    # cursor.close()
    if result is None: return None
    else: return result[1]

def next_order_id():
    query = f'SELECT MAX(order_id) FROM orders'
    cursor.execute(query)

    result = cursor.fetchone()

    if result is None: return 1
    else: return result[0] + 1


def get_total_order_price(order_id):

    query = f"SELECT get_total_order_price({order_id})"

    cursor.execute(query)

    result = cursor.fetchone()[0]


    return result

def insert_order_tracking(order_id, status):
    cursor = conn.cursor()

    query = f"INSERT INTO order_tracking(order_id, status) VALUES (%s, %s)"
    cursor.execute(query, (order_id, status))

    conn.commit()


if __name__ == '__main__':
    print(get_total_order_price(40))
    print(next_order_id())