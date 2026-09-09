import sys
from algorithms.sorting_search import SortingAlgorithms, SearchAlgorithms
from algorithms.data_structures import LinkedList, Stack, Queue, BinarySearchTree


def demo_algorithms():
    print("=== 算法演示 ===")
    
    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数组: {arr}")
    print(f"冒泡排序: {SortingAlgorithms.bubble_sort(arr.copy())}")
    print(f"快速排序: {SortingAlgorithms.quick_sort(arr.copy())}")
    print(f"归并排序: {SortingAlgorithms.merge_sort(arr.copy())}")
    
    sorted_arr = sorted(arr)
    target = 22
    print(f"\n在 {sorted_arr} 中查找 {target}")
    print(f"二分查找: 位置 {SearchAlgorithms.binary_search(sorted_arr, target)}")
    print(f"线性查找: 位置 {SearchAlgorithms.linear_search(sorted_arr, target)}")


def demo_data_structures():
    print("\n=== 数据结构演示 ===")
    
    ll = LinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    print(f"链表: {ll.display()}")
    
    stack = Stack()
    stack.push(10)
    stack.push(20)
    stack.push(30)
    print(f"栈: 大小={stack.size()}, 栈顶={stack.peek()}")
    print(f"出栈: {stack.pop()}")
    
    queue = Queue()
    queue.enqueue(100)
    queue.enqueue(200)
    print(f"队列: 大小={queue.size()}")
    print(f"出队: {queue.dequeue()}")
    
    bst = BinarySearchTree()
    for num in [5, 3, 7, 1, 9]:
        bst.insert(num)
    print(f"二叉搜索树中序遍历: {bst.inorder_traversal()}")


def main():
    print("Python 综合学习项目演示")
    print("=" * 50)
    
    demo_algorithms()
    demo_data_structures()
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("\n可用模块:")
    print("- algorithms: 算法与数据结构")
    print("- data_analysis: 数据分析与可视化")
    print("- ai_ml: 人工智能与机器学习")
    print("- web: Web应用开发")
    print("- system: 系统工具")
    print("- backend: 后端工具")
    print("\n运行测试: pytest tests/")
    print("\n启动Flask应用: python -m web.flask_app")
    print("启动FastAPI应用: python -m web.fastapi_app")


if __name__ == "__main__":
    main()