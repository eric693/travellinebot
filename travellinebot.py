from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import time
import re
import random

# 讀取環境變數
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'bd376bb55bf19b5866f13f03e4af28ac')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'PW2bcRx2rWbuJlWpA8uMCCthgAL6M1XfsmEj5bUsk1KnDBJwGcYWJh+cD5tVaxTwZyuBZYyjQxPrP+b2Yy99LmRRzsPt+UfgIhyMK244uDqWa02wUM51Y9WRzqxD1L+iVYHLPxaEd8T63rlTp5GwhgdB04t89/1O/w1cDnyilFU=+a/FFA+r6n8zeZQFkcFy1uq1qHt/GDVGLHmkClduiOgqksEdUyA7CWST4E+BergVk1A6pTjMZwdB04t89/1O/w1cDnyilFU=')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# 你的 Group ID
GROUP_ID = os.getenv('GROUP_ID', 'Uacca1f2cd08b2f6fcb81626633866a04')

# 歡迎訊息防重複控制
last_welcome_time = 0
WELCOME_COOLDOWN = 3  # 秒

# 完整行程資訊字典（包含所有行程和智能推薦標籤）
ITINERARY_INFO = {
    'C1': {
        'name': '資生堂跳島一日遊',
        'type': '跳島',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [2500, 4300],
        'tags': ['跳島', '資生堂', '香蕉船', '拖傘', '一日遊', '海島', '水上活動', '初次遊客', '經典'],
        'highlights': ['資生堂島', '香蕉船', '拖傘', '帶魚共遊'],
        'best_for': ['初次遊客', '水上活動愛好者', '想體驗經典跳島'],
        'departure': '8:00am',
        'content': """🏝️ 【C1】資生堂跳島一日遊

📍 行程景點：
• 聖文森特跳島體驗帶魚共遊
• 資生堂島上島
• 白貝項目
• 香蕉船 500披索/位、拖傘 2,500披索/位

🍽️ 包含餐點：早餐、午餐、點心、晚酒
⏰ 出發時間：8:00am
🏨 飯店：住宿安排
✨ 優點：經典跳島體驗，適合初次遊客
💰 費用：
• 4-5人｜4,300披索/人
• 6-7人｜3,200披索/人  
• 8-9人｜2,700披索/人
• 10-13人｜2,500披索/人"""
    },
    
    'B1': {
        'name': '薄荷一日遊',
        'type': '自然景觀',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [4200, 5600],
        'tags': ['薄荷島', '巧克力山', '眼鏡猴', '人造林', '遊河', '空中飛人', '越野車', '一日遊', '陸地遊'],
        'highlights': ['巧克力山', '眼鏡猴', '空中飛人', '越野車'],
        'best_for': ['喜歡自然景觀', '想看可愛動物', '喜歡陸地活動'],
        'departure': '06:00am',
        'content': """🌊 【B1】薄荷一日遊

📍 行程景點：
• 薄荷島陸地遊（專門在薄荷島）
• 巧克力山、眼鏡猴、人造林、遊河船餐
• 空中飛人+700/位
• 榛國越野車+1400php/位（一小時）

🍽️ 包含餐點：午餐
⏰ 出發時間：06:00am
✨ 優點：薄荷島深度體驗
💰 費用：
• 4-5人｜5600披索/人
• 6-7人｜4900披索/人
• 8-9人｜4500披索/人
• 10-13人｜4,200披索/人"""
    },
    
    'S8': {
        'name': '墨寶一日遊',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [2200, 4500],
        'tags': ['墨寶', '沙丁魚', '浮潛', '海灘', '一日遊', '海洋', '潛水'],
        'highlights': ['沙丁魚風暴', '墨寶白沙灘', '浮潛'],
        'best_for': ['想看沙丁魚', '喜歡浮潛', '預算友好'],
        'departure': '06:00am',
        'content': """🏖️ 【S8】墨寶一日遊

📍 行程景點：
• 墨寶沙丁魚風暴、墨寶 White Beach

🍽️ 包含餐點：早餐、午餐
⏰ 出發時間：06:00am
✨ 優點：欣賞壯觀沙丁魚群
💰 費用：
• 4-5人｜4,500披索/人
• 6-7人｜3,300披索/人
• 8-9人｜2,600披索/人
• 10-13人｜2,200披索/人"""
    },
    
    'S2': {
        'name': '朔溪一日遊',
        'type': '冒險活動',
        'duration': 1,
        'difficulty': '刺激',
        'price_range': [3800, 5800],
        'tags': ['朔溪', '嘉華山', 'kawasan', 'alegria', '冒險', '刺激', '一日遊', '瀑布', '跳水'],
        'highlights': ['全程朔溪', '瀑布跳水', '刺激冒險'],
        'best_for': ['喜歡刺激冒險', '體力充沛', '想挑戰自己'],
        'departure': '06:00am',
        'content': """🏊‍♀️ 【S2】朔溪一日遊

📍 行程景點：
• 嘉華山Kawasan 全程朔溪（4-5小時）
• Or Alegria 全程朔溪（4-5小時）

🍽️ 包含餐點：早餐、午餐
⏰ 出發時間：06:00am
✨ 優點：刺激冒險體驗
💰 費用：
• 4-5人｜5,800披索/人
• 6-7人｜4,600披索/人
• 8-9人｜4,100披索/人
• 10-13人｜3,800披索/人"""
    },
    
    'S3': {
        'name': '墨寶&朔溪一日遊',
        'type': '組合活動',
        'duration': 1,
        'difficulty': '中等',
        'price_range': [4600, 6600],
        'tags': ['墨寶', '朔溪', '沙丁魚', '冒險', '一日遊', '海洋', '瀑布', '組合'],
        'highlights': ['沙丁魚風暴', 'Kawasan朔溪', '海洋瀑布雙體驗'],
        'best_for': ['想要多重體驗', '時間有限', '喜歡豐富行程'],
        'departure': '06:00am',
        'content': """🌅 【S3】墨寶&朔溪一日遊

📍 行程景點：
• 墨寶沙丁魚風暴、墨寶White Beach
• Kawasan 朔溪

🍽️ 包含餐點：早餐、午餐、晚餐
⏰ 出發時間：06:00am
✨ 優點：結合海洋與溪流體驗
💰 費用：
• 4-5人｜6,600披索/人
• 6-7人｜5,500披索/人
• 8-9人｜4,900披索/人
• 10-13人｜4,600披索/人"""
    },
    
    'C2': {
        'name': '市區一日遊',
        'type': '文化歷史',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [1600, 3400],
        'tags': ['市區', '文化', '歷史', '教堂', '輕鬆', '一日遊', '夜景', '便宜'],
        'highlights': ['聖嬰教堂', '麥哲倫十字架', 'Tops夜景'],
        'best_for': ['喜歡文化歷史', '預算有限', '想看夜景'],
        'departure': '13:00pm',
        'content': """🏛️ 【C2】市區一日遊

📍 行程景點：
• 聖嬰教堂、麥哲倫十字架、聖佩特羅堡
• 莉雅神廟、希雅花園
• 晚餐可預定Tops夜景餐廳

🍽️ 包含餐點：不含餐
⏰ 出發時間：13:00pm
✨ 優點：文化歷史深度遊
💰 費用：
• 4-5人｜3,400披索/人
• 6-7人｜2,300披索/人
• 8-9人｜1,900披索/人
• 10-13人｜1,600披索/人"""
    },
    
    'N1': {
        'name': '善妮島一日遊',
        'type': '小島探險',
        'duration': 1,
        'difficulty': '中等',
        'price_range': [3500, 5600],
        'tags': ['善妮島', '石洞', '獨木舟', '懸崖跳水', '自然', '一日遊', '小島'],
        'highlights': ['鑽洞石洞', '獨木舟遊湖', '懸崖跳水'],
        'best_for': ['喜歡探險', '想體驗獨木舟', '不怕跳水'],
        'departure': '06:00am',
        'content': """🌺 【N1】善妮島一日遊

📍 行程景點：
• 鑽洞石洞、獨木舟遊湖、懸崖跳水

🍽️ 包含餐點：早餐、午餐
⏰ 出發時間：06:00am
✨ 優點：原始自然風光
💰 費用：
• 4-5人｜5,600披索/人
• 6-7人｜4,500披索/人
• 8-9人｜3,900披索/人
• 10-13人｜3,500披索/人"""
    },
    
    'S1': {
        'name': '宿霧鯨鯊兩日遊',
        'type': '海洋生物',
        'duration': 2,
        'difficulty': '中等',
        'price_range': [7750, 10050],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '墨寶', '朔溪', '兩日遊', '熱門', '刺激', '浮潛', '滑索'],
        'highlights': ['鯨鯊共游', '沙丁魚風暴', '全程朔溪', '高空滑索'],
        'best_for': ['想看鯨鯊', '喜歡刺激冒險', '時間充裕'],
        'departure': '6:00AM',
        'content': """🌊 【S1】宿霧鯨鯊兩日遊行程

📍 行程景點/活動：
• 歐斯陸鯨鯊浮潛 Oslob
• 墨寶沙丁魚浮潛 Moalboal
• 嘉華山全程朔溪 Kawasan（4-5小時）
• 嘉華山高空滑索 +600 php

🍽️ 包含餐點：兩日早餐、兩日午餐、首日晚餐
⏰ 第一天行程出發時間：6:00AM
🏨 飯店：Babylon Guest House Oslob New Village Luna Guest House (住歐斯陸)
✨ 優點：行程最刺激、熱門首選、首日出發時間較晚
💰 費用：
• 4-5人｜10,050披索/人
• 6-7人｜8,750披索/人
• 8-9人｜8,050披索/人
• 10-13人｜7,750披索/人"""
    },
    
    'S1A': {
        'name': '宿霧鯨鯊兩日遊（半程朔溪）',
        'type': '海洋生物',
        'duration': 2,
        'difficulty': '輕鬆',
        'price_range': [6600, 9300],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '墨寶', '朔溪', '兩日遊', '輕鬆', 'alegria', '半程'],
        'highlights': ['鯨鯊共游', '沙丁魚浮潛', '半程朔溪'],
        'best_for': ['想看鯨鯊但不要太累', '時間充裕', '初次朔溪'],
        'departure': '6:00AM',
        'content': """🐋 【S1A】宿霧鯨鯊兩日遊行程

📍 行程景點/活動：
• 歐斯陸鯨鯊浮潛 Oslob
• 墨寶沙丁魚浮潛 Moalboal
• Alegria半程朔溪（半程2小時）

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：6:00AM
🏨 飯店：Babylon Guest House Oslob New Village Luna Guest House (住歐斯陸)
✨ 優點：Alegria半程朔溪比較不累、首日出發時間較晚
💰 費用：
• 4-5人｜9,300披索/人
• 6-7人｜7,600披索/人
• 8-9人｜6,900披索/人
• 10-13人｜6,600披索/人"""
    },
    
    'SS1B': {
        'name': '宿霧鯨鯊兩日遊（SS1B版）',
        'type': '海洋生物',
        'duration': 2,
        'difficulty': '輕鬆',
        'price_range': [6600, 9300],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '墨寶', '朔溪', '兩日遊', '輕鬆', 'alegria'],
        'highlights': ['鯨鯊共游', '沙丁魚浮潛', '半程朔溪'],
        'best_for': ['想看鯨鯊但不要太累', '時間充裕', '初次朔溪'],
        'departure': '6:00AM',
        'content': """🌊 【SS1B】宿霧鯨鯊兩日遊行程

📍 行程景點/活動：
• 歐斯陸鯨鯊浮潛 Oslob
• 墨寶沙丁魚 Moalboal
• Alegria半程朔溪（半程2小時）

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：6:00AM
🏨 飯店：Babylon Guest House Oslob New Village Luna Guest House (住歐斯陸)
✨ 優點：Alegria半程朔溪比較不累
💰 費用：
• 4-5人｜9,300披索/人
• 6-7人｜7,600披索/人
• 8-9人｜6,900披索/人
• 10-13人｜6,600披索/人"""
    },
    
    'S1-1B': {
        'name': '宿霧鯨鯊兩日遊（無朔溪版）',
        'type': '海洋生物',
        'duration': 2,
        'difficulty': '輕鬆',
        'price_range': [6300, 9700],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '墨寶', '蘇米龍島', '瀑布', '兩日遊', '輕鬆', '便宜'],
        'highlights': ['鯨鯊共游', '蘇米龍島', '圖馬洛瀑布', '沙丁魚浮潛'],
        'best_for': ['想看鯨鯊', '不想朔溪', '喜歡輕鬆行程'],
        'departure': '6:00AM',
        'content': """🏝️ 【S1-1B】宿霧鯨鯊兩日遊行程

📍 行程景點/活動：
• 歐斯陸鯨鯊浮潛 Oslob
• 蘇米龍島 Sumilon Island
• 圖馬洛瀑布 Tumalog Falls
• 墨寶沙丁魚浮潛 Moalboal
• 該行程無朔溪

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：6:00AM
🏨 飯店：Babylon Guest House Oslob New Village Luna Guest House (住歐斯陸)
✨ 優點：價格較便宜、行程較輕鬆
💰 費用：
• 4-5人｜9,700披索/人
• 6-7人｜7,800披索/人
• 8-9人｜6,900披索/人
• 10-13人｜6,300披索/人"""
    },
    
    'B2': {
        'name': '薄荷島兩日遊',
        'type': '自然景觀',
        'duration': 2,
        'difficulty': '輕鬆',
        'price_range': [7400, 11350],
        'tags': ['薄荷島', '巧克力山', '眼鏡猴', '巴里卡薩島', '處女島', '兩日遊', '熱門', '空中飛人'],
        'highlights': ['巧克力山', '眼鏡猴', '巴里卡薩島', '處女島'],
        'best_for': ['喜歡自然景觀', '想看薄荷島全貌', '時間充裕'],
        'departure': '6:00am',
        'content': """🏝️ 【B2】薄荷島兩日遊

📍 行程景點：
• 巧克力山、眼鏡猴、遊河船餐
• 巴里卡薩島、處女島
• 空中飛人+700/位（自費）
• 極限越野車+1400php/位（自費）

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：6:00am
🏨 飯店：Bouna Vita Resort Green Mango Resort
✨ 優點：行程熱門首選、兩日玩完薄荷島經典行程
💰 費用：
• 4-5人｜11,350披索/人
• 6-7人｜9,150披索/人
• 8-9人｜8,050披索/人
• 10-13人｜7,400披索/人"""
    },
    
    'N2': {
        'name': '善妮島兩日遊',
        'type': '小島探險',
        'duration': 2,
        'difficulty': '中等',
        'price_range': [6000, 9100],
        'tags': ['善妮島', '純樸', '度假', '小島', '石洞', '獨木舟', '懸崖跳水', '滑索', '兩日遊'],
        'highlights': ['鑽孔石洞', '獨木舟遊湖', '懸崖跳水', '高空滑索'],
        'best_for': ['喜歡純樸小島', '想深度度假', '喜歡冒險活動'],
        'departure': '06:00am',
        'content': """🌺 【N2】善妮島兩日遊

📍 行程景點：
• 鑽孔石洞、獨木舟遊湖、懸崖跳水
• 高空滑索+300php（自費）
• Tulang island +500php（自費）

🍽️ 包含餐點：兩日早餐、兩日午餐、首日晚餐
⏰ 第一天行程出發時間：06:00am
🏨 飯店：Ocean heaven resort
✨ 優點：非常可愛的純樸小島、小編私房度假首選
💰 費用：
• 4-5人｜9,100披索/人
• 6-7人｜7,400披索/人
• 8-9人｜6,500披索/人
• 10-13人｜6,000披索/人"""
    },
    
    'N3': {
        'name': '媽媽島兩日遊',
        'type': '網美景點',
        'duration': 2,
        'difficulty': '中等',
        'price_range': [6800, 12900],
        'tags': ['媽媽島', '沙洲', 'kalaggaman', '網美', '拍照', '白沙', '潛水', '長尾鯊', '兩日遊'],
        'highlights': ['Kalaggaman白沙洲', '絕美沙洲', '潛水看長尾鯊'],
        'best_for': ['想拍網美照', '喜歡純淨沙洲', '有潛水證'],
        'departure': '3:00am',
        'content': """🏖️ 【N3】媽媽島兩日遊

📍 行程景點：
• Kalaggaman 沙洲
• 媽媽島摩托環島
• 媽媽島跳島 +500php/位（自費）

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：3:00am
🏨 飯店：Slam's Garden Dive Resort
✨ 優點：適合想拍網美照的客人、小編心中 No.1 白沙洲 Kalaggaman 絕美微景點、有潛水證想看長尾鯊必選（5,800php 三潛）
💰 費用：
• 4-5人｜12,900披索/人
• 6-7人｜9,300披索/人
• 8-9人｜7,800披索/人
• 10-13人｜6,800披索/人"""
    },
    
    'N4': {
        'name': '班塔岩兩日遊',
        'type': '網美景點',
        'duration': 2,
        'difficulty': '中等',
        'price_range': [6700, 8300],
        'tags': ['班塔岩', '魔女島', '海灘', '潟湖', '跳傘', '風帆', '網美', '拍照', '兩日遊', 'kota beach'],
        'highlights': ['班塔岩魔女島', 'Kota Beach', '潟湖沙灘', '極限跳傘'],
        'best_for': ['想拍網美照', '喜歡美麗海灘', '想體驗跳傘'],
        'departure': '4:00am',
        'content': """🌊 【N4】班塔岩兩日遊

📍 行程景點：
• 班塔岩魔女島跳島
• 絕美級海灘
• 潟湖沙灘 Balidbid Lagoon +450php/位
• 極限跳傘 +24,500php/位（自費）
• 夕陽風帆 + 1300php/位

🍽️ 包含餐點：兩日早餐、兩日午餐
⏰ 第一天行程出發時間：4:00am
🏨 飯店：Teza Resort
✨ 優點：適合想拍網美照的客人、宿霧 No.1 海灘 Kota Beach、想體驗不同角度看宿霧、極限跳傘活動（自費）
💰 費用：
• 6-7人｜8,300披索/人
• 8-9人｜7,500披索/人
• 10-13人｜6,700披索/人"""
    },
    
    'S4': {
        'name': '鯨鯊一日遊',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '中等',
        'price_range': [5400, 7200],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '朔溪', '刺激', '一日遊', '滑索', 'kawasan'],
        'highlights': ['鯨鯊共游', '全程朔溪', '高空滑索'],
        'best_for': ['想看鯨鯊', '喜歡刺激', '時間有限'],
        'departure': '5:30am',
        'content': """🌊 【S4】鯨鯊一日遊行程

📍 行程景點：
• 歐斯陸鯨鯊浮潛 Oslob
• 嘉華山全程朔溪 Kawasan（4-5小時）
• 嘉華山 高空滑索+600 php(前省45分鐘步行)

🍽️ 包含餐點：早餐、午餐
⏰ 行程出發時間：5:30am
✨ 優點：一日精華體驗
💰 費用：
• 4-5人｜7,200披索/人
• 6-7人｜6,200披索/人
• 8-9人｜5,600披索/人
• 10-13人｜5,400披索/人"""
    },
    
    'S4A': {
        'name': '鯨鯊一日遊（輕鬆版）',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [4500, 5800],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '朔溪', '輕鬆', '一日遊', '半程', 'alegria'],
        'highlights': ['鯨鯊共游', '半程朔溪'],
        'best_for': ['想看鯨鯊但不要太累', '時間有限', '初次朔溪'],
        'departure': '5:30am',
        'content': """🐋 【S4A】鯨鯊一日遊行程

📍 行程景點：
• 歐斯陸鯨鯊浮潛 Oslob
• Alegria半程朔溪（半程2小時）

🍽️ 包含餐點：早餐、午餐
⏰ 行程出發時間：5:30am
✨ 優點：較輕鬆的一日遊
💰 費用：
• 4-5人｜5,800披索/人
• 6-7人｜5,200披索/人
• 8-9人｜4,700披索/人
• 10-13人｜4,500披索/人"""
    },
    
    'S5': {
        'name': '鯨鯊+蘇米龍島一日遊',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [3900, 6400],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '蘇米龍島', '教堂', '文化', '一日遊', '海島'],
        'highlights': ['鯨鯊共游', '蘇米龍島浮潛', '喜瑪拉教堂'],
        'best_for': ['想看鯨鯊', '喜歡海島', '對文化感興趣'],
        'departure': '5:30am',
        'content': """🏝️ 【S5】鯨鯊一日遊行程

📍 行程景點：
• 歐斯陸鯨鯊浮潛 Oslob
• 蘇米龍島浮潛 Sumilon Island
• 喜瑪拉教堂 Simala Church

🍽️ 包含餐點：早餐、午餐
⏰ 行程出發時間：5:30am
✨ 優點：結合海島與文化體驗
💰 費用：
• 4-5人｜6,400披索/人
• 6-7人｜4,900披索/人
• 8-9人｜4,200披索/人
• 10-13人｜3,900披索/人"""
    },
    
    'S6': {
        'name': '鯨鯊+瀑布一日遊',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [3400, 5200],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '瀑布', '教堂', '文化', '一日遊', '自然'],
        'highlights': ['鯨鯊共游', '圖馬洛瀑布', '喜瑪拉教堂'],
        'best_for': ['想看鯨鯊', '喜歡瀑布', '對文化感興趣'],
        'departure': '5:30am',
        'content': """💧 【S6】鯨鯊一日遊行程

📍 行程景點：
• 歐斯陸鯨鯊浮潛 Oslob
• 圖馬洛瀑布 Tumalog Falls
• 喜瑪拉教堂 Simala Church

🍽️ 包含餐點：早餐、午餐
⏰ 行程出發時間：5:30am
✨ 優點：瀑布與文化的結合
💰 費用：
• 4-5人｜5,200披索/人
• 6-7人｜4,200披索/人
• 8-9人｜3,500披索/人
• 10-13人｜3,400披索/人"""
    },
    
    'S7': {
        'name': '鯨鯊+墨寶一日遊',
        'type': '海洋生物',
        'duration': 1,
        'difficulty': '輕鬆',
        'price_range': [3900, 6400],
        'tags': ['鯨鯊', '歐斯陸', 'oslob', '墨寶', '沙丁魚', '一日遊', '海洋', '浮潛'],
        'highlights': ['鯨鯊共游', '沙丁魚風暴'],
        'best_for': ['想看鯨鯊', '想看沙丁魚', '喜歡海洋生物'],
        'departure': '5:30am',
        'content': """🌊 【S7】鯨鯊一日遊行程

📍 行程景點：
• 歐斯陸鯨鯊浮潛 Oslob
• 墨寶沙丁魚 Moalboal

🍽️ 包含餐點：早餐、午餐
⏰ 行程出發時間：5:30am
✨ 優點：經典海洋雙體驗
💰 費用：
• 4-5人｜6,400披索/人
• 6-7人｜4,900披索/人
• 8-9人｜4,200披索/人
• 10-13人｜3,900披索/人"""
    }
}

