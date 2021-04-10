from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import*
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.chip import MDChip, MDChooseChip
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

import numpy as np

from kivy.lang import Builder

import sqlite3 as sql

#===================== Global Variables =======================#

#Builder.load_file("KV.kv")

chip_color = [0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 0.7]
selected_color = [0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 1.0]

#Exercise Databse each sublist has various difficulty, 0 : easy, 1 : medium, 2 : hard 
push = ( ["Pushup", "Close Grip", "Wide Grip", "Inclined Pushup"],
        ["Diamond Pushup", "Archer Pushup","Knuckle Pushup", "Declined Pushups"],
        ["Decline Diamond", "Pseudo Planche Pushup", "Explosives"] )


pull = (["Chin-ups", "Negatives", "Hanging Hold"],
        ["Leg Raises", "Slow Pullups", "Dead Hang"],
        ["Perfect Arched Pullups", "90 degree -Top Hold", "Dead Hang (1 Arm)"])

leg = (["Squats", "Bunny Hops", "Lunges", "Calf Raises"],
       ["Jumping Squats", "Jumping Lunges", "Bulgarian Split Squats",],
       ["Pistol Squats", "180 Squats", "Close-Wide Squats", "1 Legged Calf Raises"])

#List of selected exercises.
push_list = []
pull_list = []
leg_list = []

#Database Creation.
con = sql.connect("Workout.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS Plans(Plan varchar(50) UNIQUE, Push TEXT, Pull TEXT, Leg TEXT);")

