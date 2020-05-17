import sys
import numpy as np
import pyqtgraph as pg
import logging
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from modesEnum import Modes
from ui import Ui_MainWindow
from uiset import Set
from imageModel import ImageModel

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename='logging.txt', level=logging.DEBUG, format=LOG_FORMAT, filemode='w')
logger = logging.getLogger()
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        logger.debug('Begin the program')
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui_set = Set(self.ui)
        self.images = [None, None]
        self.slider_vals =[[0,0],[0,0]]


        ############## Connections #################################
        logger.debug('Connections')
        self.ui.add_btn.clicked.connect(self.add_img)
        self.ui.combo_mix.currentIndexChanged.connect(lambda index: self.set_sliders(index))
        for i in range(len(self.ui_set.combo_imgs)):
            self.connect_combo_imgs(i)
        for i in self.ui_set.combo_comps.keys():
            self.connect_combo_comps(i)
        for i in range(len(self.ui_set.sliders)):
            self.ui_set.sliders[i].valueChanged.connect(self.mix)
        for i in range(len(self.ui_set.checkboxs)):
            self.ui_set.checkboxs[i].clicked.connect(self.mix)

    def connect_combo_imgs(self, i):
        self.ui_set.combo_imgs[i].currentIndexChanged.connect(lambda n:self.draw(i, n))

    def draw(self, img_index, attr_index):
        logger.debug('choosing {} of image{}'.format(self.ui_set.combo_imgs[img_index].currentText(),img_index+1))
        if attr_index == 0:
            logger.debug('Drawing Magnitude of image{}'.format(img_index+1))
            self.draw_on(img_index + 2, 20 * np.log10(self.images[img_index].attrs[0]))
        else:
            logger.debug('Drawing {} of image{}'.format(self.ui_set.combo_imgs[img_index].currentText(),img_index+1))
            self.draw_on(img_index + 2, self.images[img_index].attrs[attr_index])

    def connect_combo_comps(self,i):
        if i == 1:
            self.ui_set.combo_comps[1][1].currentIndexChanged.connect(lambda n: self.combine(n, 2))
            self.ui_set.combo_comps[1][0].currentIndexChanged.connect(self.mix)
        if i == 2:
            self.ui_set.combo_comps[2][1].currentIndexChanged.connect(lambda n: self.combine(n, 1))
            self.ui_set.combo_comps[2][0].currentIndexChanged.connect(self.mix)

    def combine(self, current_index, index_another_combo):
        logger.debug('Handling Component combobox')
        if current_index == 0:
            self.ui_set.combo_comps[index_another_combo][1].setCurrentIndex(1)
            self.ui_set.enable_checkboxs(True)
        if current_index == 1:
            self.ui_set.combo_comps[index_another_combo][1].setCurrentIndex(0)
            self.ui_set.enable_checkboxs(True)
        if current_index == 2:
            self.ui_set.combo_comps[index_another_combo][1].setCurrentIndex(3)
            self.ui_set.enable_checkboxs(False)
        if current_index == 3:
            self.ui_set.combo_comps[index_another_combo][1].setCurrentIndex(2)
            self.ui_set.enable_checkboxs(False)
        self.mix()

    def set_sliders(self, current_index):  # for keep track of sliders of the user change form output1 to output2
        logger.debug('OutPut Changed')
        logger.debug('Drawing On Output{}'.format(current_index))
        logger.debug('getting the previous values of sliders')
        for i in range(len(self.ui_set.sliders)):
            self.ui_set.sliders[i].blockSignals(True)
            self.ui_set.sliders[i].setValue(self.slider_vals[current_index][i])
            self.ui_set.sliders[i].setValue(self.slider_vals[current_index][i])
            self.ui_set.sliders[i].blockSignals(False)
        self.mix()

    def draw_on(self, plot_index, data):
        logger.debug('Draw')
        self.ui_set.plotItems[plot_index].clear()
        img = pg.ImageItem()
        self.ui_set.plotItems[plot_index].addItem(img)
        self.ui_set.plotItems[plot_index].setXRange(min=0, max=data.shape[0], padding=0)
        self.ui_set.plotItems[plot_index].setYRange(min=0, max=data.shape[1], padding=0)
        img.setImage(data.T)
        self.ui_set.plotItems[plot_index].autoRange(padding=0)

    def is_there_image(self):
        logger.debug('Checking if there is image !')
        for i in range(len(self.images)):
            if self.images[i] is not None:
                return True
        return False

    def add_img(self):
        logger.debug('Add Image button clicked ')
        current_img = self.ui.combo_add.currentIndex()
        filename = QFileDialog(self).getOpenFileName()
        path = filename[0]
        if path != '':
            if not self.is_there_image():
                self.ui_set.set_combo_img(current_img)
            image = ImageModel(url=path)
            if self.check_size(image,current_img):
                logger.debug('Opening the image')
                self.images[current_img] = image
                self.draw_on(current_img, self.images[current_img].img_data)
                self.draw_on(current_img + 2, 20 * np.log10(self.images[current_img].attrs[0]))
                self.ui_set.enable_sliders()
                self.ui.combo_mix.setEnabled(True)
                self.mix()
            else:
                logger.debug('Error the Images must be the same size')
                msg = QMessageBox()
                msg.setWindowTitle('ERROR')
                msg.setText('Pls add images of the same size')
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()

    def check_size(self,image,current_index):
        logger.debug('check the size of image ')
        if current_index == 0:
            try:
                if self.images[1].img_data.shape == image.img_data.shape:
                    return True
                else:
                    return False
            except: # There is one image only
                return True
        else:
            try:
                if self.images[0].img_data.shape == image.img_data.shape:
                    return True
                else:
                    return False
            except: # There is one image only
                return True

    def mix(self):
        logger.debug('Getting values to mix')
        current_output = self.ui.combo_mix.currentIndex()
        comp_imgs_index = [self.ui_set.combo_comps[i][0].currentIndex() for i in self.ui_set.combo_comps.keys()]  # image index for each component
        comp_attrs_index = [self.ui_set.combo_comps[i][1].currentIndex() for i in self.ui_set.combo_comps.keys()] # attribute index for each component
        vals = np.array([self.ui_set.sliders[i].value()/100 for i in range(len(self.ui_set.sliders))])            # value for each slider

        for i in self.ui_set.combo_comps.keys():
            logger.debug('choosing {} of {} of component{}'.format(self.ui_set.combo_comps[i][1].currentText(),
                                                                        self.ui_set.combo_comps[i][0].currentText(), i))

        logger.debug('slider_val1 = {}, slider_val2 = {}'.format(vals[0],vals[1]))

        for i in range(len(self.ui_set.slider_vals)):
            self.ui_set.slider_vals[i].setText('{}%'.format(int(vals[i]*100)))

        self.slider_vals[current_output] = vals*100

        # Checking the presence of images
        logger.debug('Checking the presence of images')
        for i in comp_imgs_index:
            if self.images[i] is None:
                logger.debug('There is no image{} to be mixed '.format(i+1))
                msg = QMessageBox()
                msg.setWindowTitle('ERROR')
                msg.setText('Pls add image {}'.format(i+1))
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()
                if i == 0:
                    self.ui_set.set_combo_img(1)
                else:
                    self.ui_set.set_combo_img(0)
                return
        logger.debug('Mix')
        if comp_imgs_index[0] != comp_imgs_index[1]:   # Two Different images
            if comp_attrs_index[0] == 0:
                if self.ui_set.checkboxs[0].isChecked() and self.ui_set.checkboxs[1].isChecked():
                    logger.debug('Uniform Magnitude, Uniform Phase')
                    mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.uniform_mag_phase)
                elif self.ui_set.checkboxs[0].isChecked():
                    logger.debug('Uniform Magnitude')
                    mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.uniform_mag)
                elif self.ui_set.checkboxs[1].isChecked():
                    logger.debug('Uniform Phase')
                    mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.uniform_phase)
                else:
                    mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.magnitudeAndPhase)
            elif comp_attrs_index[0] == 1:
                if self.ui_set.checkboxs[0].isChecked() and self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.uniform_mag_phase)
                elif self.ui_set.checkboxs[0].isChecked():
                    mix = self.images[comp_imgs_index[1]].mix(self.images[comp_imgs_index[0]], vals[1], vals[0], Modes.uniform_phase)
                elif self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[1]].mix(self.images[comp_imgs_index[0]], vals[1], vals[0], Modes.uniform_mag)
                else:
                    mix = self.images[comp_imgs_index[1]].mix(self.images[comp_imgs_index[0]], vals[1], vals[0], Modes.magnitudeAndPhase)
            elif comp_attrs_index[0] == 2:
                mix = self.images[comp_imgs_index[0]].mix(self.images[comp_imgs_index[1]], vals[0], vals[1], Modes.realAndImaginary)
            else:
                mix = self.images[comp_imgs_index[1]].mix(self.images[comp_imgs_index[0]], vals[1], vals[0], Modes.realAndImaginary)
        else:  # There is only one image
            if comp_attrs_index[0] == 0:
                if self.ui_set.checkboxs[0].isChecked() and self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.uniform_mag_phase)
                elif self.ui_set.checkboxs[0].isChecked():
                    mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.uniform_mag)
                elif self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.uniform_phase)
                else:
                    mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.magnitudeAndPhase)
            elif comp_attrs_index[0] == 1:
                if self.ui_set.checkboxs[0].isChecked() and self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.uniform_mag_phase)
                elif self.ui_set.checkboxs[0].isChecked():
                    mix = self.images[comp_imgs_index[1]].mix(None, vals[1], vals[0], Modes.uniform_phase)
                elif self.ui_set.checkboxs[1].isChecked():
                    mix = self.images[comp_imgs_index[1]].mix(None, vals[1], vals[0], Modes.uniform_mag)
                else:
                    mix = self.images[comp_imgs_index[1]].mix(None, vals[1], vals[0], Modes.magnitudeAndPhase)
            elif comp_attrs_index[0] == 2:
                mix = self.images[comp_imgs_index[0]].mix(None, vals[0], vals[1], Modes.realAndImaginary)
            else:
                mix = self.images[comp_imgs_index[1]].mix(None, vals[1], vals[0], Modes.realAndImaginary)

        self.draw_on(current_output + 4, mix)


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
