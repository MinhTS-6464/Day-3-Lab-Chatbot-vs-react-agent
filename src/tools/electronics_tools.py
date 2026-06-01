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
    "WELCOME50": {"type": "fixed", "value": 50000.0, "description": "Giảm ngay 50,000 VND cho khách hàng mới"}
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
        "description": "Tính toán giá bán cuối cùng sau khi áp dụng mã giảm giá và cộng thêm 10% thuế VAT. Nhận vào giá sản phẩm (số thực) và mã giảm giá (ví dụ: 'MIMO10', 'WELCOME50'). Nếu không có mã thì truyền chuỗi rỗng ''.",
        "func": calculate_final_price
    }
]
