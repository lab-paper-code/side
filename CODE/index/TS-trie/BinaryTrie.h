#ifndef BINARYTRIE_H_
#define BINARYTRIE_H_

#include <cstdlib>
#include <iostream>
#include <vector>

namespace ods {

struct Data {
	unsigned long long x;
	int j;
	int p;
	int l;
	int r;
};


template<class N, class T, class U>
class BinaryTrieNode {
public:
	static const int POINTER_NULL_INT = -1;

	T x;

	U jump;
	U parent;

	union {
		struct {
			U left;
			U right;
		};
		U child[2];
	};
	
	BinaryTrieNode() {
		left = right = parent = jump = POINTER_NULL_INT;
	}
};


template<class Node, class T>
class BinaryTrie {	
protected:
	static const int h = 64;
	static const int temp_h = 20;  // height of temporal tree index
	static const int spat_h = 43;  // height of spatial tree index
	int STD_ARR_SIZE = 100000000;
	static const int DUMMY_IDX = 0;
	static const int ROOT_IDX = 1;

public:
	static const int POINTER_NULL_INT = -1;
	T null;
	enum { left, right };
	int n;
	std::vector<Node> arr;

	unsigned IDX;

	BinaryTrie();
	virtual ~BinaryTrie();
	bool add(T x);
	int temp_find(T x);
	int spat_find(T x, int l, long long t);
	bool IdxToFile();
	int size() { return n; }
};


template<class Node, class T>
BinaryTrie<Node,T>::BinaryTrie() {

	arr.reserve(STD_ARR_SIZE);

	arr.push_back(*(new Node()));
	arr[DUMMY_IDX].left = DUMMY_IDX;
	arr[DUMMY_IDX].right = DUMMY_IDX;

	arr.push_back(*(new Node()));
	arr[ROOT_IDX].jump = 0;

	IDX=ROOT_IDX+1;
	n = 0;
}


template<class Node, class T>
BinaryTrie<Node,T>::~BinaryTrie() {
	
}


template<class Node, class T>
bool BinaryTrie<Node,T>::add(T x) {	//assign child, parent, next, prev, left, right
	if (IDX > arr.size()){
		arr.reserve(arr.size() + STD_ARR_SIZE);
	}

	int i, c = 0;
	unsigned long long ix = x;
	unsigned long long tx = ix >> 44;
	int u = ROOT_IDX;
	// 1 - search for ix until falling out of the trie
	for (i = 0; i < temp_h; i++) {
		c = (ix >> (h-i-1)) & 1;
		if (arr[u].child[c] == POINTER_NULL_INT) break;
		u = arr[u].child[c];
	}
	
	if (i != temp_h) {
		int pred = (c == right) ? arr[u].jump : arr[arr[u].jump].left;
		arr[u].jump = POINTER_NULL_INT;  // u will have two children shortly

		// 2 - add path to ix
		for (; i < temp_h; i++) {
			c = (ix >> (h-i-1)) & 1;
			arr[u].child[c] = IDX;
			arr.push_back(*(new Node()));
			IDX++;
			arr[arr[u].child[c]].parent = u;
			u = arr[u].child[c];
		}
		
		arr[u].x = tx;
		int v = arr[u].parent;

		// 3 - add u to linked list
		// in temporal last node (20 bit), parent mean prev node and jump mean next node because they do not need jump pointer and parent pointer. 
		// to save memory size, use same variable 
		arr[u].parent = pred;
		arr[u].jump = arr[pred].jump;
		arr[arr[u].parent].jump = u;
		arr[arr[u].jump].parent = u;

		while (v != POINTER_NULL_INT) {
			if ((arr[v].left == POINTER_NULL_INT
					&& (arr[v].jump == POINTER_NULL_INT || arr[arr[v].jump].x > ix))
			|| (arr[v].right == POINTER_NULL_INT
					&& (arr[v].jump == POINTER_NULL_INT || arr[arr[v].jump].x < ix))){
				arr[v].jump = u;
			}
			v = arr[v].parent;
		}
	}

	// 4 - search for ix until falling out of the trie
	for (i = 0; i < spat_h; i++) {
		c = (ix >> (spat_h-i)) & 1;
		if (arr[u].child[c] == POINTER_NULL_INT) break;
		u = arr[u].child[c];
	}

	if (i == spat_h) return false;  // already exist

	// 5 - add path to ix
	for (; i < spat_h; i++) {
		c = (ix >> (spat_h-i)) & 1;
		arr[u].child[c] = IDX;
		arr.push_back(*(new Node()));
		IDX++;
		u = arr[u].child[c];
	}
	
	arr[u].x = x;
	n++;

	return true;
}


template<class Node, class T>
int BinaryTrie<Node, T>::temp_find(T x) {	//find index in range of temporal trie
	int i, c = 0;
	int blanknode = 0;
	int ix = x;
	int u = ROOT_IDX;
	for (i = 0; i < temp_h; i++) {
		c = (ix >> (temp_h-i-1)) & 1;
		if (arr[u].child[c] == POINTER_NULL_INT) break;
		u = arr[u].child[c];
	}
	if (i == temp_h) return u;  // found it
	u = (c == 0) ? arr[u].jump : arr[arr[u].jump].jump;
	return u == POINTER_NULL_INT ? blanknode : u;
}


template<class Node, class T>
int BinaryTrie<Node, T>::spat_find(T x, int l, long long t) {	//find index in range of spatial trie
	int i, c = 0;
	int spat_len = 2*l + 4; // we only 2*level+4 bits when check the (level)-th S2cell
	unsigned long long ix = x;
	long long u = t;


	for (i = 0; i < spat_len - 1; i++) {
		c = (ix >> (h - i - 1)) & 1;
		if (arr[u].child[c] == POINTER_NULL_INT) break;
		u = arr[u].child[c];
	}
	
	if (i == spat_len - 1)	return u;  // found it
	return POINTER_NULL_INT;
}


template<class Node, class T>
bool BinaryTrie<Node, T>::IdxToFile(){
	FILE *fp;
	fp = fopen("index.dat", "wb");
	fwrite(&(arr[0]), sizeof(arr[0]), arr.size(), fp);
	fclose(fp);
	return true;
}


template<class T, class U>
class BinaryTrieNode1 : public BinaryTrieNode<BinaryTrieNode1<T, U>, T, U> { };

template<class T, class U>
class BinaryTrie1 : public BinaryTrie<BinaryTrieNode1<T,U>, T> {};

} // namespace ods

#endif // #ifndef BINARYTRIE_H_