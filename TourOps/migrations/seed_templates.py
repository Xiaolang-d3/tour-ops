"""初始化模板数据"""
from sqlalchemy.orm import Session
from TourOps.core.database import engine
from TourOps.models.template import Template, TemplateCategory


def seed_templates():
    with Session(engine) as db:
        if db.query(Template).first():
            print("模板数据已存在，跳过")
            return

        templates = [
            Template(
                name="云南7日亲子游",
                category=TemplateCategory.FAMILY,
                duration_days=7,
                created_by=1,
                content={
                    "guest_count": 4,
                    "budget": 6000,
                    "activities": [
                        {"day": 1, "time": "09:00", "type": "transport", "name": "出发前往昆明", "start_time": "09:00", "end_time": "12:00", "location": "昆明长水机场", "cost": 0},
                        {"day": 1, "time": "14:00", "type": "attraction", "name": "翠湖公园", "start_time": "14:00", "end_time": "17:00", "location": "昆明翠湖", "cost": 0},
                        {"day": 1, "time": "18:00", "type": "meal", "name": "云南过桥米线", "start_time": "18:00", "end_time": "19:30", "location": "昆明市区", "cost": 60},
                        {"day": 2, "time": "08:00", "type": "transport", "name": "昆明→大理", "start_time": "08:00", "end_time": "12:00", "location": "大理", "cost": 150},
                        {"day": 2, "time": "14:00", "type": "attraction", "name": "大理古城", "start_time": "14:00", "end_time": "18:00", "location": "大理古城", "cost": 0},
                        {"day": 2, "time": "18:30", "type": "meal", "name": "白族风味餐", "start_time": "18:30", "end_time": "20:00", "location": "大理古城", "cost": 80},
                        {"day": 3, "time": "09:00", "type": "attraction", "name": "洱海骑行", "start_time": "09:00", "end_time": "12:00", "location": "洱海", "cost": 50},
                        {"day": 3, "time": "14:00", "type": "attraction", "name": "崇圣寺三塔", "start_time": "14:00", "end_time": "17:00", "location": "大理", "cost": 120},
                        {"day": 4, "time": "08:00", "type": "transport", "name": "大理→丽江", "start_time": "08:00", "end_time": "11:00", "location": "丽江", "cost": 100},
                        {"day": 4, "time": "14:00", "type": "attraction", "name": "丽江古城", "start_time": "14:00", "end_time": "18:00", "location": "丽江古城", "cost": 50},
                        {"day": 5, "time": "08:00", "type": "attraction", "name": "玉龙雪山", "start_time": "08:00", "end_time": "16:00", "location": "玉龙雪山", "cost": 300},
                        {"day": 5, "time": "18:00", "type": "meal", "name": "纳西族特色晚餐", "start_time": "18:00", "end_time": "19:30", "location": "丽江", "cost": 100},
                        {"day": 6, "time": "09:00", "type": "attraction", "name": "束河古镇", "start_time": "09:00", "end_time": "12:00", "location": "束河", "cost": 30},
                        {"day": 6, "time": "14:00", "type": "free", "name": "自由活动·购物", "start_time": "14:00", "end_time": "17:00", "location": "丽江", "cost": 0},
                        {"day": 7, "time": "09:00", "type": "transport", "name": "丽江→返程", "start_time": "09:00", "end_time": "12:00", "location": "丽江三义机场", "cost": 0},
                    ]
                }
            ),
            Template(
                name="北京3日商务考察",
                category=TemplateCategory.BUSINESS,
                duration_days=3,
                created_by=1,
                content={
                    "guest_count": 6,
                    "budget": 3000,
                    "activities": [
                        {"day": 1, "time": "09:00", "type": "transport", "name": "接机", "start_time": "09:00", "end_time": "10:30", "location": "首都机场", "cost": 0},
                        {"day": 1, "time": "12:00", "type": "meal", "name": "商务午宴", "start_time": "12:00", "end_time": "13:30", "location": "北京饭店", "cost": 200},
                        {"day": 1, "time": "14:00", "type": "attraction", "name": "企业参访·中关村", "start_time": "14:00", "end_time": "17:00", "location": "中关村科技园", "cost": 0},
                        {"day": 1, "time": "18:00", "type": "meal", "name": "全聚德烤鸭", "start_time": "18:00", "end_time": "20:00", "location": "前门大街", "cost": 250},
                        {"day": 2, "time": "09:00", "type": "attraction", "name": "故宫博物院", "start_time": "09:00", "end_time": "12:00", "location": "故宫", "cost": 60},
                        {"day": 2, "time": "12:30", "type": "meal", "name": "午餐", "start_time": "12:30", "end_time": "14:00", "location": "王府井", "cost": 150},
                        {"day": 2, "time": "14:30", "type": "attraction", "name": "长城·八达岭", "start_time": "14:30", "end_time": "18:00", "location": "八达岭长城", "cost": 45},
                        {"day": 3, "time": "09:00", "type": "attraction", "name": "天坛公园", "start_time": "09:00", "end_time": "11:00", "location": "天坛", "cost": 35},
                        {"day": 3, "time": "12:00", "type": "meal", "name": "告别午宴", "start_time": "12:00", "end_time": "13:30", "location": "北京", "cost": 200},
                        {"day": 3, "time": "15:00", "type": "transport", "name": "送机", "start_time": "15:00", "end_time": "17:00", "location": "首都机场", "cost": 0},
                    ]
                }
            ),
            Template(
                name="成都5日团建",
                category=TemplateCategory.TEAM_BUILDING,
                duration_days=5,
                created_by=1,
                content={
                    "guest_count": 20,
                    "budget": 4000,
                    "activities": [
                        {"day": 1, "time": "10:00", "type": "transport", "name": "抵达成都", "start_time": "10:00", "end_time": "12:00", "location": "双流机场", "cost": 0},
                        {"day": 1, "time": "14:00", "type": "attraction", "name": "宽窄巷子", "start_time": "14:00", "end_time": "17:00", "location": "宽窄巷子", "cost": 0},
                        {"day": 1, "time": "18:00", "type": "meal", "name": "火锅团建", "start_time": "18:00", "end_time": "20:30", "location": "海底捞", "cost": 150},
                        {"day": 2, "time": "08:00", "type": "attraction", "name": "大熊猫基地", "start_time": "08:00", "end_time": "12:00", "location": "熊猫基地", "cost": 55},
                        {"day": 2, "time": "14:00", "type": "free", "name": "团队拓展活动", "start_time": "14:00", "end_time": "17:00", "location": "成都", "cost": 200},
                        {"day": 3, "time": "07:00", "type": "transport", "name": "成都→九寨沟", "start_time": "07:00", "end_time": "14:00", "location": "九寨沟", "cost": 200},
                        {"day": 3, "time": "15:00", "type": "attraction", "name": "九寨沟景区", "start_time": "15:00", "end_time": "18:00", "location": "九寨沟", "cost": 250},
                        {"day": 4, "time": "08:00", "type": "attraction", "name": "九寨沟深度游", "start_time": "08:00", "end_time": "16:00", "location": "九寨沟", "cost": 0},
                        {"day": 4, "time": "18:00", "type": "meal", "name": "藏族篝火晚会", "start_time": "18:00", "end_time": "21:00", "location": "九寨沟", "cost": 180},
                        {"day": 5, "time": "08:00", "type": "transport", "name": "返回成都·送机", "start_time": "08:00", "end_time": "16:00", "location": "双流机场", "cost": 200},
                    ]
                }
            ),
            Template(
                name="西藏8日探险之旅",
                category=TemplateCategory.ADVENTURE,
                duration_days=8,
                created_by=1,
                content={
                    "guest_count": 8,
                    "budget": 8000,
                    "activities": [
                        {"day": 1, "time": "12:00", "type": "transport", "name": "抵达拉萨", "start_time": "12:00", "end_time": "14:00", "location": "拉萨贡嘎机场", "cost": 0},
                        {"day": 1, "time": "15:00", "type": "free", "name": "休息适应海拔", "start_time": "15:00", "end_time": "18:00", "location": "拉萨酒店", "cost": 0},
                        {"day": 2, "time": "09:00", "type": "attraction", "name": "布达拉宫", "start_time": "09:00", "end_time": "12:00", "location": "布达拉宫", "cost": 200},
                        {"day": 2, "time": "14:00", "type": "attraction", "name": "大昭寺·八廓街", "start_time": "14:00", "end_time": "17:00", "location": "大昭寺", "cost": 85},
                        {"day": 3, "time": "08:00", "type": "transport", "name": "拉萨→纳木错", "start_time": "08:00", "end_time": "12:00", "location": "纳木错", "cost": 300},
                        {"day": 3, "time": "13:00", "type": "attraction", "name": "纳木错湖", "start_time": "13:00", "end_time": "17:00", "location": "纳木错", "cost": 120},
                        {"day": 4, "time": "07:00", "type": "transport", "name": "纳木错→日喀则", "start_time": "07:00", "end_time": "14:00", "location": "日喀则", "cost": 350},
                        {"day": 4, "time": "15:00", "type": "attraction", "name": "扎什伦布寺", "start_time": "15:00", "end_time": "17:30", "location": "日喀则", "cost": 100},
                        {"day": 5, "time": "06:00", "type": "transport", "name": "日喀则→珠峰大本营", "start_time": "06:00", "end_time": "14:00", "location": "珠峰大本营", "cost": 400},
                        {"day": 5, "time": "15:00", "type": "attraction", "name": "珠峰大本营", "start_time": "15:00", "end_time": "19:00", "location": "珠峰大本营", "cost": 180},
                        {"day": 6, "time": "08:00", "type": "transport", "name": "珠峰→日喀则", "start_time": "08:00", "end_time": "15:00", "location": "日喀则", "cost": 350},
                        {"day": 7, "time": "08:00", "type": "transport", "name": "日喀则→拉萨", "start_time": "08:00", "end_time": "14:00", "location": "拉萨", "cost": 300},
                        {"day": 7, "time": "15:00", "type": "free", "name": "自由活动·购物", "start_time": "15:00", "end_time": "18:00", "location": "拉萨", "cost": 0},
                        {"day": 8, "time": "10:00", "type": "transport", "name": "拉萨→返程", "start_time": "10:00", "end_time": "13:00", "location": "贡嘎机场", "cost": 0},
                    ]
                }
            ),
            Template(
                name="杭州3日亲子游",
                category=TemplateCategory.FAMILY,
                duration_days=3,
                created_by=1,
                content={
                    "guest_count": 3,
                    "budget": 3000,
                    "activities": [
                        {"day": 1, "time": "10:00", "type": "attraction", "name": "西湖游船", "start_time": "10:00", "end_time": "12:00", "location": "西湖", "cost": 55},
                        {"day": 1, "time": "12:30", "type": "meal", "name": "楼外楼·西湖醋鱼", "start_time": "12:30", "end_time": "14:00", "location": "孤山路", "cost": 120},
                        {"day": 1, "time": "14:30", "type": "attraction", "name": "雷峰塔", "start_time": "14:30", "end_time": "16:30", "location": "雷峰塔", "cost": 40},
                        {"day": 2, "time": "09:00", "type": "attraction", "name": "宋城景区", "start_time": "09:00", "end_time": "15:00", "location": "宋城", "cost": 280},
                        {"day": 2, "time": "16:00", "type": "attraction", "name": "灵隐寺", "start_time": "16:00", "end_time": "18:00", "location": "灵隐寺", "cost": 75},
                        {"day": 3, "time": "09:00", "type": "attraction", "name": "千岛湖一日游", "start_time": "09:00", "end_time": "17:00", "location": "千岛湖", "cost": 200},
                    ]
                }
            ),
            Template(
                name="上海2日商务接待",
                category=TemplateCategory.BUSINESS,
                duration_days=2,
                created_by=1,
                content={
                    "guest_count": 4,
                    "budget": 2500,
                    "activities": [
                        {"day": 1, "time": "10:00", "type": "transport", "name": "接机", "start_time": "10:00", "end_time": "11:30", "location": "浦东机场", "cost": 0},
                        {"day": 1, "time": "12:00", "type": "meal", "name": "商务午宴", "start_time": "12:00", "end_time": "13:30", "location": "外滩", "cost": 300},
                        {"day": 1, "time": "14:00", "type": "attraction", "name": "陆家嘴金融区参访", "start_time": "14:00", "end_time": "17:00", "location": "陆家嘴", "cost": 0},
                        {"day": 1, "time": "18:00", "type": "meal", "name": "外滩夜景晚宴", "start_time": "18:00", "end_time": "20:30", "location": "外滩", "cost": 500},
                        {"day": 2, "time": "09:00", "type": "attraction", "name": "上海博物馆", "start_time": "09:00", "end_time": "11:30", "location": "人民广场", "cost": 0},
                        {"day": 2, "time": "12:00", "type": "meal", "name": "本帮菜午餐", "start_time": "12:00", "end_time": "13:30", "location": "南京路", "cost": 150},
                        {"day": 2, "time": "15:00", "type": "transport", "name": "送机", "start_time": "15:00", "end_time": "17:00", "location": "浦东机场", "cost": 0},
                    ]
                }
            ),
        ]

        db.add_all(templates)
        db.commit()
        print(f"模板数据初始化完成，共 {len(templates)} 个模板")


if __name__ == "__main__":
    seed_templates()
