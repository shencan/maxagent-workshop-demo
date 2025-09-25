#!/usr/bin/env python3
"""
天气查询 MCP 服务器
使用 fastmcp 库实现
"""

import os
import base64
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

# 加载 .env 文件
load_dotenv()

# 创建 FastMCP 应用
mcp = FastMCP("Weather Service")

# 天气 API 配置
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# 添加调试信息
print(f"API Key loaded: {'Yes' if WEATHER_API_KEY else 'No'}")
print(f"API Key length: {len(WEATHER_API_KEY) if WEATHER_API_KEY else 0}")

@mcp.tool()
async def get_current_weather(
    city: str = "beijing",
    country: Optional[str] = "CN",
    units: str = "metric"
) -> Dict[str, Any]:
    """
    获取指定城市的当前天气信息
    
    Args:
        city: 城市名称 (例如: "beijing", "shanghai", "New York")
        country: 国家代码 (可选，例如: "CN", "US") 
        units: 温度单位 ("metric"=摄氏度, "imperial"=华氏度)
    
    Returns:
        当前天气信息
    """
    if not WEATHER_API_KEY:
        return {"错误": "请设置环境变量 WEATHER_API_KEY"}
    
    try:
      
        # 获取 HTTP headers
        headers = get_http_headers()
      
        # 读取 userinfo header 值
        userinfo = headers.get("userinfo")
        if userinfo:
          userinfo = base64.urlsafe_b64decode(userinfo).decode("utf-8")

          # 输出userinfo
          print(f"********************* User info *****************: {userinfo}")
        else: 
          print(f"********************* None User info *****************")
      
        # 构建查询参数
        location = city
        if country:
            location = f"{city},{country}"
        
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": units,
            "lang": "zh_cn"  # 中文描述
        }
        
        # 发送 API 请求
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{WEATHER_BASE_URL}/weather", params=params)
            response.raise_for_status()
            
        data = response.json()
        
        # 格式化天气信息
        weather_info = {
            "城市": data["name"],
            "国家": data["sys"]["country"],
            "天气状况": data["weather"][0]["description"],
            "当前温度": f"{data['main']['temp']}°{'C' if units == 'metric' else 'F'}",
            "体感温度": f"{data['main']['feels_like']}°{'C' if units == 'metric' else 'F'}",
            "最低温度": f"{data['main']['temp_min']}°{'C' if units == 'metric' else 'F'}",
            "最高温度": f"{data['main']['temp_max']}°{'C' if units == 'metric' else 'F'}",
            "湿度": f"{data['main']['humidity']}%",
            "气压": f"{data['main']['pressure']} hPa",
            "风速": f"{data['wind']['speed']} {'m/s' if units == 'metric' else 'mph'}",
            "云量": f"{data['clouds']['all']}%"
        }
        
        return weather_info
        
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 404:
            return {"错误": f"未找到城市: {city}"}
        elif e.response.status_code == 401:
            return {"错误": "API密钥无效，请检查 WEATHER_API_KEY 环境变量"}
        else:
            return {"错误": f"API请求失败: {e.response.status_code}"}
    except Exception as e:
        return {"错误": f"获取天气信息失败: {str(e)}"}

def main():
    """运行 MCP 服务器"""
    mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True)

if __name__ == "__main__":
    main()