class BuildApp(Screen):     #This class handles everything on screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        diffs = [{'text' : 'Easy'}, {'text' : 'Medium'}, {'text' : 'Hard'}]

        self.drop = MDDropdownMenu(
            caller = self.ids.pushup_diff,
            items = diffs,
            width_mult = 4,
        )
        self.drop.bind(on_release=self.diff_sel) 

        self.drop1 = MDDropdownMenu(
            caller = self.ids.pullup_diff,
            items = diffs,
            width_mult = 4,
        )
        self.drop1.bind(on_release=self.diff_sel)    

        self.drop2 = MDDropdownMenu(
            caller = self.ids.legs_diff,
            items = diffs,
            width_mult = 4,
        )
        self.drop2.bind(on_release=self.diff_sel)

        self.table = MDDataTable(
            check = True,
            column_data = [
                ("Plan", dp(30)),
                ("Push", dp(50)),
                ("Pull", dp(50)),
                ("Legs", dp(50)),
            ],
            row_data =[
                ("Plan Name", "Push Exercises", "Pull Exercises", "Leg Exercises"),
                ("","","","")
            ],
            pos_hint = {"center_x":0.5, "center_y":0.35},
            size_hint = (0.75,0.25),
        )
        self.add_widget(self.table)
        self.table.bind(on_check_press = self.selection)

        

    #Adding the data to the data table
    def add_data(self, *args):
        cur.execute("SELECT *FROM Plans;")
        rows = cur.fetchall()

        for row in rows:
            self.table.row_data = [
                (row),
                ("","","","")
            ]

    def selection(self, table, table_item):
        self.sel_plan = table_item[0]
    
    #Searching a Record
    def searching(self, *args):
        plan_name = str(self.ids.plan_name.text.strip())
        cur.execute("SELECT *FROM Plans WHERE Plan = ?", (plan_name,))
        rows = cur.fetchall()
        
        for row in rows:
            self.table.row_data = [
                (row),
                ("","","","")
            ]
        print(plan_name)

    #Updating A Record
    def updation(self, *args):
        #Wasn't able to do it using self.push_str and stuff
        push_str = ", ".join([str(x) for x in push_list])
        pull_str = ", ".join([str(x) for x in pull_list])
        leg_str = ", ".join([str(x) for x in leg_list])

        record = [push_str, pull_str, leg_str, self.sel_plan]
        update = """UPDATE Plans SET Push = ?, Pull = ?, Leg = ? WHERE Plan = ?"""
        cur.execute(update, (record))

        con.commit()
        self.table.row_data=[
            (self.sel_plan, push_str, pull_str, leg_str),
            ("","","","")
        ]

    #Deleting A Record
    def deletion(self, *args):
        cur.execute("DELETE FROM Plans WHERE Plan = ?", (self.sel_plan,))
        con.commit()
        self.table.row_data = [
        ]

    #Inserting(Creating) A Record.
    def insertion(self):
        global push_list, pull_list, leg_list
        plan_name = self.ids.plan_name.text.strip()

        con = sql.connect("Workout.db")
        cur = con.cursor()

        push_str = ", ".join([str(x) for x in push_list])
        pull_str = ", ".join([str(x) for x in pull_list])
        leg_str = ", ".join([str(x) for x in leg_list])

        #record = [plan_name, self.push_str, self.pull_str, self.leg_str]
        record = [plan_name, push_str, pull_str, leg_str]
        
        cur.execute("INSERT INTO Plans(Plan, Push, Pull, Leg) VALUES(?,?,?,?)", (record))
        cur.execute("SELECT *FROM Plans WHERE Plan = ?", (plan_name,))
        rows = cur.fetchall()
        con.commit()
        con.close()
        self.add_data()
        print(rows)
        print("[RECORD INSERTED IN DATABASE SUCCESSFULLY]")



    #Fetch the Difficulty and Exercise Selection
    def diff_sel(self, menu, menu_item):
        global push, pull, leg
        print(menu.caller.text)         #menu.caller.text gives the text of the helper 
        print(menu_item.text+"\n")

        if menu.caller.text == "Push":

            if menu_item.text == "Easy":
                #Clearing previous widgets
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in push[0] + push[1] + push[2]:
                            self.remove_widget(child)

                push_e = {}

                for ex,y in zip(push[0], np.arange(0.73,-1,-0.05)):
                    push_e[round(y,2)] = ex
                
                for pos,ex in push_e.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.2, 'center_y':float(pos)},
                        on_release = self.selected_push,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)


            elif menu_item.text == "Medium":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in push[0] + push[1] + push[2]:
                            self.remove_widget(child)

                push_m = {}

                for ex,y in zip(push[1], np.arange(0.73,-1,-0.05)):
                    push_m[round(y,2)] = ex
                
                for pos,ex in push_m.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.2, 'center_y':float(pos)},
                        on_release = self.selected_push,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)

            elif menu_item.text == "Hard":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in push[0] + push[1] + push[2]:
                            self.remove_widget(child)

                push_h = {}

                for ex,y in zip(push[2], np.arange(0.73,-1,-0.05)):
                    push_h[round(y,2)] = ex
                
                for pos,ex in push_h.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.2, 'center_y':float(pos)},
                        on_release = self.selected_push,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)


        if menu.caller.text == "Pull":
            if menu_item.text == "Easy":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in pull[0] + pull[1] + pull[2]:
                            self.remove_widget(child)

                pull_e = {}

                for ex,y in zip(pull[0], np.arange(0.73,-1,-0.05)):
                    pull_e[round(y,2)] = ex
                
                for pos,ex in pull_e.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.505, 'center_y':float(pos)},
                        on_release = self.selected_pull,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)


            elif menu_item.text == "Medium":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in pull[0] + pull[1] + pull[2]:
                            self.remove_widget(child)

                pull_m = {}

                for ex,y in zip(pull[1], np.arange(0.73,-1,-0.05)):
                    pull_m[round(y,2)] = ex
                
                for pos,ex in pull_m.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.505, 'center_y':float(pos)},
                        on_release = self.selected_pull,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)

            elif menu_item.text == "Hard":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in pull[0] + pull[1] + pull[2]:
                            self.remove_widget(child)

                pull_h = {}

                for ex,y in zip(pull[2], np.arange(0.73,-1,-0.05)):
                    pull_h[round(y,2)] = ex
                
                for pos,ex in pull_h.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.505, 'center_y':float(pos)},
                        on_release = self.selected_pull,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)


        if menu.caller.text == "Legs":
            if menu_item.text == "Easy":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip): #Checks if the widget exists or not. similar to type()
                        if child.text in leg[0] + leg[1] + leg[2]:
                            self.remove_widget(child)
                            
                leg_e = {}

                for ex,y in zip(leg[0], np.arange(0.73,-1,-0.05)):
                    leg_e[round(y,2)] = ex
                
                for pos,ex in leg_e.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.8, 'center_y':float(pos)},
                        on_release = self.selected_legs,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)

            elif menu_item.text == "Medium":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in leg[0] + leg[1] + leg[2]:
                            self.remove_widget(child)

                leg_m = {}

                for ex,y in zip(leg[1], np.arange(0.73,-1,-0.05)):
                    leg_m[round(y,2)] = ex
                
                for pos,ex in leg_m.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.8, 'center_y':float(pos)},
                        on_release = self.selected_legs,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)

            elif menu_item.text == "Hard":
                #Clearing previous widgets.
                for child in self.children[:]:
                    if isinstance(child, MDChip):
                        if child.text in leg[0] + leg[1] + leg[2]:
                            self.remove_widget(child)

                leg_h = {}

                for ex,y in zip(leg[2], np.arange(0.73,-1,-0.05)):
                    leg_h[round(y,2)] = ex
                
                for pos,ex in leg_h.items():
                    chip = MDChip(
                        text= ex,
                        pos_hint = {'center_x':0.8, 'center_y':float(pos)},
                        on_release = self.selected_legs,
                        check = True
                        )
                    chip.color = chip_color
                    chip.icon = "coffee"
                    self.add_widget(chip)


    #Creating a list of selected exercises.
    def selected_push(self, chip_widget):
        if chip_widget.color == chip_color:
            #self.root.remove_widget(chip_widget) #Root refers to the parent they are inside (Screen)
            chip_widget.color = selected_color
            if chip_widget.text not in push_list:
                push_list.append(chip_widget.text)
        else:
            chip_widget.color = chip_color
            push_list.remove(chip_widget.text)
        print(f"Push : {push_list}", chip_widget.pos_hint)

    def selected_pull(self, chip_widget):
        if chip_widget.color == chip_color:
            #self.root.remove_widget(chip_widget) #Root refers to the parent they are inside (Screen)
            chip_widget.color = selected_color
            if chip_widget.text not in pull_list:
                pull_list.append(chip_widget.text)
        else:
            chip_widget.color = chip_color
            pull_list.remove(chip_widget.text)
        print(f"Pull : {pull_list}")

    def selected_legs(self, chip_widget):
        if chip_widget.color == chip_color:
            #self.root.remove_widget(chip_widget) #Root refers to the parent they are inside (Screen)
            chip_widget.color = selected_color
            if chip_widget.text not in leg_list:
                leg_list.append(chip_widget.text)
        else:
            chip_widget.color = chip_color
            leg_list.remove(chip_widget.text)
        print(f"Legs : {leg_list}")


    def submit(self, obj):

        if self.ids.plan_name.text is "":
            dialog = "Please Enter a Plan Name"
            plan_name = "Error"
        else:
            dialog = f"You successfully created a plan named : {self.ids.plan_name.text}"
            plan_name = "Success"
        
        for child in self.children[:]:
            if isinstance(child, MDChip):
                self.remove_widget(child)
        push_list.clear()
        pull_list.clear()
        leg_list.clear()

        close_btn = MDRectangleFlatButton(text = "Close", on_release = self.close_dial)
        self.dial =  MDDialog(
            title = plan_name,
            text  = dialog,
            buttons= [close_btn],
            )
        self.dial.open()

    
    def close_dial(self, obj):
        self.dial.dismiss()


class DemoApp(MDApp):
    def build(self): #Screen() is present in this function, widget positioning is done here
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_hue = "500"
        self.theme_cls.theme_style = "Dark"

        return BuildApp()
        
DemoApp().run()
