# Distributed Cache Client — Design Doc & Go Implementation

This document outlines a Go library that acts as the client for a distributed cache system spanning multiple nodes, using consistent hashing to efficiently route requests. Comments and explanatory notes are provided throughout the code and doc to clarify design and implementation decisions.

---

## 1. Requirements

- The client library needs to provide methods: `Get(key)`, `Set(key, value)`, and `Delete(key)`.
- The cache should be transparently distributed across many nodes.
- Each key must always map to the same node (unless topology changes).
- Adding/removing nodes should only remap a minimal number of keys (not reshuffle all keys).
- The design should support extensibility for concerns like retries, timeouts, replication, and serialization.

---



## 2. Architecture Overview

```
Application
   |
DistributedCacheClient
   |
+-----------------+      +---------------+      +---------------+
|  Cache Node 1   |      |  Cache Node 2 | ...  |  Cache Node N |
+-----------------+      +---------------+      +---------------+
```

The client must answer:

- Which cache node should a given key use?
- How to handle a request if a cache node is unavailable?
- How to minimize remapping of keys if nodes are added or removed?

---



## 3. Core Components

- `DistributedCacheClient`: Main API for application code.
- `CacheNode`: Abstraction of a single cache node (could be remote or in-memory in tests).
- `NodeClient`: Handles communication with a single cache node (could wrap retries etc).
- `ConsistentHashRing`: Distributes keys among nodes using consistent hashing.
- `RetryPolicy`: (Extensible) Determines behavior on failure, e.g., retry attempts.

---



## 4. Go Implementation

Explanatory comments are included throughout to clarify design choices and logic.

