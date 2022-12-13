# Written by Graham Todd and Sam Earle

import math
import time
import heapq
import numpy as np
from collections import defaultdict

class pStableHash():
    """
        An instance of a p-stable hashing scheme, which can be used for classic LSH, MultiProbeLSH, AlphaLSH, etc.

        Args:
            k: number of bands per hash function
            l: number of hash functions/tables
            r: the width of the intervals for each projection
            n_dims: the number of dimensions in our dataset, required to project data points to random lines
            seed: the random seed
        """
    def __init__(self, k, l, r, n_dims, seed=42):
        
        self.k, self.l, self.r = k, l, r
        self.n_dims = n_dims
        self.seed = seed

        # We use the largest 32-bit integer as our maximum hash value, but this could be changed without too much effort
        self.max_val = 2 ** 32 - 1
        self.p = 4294967311

        # Store each of hash function in an array of size (l, k). self.hash_functions[i][j] indicates the j'th band of the 
        # i'th table
        # self.hash_functions = [[self._generate_hash_function() for _ in range(self.k)]
        #                        for _ in range(self.l)]

        self._generate_hash_functions()

        # This dictionary maps from a data index to a list of l bucket ids (the hash of vector of k integers) indicating the 
        # keys in each hash table where the index can be found
        self.cur_data_idx = 0
        self.data_idx_to_bucket_ids = {}

        # This list stores l dictionaries, each of which maps from a hash value / bucket id to each of the data indexes which 
        # have been hashed to that bucket
        self.tables = [defaultdict(list) for _ in range(self.l)]

    def _generate_hash_function(self):
        '''
        This function should return another function which takes as input a data point (vector) and returns a hash value (an 
        integer). A vector of k such integers defines a data point's "signature" in that table, and the hash value of that 
        signature is the bucket ID
        '''

        # Generate the random projection vector
        a = np.random.normal(0, 1, size=self.n_dims)

        # Sample some random offset to nullify in expectation the effect of bin border placement
        b = np.random.random() * self.r

        # The hash function here actually only projects the item onto a random line, it doesn't assign it to a 
        # random interval. That responsibiltiy belongs to hash() and _get_collision_freqs(), which need to divide
        # the projected value by self.r and apply a floor operator
        def hash_func(x):
            return x.T @ a + b

        return hash_func

    def _generate_hash_functions(self):
        
        # First we need to generate a matrix of random normal vectors that is (l, k, n_dims)
        self.A = np.random.normal(0, 1, size=(self.l, self.k, self.n_dims))

        # Then we generate a matrix of random offsets that is l by k
        self.B = np.random.random(size=(self.l, self.k)) * self.r

    def hash(self, x):
        '''
        Hashes a data point, obtaining a hash value for each of the l tables (based on its value under each of the k bands).
        Returns the 'data index' of the data point as well as the l bucket IDs

        Args:
            x: the data point
        '''

        all_bucket_ids = []

        # This matrix multiplication broadcasts the query point so that we compute the its dot product with each random
        # vector in self.A, before adding the result to the offsets in self.B
        projected = np.matmul(self.A, x) + self.B

        # Next, convert these projections to bucket indices by dividing by r and taking the floor
        bucket_ids = np.floor(projected / self.r).astype(np.int32)

        for table_idx, table_bucket_id in enumerate(bucket_ids):
            table_bucket_id = tuple(table_bucket_id)

            # Add the data index to the current bucket
            self.tables[table_idx][table_bucket_id].append(self.cur_data_idx)
            all_bucket_ids.append(table_bucket_id)

        # Associate the bucket ids with the current data point
        self.data_idx_to_bucket_ids[self.cur_data_idx] = all_bucket_ids
        data_idx = self.cur_data_idx

        # Increment the data index
        self.cur_data_idx += 1

        return data_idx, all_bucket_ids

    def query(self, y):
        '''
        Return all of the previously-hashed approximate near neighbors to a provided query point
        '''
        raise NotImplementedError

    def get_collision_prob(self, similarity):
        '''
        Return the expected probability that the hashing scheme will return an item with specified 
        similarity to an arbitrary query point

        TODO: similarity can techincally represent different quanitites in different domains / contexts. We
            should think about how we wan to define the arguments for this function (i.e. should it take raw 
            distances? actualy pairs of points? etc.)
        '''
        raise NotImplementedError


    def _get_collision_freqs(self, y):
        '''
        For a query data point y, return a dictionary that maps from data indexes to the number of times that
        data point collides with the query point (an integer between 0 and l). 

        NOTE: if y is a data point that has been previously hashed, then this function will include its data
            index, with l collisions

        Args:
            y: a query point
        '''
        collision_freqs = defaultdict(int)

        projected = np.matmul(self.A, y) + self.B
        bucket_ids = np.floor(projected / self.r).astype(np.int32)

        for table_idx, table_bucket_id in enumerate(bucket_ids):
            table_bucket_id = tuple(table_bucket_id)

            # Keep a count of number of collisions with each other item
            for data_index in self.tables[table_idx][table_bucket_id]:
                collision_freqs[data_index] += 1

        return collision_freqs


