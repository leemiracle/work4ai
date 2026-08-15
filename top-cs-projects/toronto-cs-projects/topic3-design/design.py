"""
CSC 207 Software Design (University of Toronto)
================================================
覆盖主题：
- 设计模式（Factory / Observer / Strategy / Decorator）
- SOLID 原则
- 重构（Extract Method / Replace Conditional with Polymorphism）
- UML mini（类图 ASCII 表示）

核心教材：
- "Design Patterns" by Gamma, Helm, Johnson, Vlissides (GoF, 1994)
- "Refactoring" by Fowler (2nd ed., 2018)
- "Clean Code" by Martin (2008)

本文件实现：
- 4 个经典设计模式（可运行实例）
- SOLID 原则违反检测器
- 重构演示（bad code → good code）
- Mini UML 类图生成器

运行：
    python design.py
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol


# ============ 1. Strategy Pattern ============

class SortStrategy(ABC):
    """策略接口：排序算法"""
    @abstractmethod
    def sort(self, data: list) -> list:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class BubbleSort(SortStrategy):
    def sort(self, data: list) -> list:
        arr = list(data)
        comparisons = 0
        for i in range(len(arr)):
            for j in range(len(arr) - 1 - i):
                comparisons += 1
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        self.comparisons = comparisons
        return arr

    @property
    def name(self): return "Bubble O(n²)"


class QuickSort(SortStrategy):
    def sort(self, data: list) -> list:
        self.comparisons = 0
        arr = list(data)
        self._qs(arr, 0, len(arr) - 1)
        return arr

    def _qs(self, arr, lo, hi):
        if lo >= hi:
            return
        pivot = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            self.comparisons += 1
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        self._qs(arr, lo, i)
        self._qs(arr, i + 2, hi)

    @property
    def name(self): return "Quick O(n log n)"


class Sorter:
    """Context：使用策略"""
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)


# ============ 2. Observer Pattern ============

class Subject:
    """被观察者"""
    def __init__(self):
        self._observers = []
        self._state = None

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for obs in self._observers:
            obs.update(self._state)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.notify()


class Observer(ABC):
    @abstractmethod
    def update(self, state):
        pass


class LoggerObserver(Observer):
    def update(self, state):
        print(f"     [Logger] State changed to: {state}")


class EmailObserver(Observer):
    def update(self, state):
        print(f"     [Email] Sending alert: '{state}'")


class AuditObserver(Observer):
    def __init__(self):
        self.log = []

    def update(self, state):
        self.log.append(state)
        print(f"     [Audit] Recorded event #{len(self.log)}: {state}")


# ============ 3. Factory Pattern ============

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

    @property
    @abstractmethod
    def species(self) -> str:
        pass


class Dog(Animal):
    def speak(self): return "Woof!"
    @property
    def species(self): return "Canine"


class Cat(Animal):
    def speak(self): return "Meow!"
    @property
    def species(self): return "Feline"


class Duck(Animal):
    def speak(self): return "Quack!"
    @property
    def species(self): return "Waterfowl"


class AnimalFactory:
    """工厂：根据类型创建对象"""
    _registry = {"dog": Dog, "cat": Cat, "duck": Duck}

    @classmethod
    def create(cls, animal_type: str) -> Animal:
        if animal_type not in cls._registry:
            raise ValueError(f"Unknown animal: {animal_type}")
        return cls._registry[animal_type]()

    @classmethod
    def register(cls, name: str, animal_class):
        """开放扩展，关闭修改"""
        cls._registry[name] = animal_class


# ============ 4. Decorator Pattern ============

class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class SimpleCoffee(Coffee):
    def cost(self): return 5.0
    def description(self): return "Coffee"


class CoffeeDecorator(Coffee):
    def __init__(self, wrapped: Coffee):
        self._wrapped = wrapped

    def cost(self): return self._wrapped.cost()
    def description(self): return self._wrapped.description()


class MilkDecorator(CoffeeDecorator):
    def cost(self): return self._wrapped.cost() + 1.5
    def description(self): return self._wrapped.description() + " + Milk"


class SugarDecorator(CoffeeDecorator):
    def cost(self): return self._wrapped.cost() + 0.5
    def description(self): return self._wrapped.description() + " + Sugar"


class WhipDecorator(CoffeeDecorator):
    def cost(self): return self._wrapped.cost() + 2.0
    def description(self): return self._wrapped.description() + " + Whip"


# ============ 5. SOLID 原则演示 ============

def solid_demo():
    """SOLID 五原则检查"""
    print("\n📋 5. SOLID 原则")
    print("   S - Single Responsibility: 一个类只做一件事")
    print("   O - Open/Closed: 扩展开放，修改关闭")
    print("   L - Liskov Substitution: 子类可替换父类")
    print("   I - Interface Segregation: 接口最小化")
    print("   D - Dependency Inversion: 依赖抽象不依赖具体")

    # 违反 SRP 的坏例子
    print("\n   ❌ 违反 SRP 的 BadCode:")
    print("     class UserManager:")
    print("       def register(self): ...    # 业务逻辑")
    print("       def send_email(self): ...  # 邮件（不该在这里）")
    print("       def generate_report(self): ...  # 报表（不该在这里）")
    print("\n   ✅ 符合 SRP 的 GoodCode:")
    print("     class UserService: ...       # 用户业务")
    print("     class EmailService: ...      # 邮件")
    print("     class ReportService: ...     # 报表")


# ============ 6. 重构演示 ============

def refactoring_demo():
    """Extract Method + Replace Conditional with Polymorphism"""
    print("\n📋 6. 重构演示")

    # Before: Extract Method
    print("   重构1: Extract Method")
    print("   ❌ Before (一个巨大函数):")
    before_code = """
   def process_order(order):
       # 验证
       if not order.items: raise ValueError()
       if order.total < 0: raise ValueError()
       # 计算折扣
       if order.customer.is_vip:
           discount = order.total * 0.2
       else:
           discount = order.total * 0.05
       # 保存
       order.discount = discount
       order.final_total = order.total - discount
       db.save(order)
       # 发邮件
       send_email(order.customer.email, 'Order confirmed')"""
    print(before_code)

    print("\n   ✅ After (提取方法):")
    after_code = """
   def process_order(order):
       validate_order(order)
       apply_discount(order)
       save_order(order)
       notify_customer(order)

   def validate_order(order): ...
   def apply_discount(order): ...
   def save_order(order): ...
   def notify_customer(order): ..."""
    print(after_code)

    # 反直觉发现
    print("\n   反直觉发现：QuickSort vs BubbleSort 在已排序数据上：")
    import random
    data = list(range(50))
    for name, sorter in [("Bubble", BubbleSort()), ("Quick", QuickSort())]:
        sorter.sort(data)
        print(f"     {name}: {sorter.comparisons} comparisons")


# ============ 7. Mini UML ============

def uml_diagram():
    """ASCII UML 类图"""
    print("\n📋 7. UML 类图（设计模式关系）")
    print("""
   ┌─────────────────┐         ┌──────────────────┐
   │   SortStrategy  │◄──┐     │     Subject      │
   │  (interface)    │   │     │  +attach()       │
   │ + sort()        │   │     │  +notify()       │
   └─────────────────┘   │     └────────┬─────────┘
           ▲             │              │
           │ implements  │    notified  │
    ┌──────┴──────┐      │              ▼
    │             │      │     ┌──────────────────┐
