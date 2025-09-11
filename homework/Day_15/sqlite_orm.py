from datetime import datetime,timezone,timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

# 定义数据库连接（SQLite）
base_dir = Path(__file__).parent.resolve()
db_file = base_dir / "db" / "sqlalchemy_sqlite3.db"
db_file.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{db_file}?check_same_thread=False", 
    echo=False  # echo=True 会打印SQL语句，调试方便
    ) 
Base = declarative_base() # 得到一个 ORM 基类
Session = sessionmaker(bind=engine)
shanghai_tz = timezone(timedelta(hours=8))


# 定义表模型
class UserHomeWork(Base):
    __tablename__ = "user_homework"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(String, nullable=False, index=True)          # 学员姓名
    age = Column(Integer, nullable=False)          # 学员年龄
    homework_count = Column(Integer, nullable=False, default=0)    # 作业数量
    last_update_time = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),   # 默认存 UTC
        onupdate=lambda: datetime.now(timezone.utc)   # 更新时存 UTC
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(学员姓名：{self.student_name}| 学员年龄：{self.age}| "\
               f"作业数量：{self.homework_count}| 最后更新时间：{self.last_update_time})"

def initialize_data(session):
    """初始化数据，只插入一次"""
    # 检查表里是否已有数据
    count = session.query(UserHomeWork).count()
    if count > 0:
        print("已初始化过数据，跳过插入")
        return

    homework_dict = [
        {"student_name": "张三", "age": 37, "homework_count": 1},
        {"student_name": "李四", "age": 33, "homework_count": 5},
        {"student_name": "王五", "age": 32, "homework_count": 10},
    ]

    # 插入数据
    session.add_all([UserHomeWork(**h) for h in homework_dict])
    session.commit()
    print("数据初始化完成")

def interactive_query():
    try:
        while True:
            print("\n请输入查询选项：")
            print("输入 1：查询整个数据库")
            print("输入 2：根据学员姓名查询")
            print("输入 3：根据学员年龄查询")
            print("输入 4：根据作业数量查询")
            print("输入 0：退出")
            choice = input("输入选项（0-4）：").strip()

            if choice == "1":
                result = query_and_print()
            elif choice == "2":
                name = input("请输入学员姓名：").strip()
                result = query_and_print(filter_func=UserHomeWork.student_name == name)
            elif choice == "3":
                age = input("搜索大于输入年龄的学员,请输入学员年龄：").strip()
                if not age.isdigit():
                    raise ValueError("请输入有效数字！")          
                result = query_and_print(filter_func=UserHomeWork.age > int(age))
            elif choice == "4":
                homework_count = input("搜索大于输入作业数的学员，请输入作业数量：").strip()
                if not homework_count.isdigit():
                    raise ValueError("请输入有效数字！")   
                result = query_and_print(filter_func=UserHomeWork.homework_count > int(homework_count))
            elif choice == "0":
                print("退出查询。")
                break
            else:
                print("无效选项，请重新输入。")
                continue

            if result:
                for item in result:
                    utc_time = item.last_update_time.replace(tzinfo=timezone.utc)
                    local_time = utc_time.astimezone(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S.%f')  # 转成shanghai时区
                    # print(f"学员姓名：{item.student_name} | 学员年龄：{item.age} | 作业数量： {item.homework_count} | 最后更新时间（UTC）：{item.last_update_time}")
                    print(f"学员姓名：{item.student_name} | 学员年龄：{item.age} | 作业数量： {item.homework_count} | 最后更新时间：{local_time}")


            else:
                print("没有找到符合条件的记录。")
    except KeyboardInterrupt:
        print("\n查询被中断，已退出。")


def query_and_print(filter_func=None):
    with Session() as session_query:
        query = session_query.query(UserHomeWork)
        if filter_func is not None:
            # print(f"应用过滤条件进行查询...{filter_func}")
            query = query.filter(filter_func)
        results = query.all()
        return results

def main():
    # 创建表（不存在才创建）
    Base.metadata.create_all(engine, checkfirst=True)
    # 初始化数据
    with Session() as session_init:
        initialize_data(session_init)  # 只初始化一次
    # 交互式查询
    interactive_query()

if __name__ == "__main__":
    main()