from langchain_core.tools import tool

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}

@tool
def search_flights(origin: str, destination: str, departure_after: str = None) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    - departure_after: (Tùy chọn) Chỉ tìm chuyến bay khởi hành SAU giờ này. Định dạng 'HH:MM' (VD: '14:30').
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    """
    flights = FLIGHTS_DB.get((origin, destination))
    
    if not flights:
        reverse_flights = FLIGHTS_DB.get((destination, origin))
        if not reverse_flights:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
        else:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}, nhưng có chuyến bay theo chiều ngược lại."
    
    if departure_after:
        flights = [f for f in flights if f["departure"] >= departure_after]
        if not flights:
            return f"Không có chuyến bay nào từ {origin} đến {destination} khởi hành sau {departure_after}."

    result = f"Các chuyến bay từ {origin} đến {destination}:\n"
    for idx, flight in enumerate(flights, 1):
        formatted_price = f"{flight['price']:,}".replace(',', '.') + "đ"
        result += (
            f"{idx}. {flight['airline']} | "
            f"{flight['departure']} - {flight['arrival']} | "
            f"Giá: {formatted_price} | Hạng: {flight['class']}\n"
        )
        
    return result.strip()

@tool
def search_hotels(city: str, max_price_per_night: int = 99999999, num_nights: int = 1) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, lọc theo giá và tính tổng tiền cho số đêm lưu trú.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    - num_nights: số đêm lưu trú để tính tổng tiền, mặc định là 1 đêm.
    """
    hotels_in_city = HOTELS_DB.get(city, [])
    
    if not hotels_in_city:
        return f"Hiện tại hệ thống chưa có dữ liệu khách sạn tại {city}."
        
    filtered_hotels = [
        hotel for hotel in hotels_in_city 
        if hotel["price_per_night"] <= max_price_per_night
    ]
    
    formatted_max_price = f"{max_price_per_night:,}".replace(',', '.') + "đ"
    
    if not filtered_hotels:
        return f"Không tìm thấy khách sạn tại {city} với giá dưới {formatted_max_price}/đêm. Hãy thử tăng ngân sách."
        
    sorted_hotels = sorted(filtered_hotels, key=lambda x: x["rating"], reverse=True)
    
    result = f"Các khách sạn tại {city} (Ngân sách dưới {formatted_max_price}/đêm | Lưu trú: {num_nights} đêm):\n"
    for idx, hotel in enumerate(sorted_hotels, 1):
        price_per_night = hotel['price_per_night']
        total_price = price_per_night * num_nights
        
        fmt_price = f"{price_per_night:,}".replace(',', '.') + "đ"
        fmt_total = f"{total_price:,}".replace(',', '.') + "đ"
        
        result += (
            f"{idx}. {hotel['name']} | {hotel['stars']}⭐ | "
            f"Khu vực: {hotel['area']} | Đánh giá: {hotel['rating']}/5 | "
            f"Giá: {fmt_price}/đêm (Tổng {num_nights} đêm: {fmt_total})\n"
        )
        
    return result.strip()

def format_currency(amount: int) -> str:
    return f"{amount:,}".replace(',', '.') + "đ"

@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget (int): tổng ngân sách ban đầu (VNĐ)
    - expenses (str): chuỗi mô tả các khoản chi, định dạng 'tên_khoản:số_tiền', cách nhau bởi dấu phẩy.
    """
    expense_dict = {}
    total_expense = 0
    
    if expenses.strip():
        try:
            items = expenses.split(',')
            for item in items:
                name, amount_str = item.split(':')
                name = name.strip().replace('_', ' ').capitalize()
                amount = int(amount_str.strip())
                
                expense_dict[name] = amount
                total_expense += amount
        except ValueError:
            return (
                "Lỗi định dạng expenses! Vui lòng cung cấp đúng định dạng: 'tên_khoản:số_tiền', "
                "ví dụ: 'vé_máy_bay:890000,khách_sạn:650000'"
            )

    remaining = total_budget - total_expense
    
    result = "Bảng chi phí:\n"
    for name, amount in expense_dict.items():
        result += f"- {name}: {format_currency(amount)}\n"
        
    result += "---\n"
    result += f"Tổng chi: {format_currency(total_expense)}\n"
    result += f"Ngân sách: {format_currency(total_budget)}\n"
    result += f"Còn lại: {format_currency(remaining)}\n"
    
    if remaining < 0:
        over_budget = abs(remaining)
        result += f"\nVượt ngân sách {format_currency(over_budget)}! Cần điều chỉnh."
        
    return result.strip()