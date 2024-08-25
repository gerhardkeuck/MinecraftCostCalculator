import unittest

from main import topological_sort


class TestTopologicalSort(unittest.TestCase):

    def test_basic(self):
        graph = {
            'A': {'B', 'C'},
            'B': {'D'},
            'C': {},
            'D': {}
        }
        result = topological_sort(graph)
        # One possible correct answer is ['A', 'C', 'B', 'D']
        # There might be other correct answers but 'D' should always come after 'B' and 'B' and 'C' should always come after 'A'
        self.assertTrue(result.index('D') > result.index('B'))
        self.assertTrue(result.index('B') > result.index('A'))
        self.assertTrue(result.index('C') > result.index('A'))

    def test_cycle(self):
        graph = {
            'A': {'B'},
            'B': {'A'}
        }
        with self.assertRaises(ValueError):
            topological_sort(graph)

    def test_empty_graph(self):
        graph = {}
        self.assertEqual(topological_sort(graph), [])

    def test_disconnected_graph(self):
        graph = {
            'A': {},
            'B': {},
        }
        result = topological_sort(graph)
        self.assertTrue('A' in result)
        self.assertTrue('B' in result)

    def test_single_node(self):
        graph = {
            'A': {}
        }
        self.assertEqual(topological_sort(graph), ['A'])

    def test_graph_with_self_loop(self):
        graph = {
            'A': {'A'}
        }
        with self.assertRaises(ValueError):
            topological_sort(graph)

    def test_missing_dependency(self):
        graph = {
            'A': {'B'},
        }
        # 'B' is a dependency but doesn't have an explicit entry in the graph
        # The modified algorithm should add 'B' as an entry with no dependencies
        result = topological_sort(graph)
        self.assertTrue(result.index('B') > result.index('A'))
        self.assertIn('B', result)

    def test_multiple_missing_dependencies(self):
        graph = {
            'A': {'B', 'C'},
        }
        result = topological_sort(graph)
        self.assertTrue(result.index('B') > result.index('A'))
        self.assertTrue(result.index('C') > result.index('A'))
        self.assertIn('B', result)
        self.assertIn('C', result)


if __name__ == '__main__':
    unittest.main()
