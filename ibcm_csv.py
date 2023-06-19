import csv
class Constraint:
    def __init__(self, name, a, b, w):
        self.name = name
        self.a = a
        self.b = b
        self.w = w
    
    def __str__(self):
        return f"{self.name}({self.a}-{self.b}){self.w}"

    def __hash__(self):
        return hash((self.name, self.a, self.b, self.w))

    def __eq__(self, other):
        if isinstance(other, Constraint):
            return (self.name == other.name and
                    self.a == other.a and
                    self.b == other.b and
                    self.w == other.w)
        return False

class AnnotatedTrace:
    def __init__(self, name, constraints, label):
        self.string = name
        self.constraints = constraints
        self.label = label

class ConstraintMining:   
    def __init__(self, filename, activities, w):
        print(f'Constraint Mining: {filename}')
        self.filename = filename
        self.activities = activities
        self.local_constraints = set()
        self.window_positions = []
        self.no_windows = w
        self.window_size = 0
        self.process_csv_file()
        if self.window_size > 0:
            for lw in range(1, w):
                self.window_positions.append(self.window_size * lw)
        self.window_positions.append(len(self.activities))

    def process_csv_file(self):
        traces = []
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                traces.append(row)

        self.window_size = len(traces[0])
        
        self.activities = [activity for trace in traces for activity in trace]

    def mine_binaries(self):
        for i in range(len(self.activities)):
            for j in range(i + 1, len(self.activities)):
                self.check_constraints(i, j)
        print("Local Constraints:", self.local_constraints)

    def check_constraints(self, i, j):
        for w in self.window_positions:
            if self.check_window(i, j, w):
                constraint = (self.activities[i], self.activities[j], w)
                self.local_constraints.add(constraint)

    def check_window(self, i, j, w):
        window_activities = self.activities[w - self.window_size:w]
        if self.activities[i] in window_activities and self.activities[j] in window_activities:
            return True
        return False

if __name__ == "__main__":
    import visualizer as vis
    uploaded_file = "Market_Basket_Optimisation.csv"
    activities = [
        'A','B','C','D'
    ]
    w = 4
    miner = ConstraintMining(uploaded_file, activities, w)
    miner.mine_binaries()

    print("Local Constraints:", miner.local_constraints)
    fig = vis.visualize_local_constraints(miner.local_constraints)
    fig.show()


