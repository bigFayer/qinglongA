import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ----------------------------- 数据配置 -----------------------------
DELIVERY_DATES = [
    {"date": "2025-01-17", "type": "股指期货", "contract": "IF/IH/IC", "notice": "最后交易日为交割日前一交易日"},
    {"date": "2025-01-22", "type": "期权", "contract": "IO", "notice": "最后交易日为交割日当天"},
    {"date": "2025-02-21", "type": "股指期货", "contract": "IF/IH/IC", "notice": "最后交易日为交割日前一交易日"},
    {"date": "2025-02-26", "type": "期权", "contract": "IO", "notice": "最后交易日为交割日当天"},
    {"date": "2025-02-27", "type": "A50期货", "contract": "CN", "notice": "最后交易日为交割日前一交易日"},
    # 其他日期数据保持相同格式...
]

# ----------------------------- 函数定义 -----------------------------
def parse_date(date_str: str) -> datetime.date:
    """将日期字符串转换为datetime对象"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"日期格式错误: {date_str}, 应为YYYY-MM-DD格式") from e

def get_weekday_cn(date: datetime.date) -> str:
    """获取中文星期几"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[date.weekday()]

def check_delivery_days(days_ahead: int = 2) -> Optional[Dict[str, str]]:
    """检查距离当前日期指定天数的交割日"""
    today = datetime.now().date()
    target_date = today + timedelta(days=days_ahead)
    
    for delivery in DELIVERY_DATES:
        try:
            delivery_date = parse_date(delivery["date"])
            if delivery_date == target_date:
                # 计算距离交割日的天数
                days_remaining = (delivery_date - today).days
                delivery.update({
                    "days_remaining": days_remaining,
                    "weekday": get_weekday_cn(delivery_date)
                })
                return delivery
        except ValueError as e:
            print(f"警告: 跳过无效的交割日数据: {delivery}, 错误: {e}")
            continue
            
    return None

def generate_message_content(delivery: Dict[str, str]) -> str:
    """生成详细的消息内容"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_weekday = get_weekday_cn(datetime.now().date())
    
    # 构建Markdown格式的消息
    content = f"""
## 🚨 交割日提醒通知 🚨

**📅 当前日期**: {current_date} ({current_weekday})

### 📌 交割日详情
- **交割类型**: {delivery['type']}
- **合约代码**: {delivery.get('contract', '未指定')}
- **交割日期**: {delivery['date']} ({delivery['weekday']})
- **距离交割日**: 还有 {delivery['days_remaining']} 天

### ⚠️ 注意事项
{delivery.get('notice', '请关注交易所公告')}

### 📋 操作建议
1. 检查持仓合约的到期情况
2. 提前做好移仓或平仓准备
3. 关注保证金变化
4. 注意最后交易时间

> 系统自动提醒，请以交易所公告为准
"""
    return content

def send_serverchan_message(delivery: Dict[str, str]) -> bool:
    """通过Server酱发送微信通知"""
    sckey = os.getenv("SERVERCHAN_SCKEY")
    if not sckey:
        raise ValueError("请在环境变量中设置SERVERCHAN_SCKEY!")
    
    title = f"【交割提醒】{delivery['type']} - {delivery['date']} ({delivery['days_remaining']}天后)"
    content = generate_message_content(delivery)
    
    url = f"https://sc.ftqq.com/{sckey}.send"
    payload = {
        "text": title,
        "desp": content
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("errno") == 0:
            print(f"成功发送通知: {delivery['type']} - {delivery['date']}")
            return True
        else:
            print(f"发送失败: {result.get('errmsg', '未知错误')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
        return False

# ----------------------------- 主程序 -----------------------------
def main():
    try:
        print(f"开始检查交割日提醒... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        delivery = check_delivery_days()
        if delivery:
            print(f"发现即将到来的交割日: {delivery}")
            success = send_serverchan_message(delivery)
            if not success:
                print("通知发送失败，请检查配置")
        else:
            print(f"2天内无交割日提醒")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    main()
