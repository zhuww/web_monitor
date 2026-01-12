import configparser
import time
import schedule
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import os
# 导入Pyppeteer
from pyppeteer import launch
import asyncio

class WebMonitorAgent:
    def __init__(self, config_file='secret.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self.alert_keywords = ['告警', '错误', '严重', '警告', 'error', 'warning', 'critical', 'alert']
        self.setup_clients()
    
    def setup_clients(self):
        """设置AI模型客户端"""
        try:
            print("正在设置AI模型客户端...")
            print(f"Silicon Flow API Key: {self.config.get('silicon-flow', 'API_KEY')[:10]}...")
            print(f"Silicon Flow Base URL: {self.config.get('silicon-flow', 'BASE_URL')}")
            print(f"推理模型: {self.config.get('silicon-flow', 'REASONING_MODEL')}")
            print(f"视觉模型: {self.config.get('silicon-flow', 'VISUAL_MODEL')}")
            
            # 尝试导入OpenAI
            try:
                from openai import OpenAI
                import httpx
                
                # 创建HTTP客户端
                http_client = httpx.Client(
                    timeout=30.0,
                    follow_redirects=True,
                    verify=False,  # 禁用SSL证书验证
                )
                
                # 处理API密钥和URL
                silicon_flow_api_key = self.config.get('silicon-flow', 'API_KEY').strip('"')
                silicon_flow_base_url = self.config.get('silicon-flow', 'BASE_URL').strip('"')
                
                print(f"处理后的Silicon Flow API Key: {silicon_flow_api_key[:20]}...")
                print(f"处理后的Base URL: {silicon_flow_base_url}")
                
                # 设置Silicon Flow客户端（同时用于文本和图像分析）
                self.silicon_flow_client = OpenAI(
                    api_key=silicon_flow_api_key,
                    base_url=silicon_flow_base_url,
                    http_client=http_client
                )
                print("Silicon Flow客户端设置完成")
            except Exception as e:
                print(f"初始化OpenAI客户端失败: {e}")
                print("将使用模拟分析结果")
                self.silicon_flow_client = None
        except Exception as e:
            print(f"设置AI模型客户端时出错: {e}")
            self.silicon_flow_client = None
    
    def get_webpage(self, url):
        """获取网页内容，判断是简单网页还是复杂网页"""
        try:
            # 先尝试用requests获取
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            # 检查是否是静态内容
            soup = BeautifulSoup(response.text, 'html.parser')
            static_content = soup.get_text(separator='\n', strip=True)
            
            # 判断是否为简单网页（字符数小于10000，且没有大量脚本）
            script_tags = soup.find_all('script')
            script_count = len(script_tags)
            
            if len(static_content) < 10000 and script_count < 10:
                return 'text', static_content
            else:
                # 复杂网页，尝试使用Pyppeteer截图
                try:
                    print("尝试使用Pyppeteer获取网页截图...")
                    screenshot = self.capture_screenshot(url)
                    return 'image', screenshot
                except Exception as e:
                    print(f"截图失败，降级到文本分析: {e}")
                    # 截图失败，降级到文本分析
                    return 'text', static_content
        except Exception as e:
            print(f"获取网页失败: {e}")
            return 'error', str(e)
    
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
                    '--disable-gpu'
                ],
                executablePath=r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # 手动指定Chrome路径
            )
            
            # 创建新页面
            page = await browser.newPage()
            
            # 设置视图大小
            await page.setViewport({'width': 1920, 'height': 1080})
            
            # 导航到URL（忽略SSL错误）
            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 30000})
            
            # 等待页面加载完成 - 使用sleep代替waitForTimeout
            await asyncio.sleep(3)
            
            # 截取整个页面的截图
            screenshot = await page.screenshot({'fullPage': True, 'type': 'png'})
            
            # 关闭浏览器
            await browser.close()
            
            return screenshot
        except Exception as e:
            print(f"Pyppeteer截图出错: {e}")
            raise
    
    def capture_screenshot(self, url):
        """直接使用Pyppeteer获取网页截图"""
        try:
            print("使用Pyppeteer获取网页截图...")
            # 运行异步函数
            screenshot = asyncio.run(self.capture_screenshot_pyppeteer(url))
            return screenshot
        except Exception as e:
            print(f"Pyppeteer截图失败: {e}")
            raise
    
    def analyze_text(self, text):
        """使用Silicon Flow推理模型分析文本内容"""
        try:
            if not self.silicon_flow_client:
                # AI模型未初始化，返回模拟结果
                return "【模拟分析结果】\n页面正常，未发现告警信息。\n\n此为模拟结果，实际使用时将调用AI模型进行分析。"
            
            prompt = f"""请分析以下网页内容，重点关注是否存在告警、错误等异常信息。
如果发现异常，请生成详细的告警报告，包括：
1. 告警级别（严重/警告/信息）
2. 告警内容
3. 可能的原因
4. 建议的处理措施

如果没有发现异常，请说明页面正常。

网页内容：
{text[:3000]}  # 限制文本长度
"""
            
            # 获取模型名称和温度参数
            model_name = self.config.get('silicon-flow', 'REASONING_MODEL').strip('"')
            temperature = float(self.config.get('silicon-flow', 'temperature', fallback='0.7'))
            print(f"正在使用Silicon Flow模型: {model_name}")
            print(f"温度参数: {temperature}")
            
            response = self.silicon_flow_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的系统监控分析助手，善于从文本中识别告警信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"分析文本时出错: {e}\n\n此为错误信息，实际使用时将调用AI模型进行分析。"
    
    def analyze_image(self, image_data):
        """使用Silicon Flow视觉模型分析截图"""
        try:
            if not self.silicon_flow_client:
                # AI模型未初始化，返回模拟结果
                return "【模拟分析结果】\n页面正常，未发现告警信息。\n\n此为模拟结果，实际使用时将调用AI模型进行分析。"
            
            image = Image.open(io.BytesIO(image_data))
            
            # 保存为临时文件
            temp_path = 'temp_screenshot.png'
            image.save(temp_path)
            
            # 获取模型名称和温度参数
            model_name = self.config.get('silicon-flow', 'VISUAL_MODEL').strip('"')
            temperature = float(self.config.get('silicon-flow', 'temperature', fallback='0.7'))
            print(f"正在使用Silicon Flow视觉模型: {model_name}")
            print(f"温度参数: {temperature}")
            
            with open(temp_path, 'rb') as f:
                response = self.silicon_flow_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "你是一个专业的系统监控分析助手，善于从截图中识别告警信息。"},
                        {"role": "user", "content": [
                            {"type": "text", "text": "请分析以下网页截图，重点关注是否存在告警、错误等异常信息。如果发现异常，请生成详细的告警报告，包括：1. 告警级别（严重/警告/信息）2. 告警内容 3. 可能的原因 4. 建议的处理措施。如果没有发现异常，请说明页面正常。"},
                            {"type": "image", "image": f}
                        ]}
                    ],
                    temperature=temperature
                )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"分析图像时出错: {e}\n\n此为错误信息，实际使用时将调用AI模型进行分析。"
    
    def check_website(self, url):
        """检查单个网站"""
        print(f"\n开始检查网站: {url}")
        content_type, content = self.get_webpage(url)
        
        if content_type == 'error':
            print(f"获取网页失败: {content}")
            return
        
        # 根据内容类型选择分析方法
        if content_type == 'text':
            print("使用文本分析...")
            result = self.analyze_text(content)
        else:
            print("使用图像分析...")
            result = self.analyze_image(content)
        
        print("\n分析结果:")
        print(result)
        print("-" * 80)
    
    def start_monitoring(self, urls, interval=60):
        """开始监控任务"""
        print(f"启动网站监控，每{interval}秒检查一次")
        print(f"监控网站列表: {urls}")
        print(f"告警关键词: {self.alert_keywords}")
        print("-" * 80)
        
        # 立即执行一次检查
        for url in urls:
            self.check_website(url)
        
        # 设置定时任务
        def job():
            for url in urls:
                self.check_website(url)
        
        schedule.every(interval).seconds.do(job)
        
        # 运行调度器
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    # 示例用法
    agent = WebMonitorAgent()
    
    # 要监控的网站列表 - 使用一个简单的网站进行测试
    monitor_urls = [
        "http://example.com",  # 示例网站，实际使用时替换为需要监控的网站
        # 添加更多需要监控的网站
    ]
    
    # 启动监控，每60秒检查一次
    print("\n" + "="*80)
    print("AI监控Agent测试 - 截图功能")
    print("="*80)
    print(f"测试网站: {monitor_urls}")
    print("="*80)
    
    try:
        # 单独测试截图功能
        print("\n开始测试截图功能...")
        for url in monitor_urls:
            print(f"\n测试网站: {url}")
            screenshot = agent.capture_screenshot(url)
            print(f"截图成功，大小: {len(screenshot)} 字节")
            
            # 保存截图到文件（可选）
            screenshot_path = "test_screenshot.png"
            with open(screenshot_path, "wb") as f:
                f.write(screenshot)
            print(f"截图已保存到: {screenshot_path}")
        
        print("\n截图功能测试完成！")
    except Exception as e:
        print(f"测试时出错: {e}")