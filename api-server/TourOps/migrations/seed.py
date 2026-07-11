"""初始化示例数据"""
from sqlalchemy.orm import Session
from TourOps.core.database import engine
from TourOps.models.resource import Guide, Vehicle, Hotel, Restaurant

def seed_data():
    """填充示例数据"""
    with Session(engine) as db:
        # 检查是否已有数据
        if db.query(Guide).first():
            print("数据已存在，跳过初始化")
            return
        
        # 导游
        guides = [
            Guide(name="张明", contact_phone="13800001001", id_card="110101199001011234", 
                  languages=["中文", "英语"], regions=["北京", "天津"], notes="资深导游，10年经验"),
            Guide(name="李华", contact_phone="13800001002", id_card="310101199205052345",
                  languages=["中文", "日语"], regions=["上海", "杭州", "苏州"], notes="日语专业导游"),
            Guide(name="王芳", contact_phone="13800001003", id_card="440101199308083456",
                  languages=["中文", "粤语", "英语"], regions=["广州", "深圳", "珠海"], notes="粤港澳专线"),
            Guide(name="刘洋", contact_phone="13800001004", id_card="510101199106064567",
                  languages=["中文"], regions=["成都", "九寨沟", "峨眉山"], notes="川西线路专家"),
            Guide(name="陈静", contact_phone="13800001005", id_card="330101199407075678",
                  languages=["中文", "英语", "法语"], regions=["杭州", "乌镇", "西塘"], notes="江南水乡专线"),
        ]
        db.add_all(guides)
        
        # 车辆
        vehicles = [
            Vehicle(name="商务别克GL8", plate_number="京A12345", vehicle_type="商务车", seats=7,
                    driver_name="赵师傅", driver_phone="13900001001", notes="车况良好"),
            Vehicle(name="丰田考斯特", plate_number="京B23456", vehicle_type="中巴", seats=19,
                    driver_name="钱师傅", driver_phone="13900001002", notes="适合小团队"),
            Vehicle(name="金龙大巴", plate_number="京C34567", vehicle_type="大巴", seats=45,
                    driver_name="孙师傅", driver_phone="13900001003", notes="长途首选"),
            Vehicle(name="奔驰V260", plate_number="京D45678", vehicle_type="商务车", seats=6,
                    driver_name="李师傅", driver_phone="13900001004", notes="高端商务接待"),
            Vehicle(name="宇通大巴", plate_number="京E56789", vehicle_type="大巴", seats=53,
                    driver_name="周师傅", driver_phone="13900001005", notes="大型团队用车"),
        ]
        db.add_all(vehicles)
        
        # 酒店
        hotels = [
            Hotel(name="北京饭店", address="北京市东城区东长安街33号", star_rating=5,
                  contact_phone="010-65137766", room_types={"标准间": 800, "豪华间": 1200, "套房": 2500}),
            Hotel(name="上海和平饭店", address="上海市黄浦区南京东路20号", star_rating=5,
                  contact_phone="021-63216888", room_types={"标准间": 900, "豪华间": 1500, "套房": 3000}),
            Hotel(name="杭州西湖国宾馆", address="杭州市西湖区杨公堤18号", star_rating=5,
                  contact_phone="0571-87979889", room_types={"标准间": 700, "湖景间": 1100, "别墅": 3500}),
            Hotel(name="成都锦江宾馆", address="成都市锦江区人民南路二段80号", star_rating=4,
                  contact_phone="028-85506666", room_types={"标准间": 500, "豪华间": 800, "套房": 1500}),
            Hotel(name="广州白天鹅宾馆", address="广州市荔湾区沙面南街1号", star_rating=5,
                  contact_phone="020-81886968", room_types={"标准间": 750, "江景间": 1000, "套房": 2200}),
            Hotel(name="如家快捷酒店", address="北京市朝阳区建国路8号", star_rating=2,
                  contact_phone="010-58698888", room_types={"标准间": 250, "大床房": 280}),
        ]
        db.add_all(hotels)
        
        # 餐厅
        restaurants = [
            Restaurant(name="全聚德烤鸭店", address="北京市东城区前门大街30号", cuisine="京菜",
                       contact_phone="010-67011379", price_min=150, price_max=300, notes="百年老字号"),
            Restaurant(name="外婆家", address="杭州市西湖区湖滨路1号", cuisine="杭帮菜",
                       contact_phone="0571-87065777", price_min=60, price_max=120, notes="性价比高"),
            Restaurant(name="陈麻婆豆腐", address="成都市青羊区西玉龙街197号", cuisine="川菜",
                       contact_phone="028-86754512", price_min=50, price_max=100, notes="正宗川味"),
            Restaurant(name="绿茶餐厅", address="上海市静安区南京西路1788号", cuisine="创意菜",
                       contact_phone="021-62889777", price_min=80, price_max=150, notes="环境优雅"),
            Restaurant(name="点都德", address="广州市越秀区文明路160号", cuisine="粤菜",
                       contact_phone="020-83888222", price_min=70, price_max=130, notes="正宗早茶"),
            Restaurant(name="海底捞火锅", address="北京市朝阳区望京1号", cuisine="火锅",
                       contact_phone="010-84722345", price_min=100, price_max=200, notes="服务一流"),
        ]
        db.add_all(restaurants)
        
        db.commit()
        print("示例数据初始化完成")
        print(f"  - 导游: {len(guides)} 条")
        print(f"  - 车辆: {len(vehicles)} 条")
        print(f"  - 酒店: {len(hotels)} 条")
        print(f"  - 餐厅: {len(restaurants)} 条")

if __name__ == "__main__":
    seed_data()