class VanillaLSH(pStableHash):
    '''
    TODO

    Args:
            k: number of bands per hash function
            l: number of hash functions/tables
            r: the width of the intervals for each projection
            n_dims: the number of dimensions in our dataset, required to project data points to random lines
            seed: the random seed
    '''

    def __init__(self, k, l, r, n_dims, seed=42):
        super().__init__(k, l, r, n_dims, seed)

        self.query_total_times = []
        self.query_scan_times = []

    def query(self, y, timed=False):
        '''
        Returns the data indices of each previously-hashed item which collides with query point in at least one
        of the l tables

        Args:
            y: a query_point
            timed: a flag for whether the time taken to compute steps of the querying process should be recorded
        '''

        if timed: overall_start = time.perf_counter()
        collision_freqs = self._get_collision_freqs(y)

        if timed: scan_start = time.perf_counter()
        neighbor_idxs = list(collision_freqs.keys()) # the collision_freqs dict only includes elements that collide at least once

        if timed:
            end_time = time.perf_counter()
            self.query_total_times.append(end_time - overall_start)
            self.query_scan_times.append(end_time - scan_start)

        return neighbor_idxs


class AlphaLSH(pStableHash):
    '''
    An extension of LSH algorithms for approximate nearest neighbors, designed for use in niching and QD. In addition to 
    the typical parameters of # of tables and # of bands, this also accepts an alpha parameter when querying. An item in 
    the database is returned only if it is hashed into the same bucket as the query in at least alpha of the l tables.

    Args:
            k: number of bands per hash function
            l: number of hash functions/tables
            r: the width of the intervals for each projection
            n_dims: the number of dimensions in our dataset, required to project data points to random lines
            seed: the random seed
    '''

    def __init__(self, k, l, r, n_dims, seed=42):
        super().__init__(k, l, r, n_dims, seed)

        self.query_total_times = []
        self.query_scan_times = []


    def query(self, y, alpha=1, timed=False):
        '''
        Returns the data indices of each previously-hashed item which collides with the query point in at least
        alpha of the l tables

        Args:
            y: a query point
            alpha (int): minimum number of tables in which an item must collide with x in order l be considered a
                neighbor
            timed: a flag for whether the time taken to compute steps of the querying process should be recorded
        '''

        if timed: overall_start = time.perf_counter()
        collision_freqs = self._get_collision_freqs(y)

        if timed: scan_start = time.perf_counter()
        neighbor_idxs = [idx for idx, freq in collision_freqs.items() if freq >= alpha]
        
        if timed:
            end_time = time.perf_counter()
            self.query_total_times.append(end_time - overall_start)
            self.query_scan_times.append(end_time - scan_start)

        return neighbor_idxs


