#!/usr/bin/env python3
"""In-memory B-tree key-value store."""
import bisect

class BTreeNode:
    def __init__(self, leaf=True, t=3):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf
        self.t = t

class BTreeStore:
    def __init__(self, t=3):
        self.t = t
        self.root = BTreeNode(leaf=True, t=t)
        self._size = 0

    def get(self, key, default=None):
        return self._search(self.root, key, default)

    def _search(self, node, key, default):
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        if node.leaf:
            return default
        return self._search(node.children[i], key, default)

    def put(self, key, value):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(leaf=False, t=self.t)
            new_root.children.append(self.root)
            self._split(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)

    def _split(self, parent, i):
        t = self.t
        child = parent.children[i]
        new = BTreeNode(leaf=child.leaf, t=t)
        mid = t - 1
        parent.keys.insert(i, child.keys[mid])
        parent.values.insert(i, child.values[mid])
        parent.children.insert(i + 1, new)
        new.keys = child.keys[mid+1:]
        new.values = child.values[mid+1:]
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]
        if not child.leaf:
            new.children = child.children[mid+1:]
            child.children = child.children[:mid+1]

    def _insert_non_full(self, node, key, value):
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.values[i] = value
            return
        if node.leaf:
            node.keys.insert(i, key)
            node.values.insert(i, value)
            self._size += 1
        else:
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split(node, i)
                if key > node.keys[i]:
                    i += 1
                elif key == node.keys[i]:
                    node.values[i] = value
                    return
            self._insert_non_full(node.children[i], key, value)

    def keys_range(self, lo=None, hi=None):
        result = []
        self._range(self.root, lo, hi, result)
        return result

    def _range(self, node, lo, hi, result):
        for i, k in enumerate(node.keys):
            if not node.leaf:
                if lo is None or k >= lo:
                    self._range(node.children[i], lo, hi, result)
            if (lo is None or k >= lo) and (hi is None or k <= hi):
                result.append((k, node.values[i]))
        if not node.leaf and node.children:
            last = len(node.keys)
            if hi is None or (node.keys and node.keys[-1] <= hi):
                self._range(node.children[last], lo, hi, result)

    def __len__(self):
        return self._size

if __name__ == "__main__":
    store = BTreeStore()
    for i in range(20):
        store.put(i, f"val_{i}")
    print(f"Size: {len(store)}")
    print(f"Get 10: {store.get(10)}")
    print(f"Range 5-10: {store.keys_range(5, 10)}")

def test():
    s = BTreeStore(t=2)
    for i in range(100):
        s.put(i, i * 10)
    assert len(s) == 100
    assert s.get(50) == 500
    assert s.get(999) is None
    assert s.get(999, "default") == "default"
    # Update
    s.put(50, 9999)
    assert s.get(50) == 9999
    # Range query
    r = s.keys_range(10, 15)
    assert len(r) == 6
    assert r[0] == (10, 100)
    # String keys
    s2 = BTreeStore()
    for c in "zyxwvutsrqponmlkjihgfedcba":
        s2.put(c, ord(c))
    assert s2.get("a") == 97
    assert s2.get("z") == 122
    print("  btree_store: ALL TESTS PASSED")
