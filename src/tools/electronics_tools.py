import json
from typing import Dict, Any, List

# Mock electronics database
PRODUCTS = {
    "iphone 15 pro max": {
        "name": "iPhone 15 Pro Max",
        "category": "smartphone",
        "price": 30000000.0,
        "stock": 5,
        "specs": "Màn hình 6.7 inch Super Retina XDR, Chip Apple A17 Pro, Camera Zoom 5x, Bộ nhớ 256GB",
        "reviews": "Camera cực kỳ sắc nét, pin trâu nhưng sạc hơi chậm và giá khá cao. Đánh giá: 4.8/5."
    },
    "samsung galaxy s24 ultra": {
        "name": "Samsung Galaxy S24 Ultra",
        "category": "smartphone",
        "price": 28000000.0,
        "stock": 8,
        "specs": "Màn hình 6.8 inch QHD+ Dynamic AMOLED 2X, Snapdragon 8 Gen 3, Bút S-Pen, Bộ nhớ 256GB",
        "reviews": "Bút S-Pen rất tiện lợi, màn hình sáng đẹp xuất sắc, tuy nhiên thiết kế hơi vuông vức cấn tay. Đánh giá: 4.7/5."
    },
    "laptop asus zenbook 14": {
        "name": "Laptop Asus Zenbook 14",
        "category": "laptop",
        "price": 22000000.0,
        "stock": 3,
        "specs": "Màn hình 14 inch OLED 2.8K, CPU Ryzen 7 7730U, RAM 16GB, SSD 512GB",
        "reviews": "Màn hình OLED siêu đẹp và rực rỡ, máy mỏng nhẹ thời trang, pin dùng được tầm 8 tiếng. Loa ngoài hơi nhỏ. Đánh giá: 4.5/5."
    },
    "laptop macbook air m3": {
        "name": "Laptop MacBook Air M3",
        "category": "laptop",
        "price": 26000000.0,
        "stock": 4,
        "specs": "Màn hình 13.6 inch Liquid Retina, Chip Apple M3, RAM 8GB, SSD 256GB, Thiết kế không quạt siêu êm",
        "reviews": "Hiệu năng mượt mà, pin siêu trâu 15 tiếng, thiết kế sang trọng đẳng cấp nhưng RAM 8GB mặc định hơi ít. Đánh giá: 4.6/5."
    },
    "tai nghe sony wh-1000xm5": {
        "name": "Tai nghe Sony WH-1000XM5",
        "category": "audio",
        "price": 7000000.0,
        "stock": 10,
        "specs": "Chống ồn chủ động ANC đỉnh cao, Driver 30mm, Pin lên tới 30 giờ",
        "reviews": "Chống ồn đỉnh cao top 1 thị trường, đeo êm tai, âm bass sâu. Giá hơi đắt và không gập gọn được như XM4. Đánh giá: 4.7/5."
    },
    "ban phim co keychron k2": {
        "name": "Bàn phím cơ Keychron K2",
        "category": "accessory",
        "price": 2000000.0,
        "stock": 15,
        "specs": "Layout 75% gọn gàng, Gateron Switch, Bluetooth/Wired, Tương thích tốt macOS/Windows",
        "reviews": "Gõ phím sướng tay, pin ổn định, kết nối nhanh. Độ cao bàn phím hơi cao nên cần dùng kê tay. Đánh giá: 4.4/5."
    }
}

PROMO_CODES = {
    "MIMO10": {"type": "percent", "value": 0.10, "description": "Giảm giá 10% tổng đơn hàng"},
    "WELCOME50": {"type": "fixed", "value": 50000.0, "description": "Giảm ngay 50,000 VND cho khách hàng mới"},
    "WINNER": {
        "type": "percent",
        "value": 0.15,
        "description": "Giảm 15% cho đơn smartphone (mã chiến thắng)",
        "categories": ["smartphone"],
    },
}

SHIPPING_RATES = {
    "ha noi": 30000.0,
    "hanoi": 30000.0,
    "hồ chí minh": 50000.0,
    "ho chi minh": 50000.0,
    "da nang": 40000.0,
    "đà nẵng": 40000.0,
    "default": 80000.0,
}

def search_electronics(query: str) -> str:
    """
    Search for electronic products in the catalog based on a keyword or category.
    Args:
        query: Keyword to search (e.g. 'laptop', 'iphone', 'tai nghe', 'sony')
    Returns:
        JSON string containing the list of matched products (name, category, price, stock).
    """
    query_clean = query.lower().strip()
    results = []
    for k, v in PRODUCTS.items():
        if query_clean in k or query_clean in v["category"] or query_clean in v["specs"].lower():
            results.append({
                "name": v["name"],
                "category": v["category"],
                "price": f"{v['price']:,.0f} VND",
                "stock": v["stock"]
            })
    
    if not results:
        return f"Không tìm thấy sản phẩm nào khớp với từ khóa '{query}'."
    return json.dumps(results, ensure_ascii=False, indent=2)

def get_product_detail(product_name: str) -> str:
    """
    Retrieve detailed specifications, price, stock count, and review summary for a specific product.
    Args:
        product_name: The exact or close name of the product (e.g. 'iPhone 15 Pro Max', 'Asus Zenbook 14')
    Returns:
        JSON string with complete product details or an error message if not found.
    """
    name_clean = product_name.lower().strip()
    # Try direct match
    if name_clean in PRODUCTS:
        return json.dumps(PRODUCTS[name_clean], ensure_ascii=False, indent=2)
    
    # Try substring match
    for k, v in PRODUCTS.items():
        if name_clean in k or k in name_clean:
            return json.dumps(v, ensure_ascii=False, indent=2)
            
    return f"Không tìm thấy thông tin chi tiết cho sản phẩm '{product_name}'. Hãy dùng công cụ search_electronics để tìm đúng tên sản phẩm."

