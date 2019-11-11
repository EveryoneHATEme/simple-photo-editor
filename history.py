import sqlite3


class HistoryHandler:
    def __init__(self, obj, filename):
        self.obj = obj
        self.table = filename.split('.')[0].split('/')[-1]
        self.connection = sqlite3.connect('edit_history.db')
        cur = self.connection.cursor()
        res = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table}';").fetchall()
        if len(res) == 0:
            cur.execute(f"CREATE TABLE {self.table} "
                        f"(id INTEGER PRIMARY KEY, rotation INTEGER, horizontal_flip BOOLEAN, "
                        f"vertical_flip BOOLEAN, brightness INTEGER, contrast INTEGER, "
                        f"sharpness INTEGER, crop_left INTEGER, crop_right INTEGER, "
                        f"crop_top INTEGER, crop_bottom INTEGER, filter STRING, "
                        f"blur STRING)")
            self.id = 0
        else:
            res = cur.execute(f"SELECT * FROM {self.table}").fetchall()
            if res:
                res = res[-1]
                self.id = res[0]
                self.obj.rotation = res[1]
                self.obj.horizontal_flip = res[2]
                self.obj.vertical_flip = res[3]
                self.obj.brightness = res[4]
                self.obj.brightness_slider.setValue(res[4])
                self.obj.contrast = res[5]
                self.obj.contrast_slider.setValue(res[5])
                self.obj.sharpness = res[6]
                self.obj.sharpness_slider.setValue(res[6])
                self.obj.crop['left'] = res[7]
                self.obj.crop_left_slider.setValue(res[7])
                self.obj.crop['right'] = res[8]
                self.obj.crop_right_slider.setValue(res[8])
                self.obj.crop['top'] = res[9]
                self.obj.crop_top_slider.setValue(res[9])
                self.obj.crop['bottom'] = res[10]
                self.obj.crop_bottom_slider.setValue(res[10])
                for label in self.obj.filter_labels:
                    if label.name == res[11]:
                        label.flag = True
                        break
                for label in self.obj.blur_labels:
                    if label.name == res[12]:
                        label.flag = True
                        break
            else:
                self.id = 0
        cur.close()
        self.connection.commit()

    def write(self):
        self.id += 1
        cur = self.connection.cursor()
        if cur.execute(f'SELECT * FROM {self.table} WHERE id >= {self.id}').fetchall():
            cur.execute(f'DELETE FROM {self.table} WHERE id >= {self.id}')
        cur.execute(f"INSERT INTO {self.table}(id, rotation, "
                    f"horizontal_flip, vertical_flip, brightness, "
                    f"contrast, sharpness, crop_left, crop_right, crop_top, crop_bottom, "
                    f"filter, blur) "
                    f"VALUES({self.id}, {self.obj.rotation}, {int(self.obj.horizontal_flip)}, "
                    f"{int(self.obj.vertical_flip)}, {self.obj.brightness}, "
                    f"{self.obj.contrast}, {self.obj.sharpness}, {self.obj.crop['left']}, "
                    f"{self.obj.crop['right']}, {self.obj.crop['top']}, {self.obj.crop['bottom']}, "
                    f" '{self.obj.current_filter}', '{self.obj.current_blur}')")
        cur.close()
        self.connection.commit()

    def undo(self):
        print('undo:')
        cur = self.connection.cursor()
        self.id -= 1 if self.id > 0 else 0
        if self.id > 0:
            res = cur.execute(f"SELECT * FROM {self.table} WHERE id={self.id}").fetchone()
            self.obj.rotation = res[1]
            self.obj.horizontal_flip = res[2]
            self.obj.vertical_flip = res[3]
            self.obj.brightness = res[4]
            self.obj.brightness_slider.setValue(res[4])
            self.obj.contrast = res[5]
            self.obj.contrast_slider.setValue(res[5])
            self.obj.sharpness = res[6]
            self.obj.sharpness_slider.setValue(res[6])
            self.obj.crop['left'] = res[7]
            self.obj.crop_left_slider.setValue(100 - res[7])
            self.obj.crop['right'] = res[8]
            self.obj.crop_right_slider.setValue(100 - res[8])
            self.obj.crop['top'] = res[9]
            self.obj.crop_top_slider.setValue(100 - res[9])
            self.obj.crop['bottom'] = res[10]
            self.obj.crop_bottom_slider.setValue(100 - res[10])
            for label in self.obj.filter_labels:
                print(label.name.strip("'"), res[11])
                if label.name.strip("'") == res[11]:
                    self.obj.off_all_filters()
                    label.flag = True
                    break
            for label in self.obj.blur_labels:
                print(label.name.strip("'"), res[12])
                if label.name.strip("'") == res[12]:
                    self.obj.off_all_blurs()
                    label.flag = True
                    break

    def redo(self):
        print('redo:')
        cur = self.connection.cursor()
        res = cur.execute(f'SELECT * FROM {self.table} WHERE id > {self.id}').fetchall()
        if res:
            res = res[0]
            self.obj.rotation = res[1]
            self.obj.horizontal_flip = res[2]
            self.obj.vertical_flip = res[3]
            self.obj.brightness = res[4]
            self.obj.brightness_slider.setValue(res[4])
            self.obj.contrast = res[5]
            self.obj.contrast_slider.setValue(res[5])
            self.obj.sharpness = res[6]
            self.obj.sharpness_slider.setValue(res[6])
            self.obj.crop['left'] = res[7]
            self.obj.crop_left_slider.setValue(100 - res[7])
            self.obj.crop['right'] = res[8]
            self.obj.crop_right_slider.setValue(100 - res[8])
            self.obj.crop['top'] = res[9]
            self.obj.crop_top_slider.setValue(100 - res[9])
            self.obj.crop['bottom'] = res[10]
            self.obj.crop_bottom_slider.setValue(100 - res[10])
            for label in self.obj.filter_labels:
                if label.name.strip("'") == res[11]:
                    self.obj.off_all_filters()
                    label.flag = True
                    break
            for label in self.obj.blur_labels:
                if label.name.strip("'") == res[12]:
                    self.obj.off_all_blurs()
                    label.flag = True
                    break
            self.id += 1