class MultiProbeLSH(pStableHash):
    '''
    TODO
    '''
    def __init__(self, k, l, r, n_dims, seed=42):
        super().__init__(k, l, r, n_dims, seed)

        self.query_total_times = [] # amount of time it takes to perform an entire single query operation
        self.query_hash_times = [] # amount of time it takes to hash the query point into all l tables and k bands
        self.query_set_construction_times = [] # amount of time it takes to construct the perturbation sets
        self.query_scan_times = [] # amount of time it takes to ultimately determine all the collisions with our query
        self.query_num_perturbed_bucket_collisions = [] # the raw number of collisions in each of the buckets we get from a perturbation
        self.query_num_original_bucket_collisions = [] # the raw number of collisions in each of the buckets without any perturbations

    def query(self, y, num_perturbations, timed=False):

        if timed:
            overall_start_time = time.perf_counter()

        negative_boundary_dists = []
        positive_boundary_dists = []

        projected = np.matmul(self.A, y) + self.B
        bucket_ids = np.floor(projected / self.r).astype(np.int32)

        if timed: 
            set_construction_start_time = time.perf_counter()
            self.query_hash_times.append(set_construction_start_time - overall_start_time)

        for table_idx, table_bucket_id in enumerate(bucket_ids):

            table_proj_values = projected[table_idx]

            # Compute the distance from the query point to the positive and negative boundaries
            # of its interval, which will be used to determine the ordering of perturbation vectors
            table_negative_boundary_dists = table_proj_values - (table_bucket_id * self.r)
            table_positive_boundary_dists = self.r - table_negative_boundary_dists

            negative_boundary_dists.append(table_negative_boundary_dists)
            positive_boundary_dists.append(table_positive_boundary_dists)

        negative_boundary_dists = np.array(negative_boundary_dists)
        positive_boundary_dists = np.array(positive_boundary_dists)

        # This matrix (l x 2k) stores all of the distances from the query point to its interval boundaries.
        # X[i, j] represents the distance from the query point to the boundary corresponding to pi_j in table i
        X = np.concatenate([negative_boundary_dists, positive_boundary_dists], axis=1)

        # In the paper, each pi is a tuple of the form (i, delta), representing a band index and
        # an actual perturbation. Each entry in a row of X, above, represents one such pi (there are 2k
        # for each row)
        sorted_pi_indices = np.argsort(X, axis=1)

        # Now we convert from the indices of each pi tuple to the actual corresponding band index and
        # perturbation, which will be used later to actually access the neighboring buckets
        sorted_band_idxs = sorted_pi_indices % self.k
        sorted_perturbations = (sorted_pi_indices // self.k * 2) - 1

        # Calculate the score associated with a particular table and perturbation set, defined as the sum
        # of the squared distances of each perturbation in the set
        def score_perturbation_set(table_idx, pi_idxs):
            return np.power(X[table_idx][list(pi_idxs)], 2).sum()

        # Create a min-heap to store all of our potential perturbations. Each entry in the heap will look
        # like (score, table_index, perturbation_set), and each entry in the perturbation set is a "pi index"
        # (an element in {0, ..., 2k-1}) which represents a specific band index and perturbation
        heap = []
        for table_idx in range(self.l):
            perturbation_set = {0}
            score = score_perturbation_set(table_idx, perturbation_set)
            heap.append((score, table_idx, perturbation_set))

        heapq.heapify(heap)

        def shift_perturbation_set(pi_idxs):
            copy = perturbation_set.copy()
            max_val = max(copy)

            copy.remove(max_val)
            copy.add(max_val + 1)

            return copy

        def expand_perturbation_set(pi_idxs):
            copy = perturbation_set.copy()
            max_val = max(copy)

            copy.add(max_val + 1)

            return copy

        def validate_perturbation_set(pi_idxs):
            for idx in pi_idxs:
                if (2 * self.k) - 1 - idx in pi_idxs:
                    return False

            return True


        assert num_perturbations < (2**self.k) * self.l, "Number of perturbations was too high"


        # Generate perturbation sets in ascending order of score using the algorithm outlined in the 
        # paper, which iteratively expands / shifts existing perturbation sets (and discards invalid sets)
        actual_perturbations = []
        while len(actual_perturbations) < num_perturbations:
            score, table_idx, pi_idxs = heapq.heappop(heap)

            if validate_perturbation_set(pi_idxs):
                actual_perturbations.append((table_idx, pi_idxs))

            shifted_perturbation_set = shift_perturbation_set(pi_idxs)
            shifted_score = score_perturbation_set(table_idx, shifted_perturbation_set)
            heapq.heappush(heap, (shifted_score, table_idx, shifted_perturbation_set))

            expanded_perturbation_set = expand_perturbation_set(pi_idxs)
            expanded_score = score_perturbation_set(table_idx, expanded_perturbation_set)
            heapq.heappush(heap, (expanded_score, table_idx, expanded_perturbation_set))

        if timed:
            scan_start_time = time.perf_counter()
            self.query_set_construction_times.append(scan_start_time - set_construction_start_time)

        # Now we actually collect the near neighbors by constructing the corresponding perturbation vector out of each
        # of the previously returned perturbation sets. To do this, we map from each pi index to the corresponding band
        # index and perturbation, leaving all of the other perturbations as 0, and add that to the query's bucket ID for
        # the particular table associated with that perturbation set. This gives us a new bucket ID, and we collect all
        # of the data indices that fall into that bucket in that table. Of course, we also include all of the data indices
        # in the actual bucket of the query item
        neighbors = set([])
        for table_idx, perturbation_set in actual_perturbations:
            query_bucket_id = bucket_ids[table_idx] # this is a k-dimensional vector of intergers representing intervals

            band_idxs = sorted_band_idxs[list(perturbation_set)] 
            perturbations = sorted_perturbations[list(perturbation_set)]

            perturbation_vector = np.zeros(self.k)
            perturbation_vector[band_idxs] += perturbations

            perturbed_bucket_id = tuple((query_bucket_id + perturbation_vector).astype(np.int32))

            if timed:
                self.query_num_perturbed_bucket_collisions.append(len(self.tables[table_idx][perturbed_bucket_id]))

            for data_index in self.tables[table_idx][perturbed_bucket_id]:
                neighbors.add(data_index)

        
        # Finally, we collect all of the neighbors in the query's actual buckets
        for table_idx in range(self.l):
            query_bucket_id = tuple(bucket_ids[table_idx].astype(np.int32))

            if timed:
                self.query_num_original_bucket_collisions.append(len(self.tables[table_idx][query_bucket_id]))

            for data_index in self.tables[table_idx][query_bucket_id]:
                neighbors.add(data_index)

        if timed:
            end_time = time.perf_counter()
            self.query_scan_times.append(end_time - scan_start_time)
            self.query_total_times.append(end_time - overall_start_time)

        return neighbors

class AlphaMultiProbeLSH(pStableHash):
    '''
    TODO
    '''
    def __init__(self, k, l, r, n_dims, seed=42):
        super().__init__(k, l, r, n_dims, seed)

        self.query_total_times = [] # amount of time it takes to perform an entire single query operation
        self.query_hash_times = [] # amount of time it takes to hash the query point into all l tables and k bands
        self.query_set_construction_times = [] # amount of time it takes to construct the perturbation sets
        self.query_scan_times = [] # amount of time it takes to ultimately determine all the collisions with our query
        self.query_num_perturbed_bucket_collisions = [] # the raw number of collisions in each of the buckets we get from a perturbation
        self.query_num_original_bucket_collisions = [] # the raw number of collisions in each of the buckets without any perturbations

    def query(self, y, num_perturbations, alpha=1, timed=False):

        if timed:
            overall_start_time = time.perf_counter()

        negative_boundary_dists = []
        positive_boundary_dists = []

        projected = np.matmul(self.A, y) + self.B
        bucket_ids = np.floor(projected / self.r).astype(np.int32)

        if timed: 
            set_construction_start_time = time.perf_counter()
            self.query_hash_times.append(set_construction_start_time - overall_start_time)

        for table_idx, table_bucket_id in enumerate(bucket_ids):

            table_proj_values = projected[table_idx]

            # Compute the distance from the query point to the positive and negative boundaries
            # of its interval, which will be used to determine the ordering of perturbation vectors
            table_negative_boundary_dists = table_proj_values - (table_bucket_id * self.r)
            table_positive_boundary_dists = self.r - table_negative_boundary_dists

            negative_boundary_dists.append(table_negative_boundary_dists)
            positive_boundary_dists.append(table_positive_boundary_dists)

        negative_boundary_dists = np.array(negative_boundary_dists)
        positive_boundary_dists = np.array(positive_boundary_dists)

        # This matrix (l x 2k) stores all of the distances from the query point to its interval boundaries.
        # X[i, j] represents the distance from the query point to the boundary corresponding to pi_j in table i
        X = np.concatenate([negative_boundary_dists, positive_boundary_dists], axis=1)

        # In the paper, each pi is a tuple of the form (i, delta), representing a band index and
        # an actual perturbation. Each entry in a row of X, above, represents one such pi (there are 2k
        # for each row)
        sorted_pi_indices = np.argsort(X, axis=1)

        # Now we convert from the indices of each pi tuple to the actual corresponding band index and
        # perturbation, which will be used later to actually access the neighboring buckets
        sorted_band_idxs = sorted_pi_indices % self.k
        sorted_perturbations = (sorted_pi_indices // self.k * 2) - 1

        # Calculate the score associated with a particular table and perturbation set, defined as the sum
        # of the squared distances of each perturbation in the set
        def score_perturbation_set(table_idx, pi_idxs):
            return np.power(X[table_idx][list(pi_idxs)], 2).sum()

        # Create a min-heap to store all of our potential perturbations. Each entry in the heap will look
        # like (score, table_index, perturbation_set), and each entry in the perturbation set is a "pi index"
        # (an element in {0, ..., 2k-1}) which represents a specific band index and perturbation
        heap = []
        for table_idx in range(self.l):
            perturbation_set = {0}
            score = score_perturbation_set(table_idx, perturbation_set)
            heap.append((score, table_idx, perturbation_set))

        heapq.heapify(heap)

        def shift_perturbation_set(pi_idxs):
            copy = perturbation_set.copy()
            max_val = max(copy)

            copy.remove(max_val)
            copy.add(max_val + 1)

            return copy

        def expand_perturbation_set(pi_idxs):
            copy = perturbation_set.copy()
            max_val = max(copy)

            copy.add(max_val + 1)

            return copy

        def validate_perturbation_set(pi_idxs):
            for idx in pi_idxs:
                if (2 * self.k) - 1 - idx in pi_idxs:
                    return False

            return True


        assert num_perturbations < (2**self.k) * self.l, "Number of perturbations was too high"


        # Generate perturbation sets in ascending order of score using the algorithm outlined in the 
        # paper, which iteratively expands / shifts existing perturbation sets (and discards invalid sets)
        actual_perturbations = []
        while len(actual_perturbations) < num_perturbations:
            score, table_idx, pi_idxs = heapq.heappop(heap)

            if validate_perturbation_set(pi_idxs):
                actual_perturbations.append((table_idx, pi_idxs))

            shifted_perturbation_set = shift_perturbation_set(pi_idxs)
            shifted_score = score_perturbation_set(table_idx, shifted_perturbation_set)
            heapq.heappush(heap, (shifted_score, table_idx, shifted_perturbation_set))

            expanded_perturbation_set = expand_perturbation_set(pi_idxs)
            expanded_score = score_perturbation_set(table_idx, expanded_perturbation_set)
            heapq.heappush(heap, (expanded_score, table_idx, expanded_perturbation_set))

        if timed:
            scan_start_time = time.perf_counter()
            self.query_set_construction_times.append(scan_start_time - set_construction_start_time)

        # Now we actually collect the near neighbors by constructing the corresponding perturbation vector out of each
        # of the previously returned perturbation sets. To do this, we map from each pi index to the corresponding band
        # index and perturbation, leaving all of the other perturbations as 0, and add that to the query's bucket ID for
        # the particular table associated with that perturbation set. This gives us a new bucket ID, and we collect all
        # of the data indices that fall into that bucket in that table. Of course, we also include all of the data indices
        # in the actual bucket of the query item
        neighbor_collision_counts = defaultdict(int)
        for table_idx, perturbation_set in actual_perturbations:
            query_bucket_id = bucket_ids[table_idx] # this is a k-dimensional vector of intergers representing intervals

            band_idxs = sorted_band_idxs[list(perturbation_set)] 
            perturbations = sorted_perturbations[list(perturbation_set)]

            perturbation_vector = np.zeros(self.k)
            perturbation_vector[band_idxs] += perturbations

            perturbed_bucket_id = tuple((query_bucket_id + perturbation_vector).astype(np.int32))

            if timed:
                self.query_num_perturbed_bucket_collisions.append(len(self.tables[table_idx][perturbed_bucket_id]))

            for data_index in self.tables[table_idx][perturbed_bucket_id]:
                neighbor_collision_counts[data_index] += 1

        
        # Finally, we collect all of the neighbors in the query's actual buckets
        for table_idx in range(self.l):
            query_bucket_id = tuple(bucket_ids[table_idx].astype(np.int32))

            if timed:
                self.query_num_original_bucket_collisions.append(len(self.tables[table_idx][query_bucket_id]))

            for data_index in self.tables[table_idx][query_bucket_id]:
                neighbor_collision_counts[data_index] += 1

        # Filter based on the number of collisions
        neighbors = [data_idx for data_idx, freq in neighbor_collision_counts.items() if freq >= alpha]

        if timed:
            end_time = time.perf_counter()
            self.query_scan_times.append(end_time - scan_start_time)
            self.query_total_times.append(end_time - overall_start_time)

        return neighbors

if __name__ == "__main__":
    import h5py
    import math
    from pdb import set_trace as TT
    
    import matplotlib.pyplot as plt
    from scipy import integrate
    from tqdm import tqdm


    def f_G(x):
        """
        Gaussian distribution density function. Helper for calculating p-stable collision probability
        Args:
            x:
        Returns:
        """
        return np.exp(-x**2/2) / math.sqrt(2*math.pi)


    def collision_prob_pstable(dists, r, k, l):
        """
        Args:
            sim:
            r: the width of the buckets in the projections
            k: number of projections (bands)
            l: number of hash tables
        Returns:
            an integer or 1D vector of collision probabilities in [0, 1]
        """
        p_projs = np.empty(len(dists))

        for di, d in enumerate(dists):
            if d == 0:
                p_projs[di] = 1
                continue
            result = integrate.quad(lambda t: (1 / d) * f_G(t / d) * (1 - (t / r)), 0, r)
            p_proj = 2 * result[0]
            p_projs[di] = p_proj

        coll_probs = 1 - (1 - p_projs ** k) ** l

        return coll_probs

    file = h5py.File("data/fashion-mnist-784-euclidean.hdf5", "r")
    # file = h5py.File("data/sift-128-euclidean.hdf5", "r")

    
    train, test, true_neighbors, neighbor_dists = file["train"], file["test"], file["neighbors"], file["distances"] 




    # k = 1
    # l = 40
    # r = 100
    n_dims = 784
    seed = 42


    # pbar = tqdm(total=49*19*30, desc="Doing math")
    # for k in range(1, 20):
    #     for l in range(20, 50):
    #         for r in range(76, 125):
    #             test_idx = np.random.randint(1000)
    #             point = test[test_idx]
    #             neighbors = true_neighbors[test_idx]
    #             distances = neighbor_dists[test_idx]

    #             collision_probs = collision_prob_pstable(distances, r, k, l)

    #             min_c_prob = np.min(collision_probs)
    #             if min_c_prob > 0.9:
    #                 print(f"Successful parameter set! r = {r}, k = {k}, l = {l}")

    #             pbar.set_description(f"Doing math: r = {r}, k = {k}, l = {l}")
    #             pbar.update(1)

    # pbar.close()

        # print(f"For point {idx}, avg. distance to near neighbors = {np.mean(distances)}, avg. collision prob = {np.mean(collision_probs)}")

    k = 1
    l = 49
    r = 123


    vanilla = VanillaLSH(k, l ,r, n_dims, seed)
    alpha = AlphaLSH(k, l ,r, n_dims, seed)
    multi = MultiProbeLSH(k, l ,r, n_dims, seed)

    for data_point in tqdm(train, desc="Hashing"):
        # multi.hash(data_point / 256)
        vanilla.hash(data_point / 256)

    recalls, precisions = [], []
    for test_idx in tqdm(range(100), desc="Querying"):
        # returned_neighbors = multi.query(test[test_idx] / 256, 50)
        returned_neighbors = vanilla.query(test[test_idx] / 256)
        actual_neighbors = true_neighbors[test_idx]

        recall = len(set(returned_neighbors).intersection(set(actual_neighbors))) / len(actual_neighbors)
        precision = len(set(returned_neighbors).intersection(set(actual_neighbors))) / len(returned_neighbors)

        recalls.append(recall)
        precisions.append(precision)

    print(f"Average recall: {'%.3f' % np.mean(recalls)}")
    print(f"Average precision: {'%.3f' % np.mean(precisions)}")
    exit()

    print(vanilla.hash(point))
    print(alpha.hash(point))
    print(multi.hash(point))

    print("\n\n")
    print(vanilla.query(point))
    print(alpha.query(point, 2))
    print(multi.query(point, 2))


