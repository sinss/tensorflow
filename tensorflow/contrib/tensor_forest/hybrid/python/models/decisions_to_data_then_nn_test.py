# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for the hybrid tensor forest model."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random

# pylint: disable=unused-import

from tensorflow.contrib.tensor_forest.hybrid.python.models import decisions_to_data_then_nn
from tensorflow.contrib.tensor_forest.python import tensor_forest
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import test_util
from tensorflow.python.framework.ops import Operation
from tensorflow.python.framework.ops import Tensor
from tensorflow.python.ops import variable_scope
from tensorflow.python.platform import googletest


class DecisionsToDataThenNNTest(test_util.TensorFlowTestCase):

  def setUp(self):
    self.params = tensor_forest.ForestHParams(
        num_classes=2,
        num_features=31,
        layer_size=11,
        num_layers=13,
        num_trees=17,
        connection_probability=0.1,
        hybrid_tree_depth=4,
        regularization_strength=0.01,
        learning_rate=0.01,
        regularization="",
        weight_init_mean=0.0,
        weight_init_std=0.1)
    self.params.regression = False
    self.params.num_nodes = 2**self.params.hybrid_tree_depth - 1
    self.params.num_leaves = 2**(self.params.hybrid_tree_depth - 1)

  def testHParams(self):
    self.assertEquals(self.params.num_classes, 2)
    self.assertEquals(self.params.num_features, 31)
    self.assertEquals(self.params.layer_size, 11)
    self.assertEquals(self.params.num_layers, 13)
    self.assertEquals(self.params.num_trees, 17)
    self.assertEquals(self.params.hybrid_tree_depth, 4)
    self.assertEquals(self.params.connection_probability, 0.1)

    # Building the graphs modifies the params.
    with variable_scope.variable_scope("DecisionsToDataThenNNTest_testHParams"):
      # pylint: disable=W0612
      graph_builder = decisions_to_data_then_nn.DecisionsToDataThenNN(
          self.params)

      # Tree with depth 4 should have 2**0 + 2**1 + 2**2 + 2**3 = 15 nodes.
      self.assertEquals(self.params.num_nodes, 15)

  def testConstructionPollution(self):
    """Ensure that graph building doesn't modify the params in a bad way."""
    # pylint: disable=W0612
    data = [[random.uniform(-1, 1) for i in range(self.params.num_features)]
            for _ in range(100)]

    self.assertTrue(isinstance(self.params, tensor_forest.ForestHParams))
    self.assertFalse(
        isinstance(self.params.num_trees, tensor_forest.ForestHParams))

    with variable_scope.variable_scope(
        "DecisionsToDataThenNNTest_testConstructionPollution"):
      graph_builder = decisions_to_data_then_nn.DecisionsToDataThenNN(
          self.params)

      self.assertTrue(isinstance(self.params, tensor_forest.ForestHParams))
      self.assertFalse(
          isinstance(self.params.num_trees, tensor_forest.ForestHParams))

  def testInferenceConstruction(self):
    # pylint: disable=W0612
    data = constant_op.constant(
        [[random.uniform(-1, 1) for i in range(self.params.num_features)]
         for _ in range(100)])

    with variable_scope.variable_scope(
        "DecisionsToDataThenNNTest_testInferenceConstruction"):
      graph_builder = decisions_to_data_then_nn.DecisionsToDataThenNN(
          self.params)
      graph = graph_builder.inference_graph(data, None)

      self.assertTrue(isinstance(graph, Tensor))

  def testTrainingConstruction(self):
    # pylint: disable=W0612
    data = constant_op.constant(
        [[random.uniform(-1, 1) for i in range(self.params.num_features)]
         for _ in range(100)])

    labels = [1 for _ in range(100)]

    with variable_scope.variable_scope(
        "DecisionsToDataThenNNTest_testTrainingConstruction"):
      graph_builder = decisions_to_data_then_nn.DecisionsToDataThenNN(
          self.params)
      graph = graph_builder.training_graph(data, labels, None)

      self.assertTrue(isinstance(graph, Operation))


if __name__ == "__main__":
  googletest.main()
