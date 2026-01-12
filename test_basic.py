"""
简化版测试脚本
测试基本的网页获取和监控功能，包括图像截取和识别
"""

import configparser
import time
import requests
from bs4 import BeautifulSoup

import io
from PIL import Image
# 导入Pyppeteer
from pyppeteer import launch
import asyncio

class BasicMonitor:
    def __init__(self, config_file='secret.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self.alert_keywords = ['告警', '错误', '严重', '警告', 'error', 'warning', 'critical', 'alert']
        print("初始化基本监控器...")
        print(f"读取配置文件: {config_file}")
        print(f"告警关键词: {self.alert_keywords}")
    
    async def capture_screenshot_pyppeteer(self, url):
        """使用Pyppeteer获取网页截图（异步方法）"""
        try:
            # 启动Pyppeteer浏览器
            browser = await launch(
                headless=True,
                args=[
                    '--window-size=1920,1080',
                    '--ignore-certificate-errors',
                    '--allow-running-insecure-content',
                    '--disable-extensions',
                    '--disable-popup-blocking',
                    '--disable-default-apps',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-timeouts-for-profiling'
                ],
                executablePath=r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # 手动指定Chrome路径
            )
            
            # 创建新页面
            page = await browser.newPage()
            
            # 设置视图大小
            await page.setViewport({'width': 1920, 'height': 1080})
            
            # 导航到URL（使用更宽松的等待条件）
            await page.goto(url, {'waitUntil': 'load', 'timeout': 60000})
            
            # 等待页面加载完成
            await asyncio.sleep(5)
            
            # 截取整个页面的截图
            screenshot = await page.screenshot({'fullPage': True, 'type': 'png'})
            
            # 关闭浏览器
            await browser.close()
            
            return screenshot
        except Exception as e:
            print(f"Pyppeteer截图出错: {e}")
            # 确保浏览器关闭
            try:
                await browser.close()
            except:
                pass
            raise
    
    def capture_screenshot(self, url):
        """直接使用Pyppeteer获取网页截图"""
        try:
            print("使用Pyppeteer获取网页截图...")
            # 运行异步函数
            screenshot = asyncio.run(self.capture_screenshot_pyppeteer(url))
            print("Pyppeteer截图成功，保存为temp_screenshot.png")
            # 保存截图为文件
            image = Image.open(io.BytesIO(screenshot))
            image.save('temp_screenshot.png')
            return screenshot
        except Exception as e:
            print(f"Pyppeteer截图失败: {e}")
            raise
    
    def get_webpage(self, url):
        """获取网页内容，判断是简单网页还是复杂网页"""
        try:
            print(f"\n获取网页: {url}")
            # 尝试用requests获取
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            # 检查是否是静态内容
            soup = BeautifulSoup(response.text, 'html.parser')
            static_content = soup.get_text(separator='\n', strip=True)
            
            # 判断是否为简单网页（字符数小于10000，且没有大量脚本）
            script_tags = soup.find_all('script')
            script_count = len(script_tags)
            
            print(f"网页字符数: {len(static_content)}")
            print(f"脚本标签数: {script_count}")
            
            # 强制使用截图分析来测试截图功能
            print("强制使用截图分析来测试截图功能")
            # 尝试实际截图
            try:
                print("尝试使用Pyppeteer获取网页截图...")
                screenshot = self.capture_screenshot(url)
                print("截图成功，使用图像分析")
                return 'image', screenshot
            except Exception as e:
                print(f"截图失败，降级到文本分析: {e}")
                return 'text', static_content
        except Exception as e:
            print(f"获取网页失败: {e}")
            return 'error', str(e)
    
    def analyze_content(self, content_type, content):
        """分析网页内容"""
        if content_type == 'text':
            print("分析文本内容...")
            # 简单的关键词检查
            has_alert = any(keyword in content.lower() for keyword in self.alert_keywords)
            if has_alert:
                return "【分析结果】发现告警信息！\n\n此为模拟分析结果，实际使用时将调用AI模型进行详细分析。"
            else:
                # 检查是否有数据加载失败的情况
                if "暂无数据" in content or "数据加载中" in content or "- - - -" in content:
                    return "【分析结果】发现数据异常！\n\n页面显示数据加载失败或无数据，可能是服务端问题或非交易时间。\n\n此为模拟分析结果，实际使用时将调用AI模型进行详细分析。"
                else:
                    return "【分析结果】未发现告警信息。\n\n此为模拟分析结果，实际使用时将调用AI模型进行详细分析。"
        elif content_type == 'image':
            print("分析网页截图...")
            print("图像数据大小: {:.2f} KB".format(len(content) / 1024))
            print("截图已保存为: temp_screenshot.png")
            print("在实际使用中，系统将调用Qwen视觉模型进行详细分析")
            return "【分析结果】未发现告警信息。\n\n此为模拟分析结果，实际使用时将调用AI模型进行详细分析。"
        else:
            return f"【分析结果】获取网页失败: {content}"
    
    def check_website(self, url):
        """检查单个网站"""
        print(f"\n开始检查网站: {url}")
        content_type, content = self.get_webpage(url)
        result = self.analyze_content(content_type, content)
        print("\n分析结果:")
        print(result)
        print("-" * 80)
    
    def start_monitoring(self, urls, interval=60):
        """开始监控任务"""
        print(f"启动网站监控，每{interval}秒检查一次")
        print(f"监控网站列表: {urls}")
        print("-" * 80)
        
        # 立即执行一次检查
        for url in urls:
            self.check_website(url)
        
        # 模拟定时任务（只执行一次）
        print(f"\n模拟定时任务: 将在{interval}秒后再次检查（实际使用时会持续运行）")
        time.sleep(2)  # 只等待2秒，模拟定时任务
        print("定时任务模拟完成")

if __name__ == "__main__":
    # 示例用法
    monitor = BasicMonitor()
    
    # 要监控的网站列表
    monitor_urls = [
        "https://quote.eastmoney.com/",  # 东方财富网，用于测试
    ]
    
    # 启动监控
    monitor.start_monitoring(monitor_urls, interval=60)