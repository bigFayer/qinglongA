import os
import requests
from datetime import datetime, timedelta

# ----------------------------- 数据配置 -----------------------------
DELIVERY_DATES = [
    {"date": "2025-01-17", "type": "股指期货"},
    {"date": "2025-01-22", "type": "期权"},
    {"date": "2025-02-21", "type": "股指期货"},
    {"date": "2025-02-26", "type": "期权"},
    {"date": "2025-02-27", "type": "A50期货"},
    {"date": "2025-03-21", "type": "股指期货"},
    {"date": "2025-03-26", "type": "期权"},
    {"date": "2025-03-28", "type": "A50期货"},
    {"date": "2025-04-18", "type": "股指期货"},
    {"date": "2025-04-23", "type": "期权"},
    {"date": "2025-05-16", "type": "股指期货"},
    {"date": "2025-05-28", "type": "期权"},
    {"date": "2025-05-29", "type": "A50期货"},
    {"date": "2025-06-20", "type": "股指期货"},
    {"date": "2025-06-25", "type": "期权"},
    {"date": "2025-06-27", "type": "A50期货"},
    {"date": "2025-07-18", "type": "股指期货"},
    {"date": "2025-07-23", "type": "期权"},
    {"date": "2025-08-15", "type": "股指期货"},
    {"date": "2025-08-27", "type": "期权"},
    {"date": "2025-08-28", "type": "A50期货"},
    {"date": "2025-09-19", "type": "股指期货"},
    {"date": "2025-09-24", "type": "期权"},
    {"date": "2025-09-29", "type": "A50期货"},
    {"date": "2025-10-17", "type": "股指期货"},
    {"date": "2025-10-22", "type": "期权"},
    {"date": "2025-11-21", "type": "股指期货"},
    {"date": "2025-11-26", "type": "期权"},
    {"date": "2025-11-27", "type": "A50期货"}
]

# ----------------------------- 函数定义 -----------------------------
def parse_date(date_str):
    """将日期字符串转换为datetime对象"""
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def check_delivery_days():
    """检查距离当前日期还有2天的交割日"""
    today = datetime.now().date()
    target_date = today + timedelta(days=2)
    for delivery in DELIVERY_DATES:
        delivery_date = parse_date(delivery["date"])
        if delivery_date == target_date:
            return delivery
    return None

def send_serverchan_message(delivery):
    """通过Server酱发送微信通知"""
    sckey = os.getenv("SERVERCHAN_SCKEY")
    if not sckey:
        raise ValueError("请在GitHub Secrets中设置SERVERCHAN_SCKEY环境变量！")

    title = "交割日提醒"
    content = (
        f"类型：{delivery['type']}\n"
        f"日期：{delivery['date']}\n"
        f"当前日期：{datetime.now().strftime('%Y-%m-%d')}"
    )
    
    # 发送POST请求到Server酱接口
    url = f"https://sc.ftqq.com/{sckey}.send"
    data = {
        "text": title,
        "desp": content
    }
    response = requests.post(url, data=data)
    
    if response.json().get("errno") == 0:
        print("通知已成功发送！")
    else:
        print("发送失败，请检查SCKEY是否正确。")

# ----------------------------- 主程序 -----------------------------
if __name__ == "__main__":
    delivery = check_delivery_days()
    if delivery:
        send_serverchan_message(delivery)
    else:
        print("今天没有交割日前2天的提醒。")