# 需求關鍵字對應（智能推薦系統）
NEED_KEYWORDS = {
    # 活動類型
    '跳島': ['跳島', '島嶼', '資生堂', '香蕉船', '拖傘'],
    '浮潛': ['浮潛', '潛水', '海底', '魚', '珊瑚'],
    '朔溪': ['朔溪', '瀑布', '跳水', '刺激', '冒險', 'kawasan', 'alegria'],
    '鯨鯊': ['鯨鯊', '鯊魚', 'oslob', '歐斯陸'],
    '沙丁魚': ['沙丁魚', '魚群', '墨寶', 'moalboal'],
    
    # 景點類型
    '海灘': ['海灘', '沙灘', '海邊', '海洋', '海水'],
    '小島': ['小島', '島嶼', '跳島', '善妮島', '媽媽島', '薄荷島'],
    '瀑布': ['瀑布', '朔溪', '清水', '游泳'],
    '沙洲': ['沙洲', '白沙', 'kalaggaman', '媽媽島'],
    '山景': ['巧克力山', '山', '高處', '眺望'],
    
    # 體驗偏好
    '刺激': ['刺激', '冒險', '極限', '跳傘', '朔溪', '跳水', '懸崖'],
    '輕鬆': ['輕鬆', '休閒', '度假', '放鬆', '悠閒', '半程'],
    '拍照': ['拍照', '網美', '美照', '攝影', 'ig', '打卡'],
    '文化': ['文化', '歷史', '教堂', '古蹟', '市區'],
    
    # 時間偏好
    '一日遊': ['一日', '當天', '一天', '單日'],
    '兩日遊': ['兩日', '過夜', '兩天', '住宿'],
    
    # 預算考量
    '便宜': ['便宜', '省錢', '划算', '經濟', '預算'],
    '高檔': ['高檔', '豪華', '頂級', '奢華'],
    
    # 人數
    '情侶': ['情侶', '兩人', '浪漫', '蜜月'],
    '朋友': ['朋友', '同學', '一群人', '聚會'],
    '家庭': ['家庭', '親子', '小孩', '長輩'],
    
    # 特殊體驗
    '動物': ['眼鏡猴', '鯨鯊', '沙丁魚', '長尾鯊'],
    '水上活動': ['香蕉船', '拖傘', '獨木舟', '風帆'],
    '極限運動': ['跳傘', '空中飛人', '高空滑索', '越野車']
}

