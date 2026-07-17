# File System (In-Memory)

> Files/dirs, path ops → **Composite pattern**. 🟡

## Scope / Requirements

**In scope**
- Directory tree; create file/dir; `ls`, `cd`-style path resolve; read/write file content.
- Paths absolute (`/a/b`) simplified; no real OS mounts.

**Out of scope**
- Permissions ACL product, links, journaling disk, concurrent multi-user FS full POSIX.

**Domain invariants**
- Unique child name under a directory.
- Path resolution: each component must exist and be a directory except the final for file ops.
- Cannot `mkdir` where a node exists; cannot write to a directory as a file.
- Deleting a directory: empty-only or recursive — **pick and state**.
- Root exists and has no parent.

## Core Entities & Responsibilities

| Entity | Responsibility |
|--------|----------------|
| `Node` | Common: name, parent. |
| `File` | Bytes/string content. |
| `Directory` | Children map; composite. |
| `FileSystem` | Path parse + operations API. |

## Key Interfaces / Patterns

- **Composite:** treat file and directory uniformly as `Node` where possible (`name`, `isDir`).
- **Interpreter (light):** path string → node walk.

## End-to-End Flow

1. `mkdir("/docs")`, `write("/docs/a.txt", "hi")`.
2. `ls("/docs")` → `a.txt`.
3. `read("/docs/a.txt")` → `hi`.

## Python Skeleton

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class Node(ABC):
    def __init__(self, name: str, parent: Optional["Directory"] = None):
        self.name = name
        self.parent = parent

    @abstractmethod
    def is_dir(self) -> bool: ...


@dataclass
class File(Node):
    content: str = ""

    def __init__(self, name: str, parent: Directory | None = None, content: str = ""):
        super().__init__(name, parent)
        self.content = content

    def is_dir(self) -> bool:
        return False


class Directory(Node):
    def __init__(self, name: str, parent: Directory | None = None):
        super().__init__(name, parent)
        self.children: dict[str, Node] = {}

    def is_dir(self) -> bool:
        return True

    def add(self, node: Node) -> None:
        if node.name in self.children:
            raise RuntimeError("exists")
        node.parent = self
        self.children[node.name] = node


class FileSystem:
    def __init__(self):
        self.root = Directory("/")

    def _resolve(self, path: str, create_file: bool = False) -> Node:
        if not path.startswith("/"):
            raise ValueError("absolute paths only")
        parts = [p for p in path.split("/") if p]
        cur: Directory = self.root
        for i, part in enumerate(parts):
            last = i == len(parts) - 1
            if part not in cur.children:
                if last and create_file:
                    f = File(part, cur)
                    cur.add(f)
                    return f
                raise FileNotFoundError(path)
            node = cur.children[part]
            if last:
                return node
            if not node.is_dir():
                raise NotADirectoryError(part)
            cur = node  # type: ignore
        return self.root

    def mkdir(self, path: str) -> None:
        parts = [p for p in path.split("/") if p]
        cur = self.root
        for part in parts:
            if part not in cur.children:
                cur.add(Directory(part, cur))
            node = cur.children[part]
            if not node.is_dir():
                raise RuntimeError("file in path")
            cur = node  # type: ignore

    def write(self, path: str, content: str) -> None:
        node = self._resolve(path, create_file=True)
        if node.is_dir():
            raise IsADirectoryError(path)
        node.content = content  # type: ignore

    def read(self, path: str) -> str:
        node = self._resolve(path)
        if node.is_dir():
            raise IsADirectoryError(path)
        return node.content  # type: ignore

    def ls(self, path: str = "/") -> list[str]:
        node = self._resolve(path)
        if not node.is_dir():
            return [node.name]
        return sorted(node.children.keys())  # type: ignore
```

## Go Skeleton

```go
package fs

import (
    "errors"
    "strings"
)

type Node interface {
    Name() string
    IsDir() bool
}

type File struct {
    name    string
    Content string
}

func (f *File) Name() string { return f.name }
func (f *File) IsDir() bool  { return false }

type Dir struct {
    name     string
    Children map[string]Node
}

func (d *Dir) Name() string { return d.name }
func (d *Dir) IsDir() bool  { return true }

type FileSystem struct{ Root *Dir }

func New() *FileSystem {
    return &FileSystem{Root: &Dir{name: "/", Children: map[string]Node{}}}
}

func (fs *FileSystem) Mkdir(path string) error {
    cur := fs.Root
    for _, part := range split(path) {
        n, ok := cur.Children[part]
        if !ok {
            d := &Dir{name: part, Children: map[string]Node{}}
            cur.Children[part] = d
            cur = d
            continue
        }
        d, ok := n.(*Dir)
        if !ok {
            return errors.New("not a directory")
        }
        cur = d
    }
    return nil
}

func (fs *FileSystem) Write(path, content string) error {
    parts := split(path)
    if len(parts) == 0 {
        return errors.New("invalid")
    }
    cur := fs.Root
    for _, part := range parts[:len(parts)-1] {
        n, ok := cur.Children[part]
        if !ok {
            return errors.New("missing dir")
        }
        d, ok := n.(*Dir)
        if !ok {
            return errors.New("not a directory")
        }
        cur = d
    }
    name := parts[len(parts)-1]
    if n, ok := cur.Children[name]; ok {
        if n.IsDir() {
            return errors.New("is directory")
        }
        n.(*File).Content = content
        return nil
    }
    cur.Children[name] = &File{name: name, Content: content}
    return nil
}

func (fs *FileSystem) Read(path string) (string, error) {
    n, err := fs.resolve(path)
    if err != nil {
        return "", err
    }
    f, ok := n.(*File)
    if !ok {
        return "", errors.New("is directory")
    }
    return f.Content, nil
}

func (fs *FileSystem) resolve(path string) (Node, error) {
    cur := Node(fs.Root)
    for _, part := range split(path) {
        d, ok := cur.(*Dir)
        if !ok {
            return nil, errors.New("not a directory")
        }
        n, ok := d.Children[part]
        if !ok {
            return nil, errors.New("not found")
        }
        cur = n
    }
    return cur, nil
}

func split(path string) []string {
    var out []string
    for _, p := range strings.Split(path, "/") {
        if p != "" {
            out = append(out, p)
        }
    }
    return out
}
```

## Concurrency / Consistency

- Per-directory lock or global FS mutex for interview.
- Real FS: inode locks; mention only if asked.

## Extensions / Trade-offs / Pitfalls

- Soft links, move/rename, size quotas.
- Pitfall: not distinguishing file vs dir in path walk.
- Composite `ls` recursion for tree print — nice demo.

## Interview Discussion Points

- Why Composite vs separate APIs only?
- How would you add `chmod` without exploding every call site?
- Memory representation vs inode-like ids for large trees?

## Exercise

Create `/a/b`, write `/a/b/c.txt`, `ls /a/b`, read file.

**Follow-ups**
1. Implement `rm` for files and empty dirs.
2. Add `tree()` using composite recursion.
3. Support relative paths with a `cwd` on a session object.