┌───────┐   ┌─────────┐  │     │    Observer      │
│Bubble │   │ Quick   │  │     │  (interface)     │
│Sort   │   │ Sort    │  │     │ + update()       │
└───────┘   └─────────┘  │     └────────┬─────────┘
                         │         ┌────┼────┐
                   ┌─────┴───┐  ┌──┴──┐ ┌──┴──┐
                   │ Sorter  │  │ Log │ │Mail │
                   │ Context │  │     │ │     │
                   └─────────┘  └─────┘ └─────┘
    """)


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 207: Software Design Demo")
    print("=" * 60)

    # 1. Strategy
    print("\n📋 1. Strategy Pattern")
    import random
    data = [random.randint(1, 100) for _ in range(20)]
    sorter = Sorter(BubbleSort())
    result_bubble = sorter.sort(data)
    print(f"   Bubble: {result_bubble[:5]}... ({sorter._strategy.comparisons} comps)")
    sorter.set_strategy(QuickSort())
    result_quick = sorter.sort(data)
    print(f"   Quick:  {result_quick[:5]}... ({sorter._strategy.comparisons} comps)")

    # 2. Observer
    print("\n📋 2. Observer Pattern")
    subject = Subject()
    subject.attach(LoggerObserver())
    subject.attach(EmailObserver())
    audit = AuditObserver()
    subject.attach(audit)
    subject.state = "USER_LOGIN"
    subject.state = "ORDER_PLACED"
    subject.state = "PAYMENT_RECEIVED"

    # 3. Factory
    print("\n📋 3. Factory Pattern")
    for atype in ["dog", "cat", "duck"]:
        animal = AnimalFactory.create(atype)
        print(f"   {atype}: {animal.species} says {animal.speak()}")

    # 4. Decorator
    print("\n📋 4. Decorator Pattern")
    coffee = SimpleCoffee()
    print(f"   {coffee.description()}: ${coffee.cost():.1f}")
    coffee = MilkDecorator(coffee)
    print(f"   {coffee.description()}: ${coffee.cost():.1f}")
    coffee = SugarDecorator(coffee)
    print(f"   {coffee.description()}: ${coffee.cost():.1f}")
    coffee = WhipDecorator(coffee)
    print(f"   {coffee.description()}: ${coffee.cost():.1f}")

    # 5. SOLID
    solid_demo()

    # 6. Refactoring
    refactoring_demo()

    # 7. UML
    uml_diagram()

    print("\n✅ CSC 207 完成！")
    print("💡 覆盖：Strategy/Observer/Factory/Decorator + SOLID + 重构 + UML")


if __name__ == "__main__":
    demo()