# AI 對話式客服系統
class TravelConcierge:
    def __init__(self):
        self.conversation_starters = [
            "您好！我是您的專屬旅遊顧問 😊",
            "嗨！很高興為您服務，讓我幫您找到完美的行程 ✨",
            "歡迎！我來幫您推薦最適合的宿霧行程 🌴"
        ]
        
        self.follow_up_questions = {
            'duration': [
                "您比較想要一日遊還是兩日遊呢？",
                "時間上有什麼限制嗎？一天或兩天都可以嗎？"
            ],
            'budget': [
                "預算大概抓多少呢？我們有不同價位的選擇 💰",
                "想了解一下您的預算範圍，好為您推薦合適的行程"
            ],
            'experience': [
                "您比較喜歡刺激冒險還是輕鬆度假的感覺？",
                "想要什麼樣的體驗呢？刺激一點還是輕鬆一點？"
            ],
            'interests': [
                "有特別想看的嗎？比如鯨鯊、沙丁魚、瀑布？",
                "對什麼最感興趣？海洋生物、自然景觀、還是文化景點？"
            ]
        }
    
    def analyze_message(self, message):
        """分析用戶訊息意圖"""
        message = message.lower()
        
        # 檢測意圖類型
        intents = {
            'greeting': ['你好', 'hello', 'hi', '嗨', '您好'],
            'asking_trip': ['行程', '旅遊', '玩', '去哪', '推薦', '景點'],
            'whale_shark': ['鯨鯊', '鯊魚', 'oslob', '歐斯陸'],
            'sardines': ['沙丁魚', '魚群', '墨寶', 'moalboal'],
            'adventure': ['刺激', '冒險', '朔溪', '跳水', '極限'],
            'relaxing': ['輕鬆', '休閒', '度假', '放鬆', '悠閒'],
            'photography': ['拍照', '網美', '美照', 'ig', '打卡'],
            'budget': ['便宜', '省錢', '預算', '價格', '多少錢'],
            'one_day': ['一日', '一天', '當天', '單日'],
            'two_day': ['兩日', '兩天', '過夜', '住宿'],
            'first_time': ['第一次', '初次', '新手', '沒去過'],
            'island': ['跳島', '小島', '島嶼', '薄荷島', '善妮島'],
            'culture': ['文化', '歷史', '教堂', '市區', '古蹟'],
            'beach': ['海灘', '沙灘', '海邊', '沙洲']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in message for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents
    
    def analyze_user_needs(self, message):
        """整合原有的需求分析功能"""
        message = message.lower()
        matched_needs = []
        
        # 分析用戶訊息中的需求關鍵字
        for need_type, keywords in NEED_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message:
                    matched_needs.append(need_type)
                    break
        
        # 根據需求匹配行程
        recommendations = []
        
        for code, info in ITINERARY_INFO.items():
            score = 0
            
            # 計算匹配分數
            for need in matched_needs:
                # 檢查需求類型是否在標籤中
                if need in info['tags']:
                    score += 3
                # 檢查需求關鍵字是否在標籤中
                elif any(need_keyword in info['tags'] for need_keyword in NEED_KEYWORDS.get(need, [])):
                    score += 2
            
            # 檢查標籤是否直接匹配訊息
            for tag in info['tags']:
                if tag in message:
                    score += 1
            
            if score > 0:
                recommendations.append((code, info, score))
        
        # 按分數排序
        recommendations.sort(key=lambda x: x[2], reverse=True)
        
        return recommendations, matched_needs
    
    def generate_personalized_response(self, intents, message):
        """根據意圖生成個人化回應"""
        
        # 如果只是打招呼
        if 'greeting' in intents and len(intents) == 1:
            return self.get_conversation_starter() + "\n\n想去宿霧玩嗎？告訴我您想要什麼樣的體驗，我來為您推薦最棒的行程！"
        
        # 如果詢問行程但沒有具體需求
        if 'asking_trip' in intents and len(intents) == 1:
            return self.get_needs_assessment()
        
        # 根據具體需求推薦
        recommendations = self.get_recommendations_by_intent(intents)
        
        if recommendations:
            return self.format_recommendations(recommendations, intents)
        else:
            # 如果AI推薦沒有結果，使用原有的智能推薦系統
            old_recommendations, matched_needs = self.analyze_user_needs(message)
            if old_recommendations:
                return self.generate_recommendation_message(old_recommendations, matched_needs)
            else:
                return self.get_clarification_response(message)
    
    def get_conversation_starter(self):
        return random.choice(self.conversation_starters)
    
    def get_needs_assessment(self):
        return """我來幫您找到最適合的行程！讓我了解一下您的偏好：

🤔 您比較想要：
• 🦈 看鯨鯊、沙丁魚等海洋生物？
• 🏝️ 美麗海島、拍照打卡？
• 🌊 刺激冒險、朔溪跳水？
• 🌸 輕鬆度假、自然景觀？
• 🏛️ 文化古蹟、市區觀光？

告訴我您的想法，我會推薦最適合的行程給您！"""
    
    def get_recommendations_by_intent(self, intents):
        """根據意圖推薦行程"""
        recommendations = []
        
        # 鯨鯊相關
        if 'whale_shark' in intents:
            if 'relaxing' in intents or 'one_day' in intents:
                recommendations.append(('S4A', 3))
                recommendations.append(('S5', 2))
                recommendations.append(('S6', 2))
            elif 'two_day' in intents:
                recommendations.append(('S1', 3))
                recommendations.append(('S1A', 2))
            else:
                recommendations.append(('S1', 3))
                recommendations.append(('S4A', 2))
                recommendations.append(('S4', 2))
        
        # 沙丁魚相關
        elif 'sardines' in intents:
            recommendations.append(('S8', 3))
            recommendations.append(('S7', 2))
            recommendations.append(('S3', 2))
        
        # 冒險刺激
        elif 'adventure' in intents:
            recommendations.append(('S1', 3))
            recommendations.append(('S2', 3))
            recommendations.append(('S4', 2))
        
        # 拍照網美
        elif 'photography' in intents:
            recommendations.append(('N3', 3))
            recommendations.append(('N4', 2))
        
        # 海灘相關
        elif 'beach' in intents:
            recommendations.append(('N4', 3))
            recommendations.append(('N3', 2))
            recommendations.append(('S8', 2))
        
        # 跳島相關
        elif 'island' in intents:
            recommendations.append(('C1', 3))
            recommendations.append(('B1', 2))
            recommendations.append(('B2', 2))
        
        # 文化相關
        elif 'culture' in intents:
            recommendations.append(('C2', 3))
            recommendations.append(('S5', 2))
            recommendations.append(('S6', 2))
        
        # 輕鬆度假
        elif 'relaxing' in intents:
            if 'two_day' in intents:
                recommendations.append(('N2', 3))
                recommendations.append(('B2', 2))
            else:
                recommendations.append(('C1', 3))
                recommendations.append(('B1', 2))
                recommendations.append(('C2', 2))
        
        # 預算考量
        elif 'budget' in intents:
            recommendations.append(('C2', 3))
            recommendations.append(('S8', 2))
        
        # 第一次來
        elif 'first_time' in intents:
            recommendations.append(('C1', 3))
            recommendations.append(('S4A', 2))
            recommendations.append(('B1', 2))
        
        # 時間偏好
        elif 'one_day' in intents:
            recommendations.extend([('C1', 2), ('B1', 2), ('S4A', 2), ('S8', 2)])
        elif 'two_day' in intents:
            recommendations.extend([('S1', 3), ('N3', 2), ('B2', 2)])
        
        # 如果是一般詢問行程
        elif 'asking_trip' in intents:
            recommendations.extend([('S1', 3), ('C1', 2), ('N3', 2)])
        
        return recommendations
    
    def format_recommendations(self, recommendations, intents):
        """格式化推薦回應"""
        if not recommendations:
            return self.get_clarification_response("")
        
        # 取前3個推薦
        top_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:3]
        
        response = "根據您的需求，我為您推薦這幾個超棒的行程：\n\n"
        
        for i, (code, score) in enumerate(top_recommendations, 1):
            itinerary = ITINERARY_INFO[code]
            price_min, price_max = itinerary['price_range']
            
            response += f"🌟 **{i}. 【{code}】{itinerary['name']}**\n"
            response += f"✨ {itinerary['duration']}日遊 | {itinerary['difficulty']} | ₱{price_min:,}-{price_max:,}\n"
            response += f"🎯 適合：{' '.join(itinerary['best_for'][:2])}\n"
            response += f"📍 亮點：{' '.join(itinerary['highlights'][:2])}\n\n"
        
        response += f"💡 直接輸入行程代碼（如 {top_recommendations[0][0]}）查看完整詳情\n"
        response += "🤔 需要更多資訊或其他推薦嗎？"
        
        return response
    
    def generate_recommendation_message(self, recommendations, user_needs):
        """生成推薦訊息（原有功能）"""
        if not recommendations:
            return None
        
        if len(recommendations) == 1:
            # 只有一個推薦
            code, info, score = recommendations[0]
            return f"🎯 根據您的需求，我推薦：\n\n{info['content']}"
        
        elif len(recommendations) <= 3:
            # 多個推薦，顯示簡要信息
            message = f"🎯 根據您的需求，我為您推薦以下 {len(recommendations)} 個行程：\n\n"
            
            for i, (code, info, score) in enumerate(recommendations, 1):
                price_min, price_max = info['price_range']
                message += f"{i}. 【{code}】{info['name']}\n"
                message += f"   ⭐ {info['duration']}日遊 | ₱{price_min:,}-{price_max:,}/人\n"
                message += f"   🕐 出發時間：{info['departure']}\n\n"
            
            message += "💡 輸入行程代碼（如 S1、C1）查看詳細資訊"
            return message
        
        else:
            # 太多推薦，只顯示前3個
            message = f"🎯 找到 {len(recommendations)} 個符合的行程，為您推薦最匹配的前 3 個：\n\n"
            
            for i, (code, info, score) in enumerate(recommendations[:3], 1):
                price_min, price_max = info['price_range']
                message += f"{i}. 【{code}】{info['name']}\n"
                message += f"   ⭐ {info['duration']}日遊 | ₱{price_min:,}-{price_max:,}/人\n"
                message += f"   🕐 出發時間：{info['departure']}\n\n"
            
            message += "💡 輸入行程代碼查看詳細資訊，或告訴我更具體的需求！"
            return message
    
    def get_clarification_response(self, message):
        """獲取澄清回應"""
        clarifications = [
            "讓我更了解您的需求，好為您推薦最適合的行程！",
            "想幫您找到完美的行程，能告訴我更多您的想法嗎？",
            "我想為您推薦最棒的體驗，可以分享一下您的偏好嗎？"
        ]
        
        base_response = random.choice(clarifications)
        
        # 隨機提出一個跟進問題
        question_type = random.choice(['interests', 'experience', 'duration'])
        follow_up = random.choice(self.follow_up_questions[question_type])
        
        return f"{base_response}\n\n{follow_up}"

