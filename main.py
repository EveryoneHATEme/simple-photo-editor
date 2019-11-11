import sys
import importlib
import inspect
from operator import attrgetter
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PIL import Image, ImageQt

from UIelems import Ui_MainWindow
from draw import TransposeHandler, AdjustmentHandler, FilterHandler, BlurHandler
from history import HistoryHandler

OFF_SS = 'border: 1px solid gray'
ON_SS = 'border: 1px solid blue'


class PhotoEditorApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.default_image = None
        self.filters_loaded = False
        self.blurs_loaded = False
        self.saved = True
        self.rotation = 0
        self.horizontal_flip = False
        self.vertical_flip = False
        self.brightness = 50
        self.contrast = 50
        self.sharpness = 50
        self.crop = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        self.filename = None
        self.history_manager = None
        self.write = True
        self.current_filter = 'По_умолчанию'
        self.current_blur = 'По_умолчанию'
        self.initUI()
        self.filter_labels_list = [self.default_fliter_label, self.black_white_filter_label,
                                   self.sepia_filter_label, self.negative_filter_label]
        self.blurs_labels_list = [self.default_blur_label, self.horizontal_blur_label, self.vertical_blur_label]

    def set_default_values(self):
        """Устанавливает значения по умолчанию,
         используется при открытии файла или при нажатии кнопки Reset"""
        self.rotation = 0
        self.saved = True
        self.horizontal_flip = False
        self.vertical_flip = False
        self.filters_loaded = False
        self.blurs_loaded = False
        self.brightness = 50
        self.contrast = 50
        self.sharpness = 50
        self.crop = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        self.current_filter = 'По_умолчанию'
        self.current_blur = 'По_умолчанию'
        self.write = True
        for slider in self.crop_sliders:
            slider.setValue(100)
        for slider in self.adjusting_sliders:
            slider.setValue(50)
        for label in self.filter_labels:
            label.flag = False
            label.setStyleSheet(OFF_SS)
        self.default_fliter_label.setStyleSheet(ON_SS)
        self.default_fliter_label.flag = True
        for label in self.blur_labels:
            label.flag = False
            label.setStyleSheet(OFF_SS)
        self.default_blur_label.setStyleSheet(ON_SS)
        self.default_blur_label.flag = True

    def initUI(self):
        """Инициализирует пользовательский интерфейс
        Подключает функции к кнопкам интерфейса,
        а также отображает интерфейс"""
        self.setupUi(self)
        self.rotate_minus90_button.clicked.connect(self.rotate_minus90)
        self.rotate_minus90_button.clicked.connect(self.update_image)
        self.rotate_plus90_button.clicked.connect(self.rotate_plus90)
        self.rotate_plus90_button.clicked.connect(self.update_image)
        self.flip_horizontal_button.clicked.connect(self.flip_horizontal)
        self.flip_horizontal_button.clicked.connect(self.update_image)
        self.flip_vertical_button.clicked.connect(self.flip_vertical)
        self.flip_vertical_button.clicked.connect(self.update_image)
        self.actionOpen.triggered.connect(self.open_image)
        self.actionSave.triggered.connect(self.save_image)
        self.actionReset.triggered.connect(self.reset)
        self.actionAddFilter.triggered.connect(self.add_filter)
        self.brightness_slider.sliderReleased.connect(self.change_brightness)
        self.brightness_slider.sliderReleased.connect(self.update_image)
        self.contrast_slider.sliderReleased.connect(self.change_contrast)
        self.contrast_slider.sliderReleased.connect(self.update_image)
        self.sharpness_slider.sliderReleased.connect(self.change_sharpness)
        self.sharpness_slider.sliderReleased.connect(self.update_image)
        self.crop_left_slider.sliderReleased.connect(self.crop_left_trigger)
        self.crop_left_slider.sliderReleased.connect(self.update_image)
        self.crop_right_slider.sliderReleased.connect(self.crop_right_trigger)
        self.crop_right_slider.sliderReleased.connect(self.update_image)
        self.crop_top_slider.sliderReleased.connect(self.crop_top_trigger)
        self.crop_top_slider.sliderReleased.connect(self.update_image)
        self.crop_bottom_slider.sliderReleased.connect(self.crop_bottom_trigger)
        self.crop_bottom_slider.sliderReleased.connect(self.update_image)
        self.default_fliter_label.clicked.connect(self.activate_filter)
        self.black_white_filter_label.clicked.connect(self.activate_filter)
        self.sepia_filter_label.clicked.connect(self.activate_filter)
        self.negative_filter_label.clicked.connect(self.activate_filter)
        self.default_blur_label.clicked.connect(self.activate_blur)
        self.horizontal_blur_label.clicked.connect(self.activate_blur)
        self.vertical_blur_label.clicked.connect(self.activate_blur)
        self.default_fliter_label.resizeEvent = self.set_filters_thumbnails
        self.default_blur_label.resizeEvent = self.set_blurs_thumbnails
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.menu_tab.setVisible(False)
        self.image_label.setText('Для того, чтобы начать, загрузите фото')
        self.show()

    def update_image(self):
        """Обновляет отображаемое изображение, применяет необходимые функции
        Вызывается при любом изменении изобраения"""
        self.image = self.default_image.copy()
        for key, value in self.crop.items():
            self.image = TransposeHandler.crop(self.image, key, value)
        self.image = TransposeHandler.rotate(self.image, self.rotation)
        if self.horizontal_flip:
            self.image = TransposeHandler.horizontal_flip(self.image)
        if self.vertical_flip:
            self.image = TransposeHandler.vertical_flip(self.image)
        self.image = self.normalize_image(self.image)

        self.image = AdjustmentHandler.brightness(self.image, self.brightness)
        self.image = AdjustmentHandler.contrast(self.image, self.contrast)
        self.image = AdjustmentHandler.sharpness(self.image, self.sharpness)

        for label in self.filter_labels_list:
            print(f'{label.name}: {label.flag}')

        if any(map(attrgetter('flag'), self.filter_labels_list)):
            for label in self.filter_labels_list:
                if label.flag:
                    self.image = label.func(self.image)
                    self.current_filter = label.name
                    label.setStyleSheet(ON_SS)
                    break

        for label in self.blurs_labels_list:
            print(f'{label.name}: {label.flag}')

        if self.horizontal_blur_label.flag:
            self.image = self.horizontal_blur_label.func(self.image)
            self.horizontal_blur_label.setStyleSheet(ON_SS)
            self.current_blur = self.horizontal_blur_label.name
        elif self.vertical_blur_label.flag:
            self.image = self.vertical_blur_label.func(self.image)
            self.vertical_blur_label.setStyleSheet(ON_SS)
            self.current_blur = self.vertical_blur_label.name
        else:
            self.default_blur_label.setStyleSheet(ON_SS)
            self.current_blur = 'По_умолчанию'

        self.image_label.setPixmap(ImageQt.toqpixmap(self.image))
        self.saved = False
        if self.write and self.history_manager is not None:
            self.history_manager.write()
        self.write = True

    def normalize_image(self, image: Image.Image):
        """Изменяет размеры изображения для адекватного отображения"""
        if image.height > image.width and image.height > self.image_label.height():
            k = image.height / self.image_label.height()
            return image.resize((int(image.width / k), int(image.height / k)))
        if image.width > image.height and image.width > self.image_label.width():
            k = image.width / self.image_label.width()
            return image.resize((int(image.width / k), int(image.height / k)))
        return image

    def open_image(self):
        """Открывает изображение, выбранное пользователем, вызывает функции для отображения миниатюр"""
        if not self.saved:
            flag = QMessageBox.question(self, '', 'Есть несохраненные изменения\nВы точно хотите продолжить?',
                                        QMessageBox.Yes, QMessageBox.No)
            if flag == QMessageBox.No:
                return
        self.filename = QFileDialog.getOpenFileName(self, 'Выберите изображение', '', 'Image (*.jpg *.png)')[0]
        if self.filename != '':
            self.menu_tab.setVisible(True)
            image = ImageQt.toqpixmap(self.normalize_image(Image.open(self.filename)))
            self.image_label.setText('')
            self.image_label.setPixmap(image)
            self.default_image = ImageQt.fromqpixmap(image)
            self.image = self.default_image.copy()
            self.set_default_values()
            self.set_filters_thumbnails(None)
            self.set_blurs_thumbnails(None)
            self.history_manager = HistoryHandler(self, self.filename)
            self.update_image()

    def set_filters_thumbnails(self, event):
        """Устанавливает миниатюры для виджетов во вкладке Фильтры
        Вызывается после изменения размеров одного из виджетов, так как изначально
        виджеты имеют неправильные размеры"""
        img = TransposeHandler.resize(self.default_image, self.default_fliter_label.width(),
                                      self.default_fliter_label.height())
        self.default_fliter_label.setPixmap(ImageQt.toqpixmap(img))
        self.black_white_filter_label.setPixmap(ImageQt.toqpixmap(FilterHandler.black_white(img)))
        self.sepia_filter_label.setPixmap(ImageQt.toqpixmap(FilterHandler.sepia(img)))
        self.negative_filter_label.setPixmap(ImageQt.toqpixmap(FilterHandler.negative(img)))
        for label in self.filter_labels_list:
            label.setPixmap(ImageQt.toqpixmap(label.func(img)))
        self.filters_loaded = True

    def set_blurs_thumbnails(self, event):
        """Устанавливает миниатюры для виджетов во вкладке Размытие
        Вызывается после изменения размеров одного из виджетов, так как изначально
        виджеты имеют неправильные размеры"""
        img = TransposeHandler.resize(self.default_image, self.default_blur_label.width(),
                                      self.default_blur_label.height())
        self.default_blur_label.setPixmap(ImageQt.toqpixmap(img))
        self.horizontal_blur_label.setPixmap(ImageQt.toqpixmap(BlurHandler.horizontal_blur(img)))
        self.vertical_blur_label.setPixmap(ImageQt.toqpixmap(BlurHandler.vertical_blur(img)))
        self.blurs_loaded = True

    def save_image(self):
        """Отображает диалоговое окно для сохранения"""
        filename = QFileDialog.getSaveFileName(self, 'Сохранить как', '')[0]
        if filename != '':
            self.image.save(filename)
            self.saved = True

    def reset(self):
        self.set_default_values()
        self.update_image()

    def rotate_plus90(self):
        self.rotation += 90

    def rotate_minus90(self):
        self.rotation -= 90

    def flip_horizontal(self):
        self.horizontal_flip = not self.horizontal_flip

    def flip_vertical(self):
        self.vertical_flip = not self.vertical_flip

    def change_brightness(self):
        self.brightness = self.brightness_slider.value()

    def change_contrast(self):
        self.contrast = self.contrast_slider.value()

    def change_sharpness(self):
        self.sharpness = self.sharpness_slider.value()

    def crop_left_trigger(self):
        self.crop['left'] = 100 - self.crop_left_slider.value()

    def crop_right_trigger(self):
        self.crop['right'] = 100 - self.crop_right_slider.value()

    def crop_top_trigger(self):
        self.crop['top'] = 100 - self.crop_top_slider.value()

    def crop_bottom_trigger(self):
        self.crop['bottom'] = 100 - self.crop_bottom_slider.value()

    def off_all_blurs(self):
        for label in self.blurs_labels_list:
            label.setStyleSheet(OFF_SS)
            label.flag = False

    def activate_blur(self):
        self.off_all_blurs()
        self.sender().flag = True
        self.update_image()

    def off_all_filters(self):
        for label in self.filter_labels_list:
            label.setStyleSheet(OFF_SS)
            label.flag = False

    def activate_filter(self):
        self.off_all_filters()
        self.sender().flag = True
        self.update_image()

    def undo(self):
        self.history_manager.undo()
        self.write = False
        self.update_image()

    def redo(self):
        self.history_manager.redo()
        self.write = False
        self.update_image()

    def closeEvent(self, event):
        """Проверка на случай, если пользователь не сохранил изменения
        Вызывается при закрытии"""
        if not self.saved:
            flag = QMessageBox.question(self, '', 'Есть несохраненные изменения\nВы точно хотите выйти?',
                                        QMessageBox.Yes, QMessageBox.No)
            if flag == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def add_filter(self):
        """Добавление фильтра"""
        QMessageBox.warning(self, 'Предупреждение', 'Для правильной работы программы импортируйте файл .py,'
                                                    'содержащий функции, предназначенные только для обработки'
                                                    'изображений.\n'
                                                    'Функции должны принимать на вход объекты класса PIL.Image.Image'
                                                    'и возвращать так же объекты класса PIL.Image.Image.\n'
                                                    'Файл, содержащий функции должен находиться в одной директории '
                                                    'с main.py.',
                            QMessageBox.Ok)
        name = QFileDialog.getOpenFileName(self, 'Открыть файл с фильтрами', '', "Python file (*.py)")[0]
        if name:
            file = importlib.import_module(name.split('/')[-1].split('.')[0])
            for func in inspect.getmembers(file, inspect.isfunction):
                label = self.add_filter_label(func[1])
                label.flag = False
                label.name = func[0]
                label.func = func[1]
                self.filter_labels_list.append(label)
                label.clicked.connect(self.activate_filter)
                if self.filters_loaded:
                    img = TransposeHandler.resize(self.default_image, self.default_fliter_label.width(),
                                                  self.default_fliter_label.height())
                    label.setPixmap(ImageQt.toqpixmap(label.func(img)))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    redactor = PhotoEditorApp()
    sys.exit(app.exec())
