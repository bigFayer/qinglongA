import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ----------------------------- 2025年完整数据配置 -----------------------------
DELIVERY_DATES = [
    # 股指期货/期权（中金所）
    {"date": "2025-01-17", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-01-22", "type": "期权", "contract": "IO"},
    {"date": "2025-02-21", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-02-26", "type": "期权", "contract": "IO"},
    {"date": "2025-03-21", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-03-27", "type": "期权", "contract": "IO"},
    {"date": "2025-04-18", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-04-24", "type": "期权", "contract": "IO"},
    {"date": "2025-05-16", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-05-22", "type": "期权", "contract": "IO"},
    {"date": "2025-06-20", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-06-26", "type": "期权", "contract": "IO"},
    {"date": "2025-07-18", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-07-24", "type": "期权", "contract": "IO"},
    {"date": "2025-08-15", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-08-21", "type": "期权", "contract": "IO"},
    {"date": "2025-09-19", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-09-25", "type": "期权", "contract": "IO"},
    {"date": "2025-10-17", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-10-23", "type": "期权", "contract": "IO"},
    {"date": "2025-11-21", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-11-27", "type": "期权", "contract": "IO"},
    {"date": "2025-12-19", "type": "股指期货", "contract": "IF/IH/IC"},
    {"date": "2025-12-25", "type": "期权", "contract": "IO"},
    
    # A50期货（新交所）
    {"date": "2025-01-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-02-27", "type": "A50期货", "contract": "CN"},
    {"date": "2025-03-28", "type": "A50期货", "contract": "CN"},
    {"date": "2025-04-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-05-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-06-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-07-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-08-29", "type": "A50期货", "contract": "CN"},
    {"date": "2025-09-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-10-30", "type": "A50期货", "contract": "CN"},
    {"date": "2025-11-28", "type": "A50期货", "contract": "CN"},
    {"date": "2025-12-30", "type": "A50期货", "contract": "CN"},
    
    # 国债期货（中金所）
    {"date": "2025-01-10", "type": "国债期货", "contract": "T/TF/TS"},
    {"date": "2025-03-14", "type": "国债期货", "contract": "T/TF/TS"},
    {"date": "2025-06-13", "type": "国债期货", "contract": "T/TF/TS"},
    {"date": "2025-09-12", "type": "国债期货", "contract": "T/TF/TS"},
    {"date": "2025-12-12", "type": "国债期货", "contract": "T/TF/TS"}
]

HOLIDAYS = [
    # 2025年中国法定节假日（含调休）
    {"name": "元旦", "date": "2025-01-01"},
    {"name": "春节", "date": "2025-01-29", "note": "1月28日-2月3日放假"},
    {"name": "清明节", "date": "2025-04-04", "note": "4月4日-6日放假"},
    {"name": "劳动节", "date": "2025-05-01", "note": "5月1日-5日放假"},
    {"name": "端午节", "date": "2025-06-10", "note": "6月10日-12日放假"},
    {"name": "中秋节", "date": "2025-09-17", "note": "9月17日-19日放假"},
    {"name": "国庆节", "date": "2025-10-01", "note": "10月1日-7日放假"},
    
    # 国际主要假期（影响A50交易）
    {"name": "圣诞节", "date": "2025-12-25", "exchange": "新交所"}
]

# ----------------------------- 辅助函数 -----------------------------
def parse_date(date_str: str) -> datetime.date:
    """将日期字符串转换为datetime对象"""
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def get_weekday_cn(date: datetime.date) -> str:
    """获取中文星期几"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[date.weekday()]

def get_nearest_holiday(target_date: datetime.date) -> Dict:
    """获取最近的下一个节假日（含详细信息）"""
    nearest = None
    for holiday in sorted(HOLIDAYS, key=lambda x: parse_date(x["date"])):
        holiday_date = parse_date(holiday["date"])
        if holiday_date >= target_date:
            days_diff = (holiday_date - target_date).days
            return {
                "name": holiday["name"],
                "date": holiday["date"],
                "days_remaining": days_diff,
                "note": holiday.get("note", ""),
                "exchange": holiday.get("exchange", "中国")
            }
    return {
        "name": "2026年元旦",
        "date": "2026-01-01",
        "days_remaining": (parse_date("2026-01-01") - target_date).days,
        "note": "",
        "exchange": "中国"
    }

# ----------------------------- 核心功能 -----------------------------
def get_upcoming_deliveries(count: int = 2) -> List[Dict[str, str]]:
    """获取接下来最近的几个交割日（按时间顺序）"""
    today = datetime.now().date()
    upcoming = []
    
    for delivery in DELIVERY_DATES:
        delivery_date = parse_date(delivery["date"])
        if delivery_date >= today:
            days_remaining = (delivery_date - today).days
            holiday_info = get_nearest_holiday(delivery_date)
            
            upcoming.append({
                **delivery,
                "date_str": delivery["date"],
                "weekday": get_weekday_cn(delivery_date),
                "days_remaining": days_remaining,
                "holiday_info": holiday_info
            })
    
    # 按日期升序排序并截取
    upcoming.sort(key=lambda x: parse_date(x["date_str"]))
    return upcoming[:count]

def generate_message(deliveries: List[Dict[str, str]]) -> str:
    """生成指定格式的提醒消息"""
    today = datetime.now()
    current_date = today.strftime('%Y-%m-%d')
    current_weekday = get_weekday_cn(today.date())
    
    # 获取全局最近节假日
    nearest_holiday = get_nearest_holiday(today.date())
    
    # 构建消息内容
    message = [
        "📅 交割日提醒",
        f"🗓️ 当前日期: {current_date}｜{current_weekday}",
        ""
    ]
    
    for idx, delivery in enumerate(deliveries, 1):
        # 判断倒计时状态
        if delivery["days_remaining"] == 0:
            countdown = "0天 ⏰ 今日到期"
        elif delivery["days_remaining"] <= 3:
            countdown = f"{delivery['days_remaining']}天 🔴 紧急"
        elif delivery["days_remaining"] <= 7:
            countdown = f"{delivery['days_remaining']}天 ⚠️ 临近"
        else:
            countdown = f"{delivery['days_remaining']}天 🟢 远期"
        
        # 节假日信息
        holiday = delivery["holiday_info"]
        holiday_text = f"{holiday['name']}（{holiday['days_remaining']}天后）"
        if holiday["exchange"] != "中国":
            holiday_text += f"｜{holiday['exchange']}"
        
        message.extend([
            f"🔹 第{idx}个交割日",
            f"日期：{delivery['date_str']}｜{delivery['weekday']}",
            f"类型：{delivery['type']}｜{delivery['contract']}",
            f"倒计时：{countdown}",
            f"最近节假日：{holiday_text}",
            ""
        ])
    
    # 添加全局节假日信息
    message.extend([
        "🎯 全局最近法定节假日",
        f"名称：{nearest_holiday['name']}",
        f"日期：{nearest_holiday['date']}",
        f"倒计时：{nearest_holiday['days_remaining']}天",
        f"备注：{nearest_holiday['note']}" if nearest_holiday["note"] else ""
    ])
    
    return "\n".join(message)

def send_serverchan_message(content: str) -> bool:
    """通过Server酱发送微信通知"""
    sckey = os.getenv("SERVERCHAN_SCKEY")
    if not sckey:
        raise ValueError("未设置SERVERCHAN_SCKEY环境变量")
    
    url = f"https://sc.ftqq.com/{sckey}.send"
    payload = {
        "text": "📅 交割日提醒通知",
        "desp": content.replace("\n", "\n\n")  # Server酱需要双换行
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

# ----------------------------- 主程序 -----------------------------
def main():
    print("开始执行交割日检查...")
    
    try:
        # 获取最近2个交割日
        deliveries = get_upcoming_deliveries(2)
        
        # 生成提醒消息
        message = generate_message(deliveries)
        print("\n" + message + "\n")
        
        # 发送通知
        if send_serverchan_message(message):
            print("通知推送成功")
        else:
            print("通知推送失败")
            
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()