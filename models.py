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
