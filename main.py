# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from collections import defaultdict
from graphviz import Digraph
from decimal import Decimal
import sys

subject_to_object = defaultdict()
object_to_subject = defaultdict()
cwd_to_subject = defaultdict()
subject_label = {}
object_label = {}
for_first_output = {}
write = {"write", "sendmsg"}
obj_start_time = {}

global global_cwd
global_cwd = ""


class Object:
    def __init__(self, name, start, end, cwd, action):
        self.name = name
        self.start = start
        self.end = end
        self.cwd = cwd
        self.action = action

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def bfs(s):
    g = Digraph('G', filename="finalbfs.gv")
    visited = set()
    created = set()
    queue = list()
    queue.append(s)
    while queue:
        u = queue.pop(0)

        if u in object_to_subject:
            for v in object_to_subject[u]:
                if str(u.name) + "|" + str(v.name) not in visited:
                    # print("for " + u.name + " and " + v.name)
                    # print(u.end + " " + v.start +" | " + v.end + " " + u.start)
                    if Decimal(u.end).compare(Decimal(v.start)) >= 0:
                        if u.name not in created:
                            g.node(str(u.name))
                        if v.name not in created:
                            g.node(str(v.name))

                        visited.add(str(u.name)+"|"+str(v.name))
                        g.edge(str(v.name), str(u.name))
                        queue.append(v)
    g.render(view=True)

def draw():
    g = Digraph('G', filename="final.gv")
    created = set()
    for u in subject_to_object:
        if u.name not in created:
            g.node(u.name)
            created.add(u.name)
        for v in subject_to_object[u]:
            if v.name not in created:
                g.node(v.name)
                created.add(v.name)
    for u in subject_to_object:
        connected = set()
        for v in subject_to_object[u]:
            if v.name not in connected:
                g.edge(str(u.name), str(v.name))
                connected.add(v.name)
        del connected
    g.render(view=True)


def parse(name):
    file = open(name, "r")
    sys_dig_output = []
    for i in file:
        sys_dig_output.append(i.replace(":", "-"))

    for i in range(0, len(sys_dig_output)-1):

        splitted_line = sys_dig_output[i].split(" ")
        send_or_receive = splitted_line[5]
        if send_or_receive == ">":
            subject = splitted_line[3] + splitted_line[4]
            action = splitted_line[6]
            object_ext = splitted_line[8].replace("fd=", "").replace("'", "")
            start = splitted_line[1]
            end = ""
            for j in range(i+1, len(sys_dig_output)-1):
                end_splitted_line = sys_dig_output[j].split(" ")
                probable_end_subject = splitted_line[3] + splitted_line[4]
                if probable_end_subject == subject:
                    end = end_splitted_line[1]
                    break
            cwd = splitted_line[7]
            #swapping if action is not a write

            if object_ext.strip(" ") != "" and subject.strip(" ") != "" and action.strip(" ") != "":
                subject_obj = Object(subject, start, end, cwd, action)
                object_obj = Object(object_ext, start, end, cwd, action)
                if subject_obj not in for_first_output:
                    for_first_output[subject_obj] = [object_obj]
                else:
                    for_first_output[subject_obj].append(object_obj)

                if action not in write:
                    temp = subject_obj
                    subject_obj = object_obj
                    object_obj = temp

                #object_obj = Object(object_ext, start, end, cwd, action)
                #subject_obj = Object(subject, start, end, cwd, action)

                if subject_obj not in subject_to_object:
                    subject_to_object[subject_obj] = [object_obj]
                else:
                    subject_to_object[subject_obj].append(object_obj)

                if object_obj not in object_to_subject:
                    object_to_subject[object_obj] = [subject_obj]
                else:
                    past_start = ""
                    for i in object_to_subject:
                        if i.name == object_obj.name:
                            past_start = i.start
                            break
                    temp = object_to_subject[object_obj]
                    temp.append(subject_obj)
                    obj_with_past_time = Object(object_obj.name, past_start, end, cwd, action)
                    del object_to_subject[object_obj]
                    object_to_subject[obj_with_past_time] = temp

                if "(" in subject_obj.name and ")" in subject_obj.name:
                    if cwd not in cwd_to_subject:
                        cwd_to_subject[cwd] = {subject_obj}
                    else:
                        if subject_obj in cwd_to_subject[cwd]:
                            cwd_to_subject[cwd].remove(subject_obj)
                        cwd_to_subject[cwd].add(subject_obj)

                if "(" in object_obj.name and ")" in object_obj.name:
                    if cwd not in cwd_to_subject:
                        cwd_to_subject[cwd] = {object_obj}
                    else:
                        if object_obj in cwd_to_subject[cwd]:
                            cwd_to_subject[cwd].remove(object_obj)
                        cwd_to_subject[cwd].add(object_obj)

    del sys_dig_output

    # for i in cwd_to_subject:
    #     print()
    #     print("for "+ i)
    #     for j in cwd_to_subject[i]:
    #         print(j.name, end="\t")


    for i in object_to_subject.keys():
        if "(" in i.name and ")" in i.name:
            if i.cwd in cwd_to_subject:
                for j in cwd_to_subject[i.cwd]:
                    if j.name != i.name:
                        if j.name[0: j.name.index("(")] == i.name[0: i.name.index("(")]:
                            object_to_subject[i].append(j)




     for i in object_to_subject:
         print()
         print("for " + i.name)
         print("\t"+" by ", end="\t")
         for j in object_to_subject[i]:
             print(j.name, end="\t")


 def parse_for_cwd():
     cwd_list = list(cwd_to_subject[global_cwd])
     processed_cwd_list = []
     for i in range(0, len(cwd_list)):
         if "sh(" not in cwd_list[i].name:
             processed_cwd_list.append(cwd_list[i])

     cwd_list = processed_cwd_list
     cwd_list.sort(key=lambda x: Decimal(x.start))

     for i in cwd_list:
         print(i.name, end = " | ")
     for i in range(0, len(cwd_list) - 1):
         if cwd_list[i] in object_to_subject:
             object_to_subject[cwd_list[i]].append(cwd_list[i+1])
         else:
             object_to_subject[i] = [cwd_list[i+1]]

     for i in object_to_subject:
         print()
         print("for " + i.name)
         print("\t"+" by ", end="\t")
         for j in object_to_subject[i]:
             print(j.name, end="\t")



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    inp = sys.argv[1]
    if len(inp) > 1:
        parse(inp)
        print("Done with parsing, Please select one option:")
        print("1.Output the data in form of tuples")
        print("2.Draw the graph")
        print("3.Perform backtracking")
        opt = input()
        if opt == "1":
            file1 = open("tuples.txt", "w")
            print("writing the data to tuples.txt")
            for key in for_first_output:
                for each_value in for_first_output[key]:
                    line = "({:50s}  {:10s}  {:50s})"
                    line = line.format(key.name, each_value.action, each_value.name)
                    print(line)
                    file1.write(line)
            file1.close()
            print("written to tuples.txt")
        elif opt == "2":
            draw()
        elif opt == "3":
            print("enter the node to be backtracked")
            kay_val = input()
            key = None

            for i in object_to_subject.keys():
                if i.name == kay_val:
                    key = i
                    break
            if key:
                global_cwd = key.cwd
                bfs(key)
            else:
                print("make sure the node value is correct and the node does have ancestors")
        else:
            print("select one from above mentioned options.")
    else:
        print("give a valid input file")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