def calculate_final_price(price: float, discount_code: str) -> str:
    """
    Applies a coupon code, subtracts the discount amount, and calculates the final cost including 10% VAT.
    Args:
        price: The original price of the product (float).
        discount_code: The promo code to apply (e.g., 'MIMO10', 'WELCOME50'). If no code, use empty string "".
    Returns:
        JSON string containing original price, discount applied, tax (10% VAT), and the final price.
    """
    discount_amount = 0.0
    applied = False
    desc = "Không áp dụng"
    
    code_clean = discount_code.upper().strip()
    if code_clean in PROMO_CODES:
        promo = PROMO_CODES[code_clean]
        applied = True
        desc = promo["description"]
        if promo["type"] == "percent":
            discount_amount = price * promo["value"]
        elif promo["type"] == "fixed":
            discount_amount = promo["value"]
        # WINNER only applies to smartphone orders in lab scenario (price > 20M typical)
        if code_clean == "WINNER" and price < 10_000_000:
            applied = False
            desc = "WINNER chỉ áp dụng đơn smartphone từ 10 triệu"
            discount_amount = 0.0
    
    discounted_price = max(0.0, price - discount_amount)
    vat_tax = discounted_price * 0.10
    final_price = discounted_price + vat_tax
    
    result = {
        "original_price": f"{price:,.0f} VND",
        "discount_code": discount_code if discount_code else "Không có",
        "discount_applied": applied,
        "discount_description": desc,
        "discount_amount": f"{discount_amount:,.0f} VND",
        "price_after_discount": f"{discounted_price:,.0f} VND",
        "vat_tax_10%": f"{vat_tax:,.0f} VND",
        "final_price": f"{final_price:,.0f} VND"
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def check_stock(product_name: str, quantity: int = 1) -> str:
    """
    Check if enough units are in stock for a product.
    Args:
        product_name: Product name (e.g. 'iPhone 15 Pro Max')
        quantity: Number of units requested (integer)
    """
    name_clean = product_name.lower().strip()
    for k, v in PRODUCTS.items():
        if name_clean in k or k in name_clean or name_clean in v["name"].lower():
            available = v["stock"] >= quantity
            return json.dumps(
                {
                    "product": v["name"],
                    "requested": quantity,
                    "in_stock": available,
                    "stock_available": v["stock"],
                    "unit_price": f"{v['price']:,.0f} VND",
                },
                ensure_ascii=False,
                indent=2,
            )
    return f"Không tìm thấy sản phẩm '{product_name}' để kiểm tra tồn kho."


def calc_shipping(destination: str, weight_kg: float = 0.2) -> str:
    """
    Calculate shipping fee to a Vietnamese city.
    Args:
        destination: City name (e.g. 'Hà Nội', 'Ho Chi Minh')
        weight_kg: Package weight in kg (default 0.2 for phones)
    """
    dest = destination.lower().strip()
    base = SHIPPING_RATES.get("default", 80000.0)
    for city, fee in SHIPPING_RATES.items():
        if city in dest or dest in city:
            base = fee
            break
    extra = max(0, weight_kg - 0.5) * 20000.0
    total = base + extra
    return json.dumps(
        {
            "destination": destination,
            "weight_kg": weight_kg,
            "shipping_fee": f"{total:,.0f} VND",
        },
        ensure_ascii=False,
        indent=2,
    )


# Tool specs to expose to the ReAct agent
TOOLS_LIST = [
    {
        "name": "search_electronics",
        "description": "Tìm kiếm các thiết bị điện tử trong danh mục (ví dụ: 'laptop', 'điện thoại', 'tai nghe'). Trả về danh sách sản phẩm khớp từ khóa kèm giá và số lượng tồn kho.",
        "func": search_electronics
    },
    {
        "name": "get_product_detail",
        "description": "Lấy thông số kỹ thuật chi tiết, giá chính xác, số lượng tồn và tổng hợp đánh giá ưu/nhược điểm từ khách hàng của một sản phẩm cụ thể bằng tên đầy đủ.",
        "func": get_product_detail
    },
    {
        "name": "calculate_final_price",
        "description": "Tính toán giá bán cuối cùng sau khi áp dụng mã giảm giá và cộng thêm 10% thuế VAT. Nhận vào giá sản phẩm (số thực) và mã giảm giá (ví dụ: 'MIMO10', 'WELCOME50', 'WINNER'). Nếu không có mã thì truyền chuỗi rỗng ''.",
        "func": calculate_final_price
    }
]

TOOLS_LIST_V2 = TOOLS_LIST + [
    {
        "name": "check_stock",
        "description": "Kiểm tra tồn kho: có đủ số lượng sản phẩm không. Tham số product_name (tên đầy đủ) và quantity (số lượng, số nguyên).",
        "func": check_stock,
    },
    {
        "name": "calc_shipping",
        "description": "Tính phí giao hàng theo thành phố Việt Nam. Tham số destination (VD: 'Hà Nội') và weight_kg (float, mặc định 0.2).",
        "func": calc_shipping,
    },
]