# 初始化 AI 客服
concierge = TravelConcierge()

# 自動回覆關鍵字字典
AUTO_REPLIES = {
    '保險': """🔔 關於保險的說明：

我們旅遊行程中所使用的車輛與船隻，皆為合法營運並有投保相關責任保險，因此基本的車險與船險已包含於行程中，保障乘客在交通工具上的基本安全。

至於整趟行程的旅遊平安保險（Travel Insurance），這部分採取「選購制」。主要原因如下：

1. 外國旅客一般已在母國投保旅遊保險，保障範圍與理賠金額普遍優於當地保險
2. 若需在菲律賓投保當地的旅遊險，辦理時間通常超過一週
3. 當地保險的理賠金額普遍偏低
4. 本公司行程以短期高性價比套裝行程為主，且預訂時間普遍較短

🔔 若您對整趟行程的保險保障特別重視，我們建議可考慮加購，但也提前提醒，當地保險的保障額度與理賠標準，與多數國際保單差異頗大。""",
    
    '跳傘': """🪂 跳傘方案說明：

🔸 標準方案（STANDARD）：每人 ₱24,500
• 高空跳傘（最高達 10,000 英尺）
• 20 分鐘觀光飛行
• 30–40 秒自由落體
• 5–7 分鐘降落傘滑翔
• 跳傘證書
• 手持攝影照片與影片（Handcam）
• 剪輯後影片

🔸 高級方案（PREMIUM）：每人 ₱35,000
• 高空跳傘（最高達 10,000 英尺）
• 20 分鐘觀光飛行
• 30–40 秒自由落體
• 5–7 分鐘降落傘滑翔
• 跳傘證書
• 手持攝影照片與影片（Handcam）
• 第三位攝影師空拍照片與影片（外部攝影）
• 剪輯後影片""",
    
    '伴手禮': """🛍️ 伴手禮/餅乾/零食訂購：

滿 10包 送貨到飯店/學校
通常週四為配送日
時間為晚上18:00-22:00

請點擊下方連結，填寫訂單，填寫完成後請務必回覆：
https://forms.gle/HJKc1nDE9MNRfrp39""",
    
    '餅乾': """🛍️ 伴手禮/餅乾/零食訂購：

滿 10包 送貨到飯店/學校
通常週四為配送日
時間為晚上18:00-22:00

請點擊下方連結，填寫訂單，填寫完成後請務必回覆：
https://forms.gle/HJKc1nDE9MNRfrp39""",
    
    '零食': """🛍️ 伴手禮/餅乾/零食訂購：

滿 10包 送貨到飯店/學校
通常週四為配送日
時間為晚上18:00-22:00

請點擊下方連結，填寫訂單，填寫完成後請務必回覆：
https://forms.gle/HJKc1nDE9MNRfrp39""",
    
    '拼團': """🌴 拼團活動說明：

🔸 自組團行程
• 您可自由選擇出發日期與行程，旅費將依出團人數進行計算
• 想要擁有專屬行程的彈性，自組團是最佳選擇！

🔸 拼團活動
• 若人數不足或希望旅費更實惠，歡迎參加拼團活動！
• 拼團活動皆由遊學代辦中心每週固定於週末舉辦，提供高品質旅遊體驗
• 獲取資訊：對話框輸入joiner，並點擊連結報名！""",
    
    '信用卡': """💳 信用卡付款說明：

我們接受信用卡付款，但是要加總金額5%的稅收

請提供以下資訊，我們將寄送付款連結至您的信箱：
• 英文護照全名：
• 電子信箱：
• 帳單地址（英文）：
• 郵遞區號：""",
    
    '刷卡': """💳 信用卡付款說明：

我們接受信用卡付款，但是要加總金額5%的稅收

請提供以下資訊，我們將寄送付款連結至您的信箱：
• 英文護照全名：
• 電子信箱：
• 帳單地址（英文）：
• 郵遞區號：""",
    
    '人數': """🚐 團體人數與車輛安排說明：

每團最多以 13 人為上限，如超過 13 人，將會依照情況分成兩團（安排兩台車）。

為使行程順暢，人數分配將平均分配至兩團，並且依據分團後的實際人數計算費用。

📌 例如：
若共有 16 位旅客，將分為 2 團，每團 8 人，
則費用將以「8 人團」的價格計算。""",
    
    '客製化': """🗺️ 客製化行程安排：

哈囉～再麻煩幫我加這個帳號，會有專人協助您安排自由行客製化旅遊

Line : https://lin.ee/83r5zlu""",
    
    '自由行': """🗺️ 客製化行程安排：

哈囉～再麻煩幫我加這個帳號，會有專人協助您安排自由行客製化旅遊

Line : https://lin.ee/83r5zlu""",
    
    '導遊': """👨‍🏫 導遊說明：

我們這邊的導遊都是菲律賓當地的英文導遊，英文流利又好溝通，也很了解當地文化和各大景點的故事，帶團非常有經驗！✨

幾個優點分享給您：
1. 英文清楚好懂：英文是他們的日常語言，講話標準又親切 🗣
2. 很懂本地文化：會介紹一些不在旅遊書上的在地小知識 🌴📚
3. 超好又會帶氣氛：大多數導遊都很熱情、健談 😊🎉
4. 經驗豐富：我們配合的導遊都帶過很多團，處理各種狀況都很有方法 ✔🧳

如果您有指定要中文導遊，我們也可以幫您安排，不過中文導遊每天會多收 ₱4000 的費用哦～""",
    
    '退費': """💰 退費規定：

一、活動尚未出發 🚫
🔸 因天候因素取消（海上或陸上警報）
→ 全額退還訂金 ✅

🔸 無天候警報，客人主動取消
→ 扣除已支付的飯店或船票費用後，退還剩餘訂金（通常幾乎無法退款）⚠

二、活動已出發 🚶🚢
🔸 因特殊原因無法參加部分景點活動
→ 退還該景點門票費用 💳
例如：若南方行程無法觀賞沙丁魚，將退還門票費500 PHP 🐟

❗ 重要提醒
若無法接受上述退費規定，請勿報名 ✋
請務必告知同團成員，避免爭議 🗣""",
    
    '天氣': """💰 退費規定：

一、活動尚未出發 🚫
🔸 因天候因素取消（海上或陸上警報）
→ 全額退還訂金 ✅

🔸 無天候警報，客人主動取消
→ 扣除已支付的飯店或船票費用後，退還剩餘訂金（通常幾乎無法退款）⚠

二、活動已出發 🚶🚢
🔸 因特殊原因無法參加部分景點活動
→ 退還該景點門票費用 💳
例如：若南方行程無法觀賞沙丁魚，將退還門票費500 PHP 🐟

❗ 重要提醒
若無法接受上述退費規定，請勿報名 ✋
請務必告知同團成員，避免爭議 🗣""",
    
    '房間': """🏨 房間分配說明：

基本上我們2-3人/間房，男女分房。

倘若有情侶或者家庭成員要一起住的話，請務必特別提早告知，這樣才方便先幫您們安排。

飯店也無法保證全部房型每個人都有單人房可以睡，有時候會是大床房。""",
    
    '住宿': """🏨 房間分配說明：

基本上我們2-3人/間房，男女分房。

倘若有情侶或者家庭成員要一起住的話，請務必特別提早告知，這樣才方便先幫您們安排。

飯店也無法保證全部房型每個人都有單人房可以睡，有時候會是大床房。"""
}

# Webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Received webhook:", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 成員加入事件處理
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    global last_welcome_time
    now = time.time()
    if now - last_welcome_time < WELCOME_COOLDOWN:
        print("Skip sending welcome message due to cooldown.")
        return

    welcome_text = """🎉 歡迎加入《澳貝客遊學｜出遊群組》 🎉

嗨嗨～歡迎新朋友加入我們的出遊群組 👋
為了讓活動安排更順利，請新加入的朋友務必完成報到手續！

✅ 請到【記事本】留言報到
➡️ 寫上以下資訊：

中文名字／英文護照名／性別／語言學校
（範例：王小明／Wang Shaw Ming／男／Fella2）

⚠️ 沒有留言報到的同學，將不會列入出遊名單計算喔！

💵 訂金提醒
我們將於週四晚上 18:30 至 22:00 派員工到各語言學校門口收取訂金（現金付款）。
請準時出現並準備好正確金額，感謝配合！

🤖 我是您的智能旅遊顧問！
只要告訴我您想要什麼樣的體驗，我就能為您推薦最適合的行程 ✨
例如：「想要刺激的冒險」、「想看鯨鯊」、「適合拍照的地方」
"""
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))
    last_welcome_time = now

# 主要訊息處理 - 整合AI對話式客服和智能推薦
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == 'group':
        print("Current Group ID:", event.source.group_id)
    
    user_message = event.message.text.strip()
    user_message_lower = user_message.lower()
    
    # 1. 檢查精確的行程代碼
    sorted_codes = sorted(ITINERARY_INFO.items(), key=lambda x: len(x[0]), reverse=True)
    for code, info in sorted_codes:
        if code.lower() == user_message_lower or code.lower() in user_message_lower.split():
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text=info['content'])
            )
            print(f"Auto-replied for exact itinerary code: {code}")
            return
    
    # 2. 檢查自動回覆關鍵字
    for keyword, reply in AUTO_REPLIES.items():
        if keyword in user_message_lower:
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text=reply)
            )
            print(f"Auto-replied for keyword: {keyword}")
            return
    
    # 3. 特殊指令處理
    if 'joiner' in user_message_lower:
        joiner_reply = """🔥 iOutback Agency 澳貝客遊學 週末拼團活動 🔥
📌 報名傳送門 👉 https://forms.gle/3pxQ9kjZMHZJQXd67"""
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text=joiner_reply)
        )
        print("Replied to joiner command")
        return
    
    # 4. AI 對話式客服處理
    try:
        # 分析用戶意圖
        intents = concierge.analyze_message(user_message)
        print(f"Detected intents: {intents}")
        
        # 生成個人化回應
        ai_response = concierge.generate_personalized_response(intents, user_message)
        
        if ai_response:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=ai_response)
            )
            print(f"AI response sent for intents: {intents}")
            return
            
    except Exception as e:
        print(f"AI processing error: {e}")
    
    # 5. 如果是疑問句或求助，提供引導
    question_indicators = ['什麼', '怎麼', '如何', '推薦', '建議', '想要', '想去', '有沒有', '?', '？']
    if any(indicator in user_message for indicator in question_indicators):
        help_message = """🤔 我可以幫您推薦最適合的旅遊行程！

請告訴我您的偏好，例如：
🏝️ 想要什麼體驗：「刺激冒險」、「輕鬆度假」、「拍照打卡」
🐋 想看什麼：「鯨鯊」、「沙丁魚」、「瀑布」、「海灘」
⏰ 時間偏好：「一日遊」、「兩日遊」
💰 預算考量：「便宜一點」、「不考慮預算」

或者直接輸入行程代碼（如 S1、C1、N3）查看詳細資訊！"""
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=help_message)
        )
        print("Sent guidance message")
        return
    
    # 6. 兜底回應 - 智能客服風格
    fallback_response = """我是您的旅遊顧問，很樂意為您推薦行程！😊

🌟 您可以告訴我：
• 想看鯨鯊 🦈
• 想要刺激冒險 🌊
• 想拍美照 📸
• 想輕鬆度假 🏝️
• 預算有限 💰

或者直接問我「有什麼推薦的行程嗎？」

我會根據您的需求推薦最適合的宿霧行程！"""
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=fallback_response)
    )
    print("Sent fallback AI response")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

