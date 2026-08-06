# A Bloom filter is a space-efficient probabilistic data structure used to test whether an element is a member of a set.
# It can quickly tell if an item is definitely not in the set, or might be in the set (with some probability of false positives,
# but zero false negatives).
# Bloom filters use multiple independent hash functions to map each item into a bit array.
# To add an element, you compute several hashes and set the bits at those positions. To check membership, 
# you see if all corresponding bits are set.
# 
# Example:
# Suppose you have a Bloom filter with a bit array of size 10 and 3 hash functions.
# Let's say you add "apple" to the filter. Each hash function produces a position in the array, say 2, 5, and 7. We set those bits to 1.
# To check if "banana" is in the filter, we hash it with the 3 functions. If any bit at those positions is 0, then "banana" is definitely not present.
# However, if all bits are set (possibly by other elements), it *might* be present (could be a false positive).
# 
# You can try implementing this logic in Python using standard hash functions (e.g., hashlib with different seeds or salts) 
# and a bit array (e.g., using the bitarray module or a simple list of 0/1s).


import hashlib

class BloomFilter:
    def __init__(self, size=100, num_hashes=3):
        self.size = size                    # Number of bits in the bloom filter
        self.num_hashes = num_hashes        # Number of hash functions
        self.bit_array = [0] * size         # The bit array, simple Python list

    def _hashes(self, item):
        # Generate k different hash values for the item, as indices into the bit array
        hashes = []
        item_bytes = str(item).encode('utf-8')
        # For each hash function needed:
        hashes = []
        for i in range(self.num_hashes):
            # - 'i' is the hash function number.
            # - We make the hash for 'item' unique for each i by appending i to the bytes.
            # - i.to_bytes(2, 'little') turns i into 2 bytes for use as salt.
            salted_bytes = item_bytes + i.to_bytes(2, 'little')  # salt the input for independence
            hash_obj = hashlib.sha256(salted_bytes)              # hash the salted bytes
            digest_as_int = int.from_bytes(hash_obj.digest(), 'big')  # convert hash to integer
            index = digest_as_int % self.size                    # fit the hash into bit array range
            hashes.append(index)                                 # collect this hash position
        # Return all k (num_hashes) generated indices for this item 
        return hashes

    def add(self, item):
        for idx in self._hashes(item):
            self.bit_array[idx] = 1

    def __contains__(self, item):
        # Check if all bits corresponding to the item's hashes are set to 1
        for idx in self._hashes(item):
            if self.bit_array[idx] == 0:
                return False
        return True
 


if __name__ == "__main__":
    bf = BloomFilter(size=20, num_hashes=3)
    bf.add("apple")
    bf.add("banana")
    bf.add("grape")

    print("apple" in bf)    # Should be True
    print("banana" in bf)   # Should be True
    print("grape" in bf)    # Should be True
    print("orange" in bf)   # Might be False (likely), or True (false positive)
    print("cherry" in bf)   # Might be False (likely), or True (false positive)