#!/usr/bin/env python3
"""B-Tree key-value store with disk-like page simulation."""
import sys, json, bisect

class BTreeNode:
    def __init__(self, leaf=True):
        self.keys, self.values, self.children, self.leaf = [], [], [], leaf

class BTree:
    def __init__(self, order=4):
        self.root, self.order = BTreeNode(), order
    def search(self, key, node=None):
        node = node or self.root
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        if node.leaf: return None
        return self.search(key, node.children[i])
    def insert(self, key, value):
        r = self.root
        if len(r.keys) == 2 * self.order - 1:
            s = BTreeNode(leaf=False); s.children.append(r)
            self._split(s, 0); self.root = s
        self._insert_non_full(self.root, key, value)
    def _insert_non_full(self, node, key, value):
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.values[i] = value; return
        if node.leaf:
            node.keys.insert(i, key); node.values.insert(i, value)
        else:
            if len(node.children[i].keys) == 2 * self.order - 1:
                self._split(node, i)
                if key > node.keys[i]: i += 1
            self._insert_non_full(node.children[i], key, value)
    def _split(self, parent, i):
        t = self.order; child = parent.children[i]
        new = BTreeNode(leaf=child.leaf)
        parent.keys.insert(i, child.keys[t-1])
        parent.values.insert(i, child.values[t-1])
        parent.children.insert(i+1, new)
        new.keys, child.keys = child.keys[t:], child.keys[:t-1]
        new.values, child.values = child.values[t:], child.values[:t-1]
        if not child.leaf:
            new.children, child.children = child.children[t:], child.children[:t]
    def items(self, node=None):
        node = node or self.root
        result = []
        for i, k in enumerate(node.keys):
            if not node.leaf: result.extend(self.items(node.children[i]))
            result.append((k, node.values[i]))
        if not node.leaf and node.children: result.extend(self.items(node.children[-1]))
        return result

def main():
    if len(sys.argv) < 2:
        print("Usage: btree_store.py <get|put|list|demo> [args]"); return
    cmd = sys.argv[1]; tree = BTree()
    if cmd == "demo":
        for i in [5,3,7,1,4,6,8,2,9,0]:
            tree.insert(i, f"val_{i}")
        print(f"Items: {tree.items()}")
        print(f"Search 5: {tree.search(5)}")
        print(f"Search 99: {tree.search(99)}")
    elif cmd == "test":
        t = BTree(order=3)
        for i in range(100): t.insert(i, i*10)
        assert all(t.search(i) == i*10 for i in range(100))
        assert t.search(100) is None
        t.insert(50, 999); assert t.search(50) == 999
        items = t.items(); assert len(items) == 100
        assert items == sorted(items, key=lambda x: x[0])
        print("All tests passed!")
    else: print(f"Unknown: {cmd}")

if __name__ == "__main__": main()