# 整合版說明：
# 這是一個完整的智能旅遊客服 LINE Bot，整合了兩個版本的所有功能：
# 
# 🤖 核心功能：
# 1. 完整行程資料庫（18個行程代碼，包含所有詳細資訊）
# 2. AI 對話式客服（理解自然語言，個人化推薦）
# 3. 智能需求分析（關鍵字匹配，精準推薦）
# 4. 自動回覆系統（保險、跳傘、伴手禮等常見問題）
# 5. 行程代碼查詢（輸入代碼直接查看詳細資訊）
# 6. 新成員歡迎（含智能功能介紹）
# 7. 拼團活動連結（joiner 指令）
# 8. 智能引導系統（幫助用戶更好表達需求）
# 
# 🎯 使用方式：
# - 自然對話：「我想看鯨鯊」、「有什麼刺激的行程」
# - 行程代碼：輸入 S1、C1、N3 等查看詳細資訊
# - 關鍵字查詢：保險、跳傘、導遊等
# - 拼團報名：輸入 joiner 獲取報名連結
# 
# 🔄 處理流程：
# 1. 精確行程代碼匹配 → 直接顯示行程詳情
# 2. 關鍵字自動回覆 → 顯示相關說明
# 3. AI 意圖分析 → 個人化推薦
# 4. 智能需求匹配 → 基於標籤推薦
# 5. 疑問引導 → 提供使用指引
# 6. 兜底回應 → 確保始終有有用回覆
# 
# 這個整合版本結合了兩個版本的優點，提供更智能、更人性化的客服體驗！

# 🔸 拼團活動
# • 若人數不足或希望旅費更實惠，歡迎參加拼團活動！
# • 拼團活動皆由遊學代辦中心每週固定於週末舉辦，提供高品質旅遊體驗
# • 獲取資訊：對話框輸入joiner，並點擊連結報名！""",
    
#     '報名': """🌴 拼團活動說明：

# 🔸 自組團行程
# • 您可自由選擇出發日期與行程，旅費將依出團人數進行計算
# • 想要擁有專屬行程的彈性，自組團是最佳選擇！