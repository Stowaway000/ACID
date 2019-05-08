class Quest:
    cur = {}
    sub = []
    def __init__(self, args):
        if len(args) == 1:
            file = open(args[0] + '.q')
            line = file.readline()
            args = [0]
            while line != '\n':
                args.append(line)        
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
        line = []
        self.good_close = []
        self.good_open = []
        self.good_rewards = []
        if len(args[i]) > 1:
            line = args[i].split(';')
            for i in (len(line) - 2):
                reward = line[i]
                if 'close' in reward:
                    start = reward.find('close') + 5
                    self.good_close.append(reward[start:])
                elif 'open' in reward:
                    start = reward.find('open') + 4
                    self.good_open.append(reward[start:])
                else:
                    self.good_rewards.append(reward.strip())
        i+=1
        line = []
        self.bad_close = []
        self.bad_open = []
        self.bad_rewards = []
        if len(args[i]) > 1:
            line = args[i].split(';')
            for i in (len(line) - 2):
                reward = line[i]
                if 'close' in reward:
                    start = reward.find('close') + 5
                    self.bad_close.append(reward[start:])
                elif 'open' in reward:
                    start = reward.find('open') + 4
                    self.bad_open.append(reward[start:])
                else:
                    self.bad_rewards.append(reward.strip())            
        Quest.cur[args[0][:-3]] = self
        args = []
        line = file.readline()
        while line:
            while line != '\n':
                args.append(line)
            args[0][:-3] = Quest(args)    
            Quest.sub.append(args[0][:-3])
    @staticmethod
    def get(id ):
        return Quest.cur[id]
    def good_close():
        for task in self.good_close:
            del Quest.get(task)
        for task in self.good_open:
            args = [task]
            task = Quest(args)
    def bad_close():
        for task in self.bad_close:
            del Quest.get(task)
        for task in self.bad_open:
            args = [task]
            task = Quest(args)
    def count(name):
        if self.item_name == name:
            self.counter+=1
            if self.counter_limit == self.counter:
                self.good_close()


            