```go
package cacheclient

import (
    "errors"
    "fmt"
    "hash/crc32"
    "sort"
    "strconv"
    "sync"
)

// --------------------
// Cache Node Interface
// --------------------

// CacheNode defines how the client interacts with an underlying cache node.
// Realistic implementations would perform network communication.
type CacheNode interface {
    Get(key string) (string, error)
    Set(key, value string) error
    Delete(key string) error
    Address() string           // Used for consistent hashing ring
}

// -----------------------------------
// NodeClient: Wrapping a Cache Node
// -----------------------------------

// NodeClient wraps a CacheNode and is a convenient place to add
// retries, timeouts, or serialization (not shown in this basic example).
type NodeClient struct {
    node CacheNode
}

func (c *NodeClient) Get(key string) (string, error)   { return c.node.Get(key) }
func (c *NodeClient) Set(key, value string) error      { return c.node.Set(key, value) }
func (c *NodeClient) Delete(key string) error          { return c.node.Delete(key) }
func (c *NodeClient) Address() string                  { return c.node.Address() }

// -------------------------------------
// Consistent Hash Ring Implementation
// -------------------------------------

// ConsistentHashRing maps keys to nodes using the consistent hashing algorithm.
// 'replicaN' determines how many virtual nodes each real node gets for better distribution.
type ConsistentHashRing struct {
    hashKeys []uint32           // Sorted hash ring (virtual nodes)
    nodeMap  map[uint32]*NodeClient
    replicaN int
    hashLock sync.RWMutex
}

// NewConsistentHashRing initializes a new hash ring.
func NewConsistentHashRing(replicaN int) *ConsistentHashRing {
    return &ConsistentHashRing{
        nodeMap:  make(map[uint32]*NodeClient),
        replicaN: replicaN,
    }
}

// AddNode places multiple replicas of the node on the hash ring for load distribution.
func (r *ConsistentHashRing) AddNode(node *NodeClient) {
    r.hashLock.Lock()
    defer r.hashLock.Unlock()
    for i := 0; i < r.replicaN; i++ {
        hash := crc32.ChecksumIEEE([]byte(node.Address() + ":" + strconv.Itoa(i)))
        r.hashKeys = append(r.hashKeys, hash)
        r.nodeMap[hash] = node
    }
    // Always keep the hash keys sorted for efficient lookup.
    sort.Slice(r.hashKeys, func(i, j int) bool { return r.hashKeys[i] < r.hashKeys[j] })
}

// RemoveNode eliminates all virtual node entries for the specified address from the ring.
func (r *ConsistentHashRing) RemoveNode(address string) {
    r.hashLock.Lock()
    defer r.hashLock.Unlock()
    filtered := r.hashKeys[:0]
    for _, hash := range r.hashKeys {
        if r.nodeMap[hash].Address() == address {
            delete(r.nodeMap, hash)
        } else {
            filtered = append(filtered, hash)
        }
    }
    r.hashKeys = filtered
}

// GetNode determines the correct node for a given key using consistent hashing.
func (r *ConsistentHashRing) GetNode(key string) (*NodeClient, error) {
    r.hashLock.RLock()
    defer r.hashLock.RUnlock()
    if len(r.hashKeys) == 0 {
        return nil, errors.New("no nodes in hash ring")
    }
    h := crc32.ChecksumIEEE([]byte(key))
    // Find first hash >= h; wrap around if needed.
    idx := sort.Search(len(r.hashKeys), func(i int) bool { return r.hashKeys[i] >= h })
    if idx == len(r.hashKeys) {
        idx = 0
    }
    return r.nodeMap[r.hashKeys[idx]], nil
}

// -----------------------------------
// Distributed Cache Client API
// -----------------------------------

// DistributedCacheClient exposes the methods used by application code.
// It hides details of distribution and hashing.
type DistributedCacheClient struct {
    ring *ConsistentHashRing
}

// NewDistributedCacheClient creates the client and internally constructs a hash ring.
func NewDistributedCacheClient(nodes []CacheNode) *DistributedCacheClient {
    ring := NewConsistentHashRing(100) // 100 virtual nodes per real node for even key spread
    for _, n := range nodes {
        nc := &NodeClient{node: n}
        ring.AddNode(nc)
    }
    return &DistributedCacheClient{ring: ring}
}

// Get/Set/Delete all consult the hash ring to find the right node for each key.
func (c *DistributedCacheClient) Get(key string) (string, error) {
    node, err := c.ring.GetNode(key)
    if err != nil {
        return "", err
    }
    return node.Get(key)
}

func (c *DistributedCacheClient) Set(key, value string) error {
    node, err := c.ring.GetNode(key)
    if err != nil {
        return err
    }
    return node.Set(key, value)
}

func (c *DistributedCacheClient) Delete(key string) error {
    node, err := c.ring.GetNode(key)
    if err != nil {
        return err
    }
    return node.Delete(key)
}

// -----------------------------------------------------------------
// DummyCacheNode: In-memory implementation for demonstration/testing
// -----------------------------------------------------------------

// DummyCacheNode simulates a cache node locally.
type DummyCacheNode struct {
    addr  string
    store map[string]string
    mu    sync.RWMutex
}

func NewDummyCacheNode(addr string) *DummyCacheNode {
    return &DummyCacheNode{addr: addr, store: make(map[string]string)}
}
func (d *DummyCacheNode) Get(key string) (string, error) {
    d.mu.RLock()
    defer d.mu.RUnlock()
    val, ok := d.store[key]
    if !ok {
        return "", errors.New("not found")
    }
    return val, nil
}
func (d *DummyCacheNode) Set(key, value string) error {
    d.mu.Lock()
    defer d.mu.Unlock()
    d.store[key] = value
    return nil
}
func (d *DummyCacheNode) Delete(key string) error {
    d.mu.Lock()
    defer d.mu.Unlock()
    delete(d.store, key)
    return nil
}
func (d *DummyCacheNode) Address() string {
    return d.addr
}

// -----------------------
// Example Usage / Testing
// -----------------------

// This main demonstrates creating three dummy nodes,
// putting them in the distributed client, and performing basic ops.
func main() {
    nodes := []CacheNode{
        NewDummyCacheNode("node1"),
        NewDummyCacheNode("node2"),
        NewDummyCacheNode("node3"),
    }
    client := NewDistributedCacheClient(nodes)

    // Set operation routes "foo" and "baz" to their respective nodes
    client.Set("foo", "bar")
    client.Set("baz", "qux")

    // Get operation accesses the same node "foo" was placed on
    v, _ := client.Get("foo")
    fmt.Println("foo =", v)

    v2, _ := client.Get("baz")
    fmt.Println("baz =", v2)
}
```

---



## 5. Extensibility & Production Considerations

- Retry, timeout, network connection, and serialization should be layered into `NodeClient` as needed.
- In the real world, failures to contact a node can be handled by fallback policies or by considering replication.
- Virtual nodes (replica count) improve key distribution, especially when the node count is small.

---

**Summary:**
This Go implementation covers the general design and coding of a distributed cache client that employs consistent hashing. The code is commented for clarity. In practice, the `CacheNode` interface would be backed by remote calls or networked clients, and more advanced concerns would be layered on as wrappable decorators or policies.