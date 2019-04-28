class Quest:
    cur = {}
    sub = []
    def __init__(self, args):
        file = open('<args[0]>.q')
        line = file.readline()
        args = [0]
        while line != '\n':
            args.append(line)
        if len(args) == 1:                
            self.name = args[0][:-3]
            self.description = ''
            for i in range(1,len(args) - 5):
                self.description += args[i][:-2]
            self.description += args[i][:-3]
            i+=1
            line = args[i].split()
            if len(line) > 1:
                self.item_name = line[0]
                self.counter = 0;
                self.counter_limit = int(line[len(line) - 1][:-1])
                for j in range(0, len(line) - 2):
                    self.item_name += line[j]
            i+=1        
