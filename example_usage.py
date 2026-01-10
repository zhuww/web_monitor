"""
AI Agent使用示例
=================
此文件展示了如何使用WebMonitorAgent进行网站监控
"""

from ai_agent import WebMonitorAgent

def main():
    # 初始化AI Agent
    agent = WebMonitorAgent()
    
    # 配置要监控的网站列表
    # 替换为您需要监控的实际网站
    monitor_urls = [
        "https://quote.eastmoney.com/ZS000001.html",  # 示例网站
        # 添加更多需要监控的网站
        # 例如: "http://your-monitoring-system.com/dashboard",
        #       "http://your-api-service.com/status",
    ]
    
    # 配置监控间隔（秒）
    monitor_interval = 60  # 每60秒检查一次
    
    # 启动监控
    print("正在启动AI监控Agent...")
    print(f"监控网站: {monitor_urls}")
    print(f"监控间隔: {monitor_interval}秒")
    print("按 Ctrl+C 停止监控\n")
    
    try:
        agent.start_monitoring(monitor_urls, interval=monitor_interval)
    except KeyboardInterrupt:
        print("\n监控已手动停止")

if __name__ == "__main__":
    main()