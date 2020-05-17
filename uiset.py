import logging
logger = logging.getLogger()
class Set:
    def __init__(self, ui):
        logger.debug('Initializing UI')
        self.plotItems = [
            ui.gView_img1, ui.gView_img2,
            ui.gView_trans1, ui.gView_trans2,
            ui.gView_output1, ui.gView_output2
        ]

        self.combo_imgs = [ui.combo_img1, ui.combo_img2]

        self.combo_comps = {
            1: [ui.combo_comp1_img, ui.combo_comp1],
            2: [ui.combo_comp2_img, ui.combo_comp2]
        }
        self.combo_comps[2][1].setCurrentIndex(1)

        self.sliders = [ui.slider_comp1, ui.slider_comp2]

        self.slider_vals = [ui.slider_val1, ui.slider_val2]

        self.checkboxs = [ui.comp1_uniform, ui.comp2_uniform]

        for i in range(len(self.sliders)):
            self.sliders[i].setMinimum(0)
            self.sliders[i].setMaximum(100)
            self.sliders[i].setTickInterval(1)
            self.sliders[i].setDisabled(True)
            self.checkboxs[i].setDisabled(True)
            self.combo_comps[i+1][0].setDisabled(True)
            self.combo_comps[i+1][1].setDisabled(True)
            self.slider_vals[i].setText('0%')

        ui.combo_mix.setDisabled(True)

        self.set_plots()

    def set_plots(self):
        for i in range(len(self.plotItems)):
            self.plotItems[i].showAxis('bottom', False)
            self.plotItems[i].showAxis('left', False)
            self.plotItems[i].setBackground('w')
            self.plotItems[i].invertY(True)

    def enable_sliders(self):
        for i in range(len(self.sliders)):
            self.sliders[i].setEnabled(True)
            self.checkboxs[i].setEnabled(True)
            self.combo_comps[i+1][0].setEnabled(True)
            self.combo_comps[i+1][1].setEnabled(True)


    def enable_checkboxs(self, bool):
        for i in range(len(self.checkboxs)):
            self.checkboxs[i].setEnabled(bool)

    def set_combo_img(self,current_index):
        for i in self.combo_comps.keys():
            self.combo_comps[i][0].blockSignals(True)
            self.combo_comps[i][0].setCurrentIndex(current_index)
            self.combo_comps[i][0].blockSignals(False)
