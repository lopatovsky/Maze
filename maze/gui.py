"""
Dude's Maze

The maze creator, generator and solver.
Choose your dude and let find his way towards the castle!

| Copyright © 2016 Lukáš Lopatovský

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

source: https://github.com/lopatovsky/Maze
All the graphic come from: http://opengameart.org/users/kenney
"""
import asyncio
from quamash import QEventLoop
from PyQt5 import QtWidgets, uic, QtGui, QtCore, QtSvg
import numpy
import glob
import os
from docutils.core import publish_parts
from . import maze_generator, maze_solver, actor

CELL_SIZE = 24

class image:
    def __init__( self, name, path, num = -3 ):
        self.name = name
        self.path = path
        self.num = num
        self.svg = QtSvg.QSvgRenderer( self.path )

IMG = {}

for (item, num) in [ ('Grass',0), ('Wall',-1), ('Wall2',-2), ('Castle',1), ('Dude1',2), ('Dude2',3), ('Dude3',4), ('Dude4',5), ('Dude5',6) ]:
    IMG[ item ] = image( item, 'img/' + item.lower() + '.svg', num )

LINES = {}
for item in glob.glob('img/lines/*.svg'):
    name = os.path.splitext( os.path.basename(item) )[0]
    LINES[ name ] = image( name, item)

ARROWS = {}
for item in glob.glob('img/arrows/*.svg'):
    name = os.path.splitext( os.path.basename(item) )[0]
    ARROWS[ name ] = image( name, item)

DIR_TO_NUM = {b'^':0,b'>':1,b'v':2,b'<':3}

VALUE_ROLE = QtCore.Qt.UserRole


