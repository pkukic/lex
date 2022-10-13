class RegexPrep:
    
    def __init__(self, file: str, target: str):
        self.in_file = file
        self.target = target
        self.prev_regex = {}
    

    def change_references_to_regex(self, regex_with_references: str) -> str:
        out_regex = regex_with_references
        for name, reg in self.prev_regex.items():
            out_regex = out_regex.replace(name, "(" + reg + ")")
        return out_regex
    

    def start(self):
        with open(self.target, 'w') as wf:
            with open(self.in_file, 'r') as rf:
                for line in rf.readlines():
                    if line.startswith("{") and line != "{\n":
                        # for regex definitions
                        index = line.find(" ")
                        name, reg = line[:index + 1], line[index + 1:-1] # remove the \n from the end
                        processed = self.change_references_to_regex(reg)
                        self.prev_regex.update({name[:-1]: processed})
                    elif line.startswith("%X"):
                        wf.write(line)
                    elif line.startswith("%L"):
                        wf.write(line)
                    elif line.startswith("<"):
                        # for actions
                        index = line.find(">")
                        new_line = line[0:index + 1]
                        processed = self.change_references_to_regex(line[index + 1:-1])
                        new_line = new_line + processed
                        if not new_line.endswith("\n"):
                            new_line = new_line + "\n"
                        wf.write(new_line)
                    else:
                        new_line = line
                        wf.write(new_line)
                    