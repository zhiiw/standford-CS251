#!python3

import sys
import hashlib
from base64 import b64encode, b64decode
import math

prooffile = "proof.txt"  # File where Merkle proof will be written.

MAXHEIGHT = 20  # Max height of Merkle tree


class MerkleProof:
    def __init__(self, leaf, pos, path):
        self.leaf = leaf  # data of leaf being checked
        self.pos = pos  # the position in the tree of the leaf being checked
        self.path = path  # the path of hashes, from bottom to the top of tree


def hash_leaf(leaf):
    """hash a leaf value."""
    sha256 = hashlib.sha256()
    sha256.update(b"leaf:")  # hash prefix for a leaf
    sha256.update(leaf)

    return sha256.digest()


def hash_internal_node(left, right):
    """hash an internal node."""
    sha256 = hashlib.sha256()
    sha256.update(b"node:")  # hash prefix for an internal node
    sha256.update(left)
    sha256.update(right)
    return sha256.digest()


##  The prefixes in the two functions above are a security measure.
##  They provide domain separation, meaning that the domain of a leaf hash
##  is seperated from the domain of an internal node hash.
##  This ensures that the verifier cannot mistake a leaf hash for 
##  an internal node hash, and vice versa. 


def gen_merkle_proof(leaves, pos):
    """Takes as input a list of leaves and a leaf position (pos).
       Returns the Merkle proof for the leaf at pos."""

    height = math.ceil(math.log(len(leaves), 2))
    assert height < MAXHEIGHT, "Too many leaves."

    # hash all the leaves
    state = list(map(hash_leaf, leaves))

    # Pad the list of hashed leaves to a power of two
    padlen = (2 ** height) - len(leaves)
    state += [b"\x00"] * padlen

    # initialize a list that will contain the hashes in the proof
    path = []

    level_pos = pos  # local copy of pos
    temp_list = state  # local copy of state
    for level in range(height):

        # compute the sibling position
        if level_pos % 2 == 0:
            sibling_pos = level_pos + 1
        else:
            sibling_pos = level_pos - 1

        # append the sibling hash to the proof
        path.append(temp_list[sibling_pos])
        temp_list = list(map(hash_internal_node, temp_list[::2], temp_list[1::2]))
        level_pos = level_pos // 2

    # create and return the Merkle proof

    # return a list of hashes that makes up the Merkle proof
    return path


### Helper function
def write_proof(filename, proof: MerkleProof):
    fp = open(filename, "w")
    print("leaf position: {pos:d}".format(pos=proof.pos), file=fp)
    print("leaf value: \"{leaf:s}\"".format(leaf=proof.leaf.decode('utf-8')), file=fp)
    print("Hash values in proof:", file=fp)
    for i in range(len(proof.path)):
        print("  {:s}".format(b64encode(proof.path[i]).decode('utf-8')), file=fp)
    fp.close()


### Main program
if __name__ == "__main__":
    # Generate 1000 leaves
    leaves = [b"data item " + str(i).encode() for i in range(1000)]
    print('\nI generated 1000 leaves for a Merkle tree of height 10.')

    # Generate proof for leaf #743
    pos = 743
    path = gen_merkle_proof(leaves, pos)
    proof = MerkleProof(leaves[pos], pos, path)

    # write proof to file
    write_proof(prooffile, proof)

    print('I generated a Merkle proof for leaf #{} in file {}\n'.format(pos, prooffile))
    sys.exit(0)



