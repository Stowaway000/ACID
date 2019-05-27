class Quest:
    cur = {}
    closed = []
    cache = {}
    def __init__(self, args):
        if len(args) == 1:
            file = open(args[0] + '.q')
            line = file.readline()
            args = [0]
            while line != '\n':
                args.append(line.strip())
                line = file.readline()
        self.name = args[0][:-1]
        self.description = ''
        for i in range(1,len(args) - 5):
            self.description += args[i]
        self.description += args[i][:-1]
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
                if 'close g' in reward:
                    start = reward.find('close') + 5
                    self.good_close.append([reward[start:],'g'])
                elif 'close b' in reward:
                    start = reward.find('close') + 5
                    self.good_close.append([reward[start:],'b'])    
                elif 'open g' in reward:
                    start = reward.find('open') + 4
                    self.good_open.append([reward[start:], 'g'])
                elif 'open g' in reward:
                    start = reward.find('open') + 4
                    self.good_open.append([reward[start:], 'g'])    
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
                if 'close g' in reward:
                    start = reward.find('close') + 5
                    self.bad_close.append([reward[start:], 'g'])
                elif 'close b' in reward:
                    start = reward.find('close') + 5
                    self.bad_close.append([reward[start:],'b'])    
                elif 'open g' in reward:
                    start = reward.find('open') + 4
                    self.bad_open.append([reward[start:], 'g'])    
                elif 'open b' in reward:
                    start = reward.find('open') + 4
                    self.bad_open.append([reward[start:],'b'])
                elif 'add' in reward:
                    start = reward.find('open') + 3
                    self.bad_rewards.append(reward[start:])            
        Quest.cur[args[0][:-1]] = self
        args = []
        line = file.readline()
        while line != '\n':
                args.append(line.strip())
                line = file.readline()
        args[0][:-1] = Quest(args)    
        Quest.cur[args[0][:-1]] = Quest(args[0][:-1])
        while line:
            while line != '\n':
                args.append(line.strip())
                line = file.readline()
            args[0][:-1] = Quest(args)    
            Quest.cache[args[0][:-1]] = Quest(args[0][:-1])
    @staticmethod
    def get(id ):
        if id in Quest.cur:
            return Quest.cur[id]
        else:
            return None
    def good_close():
        for task in self.good_close:
            if Quest.get(task[0]) == None:
                Quest.closed.append(task[0])
            else:
                if task[1] == 'g':
                    task[0].good_close()
                else:
                    task[0].bad_close()
        for task in self.good_open:
            if not task[0] in Quest.closed:
                if task[0] in Quest.cache:
                    Quest.cur[task[0]] = Quest.cache[task[0]]
                    del Quest.cache[task[0]]
                else:    
                    args = []
                    task = Quest(args)
        for obj in self.good_reward:           
            mainhero.inventory.add(obj, 1)        
                
        del Quest.cur[task[0]]       
    def bad_close():
        for task in self.bad_close:
            if Quest.get(task[0]) == None:
                Quest.closed.append(task[0])
            else:
                if task[1] == 'g':
                    task[0].good_close()
                else:
                    task[0].bad_close()
        for task in self.bad_open:
            if not task[0] in Quest.closed:
                if task[0] in Quest.cache:
                    Quest.cur[task[0]] = Quest.cache[task[0]]
                    del Quest.cache[task[0]]
                else:    
                    args = []
                    task = Quest(args)
        for obj in self.bad_reward:           
            mainhero.inventory.add(obj, 1)        
                
        del Quest.cur[task[0]]
    def count(name):
        if self.item_name == name:
            self.counter+=1
            if self.counter_limit == self.counter:
                self.good_close()


            