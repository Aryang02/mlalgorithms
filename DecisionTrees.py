import numpy as np
from collections import Counter

class Node():
  def __init__(self, feature = None, threshold = None, left = None, right = None, *, value = None):
    self.feature = feature
    self.threshold = threshold
    self.left = left
    self.right = right
    self.value = value
    
  def is_leaf_node(self):  
    return self.value is not None
  
  
class DecisionTree():
  
  def __init__(self, min_samples_split = 2, max_depth = 100, n_features = None):
    self.min_samples_split = min_samples_split
    self.max_depth = max_depth
    self.n_features = n_features
    self.root = None
    
  def fit(self, X, y):
    self.n_features = X.shape[1] if not self.n_features else min(X.shape[1], self.n_features)
    self.root = self._grow_tree(X, y)
    
  def _grow_tree(self, X, y, depth = 0):
    n_samples, n_features = X.shape
    n_labels = len(np.unique(y))

    #check stopping criteria
    if(depth>= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split):
      leaf_value = self._most_common_label(y)
      return Node(value = leaf_value)

    #find the best split
    feat_idxs = np.random.choice(n_features, self.n_features, replace = False)
    best_thres, best_feature = self.best_split(X, y, feat_idxs)
    
    #create child nodes
    left_idxs, right_idxs = self._split(X[:, best_feature], best_thres)
    left = self._grow_tree(X[left_idxs, :], y[left_idxs], depth+1)
    right = self._grow_tree(X[right_idxs, :], y[right_idxs], depth+1)
    return Node(best_feature, best_thres, left, right)
  
  def _most_common_label(self, y):
    counter = Counter(y)
    value = counter.most_common(1)[0][0]
    return value
  
  def best_split(self, X, y, feat_idxs):
    best_gain = -1
    split_idx, split_thr = None, None
    
    for feat_idx in feat_idxs:
      X_column = X[:, feat_idx]
      thresholds = np.unique(X_column)
      
      for thr in thresholds:
        gain = self.info_gain(X_column, y, thr)
        
        if gain>best_gain:
          best_gain = gain
          split_idx = feat_idx
          split_thr = thr
    
    return split_thr, split_idx
  
  def info_gain(self, X_column, y, threshold):
    
    #parent entropy
    par_entropy = self.entropy(y)
    
    #create children
    left_idxs, right_idxs = self._split(X_column, threshold)
    if len(left_idxs) == 0 or len(right_idxs) == 0:
      return 0
    
    #calculate weighted avg entropy of children
    n = len(y)
    n_l, n_r = len(left_idxs), len(right_idxs)
    e_l, e_r = self.entropy(y[left_idxs]), self.entropy(y[right_idxs])
    child_entropy = (n_l/n) * e_l + (n_r/n) * e_r
    
    #calculate the info gain
    info_gain = par_entropy - child_entropy
    return info_gain
    
    
  def _split(self, X_column, threshold):
    left_idxs = np.argwhere(X_column <= threshold).flatten()
    right_idxs = np.argwhere(X_column > threshold).flatten()
    return left_idxs, right_idxs
    
  def entropy(self, y):
    hist = np.bincount(y)
    pxs = hist / len(y)
    return -np.sum([p * np.log(p) for p in pxs if p>0])
    
  def predict(self, X):
    return np.array([self._traverse(x, self.root) for x in X])
  
  def _traverse(self, x, node):
    if node.is_leaf_node():
      return node.value
    
    if x[node.feature]<=node.threshold:
      return self._traverse(x, node.left)
    return self._traverse(x, node.right)