class GridWidget(QtWidgets.QWidget):

    def __init__(self, array):

        super().__init__()
        self.cell_size = CELL_SIZE
        self.array = array
        self.set_grid_size()
        self.play_mode = False;
        self.dudes = {}

    def _ptol(self,x,y):
        return y // self.cell_size, x // self.cell_size

    def _ltop(self, row,column):
        return column * self.cell_size , row * self.cell_size

    def set_grid_size(self):
        # Bludiště může být jinak velké, tak musíme změnit velikost Gridu;
        rows, cols = self.array.shape
        size = self._ltop(rows, cols)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def __get_paths(self, solved):


        paths = numpy.full( (*self.array.shape,4)  , b'0', dtype=('a',1))

        dudes = numpy.argwhere(self.array >= 2)

        for dude in dudes:
            try:
                path = solved.path( *dude )
            except ValueError:
                continue

            get_in = DIR_TO_NUM[ self.directions[ path[0] ] ]  #first p doesn't have in, use out instead

            for p in path:
                #if paths[ (*p) , get_in ] == b'1': break #optimization for too many dudes
                paths[ (*p) , get_in ] = b'1'
                if self.directions[p] == b'X': break
                get_out = DIR_TO_NUM[ self.directions[p] ]
                paths[ (*p) , get_out ] = b'1'
                get_in = (get_out + 2 ) % 4   # 0->2, 1->3, 2->0, 3->1

        return paths

    def update_actor( self, actor ):
        dude = self.dudes[ (actor.row, actor.column) ]
        pass

    def _animate_dude( self, point ):

        if point not in self.dudes:
            self.dudes[point] = actor.Actor(self, *point, self.array[point] )
        elif not self.dudes[point].kind == self.array[point]:
            self.dudes[point] = actor.Actor(self, *point, self.array[point]  )
        else:
            pass

        print(point)
        print( self.dudes[point].kind )




    def paintEvent(self, event):

        row_size, col_size = self.array.shape


        solved = maze_solver.analyze( self.array )
        self.directions = solved.directions

        paths = self.__get_paths( solved )

        painter = QtGui.QPainter(self)  # budeme kreslit

        paths_view = paths.view('S4')

        for row in range(row_size):
            for column in range(col_size):
                # získáme čtvereček, který budeme vybarvovat
                x, y = self._ltop(row, column)
                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size )

                color = QtGui.QColor(255, 255, 255)

                # vyplníme čtvereček barvou
                painter.fillRect(rect, QtGui.QBrush(color))

                #if self.play_mode:
                IMG['Grass'].svg.render(painter,rect)

                if not self.play_mode:

                    if paths_view[row,column][0] != b'0000':
                        LINES[ paths_view[row,column][0].decode("utf-8") ].svg.render(painter,rect)
                        if self.directions[row,column] != b'X':
                            ARROWS[ str(DIR_TO_NUM[self.directions[row,column] ])  ].svg.render(painter,rect)

                #TODO - space for more effective approach
                if self.array[row,column] != 0:
                    for img in IMG.values():
                        if self.array[row, column] == img.num:
                            if self.play_mode and img.num >= 2:
                                self._animate_dude( (row,column) )
                            else:
                                img.svg.render(painter,rect)
        self.set_grid_size()

    def wheelEvent(self, event):

        if event.modifiers() == QtCore.Qt.ControlModifier:
            degrees = event.angleDelta().y() / 8
            self.cell_size += round(self.cell_size*degrees/100)
            event.accept()
        else:
            event.ignore()

        self.update()

    def mousePressEvent(self, event):

        row, column = self._ptol( event.x() , event.y() )

        shape = self.array.shape

        if 0 <= row < shape[0] and 0 <= column < shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                if not self.play_mode or self.array[row,column] == 0:
                    self.array[row,column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                if not self.play_mode or self.array[row,column] == -1:
                    self.array[row,column] = 0
            else:
                return

            self.update()



class Gui():

    def __init__(self):

        self.app = QtWidgets.QApplication([])
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)


        self.window = QtWidgets.QMainWindow()
        with open ('GUI/mainwindow.ui') as f:
            uic.loadUi(f,self.window)

        array = numpy.zeros((10,13), dtype=numpy.int8 )
        self.grid = GridWidget(array)

        scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea') # alebo aj QtWidgets.Qwidget - dedi
        scroll_area.setWidget( self.grid )

        self._action( 'actionNew').triggered.connect( self._new_dialog )
        self._action( 'actionOpen').triggered.connect( self._open_dialog )
        self._action( 'actionSave').triggered.connect( self._save_dialog )
        self._action( 'actionAbout').triggered.connect( self._about_dialog )

        self._add_palette()


        self.play_action = self._action('actionPlay')
        self.play_action.triggered.connect( self._play )


        self.toolbar = self.window.findChild(QtWidgets.QToolBar, 'toolBar')



    def _action( self, action_name ):
        return self.window.findChild(QtWidgets.QAction, action_name )

    def _add_palette( self ):
        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')
        self._fill_palette( )

    def _open_dialog(self):

        dialog = QtWidgets.QFileDialog(self.window)
        result = dialog.exec()

        if result == QtWidgets.QDialog.Rejected:
            return

        path = dialog.selectedFiles()[0]
        try:
            self.grid.array = numpy.loadtxt(path, dtype=numpy.int32)

        except OSError as e:
            self._alert_dialog( True, 'Error', 'File not found!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except ValueError as e:
            self._alert_dialog( True, 'Error', 'Corrupted file!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except IOError as e:
            self._alert_dialog( True, 'Error', 'Permission denied!', str(e), QtWidgets.QMessageBox.Warning )
            return
        except BaseException as e:
            self._alert_dialog( True, 'Weird Error', path , str(e), QtWidgets.QMessageBox.Warning )
            return

        self.grid.set_grid_size()
        self.grid.update()

    async def _update_time(self):
            value = 0
            while True:
                self.display.display(value)
                await asyncio.sleep(1)
                value += 1

    def _play(self):
        isChecked = self.play_action.isChecked()
        self.grid.play_mode = isChecked
        self.grid.update()

        if isChecked:
            self.grid.selected = -1
            self.palette.hide()
            self.display = QtWidgets.QLCDNumber()
            self.toolbar.addWidget( self.display )
            asyncio.ensure_future(self._update_time())
        else:
            self.palette.show()
            #self.display.hide()


    def _alert_dialog(self, modal, title, text, detail, icon):

        dialog = QtWidgets.QMessageBox(self.window)

        dialog.setWindowTitle(title)
        dialog.setText(text)
        if detail != '': dialog.setDetailedText(detail)
        dialog.setIcon(icon)
        if modal:
            result = dialog.exec()

            if result == QtWidgets.QDialog.Rejected:
                return
        else:
            dialog.show()

    def _about_dialog( self ):

        html = publish_parts(__doc__, writer_name='html')['html_body']
        self._alert_dialog( False, 'About', html , '', QtWidgets.QMessageBox.Information )

    def _save_dialog(self):

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.window)

        if not path:
            return
        try:
            numpy.savetxt(path, self.grid.array )
        except BaseException as e:
            self._alert_dialog( True, 'Save Error', path , str(e), QtWidgets.QMessageBox.Warning )
            return


    def _new_dialog(self):

        dialog = QtWidgets.QDialog(self.window)
        with open ('GUI/newmaze.ui') as f:
            uic.loadUi(f,dialog)
        result = dialog.exec()

        if result == QtWidgets.QDialog.Rejected:
            # Dialog uživatel zavřel nebo klikl na Cancel
            return

        # Načtení hodnot ze SpinBoxů
        cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
        rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()
        random = dialog.findChild(QtWidgets.QCheckBox, 'randomcheckBox').isChecked()  #TODO QButtonGroup + empty, file

        # Vytvoření nového bludiště
        if random:
            self.grid.array = maze_generator.generate_maze( cols, rows )
        else:
            self.grid.array = numpy.zeros((rows, cols), dtype=numpy.int32)


        self.grid.set_grid_size()

        self.grid.update() #TODO --when big resolution update only currently visible field

    def _add_item( self, palette, img ):

        item = QtWidgets.QListWidgetItem( img.name )
        icon = QtGui.QIcon( img.path )
        item.setIcon( icon )
        palette.addItem(item)
        item.setData( VALUE_ROLE, img.num )

    def _fill_palette( self ):


        for img in sorted(IMG.values(), key=lambda x: x.num ):
            self._add_item( self.palette, img )

        def item_activated( ):
            for item in self.palette.selectedItems():
                self.grid.selected = item.data(VALUE_ROLE)
                #row_num = palette.indexFromItem(item).row()

        self.palette.itemSelectionChanged.connect(item_activated )
        self.palette.setCurrentRow(1)


    def run(self):
        self.window.show()
        return self.loop.run_forever()

def main():

    gui = Gui()
    return gui.run()


