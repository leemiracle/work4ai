import pytest
from algorithms.sorting_search import SortingAlgorithms, SearchAlgorithms
from algorithms.data_structures import LinkedList, Stack, Queue, BinarySearchTree


class TestSortingAlgorithms:
    
    def test_bubble_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        result = SortingAlgorithms.bubble_sort(arr.copy())
        assert result == sorted(arr)
    
    def test_quick_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        result = SortingAlgorithms.quick_sort(arr.copy())
        assert result == sorted(arr)
    
    def test_merge_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        result = SortingAlgorithms.merge_sort(arr.copy())
        assert result == sorted(arr)


class TestSearchAlgorithms:
    
    def test_binary_search(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert SearchAlgorithms.binary_search(arr, 5) == 4
        assert SearchAlgorithms.binary_search(arr, 1) == 0
        assert SearchAlgorithms.binary_search(arr, 10) == 9
        assert SearchAlgorithms.binary_search(arr, 11) == -1
    
    def test_linear_search(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert SearchAlgorithms.linear_search(arr, 5) == 4
        assert SearchAlgorithms.linear_search(arr, 1) == 0
        assert SearchAlgorithms.linear_search(arr, 11) == -1


class TestDataStructures:
    
    def test_linked_list(self):
        ll = LinkedList()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert "1" in ll.display()
        assert "2" in ll.display()
        assert "3" in ll.display()
    
    def test_stack(self):
        stack = Stack()
        assert stack.is_empty()
        
        stack.push(1)
        stack.push(2)
        stack.push(3)
        
        assert stack.size() == 3
        assert stack.peek() == 3
        assert stack.pop() == 3
        assert stack.size() == 2
    
    def test_queue(self):
        queue = Queue()
        assert queue.is_empty()
        
        queue.enqueue(1)
        queue.enqueue(2)
        queue.enqueue(3)
        
        assert queue.size() == 3
        assert queue.dequeue() == 1
        assert queue.size() == 2
    
    def test_binary_search_tree(self):
        bst = BinarySearchTree()
        bst.insert(5)
        bst.insert(3)
        bst.insert(7)
        bst.insert(1)
        bst.insert(9)
        
        inorder = bst.inorder_traversal()
        assert inorder == [1, 3, 5, 7, 9]